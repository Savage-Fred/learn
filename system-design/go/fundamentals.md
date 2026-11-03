# Core Fundamentals & Invariants: Go for Distributed Systems & Cloud Infrastructure

This document articulates the axiomatic invariants, theoretical grounding, mental models, idiomatic code implementations, architectural tradeoffs, and failure modes governing this topic.

---

## 1. Axiomatic Core Invariants

### Invariant 1: CSP Share Memory By Communicating Invariant
$$
\text{Do not communicate by sharing memory; instead, share memory by communicating over typed channels } (\text{chan } T).
$$
**Implications & Guarantees**: Ownership of data is transferred explicitly across goroutine boundaries, eliminating race conditions on shared memory buffers.

### Invariant 2: Context Propagation Invariant
$$
\forall \text{ RPC or goroutine spawn }, \text{ctx is passed as first parameter}. \quad \text{Done}() \text{ signal must trigger immediate abort and resource cleanup}.
$$
**Implications & Guarantees**: Never store Context in a struct; cancellations and deadlines cascade hierarchically down the call tree, preventing orphaned background work.

### Invariant 3: Goroutine Lifecycle Containment Invariant
$$
\forall \text{ goroutine } g, \exists \text{ deterministic termination condition } C \text{ such that } g \text{ exits within bounded time } t < \infty.
$$
**Implications & Guarantees**: Spawning a goroutine without a guaranteed exit path (e.g. listening on an unclosed channel) creates an unrecoverable memory leak.

---

## 2. Core Mental Models

### Mental Model 1: The GMP Runtime Scheduler
G = Goroutine (lightweight 2KB stack), M = OS Thread (Machine), P = Logical Processor (GOMAXPROCS). Each P maintains a local run queue of 256 goroutines. When a P's queue is empty, it steals half the work from another P. Sysmon preempts long-running goroutines (>10ms) cooperatively or via OS signals.

### Mental Model 2: Escape Analysis and the GC Tri-Color Model
The compiler determines if a variable's address escapes the function activation frame. Escaped variables move to the heap, creating work for the concurrent tri-color mark-and-sweep GC. Keeping variables on the stack eliminates GC overhead entirely.

---

## 3. Idiomatic Code Examples

### Sliding-Window Rate Limiter and Single-Flight Coalescer in Go
```go
package main

import (
	"context"
	"sync"
	"time"
	"errors"
)

// SingleFlight suppresses duplicate concurrent requests for the same key.
type SingleFlight struct {
	mu sync.Mutex
	m  map[string]*call
}

type call struct {
	wg  sync.WaitGroup
	val any
	err error
}

func (g *SingleFlight) Do(key string, fn func() (any, error)) (any, error) {
	g.mu.Lock()
	if g.m == nil {
		g.m = make(map[string]*call)
	}
	if c, ok := g.m[key]; ok {
		g.mu.Unlock()
		c.wg.Wait()
		return c.val, c.err
	}
	c := new(call)
	c.wg.Add(1)
	g.m[key] = c
	g.mu.Unlock()

	c.val, c.err = fn()
	c.wg.Done()

	g.mu.Lock()
	delete(g.m, key)
	g.mu.Unlock()

	return c.val, c.err
}

// BoundedWorkerPool processes tasks with bounded concurrency and context cancellation.
func ProcessPipeline(ctx context.Context, items []string, maxWorkers int, processFn func(context.Context, string) error) error {
	jobs := make(chan string)
	errChan := make(chan error, maxWorkers)
	var wg sync.WaitGroup

	for i := 0; i < maxWorkers; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for {
				select {
				case <-ctx.Done():
					return
				case item, ok := <-jobs:
					if !ok {
						return
					}
					if err := processFn(ctx, item); err != nil {
						select {
						case errChan <- err:
						default:
						}
					}
				}
			}
		}()
	}

	go func() {
		defer close(jobs)
		for _, item := range items {
			select {
			case <-ctx.Done():
				return
			case jobs <- item:
			}
		}
	}()

	wg.Wait()
	close(errChan)

	if err, ok := <-errChan; ok {
		return err
	}
	return ctx.Err()
}
```
**Analysis**: Demonstrates SingleFlight request deduplication and a resilient bounded worker pool with context propagation and zero goroutine leaks.

---

## 4. Architectural Tradeoffs

### Buffered vs Unbuffered Channels
Unbuffered channels provide synchronous handoff invariants (sender blocks until receiver is ready), guaranteeing synchronization. Buffered channels decouple producers and consumers, absorbing bursts, but risk unbounded memory growth or delayed backpressure if sized too large.

### sync.Mutex vs Channel Coordination
Channels are ideal for passing ownership of data and orchestrating workflows (select, cancellation). Mutexes are simpler, faster, and consume less memory when protecting simple shared in-memory counters or hash maps.

---

## 5. Common Failure Modes & Anti-Patterns

### Failure Mode 1: Goroutine Leak on Nil Channel or Blocked Send
- **Root Cause**: Sending to an unbuffered channel when no receiver is listening, or receiving on a channel that is never closed, leaves the goroutine running forever, permanently leaking its stack and referenced heap objects.
- **Mitigation & Invariant Defense**: Always select with ctx.Done() or ensure deferred channel closing by the producing goroutine.

### Failure Mode 2: Loop Variable Capture in Goroutines (pre-Go 1.22)
- **Root Cause**: Spawning goroutines inside a for loop capturing the loop variable by reference causes all goroutines to observe the final loop value.
- **Mitigation & Invariant Defense**: Pass the variable as an explicit parameter to the goroutine closure: go func(val string) { ... }(val).
