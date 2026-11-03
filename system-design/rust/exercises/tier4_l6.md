# Exercise TIER4_L6: Lock-Free Ring Buffer for Streaming Tokens with Custom Atomics

**Objective**: Architect a high-performance lock-free ring buffer in Rust for streaming LLM inference tokens with custom memory ordering and zero heap allocations in critical path.

---

## Problem Statement

Implement `LockFreeTokenStream<T, const N: usize>`. Multiple producer threads stream generated token IDs to a consumer thread. Implement a multi-producer single-consumer (MPSC) lock-free ring buffer using atomic sequence numbers, cache-line padded indices, and explicit memory ordering. Prove that uninitialized memory is never exposed to the consumer.

---

## Formal Constraints

- Latency: Sub-50ns push/pop operations.
- Safety: Formal proof of data race freedom using Acquire and Release memory orderings.
- Cache alignment: Align buffer structures to 64-byte cache line boundaries (#[repr(align(64))]) to eliminate false sharing.

---

## Starter Code

```python
use std::sync::atomic::{AtomicUsize, Ordering};
use std::cell::UnsafeCell;

#[repr(align(64))]
pub struct MpscTokenRingBuffer<T, const N: usize> {
    // TODO: Cache-aligned head and tail pointers, slot array
}

impl<T: Copy + Default, const N: usize> MpscTokenRingBuffer<T, N> {
    pub fn new() -> Self {
        unimplemented!()
    }

    pub fn try_push(&self, item: T) -> Result<(), T> {
        // TODO: Atomic CAS reservation and Release store
        unimplemented!()
    }

    pub fn try_pop(&self) -> Option<T> {
        // TODO: Consumer Acquire load
        unimplemented!()
    }
}
```

---

## Verification Test Cases

- [ ] **Test Case**: 4 producers and 1 consumer transfer 10,000,000 tokens with zero loss or corruption.
- [ ] **Test Case**: Assert zero false sharing between producer and consumer cache lines under perf profiling.
- [ ] **Test Case**: Miri passes without undefined behavior or data race errors.

---

## Solution & Invariant Check

Producers reserve slot via atomic fetch_add on tail; write payload; set turn flag with Ordering::Release; consumer waits for turn flag with Ordering::Acquire.