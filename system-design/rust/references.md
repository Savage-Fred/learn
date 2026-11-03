# Authoritative References & Citations: Rust for High-Performance Scalable Systems

This curriculum grounds all concepts, exercises, and rubrics in peer-reviewed academic literature, formal standards (RFCs, NIST, IETF), foundational textbooks, and verified tier-1 industry interview loops.

## Citable Bibliography

### The Rust Programming Language (2023)
- **Authors**: Steve Klabnik, Carol Nichols
- **Type**: `book`
- **Canonical URL / DOI**: [https://doc.rust-lang.org/book/](https://doc.rust-lang.org/book/)
- **Role Relevance**: Track-1-SWE, Track-4-Research-Eng
- **Core Invariants Extracted**:
  - Ownership and borrowing eliminate dangling pointers and data races at compile time.
  - Trait objects enable dynamic dispatch while preserving memory safety.
- **Interview Loop Calibration**:
  - *Target Company & Level*: Anthropic (L5)
  - *Round*: Systems Architecture & Code Taste
  - *Prompt Summary*: Implement a high-throughput worker pool in Rust that distributes work across threads with graceful shutdown on drop.
  - *Expected Evaluation Signals*:
    - Idiomatic ownership transfers without unnecessary clones
    - Clean RAII shutdown implementation using Drop trait

```bibtex
@book{klabnik2023rust,
  title={The Rust Programming Language},
  author={Klabnik, Steve and Nichols, Carol},
  year={2023},
  edition={2nd},
  publisher={No Starch Press}
}
```

### Rust Atomics and Locks: Low-Level Concurrency in Practice (2023)
- **Authors**: Mara Bos
- **Type**: `book`
- **Canonical URL / DOI**: [https://marabos.nl/atomics/](https://marabos.nl/atomics/)
- **Role Relevance**: Track-1-SWE, Track-4-Research-Eng
- **Core Invariants Extracted**:
  - Acquire-Release ordering establishes happens-before relationships between threads.
  - UnsafeCell is the only legal primitive for interior mutability in Rust.
- **Interview Loop Calibration**:
  - *Target Company & Level*: Databricks (L5)
  - *Round*: Low-Level Concurrency & Systems
  - *Prompt Summary*: Implement a concurrent lock-free ring buffer in Rust with custom atomics and explicit memory ordering.
  - *Expected Evaluation Signals*:
    - Correct choice of Acquire, Release, and Relaxed orderings
    - Safe implementation of Send and Sync for custom types

```bibtex
@book{bos2023atomics,
  title={Rust Atomics and Locks: Low-Level Concurrency in Practice},
  author={Bos, Mara},
  year={2023},
  publisher={O'Reilly Media}
}
```
