# Exercise TIER4_L6: Online Minimum-Cost Flow Dispatcher for Multi-Cloud Cluster

**Objective**: Design an online min-cost maximum-flow dispatch engine for routing inference requests across multi-cloud GPU clusters under dynamic bandwidth costs and latency constraints.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `clrs-4th-ed-2022`, `kleinberg-tardos-2005`
- **Applicable Citations**:
  - [Introduction to Algorithms](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) (2022)
  - [Algorithm Design](https://www.pearson.com/en-us/subject-catalog/p/algorithm-design/P200000003260) (2005)

---

## Problem Statement

Architect and implement `OnlineClusterDispatcher`. It receives batches of token requests with latency SLAs and must dispatch them across GPU clusters with finite VRAM capacities and variable bandwidth transit costs. Implement successive shortest path with SPFA or cycle-canceling, supporting incremental edge updates without recomputing flow from scratch.

---

## Formal Constraints

- Clusters: 50 GPU clusters, 100,000 requests per minute.
- Dynamic pricing: Network edge costs fluctuate dynamically based on congestion.
- Deadlines: Strict 50ms dispatch latency deadline.

---

## Starter Code

```python
class OnlineClusterDispatcher:
    def __init__(self, cluster_capacities: dict, latency_matrix: dict):
        # TODO: Initialize min-cost flow network
        pass

    def update_edge_cost(self, u: str, v: str, new_cost: float):
        """Incrementally update edge cost and eliminate negative cycles if created."""
        pass

    def dispatch_batch(self, requests: list) -> dict:
        """Route requests minimizing total cost while satisfying capacity and latency."""
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Routes requests to lowest-cost cluster until capacity saturates, then spills over to secondary cluster.
- [ ] **Test Case**: Dynamic cost update triggers incremental reroute without full recomputation.
- [ ] **Test Case**: Proves zero SLA violations under 95% cluster utilization.

---

## Solution & Invariant Check

Min-Cost Max-Flow using node potentials (Johnson's transformation) allowing Dijkstra for fast incremental augmenting paths.