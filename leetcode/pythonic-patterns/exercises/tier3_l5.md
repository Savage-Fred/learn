# Exercise TIER3_L5: Asynchronous Rate-Limited Task Pipeline with Backpressure

**Objective**: Build a high-concurrency streaming pipeline using asyncio.Queue, TaskGroup, and asyncio.Semaphore preventing memory exhaustion and task cancellation leaks.

---

## Problem Statement

Implement `AsyncStreamPipeline` which accepts an asynchronous generator of raw records. It must feed tasks into a worker pool bounded by `max_concurrency` and rate-limited to `rate_limit_rps`. If workers fall behind and queue depth reaches `max_queue_depth`, backpressure must pause ingestion from the generator. Must support graceful shutdown and signal cancellation.

---

## Formal Constraints

- Throughput: Process 10,000 asynchronous items with concurrency bounded to N workers.
- Rate limit: Max R requests per second using a leaky-bucket or token-bucket algorithm.
- Resilience: Unhandled exceptions in one task must not crash sibling tasks without orderly cancellation.

---

## Starter Code

```python
import asyncio
from typing import AsyncIterable, Callable, Any

class AsyncStreamPipeline:
    def __init__(self, max_concurrency: int, rate_limit_rps: float, max_queue_depth: int):
        self.max_concurrency = max_concurrency
        self.rate_limit_rps = rate_limit_rps
        self.max_queue_depth = max_queue_depth

    async def run(self, source_gen: AsyncIterable[Any], worker_fn: Callable[[Any], Any]):
        # TODO: Implement backpressure queue and worker pool
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Queue depth never exceeds max_queue_depth during slow worker test.
- [ ] **Test Case**: Effective rate limit does not exceed specified RPS over a 5-second window.
- [ ] **Test Case**: Worker cancellation handles CancelledError cleanly and drains pending tasks.

---

## Solution & Invariant Check

Uses asyncio.Queue(maxsize=max_queue_depth) for natural backpressure; asyncio.TaskGroup for exception cascading and structured concurrency.