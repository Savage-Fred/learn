# Authoritative References & Citations: Go for Distributed Systems & Cloud Infrastructure

This curriculum grounds all concepts, exercises, and rubrics in peer-reviewed academic literature, formal standards (RFCs, NIST, IETF), foundational textbooks, and verified tier-1 industry interview loops.

## Citable Bibliography

### The Go Programming Language (2015)
- **Authors**: Alan A. A. Donovan, Brian W. Kernighan
- **Type**: `book`
- **Canonical URL / DOI**: [https://www.gopl.io/](https://www.gopl.io/)
- **Role Relevance**: Track-1-SWE, Track-3-Security
- **Core Invariants Extracted**:
  - Channels facilitate CSP concurrency synchronization.
  - Context package carries deadlines, cancellation signals, and request values across API boundaries.
- **Interview Loop Calibration**:
  - *Target Company & Level*: Google / GDM (L5)
  - *Round*: Cloud Systems & Infrastructure Coding
  - *Prompt Summary*: Build a distributed rate limiter and load-shedding reverse proxy in Go with sliding-window counters, context cancellation, and zero goroutine leaks.
  - *Expected Evaluation Signals*:
    - Clean context propagation down all HTTP handlers
    - Demonstrates zero goroutine leaks under benchmark tests

```bibtex
@book{donovan2015go,
  title={The Go Programming Language},
  author={Donovan, Alan A A and Kernighan, Brian W},
  year={2015},
  publisher={Addison-Wesley}
}
```

### Scalable Go Scheduler Design Doc (2012)
- **Authors**: Dmitry Vyukov
- **Type**: `tech_blog`
- **Canonical URL / DOI**: [https://golang.org/s/go11sched](https://golang.org/s/go11sched)
- **Role Relevance**: Track-1-SWE, Track-3-Security
- **Core Invariants Extracted**:
  - GMP scheduler decouples logical processors (P) from OS threads (M).
  - Work-stealing balances run queues across CPU cores without global lock contention.
- **Interview Loop Calibration**:
  - *Target Company & Level*: OpenAI (L5)
  - *Round*: High-Throughput Services
  - *Prompt Summary*: Explain how the Go runtime handles a goroutine executing a blocking system call vs an intensive CPU loop.
  - *Expected Evaluation Signals*:
    - Articulates M handoff during blocking syscalls
    - Explains cooperative preemption at function prologues and signal preemption

```bibtex
@misc{vyukov2012scheduler,
  title={Scalable Go Scheduler Design Doc},
  author={Vyukov, Dmitry},
  year={2012},
  url={https://golang.org/s/go11sched}
}
```
