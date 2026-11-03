# Topic: Rust for High-Performance Scalable Systems

**Domain**: `system-design`  
**Topic ID**: `rust`  
**Canonical Path**: `system-design/rust/`

## Overview

Deep systems engineering in Rust covering memory safety invariants (ownership, borrowing, lifetimes), Send and Sync concurrency markers, interior mutability, lock-free atomics (Acquire/Release memory ordering), zero-cost monomorphization, Tokio asynchronous runtime internals, and cancellation safety in tokio::select!.

---

## Learning Objectives

- Prove memory safety and data race freedom at compile time using ownership, borrowing, and lifetime bounds.
- Utilize Send and Sync trait markers to enforce thread boundary safety without runtime overhead.
- Implement high-performance lock-free data structures using atomic primitives and explicit memory orderings (Acquire, Release, Relaxed).
- Architect zero-cost abstractions leveraging traits, associated types, and compiler monomorphization.
- Design resilient asynchronous runtimes using Tokio, ensuring cancellation safety in select! branches and avoiding pinned memory leaks.

## Prerequisite Knowledge Graph

- Low-level systems programming concepts (pointers, stack vs heap, memory layouts).
- C/C++ memory models (data races, undefined behavior).
- Basic multi-threaded concurrency (mutexes, atomics, thread spawning).

---

## Role Track Relevance

### Track 1: FAANG SWE + AI Lab SWE (L5/L6)
- **Focus & Competencies**: High-throughput network proxies, zero-copy buffer management, lock-free queues, and low-latency storage engines.

### Track 3: FAANG + AI Labs Security Engineer (L5-L6)
- **Focus & Competencies**: Memory-safe systems programming, lock-free concurrency, kernel and hypervisor security, and zero-overhead cryptographic abstractions.

### Track 4: AI Lab Research Engineer (non-PhD) (L4/L5)
- **Focus & Competencies**: GPU inference serving harnesses, custom PyO3 tensor bindings, and zero-allocation critical loops.

---

## Company Profiles & Cultural Bars (The 7 Notable Companies)

### Databricks
- **Technical Focus**: Query engine vectorization in Rust/C++, custom memory allocators, io_uring asynchronous I/O, and zero-copy Arrow data transfers.
- **Observable Evaluation Signals**:
  - Lock-free data structures
  - Cache line alignment
  - Explicit atomic memory ordering

### Anthropic
- **Technical Focus**: High-reliability distributed training harnesses, clean error domains (thiserror/anyhow), and resilient asynchronous network pipelines in Rust.
- **Observable Evaluation Signals**:
  - Tokio cancellation safety
  - RAII resource cleanup
  - Clean trait architecture

### OpenAI
- **Technical Focus**: Low-latency streaming token distribution, high-throughput inference proxies, and speculative decoding execution harnesses.
- **Observable Evaluation Signals**:
  - Sub-millisecond latency bounds
  - Zero unnecessary allocations
  - Flawless async concurrency

### Google / GDM
- **Technical Focus**: Rust systems security, replacing legacy C++ networking components, formal safety proofs, and interoperability via cxx/bindgen.
- **Observable Evaluation Signals**:
  - Safe Rust encapsulation of unsafe blocks
  - Comprehensive unit testing
  - Memory footprint minimization

### Meta
- **Technical Focus**: Rust for core systems infrastructure (Mononoke source control, network daemons), high concurrency, and compiler performance.
- **Observable Evaluation Signals**:
  - Concurrency profiling
  - Channel synchronization patterns
  - Efficient serialization (Bincode/Serde)

### Apple
- **Technical Focus**: Systems programming on Darwin/macOS, low power footprint, deterministic destruction, and tight memory limits.
- **Observable Evaluation Signals**:
  - Zero heap allocation in inner loops
  - ARC/Rust interop
  - Deterministic performance

### Netflix
- **Technical Focus**: Edge networking proxies (Zuul in Rust), high-throughput HTTP/3 and QUIC implementations, and chaos resilience.
- **Observable Evaluation Signals**:
  - Asynchronous stream backpressure
  - Resilience under load shedding
  - Metrics and tracing integration

---

## Standard 5-Artifact Topic Layout

1. **[Fundamentals](./fundamentals.md)**: Core axiomatic invariants, theoretical proofs, mental models, idiomatic code examples, architectural tradeoffs, and failure modes.
2. **[References (YAML)](./references.yaml)** & **[References (Markdown)](./references.md)**: Citable peer-reviewed literature (with DOIs/arXiv IDs), official standards/RFCs, foundational textbooks, and interview loop calibrations.
3. **[Evaluation Rubric](./rubric.md)**: L4 vs L5 vs L6 scoring criteria across the 5 dimensions (Decomposition, Technical Execution, Architecture, Resilience, Communication) matching `docs/ux-spec.md`.
4. **[Adaptive Exercises](./exercises/)**: Tiered problem sets spanning diagnostic starter, mid-level L4, senior L5, and staff L6.
5. **[Durable Learnings](./learnings/)**: Destination directory for user's durable notes and deep-dive captures.