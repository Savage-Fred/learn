# Core Fundamentals & Invariants: Advanced Data Structures & Indexing

This document articulates the axiomatic invariants, theoretical grounding, mental models, idiomatic code implementations, architectural tradeoffs, and failure modes governing this topic.

---

## 1. Axiomatic Core Invariants

### Invariant 1: Cache Line Locality Invariant
$$
\text{Cache line size } B = 64 \text{ bytes}. \text{ Node branching factor } M = \lfloor B / \text{sizeof}(\text{entry}) \rfloor \text{ minimizes L1/L2 cache misses: } O(\log_M N) \ll O(\log_2 N).
$$
**Implications & Guarantees**: Cache-conscious B+ trees drastically outperform pointer-based binary trees (AVL, Red-Black) on modern superscalar CPUs.

### Invariant 2: DSU Inverse Ackermann Invariant
$$
\text{For a sequence of } m \text{ operations on } n \text{ elements, DSU with union-by-rank and path compression runs in } O(m \cdot \alpha(n)) \text{ time}.
$$
**Implications & Guarantees**: For all practical purposes (n < 10^{80}), \alpha(n) \le 4, rendering DSU operations effectively constant time.

### Invariant 3: Count-Min Sketch Accuracy Invariant
$$
\hat{a}_i \le a_i + \epsilon \|a\|_1 \text{ with probability at least } 1 - \delta, \text{ where } w = \lceil e / \epsilon \rceil, d = \lceil \ln(1 / \delta) \rceil.
$$
**Implications & Guarantees**: Guarantees that frequency estimates over unbounded data streams never underestimate true counts and have strictly bounded overestimation.

---

## 2. Core Mental Models

### Mental Model 1: Pointer Chasing vs Contiguous Memory Strides
Modern CPUs fetch 64 bytes per cache line. Traversing linked lists or binary trees incurs a 50-100ns DRAM latency penalty per pointer dereference. B+ tree nodes and contiguous arrays pack multiple elements per cache line, achieving near-zero wait states.

### Mental Model 2: Hierarchical Proximity Graphs (HNSW)
HNSW constructs multi-layer graphs inspired by SkipLists. Top layers contain long-range highway edges for fast coarse routing; bottom layers contain dense local nearest-neighbor graphs for precise clustering. Search complexity scales as O(log N).

---

## 3. Idiomatic Code Examples

### Count-Min Sketch in Python with MurmurHash Invariants
```python
import math
import hashlib
from typing import List

class CountMinSketch:
    """Probabilistic streaming frequency estimator with (epsilon, delta) guarantees."""
    def __init__(self, epsilon: float, delta: float):
        if not (0 < epsilon < 1 and 0 < delta < 1):
            raise ValueError("epsilon and delta must be in (0, 1)")
        self.epsilon = epsilon
        self.delta = delta
        self.width = math.ceil(math.e / epsilon)
        self.depth = math.ceil(math.log(1.0 / delta))
        self.table: List[List[int]] = [[0] * self.width for _ in range(self.depth)]

    def _hash(self, item: str, seed: int) -> int:
        h = hashlib.sha256(f"{seed}:{item}".encode("utf-8")).digest()
        # Extract integer from first 8 bytes
        return int.from_bytes(h[:8], "big") % self.width

    def add(self, item: str, count: int = 1) -> None:
        for i in range(self.depth):
            col = self._hash(item, i)
            self.table[i][col] += count

    def estimate(self, item: str) -> int:
        """Returns upper-bound frequency estimate for item."""
        min_val = float("inf")
        for i in range(self.depth):
            col = self._hash(item, i)
            min_val = min(min_val, self.table[i][col])
        return int(min_val)
```
**Analysis**: Demonstrates Count-Min Sketch sizing width = ceil(e/eps) and depth = ceil(ln(1/delta)) to guarantee frequency estimation bounds.

---

## 4. Architectural Tradeoffs

### B+ Tree vs LSM-Tree (Log-Structured Merge Tree)
B+ trees provide fast O(log N) point reads and range scans with in-place page updates, but suffer from write amplification on random writes. LSM-trees append writes sequentially to a write-ahead log and memtable (high write throughput), but require multi-level compactions and Bloom filter lookups for point reads.

### Exact ANN (Flat Index) vs Approximate HNSW
Exact flat search computes cosine similarity against all N embeddings (100% recall, but O(N) latency, unscalable for N > 1M). HNSW provides 95-99% recall in sub-millisecond O(log N) time, at the expense of higher RAM usage to store graph adjacency lists.

---

## 5. Common Failure Modes & Anti-Patterns

### Failure Mode 1: Bloom Filter Saturation
- **Root Cause**: Inserting more elements than the design capacity N causes the bit array fill ratio to approach 1.0, driving false positive probability toward 100%.
- **Mitigation & Invariant Defense**: Monitor bit density (optimal density is 50%); scale using Scalable Bloom Filters or re-index into larger filter.

### Failure Mode 2: Lock-Free ABA Problem
- **Root Cause**: A thread reads pointer A, is suspended, another thread frees A, allocates B at the same address, and frees B. When the first thread resumes, CAS sees value A and succeeds despite underlying memory corruption.
- **Mitigation & Invariant Defense**: Use tagged pointers (version counter coupled with pointer) or epoch-based memory reclamation.
