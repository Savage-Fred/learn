# Exercise TIER2_L4: Segment Tree with Lazy Propagation for Range Updates

**Objective**: Implement an in-memory Segment Tree supporting both range sum queries and range addition updates in O(log N) time.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `herlihy-shavit-2020`, `hnsw-malkov-2018`
- **Applicable Citations**:
  - [The Art of Multiprocessor Programming](https://www.sciencedirect.com/book/9780124159501/the-art-of-multiprocessor-programming) (2020)
  - [Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs](https://ieeexplore.ieee.org/document/8594632) (2018)

---

## Problem Statement

Implement `LazySegmentTree(arr: List[int])`. Support `update_range(left: int, right: int, val: int)` which adds `val` to all elements in `[left, right]`, and `query_range(left: int, right: int) -> int` which returns the sum of elements in `[left, right]`. Uses lazy propagation to defer child updates.

---

## Formal Constraints

- Array size: Up to 100,000 elements.
- Operations: Up to 100,000 range updates and queries.
- Time complexity: O(log N) per query and update.

---

## Starter Code

```python
from typing import List

class LazySegmentTree:
    def __init__(self, arr: List[int]):
        self.n = len(arr)
        self.tree = [0] * (4 * self.n)
        self.lazy = [0] * (4 * self.n)
        # TODO: Build initial segment tree

    def update_range(self, l: int, r: int, val: int) -> None:
        # TODO: Implement range addition with lazy propagation
        pass

    def query_range(self, l: int, r: int) -> int:
        # TODO: Implement range sum query
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Point updates and queries match naive array sums.
- [ ] **Test Case**: Overlapping range updates accumulate properly in lazy nodes.
- [ ] **Test Case**: 100,000 randomized operations complete in under 500ms.

---

## Solution & Invariant Check

Before descending to children in query or update, pushdown pending lazy additions and update child tree values by lazy * child_segment_length.