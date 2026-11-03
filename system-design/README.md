# Domain: Distributed Systems & Scalable Architecture

**Directory**: `system-design/`  
**Platform Domain ID**: `system-design`

## Overview

High-throughput, fault-tolerant distributed architectures, large-scale statistical experimentation, and low-level systems programming in Rust and Go.

---

## Priority Topics & Curriculum Index

### [Statistics for Data Analysis](./statistics/)
- **Path**: `system-design/statistics/`
- **Focus**: Hypothesis testing, Bonferroni/FDR correction, CUPED variance reduction, sequential testing (SPRT), bootstrap resampling, and SUTVA violations.
- **Artifacts**: [Fundamentals](./statistics/fundamentals.md) | [References](./statistics/references.md) | [Rubric](./statistics/rubric.md) | [Exercises](./statistics/exercises/) | [Learnings](./statistics/learnings/)

### [Rust Systems Programming](./rust/)
- **Path**: `system-design/rust/`
- **Focus**: Ownership, borrowing, lifetimes ('a), Send/Sync thread boundaries, atomic memory ordering (Acquire/Release), and async cancellation safety.
- **Artifacts**: [Fundamentals](./rust/fundamentals.md) | [References](./rust/references.md) | [Rubric](./rust/rubric.md) | [Exercises](./rust/exercises/) | [Learnings](./rust/learnings/)

### [Go Distributed Systems](./go/)
- **Path**: `system-design/go/`
- **Focus**: CSP channel synchronization, GMP runtime work-stealing scheduler, context propagation, escape analysis, and tri-color concurrent GC.
- **Artifacts**: [Fundamentals](./go/fundamentals.md) | [References](./go/references.md) | [Rubric](./go/rubric.md) | [Exercises](./go/exercises/) | [Learnings](./go/learnings/)

---

## Target Role Tracks & Seniority Calibrations

### Track 1: FAANG SWE + AI Lab SWE (L5 (Senior) & L6 (Staff))
Multi-region distributed consensus, partition tolerance, tail-latency mitigation, and low-allocation network services.

### Track 3: FAANG Security Engineer (L4-L6)
Network perimeter defenses, memory safety invariants via Rust, and robust RPC reverse proxying via Go.

### Track 4: AI Lab Research Engineer (L4-L5)
Statistical validation of model evaluations, high-throughput inference serving engines, and io_uring networking.

---

## Company Profiles & Cultural Bars

- **OpenAI**: Low-latency streaming token distribution, distributed KV-cache paging, and speculative decoding harnesses.
- **Google / GDM**: Massive distributed storage (Spanner, Bigtable), Borg-scale RPC orchestration, and zero-leak goroutine scheduling.
- **Anthropic**: High-reliability distributed training harnesses, clean error domains, and resilient RPC interfaces.
- **Meta**: Social-graph scale (TAO, Memcached), high-frequency metric collection, and rapid multi-region failover.
- **Databricks**: Vectorized query engines, LSM/B-tree storage architectures, and io_uring asynchronous I/O in Rust.
- **Netflix**: A/B testing platforms, chaos engineering resilience, EVCache microsecond caching, and RPC load shedding.
- **Apple**: Scalable cloud services supporting billion-device footprints with strict SLA and telemetry boundaries.

---

## Standard 5-Artifact Contract

Every topic directory inside this domain adheres strictly to the canonical 5-artifact layout:
1. `README.md`: Scope, role alignment, company calibration, and topic navigation.
2. `fundamentals.md`: Core axiomatic invariants, proofs, idiomatic code, and failure modes.
3. `references.yaml` & `references.md`: Citable academic papers, RFCs, books, and verified interview loops.
4. `rubric.md`: Role-calibrated 5-dimension scoring criteria across L4, L5, and L6.
5. `exercises/`: Tiered adaptive problem sets (`tier1_starter.md`, `tier2_l4.md`, `tier3_l5.md`, `tier4_l6.md`).
6. `learnings/`: Git-committed destination for user's durable notes and deep-dive captures.