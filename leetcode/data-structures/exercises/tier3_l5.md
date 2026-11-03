# Exercise TIER3_L5: Lock-Free Concurrent Michael-Scott Queue

**Objective**: Implement a lock-free FIFO queue using atomic Compare-And-Swap (CAS) primitives and cooperative tail advancement.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `herlihy-shavit-2020`, `hnsw-malkov-2018`
- **Applicable Citations**:
  - [The Art of Multiprocessor Programming](https://www.sciencedirect.com/book/9780124159501/the-art-of-multiprocessor-programming) (2020)
  - [Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs](https://ieeexplore.ieee.org/document/8594632) (2018)

---

## Problem Statement

Implement `LockFreeQueue`. Use atomic reference updates (or Python's simulated atomic CAS loop) with a dummy head node. `enqueue(val)` must append a node using CAS and advance tail cooperatively. `dequeue() -> Optional[Any]` must advance head and return item, returning None if queue is empty. Explain ABA problem mitigation.

---

## Formal Constraints

- Thread safety: Multiple concurrent producer and consumer threads without mutex locks.
- Progress guarantee: Lock-free (system-wide progress guaranteed).
- Time complexity: O(1) amortized enqueue and dequeue.

---

## Starter Code

```python
class Node:
    def __init__(self, val):
        self.val = val
        self.next = None

class LockFreeQueue:
    def __init__(self):
        dummy = Node(None)
        self.head = dummy
        self.tail = dummy

    def enqueue(self, val) -> None:
        # TODO: Implement lock-free enqueue with cooperative tail advancement
        pass

    def dequeue(self):
        # TODO: Implement lock-free dequeue
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: 10 threads enqueuing 1,000 items each results in exactly 10,000 items dequeued.
- [ ] **Test Case**: Dequeue on empty queue returns None without hanging.
- [ ] **Test Case**: No items lost or duplicated under heavy thread contention.

---

## Solution & Invariant Check

Tail insertion uses CAS to link next; if tail.next is not None, enqueuer helps advance tail before attempting its own insertion.