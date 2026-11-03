# Exercise TIER2_L4: In-Memory Cache with Single-Flight Request Coalescing

**Objective**: Build a thread-safe in-memory cache in Go with single-flight request coalescing to prevent cache thundering herd under high concurrency.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `donovan-kernighan-go-2015`, `vyukov-go-scheduler-2012`
- **Applicable Citations**:
  - [The Go Programming Language](https://www.gopl.io/) (2015)
  - [Scalable Go Scheduler Design Doc](https://golang.org/s/go11sched) (2012)

---

## Problem Statement

Implement `CacheWithSingleFlight`. Implement `Get(ctx context.Context, key string, fetchFn func(context.Context) (string, error)) (string, error)`. If the key exists in cache, return immediately. If not, only one goroutine may invoke `fetchFn`, while all other concurrent callers block waiting for the result of that single execution, populating the cache and returning.

---

## Formal Constraints

- Concurrency: 10,000 concurrent goroutines querying the same expired key.
- Coalescing: The expensive backend fetch function must be invoked exactly once.
- Thread safety: Mutex protection for cache reads/writes.

---

## Starter Code

```python
package main

import (
	"context"
	"sync"
)

type CacheWithSingleFlight struct {
	mu    sync.RWMutex
	store map[string]string
	// TODO: Add singleflight synchronization
}

func NewCache() *CacheWithSingleFlight {
	return &CacheWithSingleFlight{
		store: make(map[string]string),
	}
}

func (c *CacheWithSingleFlight) Get(ctx context.Context, key string, fetchFn func(context.Context) (string, error)) (string, error) {
	// TODO: Check cache, coalesce concurrent fetches, update cache
	return "", nil
}
```

---

## Verification Test Cases

- [ ] **Test Case**: 10,000 goroutines querying same key results in fetchFn being called exactly once.
- [ ] **Test Case**: Subsequent calls after cache population return cached value without calling fetchFn.
- [ ] **Test Case**: If fetchFn returns an error, the error is returned to all waiting callers and not cached.

---

## Solution & Invariant Check

Uses sync.WaitGroup and map[string]*call guarded by mutex; callers wait on wg.Wait() and receive shared result.