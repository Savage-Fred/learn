# Exercise TIER3_L5: Asynchronous Rate-Limited Token Bucket in Tokio

**Objective**: Build an asynchronous rate-limiter in Rust using Tokio, atomic clock tracking, and cancellation-safe select! loops.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `klabnik-rust-book-2023`, `mara-bos-atomics-2023`
- **Applicable Citations**:
  - [The Rust Programming Language](https://doc.rust-lang.org/book/) (2023)
  - [Rust Atomics and Locks: Low-Level Concurrency in Practice](https://marabos.nl/atomics/) (2023)

---

## Problem Statement

Implement `RateLimiter::new(rate_per_sec: f64, burst_capacity: f64)`. Implement `async fn acquire(&self, tokens: f64)` which sleeps non-blockingly until sufficient tokens are available. Ensure multiple concurrent Tokio tasks can acquire tokens without race conditions or token over-allocation.

---

## Formal Constraints

- Throughput: Handle 100,000 rate-limit checks per second with sub-microsecond latency.
- Algorithm: Token bucket with continuous fractional replenishment.
- Cancellation safety: Dropping an acquire future must not leak tokens.

---

## Starter Code

```python
use std::sync::Arc;
use tokio::sync::Mutex;
use tokio::time::{Instant, Duration};

pub struct RateLimiter {
    // TODO: Define internal state
}

impl RateLimiter {
    pub fn new(rate_per_sec: f64, burst_capacity: f64) -> Self {
        unimplemented!()
    }

    pub async fn acquire(&self, tokens: f64) {
        // TODO: Sleep asynchronously until tokens are replenished
    }
}
```

---

## Verification Test Cases

- [ ] **Test Case**: Burst requests up to burst_capacity succeed instantly.
- [ ] **Test Case**: Sustained requests are throttled exactly to rate_per_sec over a 5-second interval.
- [ ] **Test Case**: Tokio task cancellation does not corrupt internal token counters.

---

## Solution & Invariant Check

Calculates tokens replenished = (now - last_update) * rate; updates state under mutex or atomic compare_exchange.