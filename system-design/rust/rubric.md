# Evaluation Rubric & Calibration Guide: Rust for High-Performance Scalable Systems

This rubric defines the scoring calibration for mock interview assessments, coding exercises, and technical design evaluations across five standardized dimensions.

## Seniority Level Overview

- **L4 (Mid-Level)**: Writes idiomatic safe Rust; navigates borrow checker errors comfortably; uses standard error handling (Result/Option); implements standard traits (Clone, Debug, PartialEq).
- **L5 (Senior)**: Fluently uses lifetimes and generics; implements custom traits and interior mutability (RefCell, Mutex); writes safe concurrent code with Tokio; analyzes cancellation safety.
- **L6 (Staff / Principal)**: Designs lock-free data structures using atomics and unsafe Rust with formal sound invariants; optimizes memory layout for cache lines and SIMD; architects zero-copy networking engines.

---

## The 5 Scoring Dimensions

### Dimension 1: Problem Decomposition & Invariant Formulation (Weight: 20%)
*Formulation of ownership boundaries, lifetime scopes, and concurrency markers.*

#### L4 (Mid-Level) Criteria
- Structures data models using clean structs and enums.
- Uses references appropriately without excessive cloning.

#### L5 (Senior) Criteria
- Identifies ownership transfers vs borrows across thread boundaries.
- Formulates explicit lifetime constraints ('a).

#### L6 (Staff) Criteria
- Proves soundness of unsafe blocks and lock-free atomic ordering invariants.

#### Observable Anti-Patterns
- ❌ **Clone-Everything Fix**: Calling .clone() indiscriminately to bypass borrow checker errors.

---

### Dimension 2: Technical Execution & Code Craftsmanship (Weight: 25%)
*Clean, idiomatic Rust code, error propagation with ?, pattern matching, and trait implementations.*

#### L4 (Mid-Level) Criteria
- Uses match and if let fluently.
- Propagates errors cleanly using Result and the ? operator.

#### L5 (Senior) Criteria
- Implements From/Into, AsRef, and Deref traits properly.
- Implements custom Drop for deterministic cleanup.

#### L6 (Staff) Criteria
- Writes minimal, audited unsafe code encapsulated behind strictly sound public APIs.

#### Observable Anti-Patterns
- ❌ **Unwrapping Everywhere**: Using .unwrap() or .expect() in production paths without handling errors.

---

### Dimension 3: Systems Architecture & Trade-Off Rigor (Weight: 25%)
*Understanding compilation model, binary bloat, memory layout, and asynchronous executors.*

#### L4 (Mid-Level) Criteria
- Understands stack allocation vs heap (Box<T>).
- Uses channels (mpsc) for thread communication.

#### L5 (Senior) Criteria
- Explains Tokio reactor pattern and epoll event loops.
- Evaluates Box<dyn Trait> dynamic dispatch vs generic static dispatch.

#### L6 (Staff) Criteria
- Calculates exact struct padding and memory alignment (#[repr(C)], #[repr(align(64))]).

#### Observable Anti-Patterns
- ❌ **Blocking Async Runtime**: Calling std::thread::sleep or synchronous disk I/O inside a Tokio async task.

---

### Dimension 4: Resilience, Security & Edge Case Posture (Weight: 15%)
*Handling panic recovery, cancellation safety, poison mutexes, and integer overflow.*

#### L4 (Mid-Level) Criteria
- Handles Option::None and Err variants gracefully.
- Checks array index bounds.

#### L5 (Senior) Criteria
- Handles Mutex poisoning safely.
- Guards against cancellation loss in tokio::select! branches.

#### L6 (Staff) Criteria
- Ensures memory ordering soundness on weakly-ordered CPU architectures (ARM/PowerPC).

#### Observable Anti-Patterns
- ❌ **Ignoring Cancellation**: Dropping futures mid-transaction in select! leading to half-written state.

---

### Dimension 5: Communication & Calibration Level (Weight: 15%)
*Precision of systems terminology, memory model explanations, and responsiveness.*

#### L4 (Mid-Level) Criteria
- Explains what the borrow checker is complaining about.
- Follows guidance on lifetime syntax.

#### L5 (Senior) Criteria
- Articulates memory model happens-before relationships clearly.
- Justifies architectural choices using zero-cost abstraction principles.

#### L6 (Staff) Criteria
- Commands authority on systems performance and kernel-level interactions.

#### Observable Anti-Patterns
- ❌ **Vague Jargon**: Using words like 'zero-cost' without explaining what machine instructions are generated.

---

## Composite Scoring Calibration

- **Score 1.0 – 2.4 (Below Bar / Not Passing)**: Deficient in core invariants; misses basic correctness constraints; unhandled runtime exceptions.
- **Score 2.5 – 3.4 (L4 Mid-Level Standard)**: Produces working, clean code; identifies edge cases with standard test inputs; needs scaffolding for multi-node tradeoffs.
- **Score 3.5 – 4.4 (L5 Senior Bar - Strong Hire)**: Formulates mathematical/architectural invariants up front; anticipates distributed failure modes; proves time/space bounds.
- **Score 4.5 – 5.0 (L6 Staff Bar - Exceptional)**: Strategic problem reframing; anticipates cascading failure and adversarial vectors; balances cross-cutting organizational invariants.