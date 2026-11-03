# Evaluation Rubric & Calibration Guide: Pythonic Coding Patterns

This rubric defines the scoring calibration for mock interview assessments, coding exercises, and technical design evaluations across five standardized dimensions.

## Seniority Level Overview

- **L4 (Mid-Level)**: Writes clean, working Python conforming to standard syntax; uses comprehensions and standard library data structures; handles basic exceptions.
- **L5 (Senior)**: Fluently implements dunder protocols; designs memory-bounded generator pipelines; articulates CPython GIL and memory allocation dynamics; structures concurrent code defensively.
- **L6 (Staff / Principal)**: Architects low-latency, high-throughput systems; leverages zero-copy buffer protocols and custom memory arenas; refactors multi-process architectures to minimize IPC overhead.

---

## The 5 Scoring Dimensions

### Dimension 1: Problem Decomposition & Invariant Formulation (Weight: 20%)
*Ability to formulate clear architectural invariants (e.g. O(1) memory bound, structural duck typing) before writing code.*

#### L4 (Mid-Level) Criteria
- Breaks down requirement into standard functions and classes.
- Identifies basic inputs, outputs, and null checks.

#### L5 (Senior) Criteria
- Identifies memory bounded streaming invariant up front.
- Specifies protocol interface separating consumer from producer.

#### L6 (Staff) Criteria
- Anticipates backpressure and cancellation invariants across async boundaries.
- Designs modular abstraction with zero leakage of implementation details.

#### Observable Anti-Patterns
- ❌ **Premature Concrete Coupling**: Tying code to concrete list or dict types instead of Iterable or Mapping protocols.

---

### Dimension 2: Technical Execution & Code Craftsmanship (Weight: 25%)
*Fluency with Python Data Model, PEP 544 typing, dunder methods, and memory management.*

#### L4 (Mid-Level) Criteria
- Writes syntactically correct Python with type annotations.
- Correctly implements __init__ and basic helper methods.

#### L5 (Senior) Criteria
- Implements dunder protocols (__iter__, __enter__, __getitem__) with proper semantics.
- Uses __slots__ for high-volume objects; avoids mutable default arguments.

#### L6 (Staff) Criteria
- Employs advanced typing (ParamSpec, TypeVarTuple); optimizes memory via weakref or buffer protocol.
- Guarantees zero-leak object disposal.

#### Observable Anti-Patterns
- ❌ **List Materialization**: Calling list(gen) on unbounded streams, causing O(N) memory exhaustion.

---

### Dimension 3: Systems Architecture & Trade-Off Rigor (Weight: 25%)
*Justification of architectural choices between threads, processes, and async event loops.*

#### L4 (Mid-Level) Criteria
- Understands difference between CPU-bound and I/O-bound tasks.
- Uses standard threading or asyncio library.

#### L5 (Senior) Criteria
- Articulates GIL implications on thread pools vs multiprocessing.
- Justifies asyncio TaskGroup usage and cancellation scopes.

#### L6 (Staff) Criteria
- Quantifies memory footprint of process fork vs thread pool vs shared memory IPC.
- Architects hybrid multiprocessing + asyncio runtimes for high-throughput serving.

#### Observable Anti-Patterns
- ❌ **Event Loop Blocking**: Invoking blocking synchronous I/O inside async coroutines.

---

### Dimension 4: Resilience, Security & Edge Case Posture (Weight: 15%)
*Handling of boundary conditions, GeneratorExit, signal cancellation, and thread race conditions.*

#### L4 (Mid-Level) Criteria
- Catches standard exceptions (KeyError, ValueError, IndexError).
- Validates presence of required configuration fields.

#### L5 (Senior) Criteria
- Gracefully handles GeneratorExit in generator pipelines.
- Uses reentrant locks (RLock) to prevent reentrancy deadlocks.

#### L6 (Staff) Criteria
- Designs graceful shutdown cascades for async tasks under SIGTERM/SIGINT.
- Prevents memory leaks in circular references via weakref.

#### Observable Anti-Patterns
- ❌ **Swallowing Exceptions**: Using bare except: pass that hides KeyboardInterrupt and SystemExit.

---

### Dimension 5: Communication & Calibration Level (Weight: 15%)
*Clarity of technical explanations, trade-off articulation, and responsiveness to interviewer probes.*

#### L4 (Mid-Level) Criteria
- Explains what code is doing step by step.
- Receptive to hints and edge-case suggestions.

#### L5 (Senior) Criteria
- Proactively explains memory and algorithmic trade-offs.
- Communicates confidence in invariant formulation.

#### L6 (Staff) Criteria
- Drives high-level architectural discussion with precision.
- Frames technical decisions around company business constraints.

#### Observable Anti-Patterns
- ❌ **Defensive Dogmatism**: Arguing against interviewer constraints or refusing to consider trade-offs.

---

## Composite Scoring Calibration

- **Score 1.0 – 2.4 (Below Bar / Not Passing)**: Deficient in core invariants; misses basic correctness constraints; unhandled runtime exceptions.
- **Score 2.5 – 3.4 (L4 Mid-Level Standard)**: Produces working, clean code; identifies edge cases with standard test inputs; needs scaffolding for multi-node tradeoffs.
- **Score 3.5 – 4.4 (L5 Senior Bar - Strong Hire)**: Formulates mathematical/architectural invariants up front; anticipates distributed failure modes; proves time/space bounds.
- **Score 4.5 – 5.0 (L6 Staff Bar - Exceptional)**: Strategic problem reframing; anticipates cascading failure and adversarial vectors; balances cross-cutting organizational invariants.