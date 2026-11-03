# Exercise TIER3_L5: Distributed Leader Election Client with Lease Keep-Alives

**Objective**: Implement a distributed leader election client in Go using etcd/Consul lease primitives with automatic lease keep-alives and context-aware failover.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `donovan-kernighan-go-2015`, `vyukov-go-scheduler-2012`
- **Applicable Citations**:
  - [The Go Programming Language](https://www.gopl.io/) (2015)
  - [Scalable Go Scheduler Design Doc](https://golang.org/s/go11sched) (2012)

---

## Problem Statement

Implement `LeaderElectionClient(nodeID: string, leaseTTL: time.Duration)`. Support `Campaign(ctx context.Context) <-chan LeaderStatus`. The client attempts to acquire the leader lease. When acquired, it starts a background keep-alive loop. If the context is cancelled or keep-alive fails, it relinquishes leadership and yields to secondary candidates. Returns status channel notifying application of leadership changes.

---

## Formal Constraints

- Lease TTL: 5-second lease heartbeat.
- Failover: If leader crashes, secondary candidate must acquire lease within 6 seconds.
- Safety: Fencing token ensures split-brain leader cannot issue commands after lease expiry.

---

## Starter Code

```python
package main

import (
	"context"
	"time"
)

type LeaderStatus struct {
	IsLeader bool
	Term     int64
}

type LeaderElectionClient struct {
	nodeID   string
	leaseTTL time.Duration
	// TODO: State and connection fields
}

func NewLeaderElectionClient(nodeID string, ttl time.Duration) *LeaderElectionClient {
	return &LeaderElectionClient{nodeID: nodeID, leaseTTL: ttl}
}

func (c *LeaderElectionClient) Campaign(ctx context.Context) <-chan LeaderStatus {
	statusCh := make(chan LeaderStatus)
	// TODO: Campaign loop and keep-alive
	return statusCh
}
```

---

## Verification Test Cases

- [ ] **Test Case**: Primary candidate acquires leadership and successfully sends keep-alives.
- [ ] **Test Case**: Simulated network drop on primary leads to lease expiry and secondary candidate claiming leadership.
- [ ] **Test Case**: Context cancellation causes leader to gracefully step down and release lease.

---

## Solution & Invariant Check

Atomic term counter increments on every election; lease keep-alive runs on time.Ticker; select handles ticker vs ctx.Done().