# Exercise TIER1_STARTER: Disjoint Set Union with Path Compression and Union by Rank

**Objective**: Build a robust, generic Disjoint Set Union (DSU) data structure proving O(alpha(N)) amortized complexity.

---

## Problem Statement

Implement `DisjointSetUnion(n: int)`. Support `find(u: int) -> int` with path compression, `union(u: int, v: int) -> bool` with union by rank (returning True if merged, False if already in the same set), and `count_components() -> int`. All operations must run in O(alpha(N)) amortized time.

---

## Invariant Scaffolding & Guidance

- find(u) must flatten the tree by pointing u directly to the root (path compression).
- union(u, v) must attach the tree with smaller rank under the root of the tree with larger rank.

---

## Starter Code

```python
class DisjointSetUnion:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.num_components = n

    def find(self, u: int) -> int:
        # TODO: Path compression
        pass

    def union(self, u: int, v: int) -> bool:
        # TODO: Union by rank
        pass

    def count_components(self) -> int:
        return self.num_components
```

---

## Verification Test Cases

- [ ] **Test Case**: Union chain 0-1, 1-2, 2-3 reduces component count to n-3 and flattens find paths.
- [ ] **Test Case**: Redundant union on already connected nodes returns False and leaves count unchanged.
- [ ] **Test Case**: Handles single-node sets and n=100,000 operations in under 200ms.

---

## Solution & Invariant Check

Parent pointers recursively compress during find: parent[u] = find(parent[u]). Rank increments only on equal-rank unions.