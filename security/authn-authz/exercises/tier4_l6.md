# Exercise TIER4_L6: Multi-Region Distributed Policy Engine with Zookie Consistency

**Objective**: Architect a globally distributed authorization evaluation service that enforces Zanzibar external consistency (Zookies) across multi-region read replicas.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `google-zanzibar-2019`, `oauth-2-1-draft`
- **Applicable Citations**:
  - [Zanzibar: Google’s Consistent, Global Authorization System](https://www.usenix.org/conference/atc19/presentation/pang) (2019)
  - [The OAuth 2.1 Authorization Framework](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/) (2024)

---

## Problem Statement

Architect `DistributedZanzibarGateway`. When an ACL mutation occurs, primary writes to Spanner and returns a Zookie (Spanner commit timestamp). When a check request arrives with a Zookie, the gateway routes to a local read replica. If the replica's safe read timestamp is behind the Zookie, it must either wait or read from a consistent replica. Design the consensus coordination, caching, and failover architecture.

---

## Formal Constraints

- Scale: 1,000,000 authorization checks per second across 3 cloud regions.
- Consistency: Zero New-Enemy leaks; read replicas must wait until local snapshot timestamp >= Zookie timestamp.
- Availability: Bounded fallback if primary database is unreachable.

---

## Starter Code

```python
class DistributedZanzibarGateway:
    def __init__(self, region_id: str, replica_cluster: list):
        self.region_id = region_id
        self.replicas = replica_cluster

    def check(self, zookie: str, object_str: str, permission: str, subject_str: str) -> bool:
        """Evaluate authorization check enforcing snapshot consistency timestamp."""
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Read replica with safe timestamp >= Zookie evaluates locally with < 1ms latency.
- [ ] **Test Case**: Stale read replica with safe timestamp < Zookie pauses or redirects to fresh replica.
- [ ] **Test Case**: Proves zero unauthorized reads during concurrent ACL revoke and document read.

---

## Solution & Invariant Check

Zookie encodes Spanner commit timestamp; local replicas track safe read watermarks; request is held or escalated to leader if watermark < zookie.