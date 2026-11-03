# Exercise TIER4_L6: High-Throughput gRPC Streaming Gateway with Zero-Allocation Buffers

**Objective**: Architect a high-throughput streaming reverse proxy in Go handling 100,000 concurrent bidirectional streams with bounded heap allocations and zero goroutine leaks.

---

## Problem Statement

Design and implement `StreamingGateway`. Accept inbound gRPC/TCP byte frames, route to target backend microservice, and stream bidirectional responses. Use `sync.Pool` to reuse byte slice buffers (avoiding GC churn). Implement adaptive load shedding: if an output buffer fills beyond 80% capacity, drop low-priority telemetry frames while preserving control frames. Assert zero goroutine leaks on stream disconnects.

---

## Formal Constraints

- Throughput: 100,000 active streams; 1,000,000 messages per second.
- Memory bounds: Zero heap allocations in critical frame proxying path using sync.Pool.
- Load shedding: Graceful backpressure and frame dropping when downstream consumer lags.

---

## Starter Code

```python
package main

import (
	"context"
	"net"
	"sync"
)

type StreamingGateway struct {
	bufPool sync.Pool
	// TODO: Connection tracking and load shedding configuration
}

func NewStreamingGateway(bufferSize int) *StreamingGateway {
	return &StreamingGateway{
		bufPool: sync.Pool{
			New: func() any {
				b := make([]byte, bufferSize)
				return &b
			},
		},
	}
}

func (g *StreamingGateway) ProxyStream(ctx context.Context, clientConn net.Conn, backendConn net.Conn) error {
	// TODO: Bidirectional zero-allocation copy with load shedding and clean teardown
	return nil
}
```

---

## Verification Test Cases

- [ ] **Test Case**: Proxies 1GB of bidirectional stream data with zero GC pauses exceeding 1ms.
- [ ] **Test Case**: Under consumer lag, drops telemetry frames and maintains p99 latency < 5ms for control frames.
- [ ] **Test Case**: Abrupt client disconnect cleans up all goroutines and returns buffers to sync.Pool.

---

## Solution & Invariant Check

Recycles byte slices via sync.Pool; coordinates bidirectional copy using sync.WaitGroup and context cancellation; uses io.CopyBuffer.