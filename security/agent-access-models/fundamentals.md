# Core Fundamentals & Invariants: Access Models for Autonomous Agents

This document articulates the axiomatic invariants, theoretical grounding, mental models, idiomatic code implementations, architectural tradeoffs, and failure modes governing this topic.

---

## 1. Axiomatic Core Invariants

### Invariant 1: Non-Ambient Capability Invariant
$$
\forall \text{ tool execution } T(P), \text{ Agent must present capability token } C \text{ such that } \text{Scope}(C) \supseteq \text{RequiredPerms}(T, P) \land \text{Subject}(C) = \text{Principal}.
$$
**Implications & Guarantees**: Agents do not inherit broad ambient credentials (e.g. root API keys); every action requires an explicit, attenuated capability token bound to the specific operation.

### Invariant 2: Monotonic Privilege Attenuation Invariant
$$
\forall \text{ delegation step } i \to i+1, \text{Scope}(C_{i+1}) \subseteq \text{Scope}(C_i) \land \text{TTL}(C_{i+1}) \le \text{TTL}(C_i).
$$
**Implications & Guarantees**: As capabilities are delegated from User to Lead Agent to Subagent to Tool, privileges can only shrink or remain equal, never expand.

### Invariant 3: Dual-Control Cryptographic HITL Invariant
$$
\forall T \in \text{HighConsequenceTools}, \text{Execute}(T) \implies \text{VerifySig}(K_{user}, \text{Digest}(T, P)).
$$
**Implications & Guarantees**: High-risk actions (e.g. wire transfers, deletions, public posts) cannot be authorized by the LLM alone; they require an out-of-band cryptographic signature from the human principal.

---

## 2. Core Mental Models

### Mental Model 1: The Confused Deputy in Natural Language Systems
In 1988, Norm Hardy identified that a deputy program with broad authority can be tricked by an unauthorized client into misusing its authority. In LLMs, natural language prompt injection is the ultimate confused deputy exploit: the untrusted user or external web page tricks the agent into using its legitimate tools maliciously.

### Mental Model 2: Macaroons and Decentralized Caveats
Macaroons are bearer tokens with cryptographic chained HMACs that allow contextual caveats (attenuations) to be appended by any intermediate hop without contacting the issuing authority. E.g., 'only valid for read operations', 'only valid before 10:00 AM', 'only valid for customer_id=123'.

---

## 3. Idiomatic Code Examples

### Chained HMAC Capability Token with Monotonic Caveat Attenuation
```python
import hmac
import hashlib
import time
from typing import List, Tuple

class AttenuatedCapabilityToken:
    """Implements HMAC-chained capability token with client-side caveat attenuation."""
    def __init__(self, token_id: str, secret_key: bytes):
        self.token_id = token_id
        self.caveats: List[str] = []
        # Initial signature = HMAC(secret_key, token_id)
        self.signature = hmac.new(secret_key, token_id.encode("utf-8"), hashlib.sha256).digest()

    def add_caveat(self, caveat: str) -> "AttenuatedCapabilityToken":
        """Attenuate token by chaining a new caveat to the signature."""
        new_token = AttenuatedCapabilityToken.__new__(AttenuatedCapabilityToken)
        new_token.token_id = self.token_id
        new_token.caveats = list(self.caveats) + [caveat]
        # New signature = HMAC(previous_signature, caveat)
        new_token.signature = hmac.new(self.signature, caveat.encode("utf-8"), hashlib.sha256).digest()
        return new_token

    def verify(self, secret_key: bytes, context: dict) -> bool:
        """Verify entire caveat chain from original secret key."""
        # Recompute signature from base key
        curr_sig = hmac.new(secret_key, self.token_id.encode("utf-8"), hashlib.sha256).digest()
        for caveat in self.caveats:
            key, val = caveat.split("=")
            # Check context validity
            if key == "max_time":
                if time.time() > float(val):
                    return False
            elif key == "allowed_tool":
                if context.get("tool") != val:
                    return False
            elif key == "read_only":
                if context.get("action") != "read":
                    return False
            # Advance HMAC chain
            curr_sig = hmac.new(curr_sig, caveat.encode("utf-8"), hashlib.sha256).digest()
        
        return hmac.compare_digest(curr_sig, self.signature)
```
**Analysis**: Demonstrates cryptographic capability attenuation: an agent can restrict its own token before passing it to a subagent, but cannot forge unattenuated tokens.

---

## 4. Architectural Tradeoffs

### MicroVM (Firecracker) vs Linux Container (gVisor/Docker)
Firecracker microVMs provide hardware-level virtualization isolation (KVM) with independent Linux kernels, booting in < 10ms with ~5MB memory footprint. gVisor runs inside container hosts with a user-space Go kernel intercepting syscalls. Firecracker provides stronger isolation against kernel zero-days, but lacks shared-filesystem flexibility.

### Client-Side Caveat Attenuation vs Centralized Token Minting
Chained HMAC tokens (Macaroons) allow intermediate agents to attenuate tokens offline without RPC calls to an auth server. However, token revocation requires maintaining an active blocklist or short expiration windows.

---

## 5. Common Failure Modes & Anti-Patterns

### Failure Mode 1: Ambient API Key Leakage via Agent Shell
- **Root Cause**: Storing an administrative OPENAI_API_KEY or AWS_SECRET_ACCESS_KEY in the agent's environment variables allows any untrusted Python script executed by the agent to print or exfiltrate the key.
- **Mitigation & Invariant Defense**: Never inject static keys into execution environments. Use dynamic metadata service with ephemeral credentials (e.g. AWS IAM roles for service accounts).

### Failure Mode 2: Transitive Delegation Scope Creep
- **Root Cause**: Agent A delegates a token to Agent B, which delegates to Agent C. Without monotonic attenuation checks, Agent B mints a broader token or strips expiration timestamps.
- **Mitigation & Invariant Defense**: Enforce RFC 8693 token exchange validating that requested scope is a strict subset of the caller's active scope.
