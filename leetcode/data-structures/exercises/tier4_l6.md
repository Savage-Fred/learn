# Exercise TIER4_L6: Hierarchical Navigable Small World (HNSW) Vector Index

**Objective**: Architect a production-grade HNSW vector index structure supporting concurrent insertion and cosine similarity search over 1,000,000 embeddings.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `herlihy-shavit-2020`, `hnsw-malkov-2018`
- **Applicable Citations**:
  - [The Art of Multiprocessor Programming](https://www.sciencedirect.com/book/9780124159501/the-art-of-multiprocessor-programming) (2020)
  - [Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs](https://ieeexplore.ieee.org/document/8594632) (2018)

---

## Problem Statement

Design and implement `HNSWIndex(dim=128, M=16, ef_construction=100)`. Implement multi-layer skip-graph creation, heuristic neighbor pruning with degree bound M, and greedy beam-search routing with parameter `ef_search`. Include memory layout design and concurrent read-write synchronization strategies.

---

## Formal Constraints

- Query latency: Sub-millisecond (p99 < 1ms) for 128-dimensional vectors.
- Recall: > 95% 10-recall@10 compared to brute-force exact search.
- Memory bounds: Contiguous memory-mapped arrays for adjacency lists to minimize heap fragmentation.

---

## Starter Code

```python
import numpy as np

class HNSWIndex:
    def __init__(self, dim: int = 128, M: int = 16, ef_construction: int = 100):
        self.dim = dim
        self.M = M
        self.ef_construction = ef_construction
        # TODO: Initialize multi-layer graph structures

    def insert(self, vector: np.ndarray) -> int:
        """Insert vector and return assigned vector ID."""
        pass

    def search_knn(self, query: np.ndarray, k: int = 10, ef_search: int = 50) -> list:
        """Search k approximate nearest neighbors using greedy beam search."""
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Insert 10,000 random vectors; query k=10; verify > 95% recall against exact dot product.
- [ ] **Test Case**: Verify search visits O(log N) nodes on average.
- [ ] **Test Case**: Verify memory footprint is strictly bounded by M * sizeof(int32) * N.

---

## Solution & Invariant Check

Layer assignment follows exponential decay distribution; search descends greedy closest neighbors from top layer down to layer 0; layer 0 executes beam search with priority queue.