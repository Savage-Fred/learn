# Evaluation Rubric & Calibration Guide: Go for Distributed Systems & Cloud Infrastructure

This rubric defines the scoring calibration for mock interview assessments, coding exercises, and technical design evaluations across five standardized dimensions.

## Seniority Level Overview

- **L4 (Mid-Level)**: Writes clean Go code conforming to gofmt and standard idioms; handles errors explicitly without ignoring err; implements basic goroutines, channels, and sync.WaitGroup.
- **L5 (Senior)**: Fluently designs CSP pipelines with select and channel closures; implements context cancellation across distributed calls; articulates GMP scheduler mechanics; prevents goroutine leaks.
- **L6 (Staff / Principal)**: Architects high-throughput, low-allocation Go services; uses sync.Pool and escape analysis to achieve zero-allocation inner loops; designs distributed consensus clients (Raft/etcd).

---

## The 5 Scoring Dimensions

### Dimension 1: Problem Decomposition & Invariant Formulation (Weight: 20%)
*Formulation of concurrency invariants, channel ownership, and context hierarchy.*

#### L4 (Mid-Level) Criteria
- Breaks down concurrency requirements into worker and pipeline stages.
- Passes ctx as the first parameter.

#### L5 (Senior) Criteria
- Identifies producer-consumer channel ownership (only producer closes channel).
- Formulates clean cancellation cascading rules.

#### L6 (Staff) Criteria
- Designs lock-free buffer pooling and zero-allocation streaming architectures.

#### Observable Anti-Patterns
- ❌ **Orphaned Goroutine**: Spawning a background goroutine with no cancellation channel or termination condition.

---

### Dimension 2: Technical Execution & Code Craftsmanship (Weight: 25%)
*Idiomatic Go syntax, explicit error handling, channel closing, and pointer vs value semantics.*

#### L4 (Mid-Level) Criteria
- Never ignores returned errors: if err != nil { return err }.
- Uses defer for unlocking and resource closure.

#### L5 (Senior) Criteria
- Uses sync.Once for thread-safe initialization.
- Avoids sharing memory without proper sync primitives or channels.

#### L6 (Staff) Criteria
- Optimizes memory layout to prevent heap escape via escape analysis benchmarks.

#### Observable Anti-Patterns
- ❌ **Receiver-Side Channel Close**: Closing a channel on the consumer side, causing panic on concurrent send.

---

### Dimension 3: Systems Architecture & Trade-Off Rigor (Weight: 25%)
*Deep understanding of the Go runtime, GC pacing, memory allocations, and network multiplexing.*

#### L4 (Mid-Level) Criteria
- Understands difference between buffered and unbuffered channels.
- Uses GOMAXPROCS appropriately.

#### L5 (Senior) Criteria
- Explains work-stealing algorithm in GMP scheduler.
- Evaluates channel communication overhead vs sync.Mutex.

#### L6 (Staff) Criteria
- Tunes GC pacing (GOGC, GOMEMLIMIT) for multi-gigabyte memory heaps.

#### Observable Anti-Patterns
- ❌ **Unbounded Concurrency**: Spawning an unrestricted goroutine per HTTP request without worker pool or semaphore bounding.

---

### Dimension 4: Resilience, Security & Edge Case Posture (Weight: 15%)
*Handling timeouts, network partitions, circuit breaking, panic recovery, and race conditions.*

#### L4 (Mid-Level) Criteria
- Recovers from unexpected panics at service boundary.
- Sets HTTP client timeouts.

#### L5 (Senior) Criteria
- Guards against cache thundering herd using singleflight.
- Implements exponential backoff with jitter on retries.

#### L6 (Staff) Criteria
- Detects deadlocks and race conditions using go test -race; proves safety under partition.

#### Observable Anti-Patterns
- ❌ **Infinite HTTP Client Timeout**: Using http.DefaultClient without timeouts, leading to connection exhaustion under network outage.

---

### Dimension 5: Communication & Calibration Level (Weight: 15%)
*Clarity of distributed systems concepts, Go idiom communication, and trade-off justification.*

#### L4 (Mid-Level) Criteria
- Walks through channel data flow clearly.
- Explains why error was returned.

#### L5 (Senior) Criteria
- Articulates concurrency failure modes with clarity.
- Explains trade-offs between sync.Pool and garbage collection.

#### L6 (Staff) Criteria
- Commands authority on distributed systems reliability and microservice architecture.

#### Observable Anti-Patterns
- ❌ **Dogmatic Channel Overuse**: Insisting on channels where a simple atomic or mutex is 10x faster and clearer.

---

## Composite Scoring Calibration

- **Score 1.0 – 2.4 (Below Bar / Not Passing)**: Deficient in core invariants; misses basic correctness constraints; unhandled runtime exceptions.
- **Score 2.5 – 3.4 (L4 Mid-Level Standard)**: Produces working, clean code; identifies edge cases with standard test inputs; needs scaffolding for multi-node tradeoffs.
- **Score 3.5 – 4.4 (L5 Senior Bar - Strong Hire)**: Formulates mathematical/architectural invariants up front; anticipates distributed failure modes; proves time/space bounds.
- **Score 4.5 – 5.0 (L6 Staff Bar - Exceptional)**: Strategic problem reframing; anticipates cascading failure and adversarial vectors; balances cross-cutting organizational invariants.