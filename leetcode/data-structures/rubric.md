# Evaluation Rubric & Calibration Guide: Advanced Data Structures & Indexing

This rubric defines the scoring calibration for mock interview assessments, coding exercises, and technical design evaluations across five standardized dimensions.

## Seniority Level Overview

- **L4 (Mid-Level)**: Implements standard trees, hash maps, heaps, and DSU with path compression; calculates basic time/space complexities; handles boundary cases.
- **L5 (Senior)**: Implements segment trees with lazy propagation; sizes probabilistic sketches (Bloom, Count-Min) to exact error bounds; articulates cache line locality and lock coupling.
- **L6 (Staff / Principal)**: Architects lock-free or vectorized data structures; designs high-dimensional vector index structures (HNSW); optimizes memory down to cache-line and SIMD alignment.

---

## The 5 Scoring Dimensions

### Dimension 1: Problem Decomposition & Invariant Formulation (Weight: 20%)
*Formulation of structural invariants (e.g. tree balance, heap order, sketch error bounds).*

#### L4 (Mid-Level) Criteria
- Identifies appropriate data structure for lookup and insert requirements.
- Maintains basic binary search tree invariants.

#### L5 (Senior) Criteria
- Proves DSU amortized complexity or calculates Bloom filter false positive formula.
- Formulates lazy propagation invariants for range updates.

#### L6 (Staff) Criteria
- Designs cache-conscious layout conforming to hardware cache line widths.
- Formulates lock-free linearization points.

#### Observable Anti-Patterns
- ❌ **Uncalibrated Sizing**: Arbitrarily picking sketch dimensions without calculating epsilon and delta.

---

### Dimension 2: Technical Execution & Code Craftsmanship (Weight: 25%)
*Clean, bug-free implementation of pointer manipulations, bitwise operations, and memory allocations.*

#### L4 (Mid-Level) Criteria
- Implements Trie or DSU without recursion overflow.
- Handles root insertion and empty tree cases cleanly.

#### L5 (Senior) Criteria
- Implements segment tree with lazy propagation cleanly.
- Implements Count-Min or Bloom filter with independent hashing.

#### L6 (Staff) Criteria
- Writes atomic CAS loops with correct memory ordering.
- Optimizes memory layout using contiguous flat arrays.

#### Observable Anti-Patterns
- ❌ **Memory Leak in Dynamic Nodes**: Losing references to child nodes leading to uncollectable garbage.

---

### Dimension 3: Systems Architecture & Trade-Off Rigor (Weight: 25%)
*Deep understanding of cache hierarchy, memory layout, and operational trade-offs.*

#### L4 (Mid-Level) Criteria
- Understands memory differences between arrays and linked lists.
- States time complexity of search, insert, and delete.

#### L5 (Senior) Criteria
- Explains why B+ trees outperform AVL trees on modern SSDs and RAM.
- Quantifies trade-off between false positive rate and bit array size.

#### L6 (Staff) Criteria
- Calculates exact cache line misses and SIMD vectorization potential.
- Architects hybrid disk/RAM indexing engines.

#### Observable Anti-Patterns
- ❌ **Ignoring Hardware Reality**: Assuming pointer chasing is as fast as sequential array iteration.

---

### Dimension 4: Resilience, Security & Edge Case Posture (Weight: 15%)
*Handling hash collisions, capacity saturation, race conditions, and numeric overflow.*

#### L4 (Mid-Level) Criteria
- Handles duplicate keys and non-existent queries safely.
- Guards against divide-by-zero in empty collections.

#### L5 (Senior) Criteria
- Handles sketch saturation and counter overflow.
- Ensures thread safety under concurrent reads and writes.

#### L6 (Staff) Criteria
- Mitigates ABA problem in lock-free CAS structures using hazard pointers.

#### Observable Anti-Patterns
- ❌ **Silent Overflow**: Allowing 32-bit counter overflow in high-throughput frequency sketches.

---

### Dimension 5: Communication & Calibration Level (Weight: 15%)
*Ability to explain complex data structures clearly with concrete mathematical backing.*

#### L4 (Mid-Level) Criteria
- Walks through insertion and lookup steps clearly.
- Answers questions about Big-O complexity accurately.

#### L5 (Senior) Criteria
- Articulates mathematical derivation of sketch error bounds.
- Explains concurrency invariants with precision.

#### L6 (Staff) Criteria
- Drives architectural discussion at the hardware and platform level.

#### Observable Anti-Patterns
- ❌ **Rambling Speculation**: Guessing mathematical bounds without deriving them from first principles.

---

## Composite Scoring Calibration

- **Score 1.0 – 2.4 (Below Bar / Not Passing)**: Deficient in core invariants; misses basic correctness constraints; unhandled runtime exceptions.
- **Score 2.5 – 3.4 (L4 Mid-Level Standard)**: Produces working, clean code; identifies edge cases with standard test inputs; needs scaffolding for multi-node tradeoffs.
- **Score 3.5 – 4.4 (L5 Senior Bar - Strong Hire)**: Formulates mathematical/architectural invariants up front; anticipates distributed failure modes; proves time/space bounds.
- **Score 4.5 – 5.0 (L6 Staff Bar - Exceptional)**: Strategic problem reframing; anticipates cascading failure and adversarial vectors; balances cross-cutting organizational invariants.