# Exercise TIER3_L5: ReBAC Google Zanzibar Tuple Engine with Cycle Detection

**Objective**: Design an in-memory relationship-based authorization engine evaluating recursive group memberships with cycle detection.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `google-zanzibar-2019`, `oauth-2-1-draft`
- **Applicable Citations**:
  - [Zanzibar: Google’s Consistent, Global Authorization System](https://www.usenix.org/conference/atc19/presentation/pang) (2019)
  - [The OAuth 2.1 Authorization Framework](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/) (2024)

---

## Problem Statement

Implement `ZanzibarEngine`. Support `write_tuple(object_ns, object_id, relation, subject_ns, subject_id, subject_relation)` and `check_permission(object_ns, object_id, permission, subject_ns, subject_id) -> bool`. Support namespace rewrite rules (e.g. `viewer` is granted if user is `editor`). Handle deep nested groups and cycle detection.

---

## Formal Constraints

- Tuples: Support up to 100,000 relation tuples.
- Query latency: Sub-5ms evaluation for graph depth <= 10.
- Safety: Cyclic memberships (A in B, B in A) must not cause infinite recursion.

---

## Starter Code

```python
class ZanzibarEngine:
    def __init__(self, namespace_configs: dict):
        self.namespace_configs = namespace_configs
        # TODO: Initialize tuple store

    def write_tuple(self, obj_ns: str, obj_id: str, relation: str, 
                    sub_ns: str, sub_id: str, sub_rel: str = None) -> None:
        pass

    def check_permission(self, obj_ns: str, obj_id: str, perm: str, 
                         sub_ns: str, sub_id: str) -> bool:
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Direct user access returns True.
- [ ] **Test Case**: Nested group access (User -> Eng Team -> Admin Group -> Doc Editor) returns True.
- [ ] **Test Case**: Circular group membership returns False cleanly without StackOverflow.

---

## Solution & Invariant Check

Recursive BFS/DFS traversal over relation graph with visited set of (ns, id, rel) tuples; expands relation definitions according to namespace configuration.