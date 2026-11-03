# Topic: Advanced Data Structures & Indexing

**Domain**: `leetcode`  
**Topic ID**: `data-structures`  
**Canonical Path**: `leetcode/data-structures/`

## Overview

Deep systems and algorithmic grounding in cache-conscious trees (B+ Tree, Masstree), Disjoint Set Union with inverse Ackermann complexity, probabilistic streaming sketches (Bloom Filter, Count-Min, HyperLogLog), vector indexing (HNSW), and lock-free concurrent queues.

---

## Learning Objectives

- Analyze cache-line alignment and pointer dereferencing impact on modern hardware memory hierarchies.
- Implement Disjoint Set Union (DSU) with union-by-rank and path compression, proving O(alpha(N)) amortized complexity.
- Design probabilistic streaming data structures (Bloom filter, Count-Min Sketch, HyperLogLog) with formal error bounds.
- Construct Hierarchical Navigable Small World (HNSW) proximity graphs for sub-millisecond approximate nearest neighbor (ANN) vector search.
- Implement lock-free concurrent data structures using atomic CAS (Compare-And-Swap) primitives and hazard pointer memory reclamation.

## Prerequisite Knowledge Graph

- Standard data structures (Binary Search Trees, Hash Tables, Heaps).
- Hardware memory hierarchy (L1/L2/L3 caches, cache lines, DRAM latency).
- Basic concurrency (mutexes, atomic operations, race conditions).

---

## Role Track Relevance

### Track 1: FAANG SWE + AI Lab SWE (L5/L6)
- **Focus & Competencies**: Cache-conscious memory layout, lock-free queues, B+ tree index engines, and high-concurrency data structures.

### Track 4: AI Lab Research Engineer (non-PhD) (L4/L5)
- **Focus & Competencies**: High-dimensional vector indexing (HNSW, IVF-PQ), GPU memory management, and streaming sketches for dataset deduplication.

---

## Company Profiles & Cultural Bars (The 7 Notable Companies)

### Databricks
- **Technical Focus**: In-memory B+ trees, optimistic lock coupling, cache line alignment, and vectorized columnar data structures.
- **Observable Evaluation Signals**:
  - Awareness of CPU cache line invalidation
  - Lock-free synchronization
  - Zero-copy memory layouts

### Google / GDM
- **Technical Focus**: Mathematical proof of DSU inverse Ackermann bound, probabilistic sketch error guarantees, and balanced tree invariants.
- **Observable Evaluation Signals**:
  - Formal error bound calculations
  - Proof of path compression complexity
  - Clean invariant assertions

### OpenAI
- **Technical Focus**: High-throughput vector indexing (HNSW) for retrieval augmented generation (RAG) and embedding similarity search under tight latency budgets.
- **Observable Evaluation Signals**:
  - Sub-millisecond query latency
  - Bounded graph degree
  - Concurrent insertion safety

### Meta
- **Technical Focus**: Streaming sketches (HyperLogLog, Count-Min) for counting billions of daily active users and tracking trending topics.
- **Observable Evaluation Signals**:
  - Space-accuracy trade-offs
  - Hash function quality (Murmur3/xxHash)
  - Mergeability of sketches

### Anthropic
- **Technical Focus**: Clean, robust concurrent data structures, verifiable thread safety, and defensive bounds checking.
- **Observable Evaluation Signals**:
  - No data races
  - Clean encapsulation
  - Clear invariant documentation

### Netflix
- **Technical Focus**: Bloom filters in recommendation caching and distributed routing tables, preventing cache stampedes.
- **Observable Evaluation Signals**:
  - False positive rate tuning
  - Optimal bit array sizing
  - Serialization efficiency

### Apple
- **Technical Focus**: On-device indexing under tight RAM budgets, minimizing memory fragmentation and flash write cycles.
- **Observable Evaluation Signals**:
  - Compact memory representations
  - Predictable memory bounds
  - Zero memory leaks

---

## Standard 5-Artifact Topic Layout

1. **[Fundamentals](./fundamentals.md)**: Core axiomatic invariants, theoretical proofs, mental models, idiomatic code examples, architectural tradeoffs, and failure modes.
2. **[References (YAML)](./references.yaml)** & **[References (Markdown)](./references.md)**: Citable peer-reviewed literature (with DOIs/arXiv IDs), official standards/RFCs, foundational textbooks, and interview loop calibrations.
3. **[Evaluation Rubric](./rubric.md)**: L4 vs L5 vs L6 scoring criteria across the 5 dimensions (Decomposition, Technical Execution, Architecture, Resilience, Communication) matching `docs/ux-spec.md`.
4. **[Adaptive Exercises](./exercises/)**: Tiered problem sets spanning diagnostic starter, mid-level L4, senior L5, and staff L6.
5. **[Durable Learnings](./learnings/)**: Destination directory for user's durable notes and deep-dive captures.