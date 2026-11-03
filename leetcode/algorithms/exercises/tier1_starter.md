# Exercise TIER1_STARTER: Tarjan's Strongly Connected Components and Topological Sort

**Objective**: Implement Tarjan's SCC algorithm on a directed graph and condense the components into an acyclic DAG.

---

## Problem Statement

Given a directed graph with `N` nodes and a list of directed edges, implement `find_sccs(n, edges) -> List[List[int]]`. The function must return all strongly connected components in topological order of the condensed DAG in O(V + E) time.

---

## Invariant Scaffolding & Guidance

- A node's low-link value represents the smallest discovery time reachable via back-edges in its DFS subtree.
- A node is an SCC root if discovery_time[u] == low_link[u].

---

## Starter Code

```python
from typing import List

def find_sccs(n: int, edges: List[List[int]]) -> List[List[int]]:
    # TODO: Implement Tarjan's SCC algorithm
    pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Simple cycle (0 -> 1 -> 2 -> 0) returns single SCC [0, 1, 2].
- [ ] **Test Case**: DAG with no cycles returns N individual single-node SCCs in topological order.
- [ ] **Test Case**: Disconnected graph with multiple independent components.

---

## Solution & Invariant Check

Single DFS traversal tracking dfs_num, dfs_low, and an on_stack boolean array.