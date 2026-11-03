# Core Fundamentals & Invariants: Modern AuthN & AuthZ

This document articulates the axiomatic invariants, theoretical grounding, mental models, idiomatic code implementations, architectural tradeoffs, and failure modes governing this topic.

---

## 1. Axiomatic Core Invariants

### Invariant 1: Token Signature Verification Invariant
$$
\text{ValidToken}(T) \iff \text{VerifySig}(T.\text{header}, T.\text{payload}, K_{pub}^{\text{kid}}) \land T.\text{exp} > t_{now} \land T.\text{iss} = I_{trusted} \land T.\text{aud} = A_{expected} \land T.\text{nbf} \le t_{now}.
$$
**Implications & Guarantees**: A token cannot be trusted without verifying the cryptographic signature against an authoritative, unexpired public key matching the key ID (kid).

### Invariant 2: Zanzibar External Consistency & New-Enemy Invariant
$$
\forall \text{ check requests with snapshot token } z, \text{ evaluation time } t_{eval} \ge t_{write}(z).
$$
**Implications & Guarantees**: Prevents ACL evaluation from observing stale permissions when an object's ACL was updated prior to the request, completely eliminating unauthorized access leaks.

### Invariant 3: PKCE Code Verification Invariant
$$
\text{Base64URL}(\text{SHA256}(\text{code\_verifier})) = \text{code\_challenge}.
$$
**Implications & Guarantees**: Ensures that the client exchanging the authorization code for tokens is the exact same client that initiated the authorization flow, preventing code interception on public devices.

---

## 2. Core Mental Models

### Mental Model 1: Identity vs Capability: Who You Are vs What You Hold
Authentication identifies the actor (Subject). Authorization determines capabilities over target Resources. Modern systems avoid ambient authority (passing user credentials everywhere) and instead pass attenuated capabilities.

### Mental Model 2: The ReBAC Graph Model (Google Zanzibar)
Permissions are modeled as directed edges in a graph: (object, relation, user). 'doc:123#viewer@user:alice'. Group memberships are relations: 'doc:123#viewer@group:eng#member'. Permission evaluation is reachability in a directed graph.

---

## 3. Idiomatic Code Examples

### Minimal Google Zanzibar ReBAC Engine with Group Expansion and Cycle Detection
```python
from typing import Set, Tuple, Dict, List

# Tuple format: (object_namespace, object_id, relation, user_namespace, user_id, user_relation)
# E.g. ("doc", "readme", "viewer", "group", "engineers", "member")
# Or direct user: ("doc", "readme", "viewer", "user", "alice", None)

class ZanzibarReBACEngine:
    def __init__(self):
        self.tuples: Set[Tuple[str, str, str, str, str, Optional[str]]] = set()

    def add_tuple(self, obj_ns: str, obj_id: str, relation: str, 
                  user_ns: str, user_id: str, user_rel: str = None) -> None:
        self.tuples.add((obj_ns, obj_id, relation, user_ns, user_id, user_rel))

    def check(self, obj_ns: str, obj_id: str, permission: str, 
              user_ns: str, user_id: str) -> bool:
        """Evaluates whether (user_ns, user_id) has permission on (obj_ns, obj_id)."""
        visited: Set[Tuple[str, str, str]] = set()

        def _evaluate(curr_ns: str, curr_id: str, curr_rel: str) -> bool:
            state_key = (curr_ns, curr_id, curr_rel)
            if state_key in visited:
                return False  # Prevent infinite loops in cyclic group memberships
            visited.add(state_key)

            for t in self.tuples:
                o_ns, o_id, r, u_ns, u_id, u_rel = t
                if o_ns == curr_ns and o_id == curr_id and r == curr_rel:
                    # Direct user match
                    if u_rel is None and u_ns == user_ns and u_id == user_id:
                        return True
                    # Indirect group relation expansion
                    if u_rel is not None:
                        if _evaluate(u_ns, u_id, u_rel):
                            return True
            return False

        return _evaluate(obj_ns, obj_id, permission)
```
**Analysis**: Demonstrates relationship-based authorization with recursive set-rewrites, group membership expansion, and cycle detection.

---

## 4. Architectural Tradeoffs

### Stateless JWTs vs Centralized Session Tokens
Stateless JWTs eliminate database lookups at the API gateway, enabling massive scale. However, immediate revocation is difficult without maintaining a distributed revocation blocklist. Centralized sessions support instant revocation, but require every RPC to query a shared session store (Redis/DB), creating a central point of failure and latency bottleneck.

### RBAC vs ReBAC
RBAC is simple to manage and performant for coarse roles (Admin, Editor), but fails to scale when permissions depend on individual resource ownership or dynamic hierarchical relationships. ReBAC handles arbitrary resource graphs, but requires complex graph reachability queries that must be cached carefully.

---

## 5. Common Failure Modes & Anti-Patterns

### Failure Mode 1: JWT 'none' Algorithm Vulnerability
- **Root Cause**: Vulnerable libraries accept tokens with alg: 'none' or fail to enforce that the key used for signature verification matches the expected cryptographic algorithm.
- **Mitigation & Invariant Defense**: Strictly whitelist allowed verification algorithms (e.g. RS256, EdDSA only) and reject alg: none unconditionally.

### Failure Mode 2: The New-Enemy Problem in ReBAC
- **Root Cause**: A user removes an unauthorized person from a document ACL. If the user then writes sensitive data and an ACL evaluation evaluates against a stale read replica, the removed person can still view the new data.
- **Mitigation & Invariant Defense**: Enforce Zanzibar external consistency using snapshot tokens (Zookies) bound to Spanner commit timestamps.
