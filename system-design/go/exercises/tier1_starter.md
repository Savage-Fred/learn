# Exercise TIER1_STARTER: Concurrent Pipeline Pattern with Channels in Go

**Objective**: Build a concurrent streaming pipeline in Go connecting generator, transform, and sink stages via channels with graceful context cancellation.

---

## Problem Statement

Implement three pipeline functions: `Generator(ctx context.Context, nums ...int) <-chan int`, `Square(ctx context.Context, in <-chan int) <-chan int`, and `Sink(ctx context.Context, in <-chan int) []int`. The pipeline must stream integers, compute squares concurrently, and collect results. If ctx is cancelled mid-stream, all goroutines must exit cleanly with zero leaks.

---

## Invariant Scaffolding & Guidance

- The producing goroutine exclusively owns and closes its outbound channel.
- Every stage listens on ctx.Done() to terminate promptly on cancellation.

---

## Starter Code

```python
package main

import "context"

func Generator(ctx context.Context, nums ...int) <-chan int {
    out := make(chan int)
    // TODO: Stream numbers and handle cancellation
    return out
}

func Square(ctx context.Context, in <-chan int) <-chan int {
    out := make(chan int)
    // TODO: Compute squares and handle cancellation
    return out
}

func Sink(ctx context.Context, in <-chan int) []int {
    // TODO: Collect results until channel closed or ctx cancelled
    return nil
}
```

---

## Verification Test Cases

- [ ] **Test Case**: Pipelining [1, 2, 3, 4] yields [1, 4, 9, 16].
- [ ] **Test Case**: Cancelling ctx before completion causes all goroutines to exit immediately.
- [ ] **Test Case**: Zero goroutines leaked verified via runtime.NumGoroutine().

---

## Solution & Invariant Check

Defer close(out); select on out <- val vs <-ctx.Done().