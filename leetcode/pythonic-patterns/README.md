# Topic: Pythonic Coding Patterns

**Domain**: `leetcode`  
**Topic ID**: `pythonic-patterns`  
**Canonical Path**: `leetcode/pythonic-patterns/`

## Overview

Deep, grounded mastery of the Python Data Model, dunder protocols, structural typing (PEP 544), generator pipelines, memory layouts, and asynchronous concurrency primitives for high-performance engineering.

---

## Learning Objectives

- Implement custom container and stream types conforming strictly to Python Data Model protocols (__iter__, __enter__, __getitem__, __call__).
- Leverage typing.Protocol for static structural duck typing without runtime class coupling.
- Construct zero-copy, memory-bounded O(1) generator pipelines for processing massive data streams.
- Optimize memory usage and instance overhead using __slots__, weakref, and object arena allocations.
- Design resilient asyncio concurrent pipelines avoiding event loop starvation, unhandled task cancellations, and GIL bottlenecks.

## Prerequisite Knowledge Graph

- Intermediate Python syntax (comprehensions, basic classes, functions).
- Basic understanding of time/space algorithmic complexity (Big-O).
- Foundational understanding of operating system processes vs threads.

---

## Role Track Relevance

### Track 1: FAANG SWE + AI Lab SWE (L5/L6)
- **Focus & Competencies**: Clean architectural modularity, high-concurrency event loops, zero-copy batching, and sub-millisecond execution paths.

### Track 4: AI Lab Research Engineer (non-PhD) (L4/L5)
- **Focus & Competencies**: Streaming tensor data loaders, multiprocessing shared memory buffers, PyTorch custom dataset pipelines, and zero-allocation critical loops.

---

## Company Profiles & Cultural Bars (The 7 Notable Companies)

### OpenAI
- **Technical Focus**: Streaming tensor batcher with zero-copy slices, graceful generator shutdown, and live debugging under time constraints.
- **Observable Evaluation Signals**:
  - Idiomatic dunder implementations
  - Bounded memory footprints
  - Flawless error propagation

### Google / GDM
- **Technical Focus**: Type-safe structural typing, comprehensive unit tests, clear separation of concerns, and clean protocol contracts.
- **Observable Evaluation Signals**:
  - PEP 544 Protocol typing
  - Docstrings and invariants
  - Deterministic boundary testing

### Anthropic
- **Technical Focus**: High craftsmanship, defensive boundary assertions, clean exception hierarchies, and readable idiomatic Python.
- **Observable Evaluation Signals**:
  - No over-engineering
  - Immutability where appropriate
  - Graceful resource cleanup

### Meta
- **Technical Focus**: Rapid algorithmic execution, fluent use of itertools and collections, and immediate back-of-the-envelope memory estimates.
- **Observable Evaluation Signals**:
  - Speed of correct execution
  - Minimal allocations
  - Generator composition

### Databricks
- **Technical Focus**: Memory layouts, cache locality, Python/C interop awareness, and minimizing GIL contention in multiprocessing.
- **Observable Evaluation Signals**:
  - __slots__ memory optimization
  - Zero-copy buffer protocol
  - Thread safety

### Netflix
- **Technical Focus**: Asyncio resilient microservices, timeout handling, circuit breakers in coroutines, and distributed pipeline integration.
- **Observable Evaluation Signals**:
  - TaskGroup error handling
  - Contextvars propagation
  - Graceful degradation

### Apple
- **Technical Focus**: Efficient on-device Python scripting, memory bounds, zero memory leaks across long-running daemon cycles.
- **Observable Evaluation Signals**:
  - Cycle detection in GC
  - Weakref caching
  - Resource cleanup guarantees

---

## Standard 5-Artifact Topic Layout

1. **[Fundamentals](./fundamentals.md)**: Core axiomatic invariants, theoretical proofs, mental models, idiomatic code examples, architectural tradeoffs, and failure modes.
2. **[References (YAML)](./references.yaml)** & **[References (Markdown)](./references.md)**: Citable peer-reviewed papers (with DOIs/arXiv IDs), official RFCs, foundational textbooks, and recent verified tier-1 interview loop calibrations.
3. **[Evaluation Rubric](./rubric.md)**: L4 vs L5 vs L6 scoring criteria across the 5 dimensions (Decomposition, Technical Execution, Architecture, Resilience, Communication) matching `docs/ux-spec.md`.
4. **[Adaptive Exercises](./exercises/)**: Tiered problem sets spanning diagnostic starter, mid-level L4, senior L5, and staff L6.
5. **[Durable Learnings](./learnings/)**: Destination directory for user's durable notes and deep-dive captures.