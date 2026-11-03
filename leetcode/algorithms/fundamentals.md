# Core Fundamentals & Invariants: Master's-Level Algorithms

This document articulates the axiomatic invariants, theoretical grounding, mental models, idiomatic code implementations, architectural tradeoffs, and failure modes governing this topic.

---

## 1. Axiomatic Core Invariants

### Invariant 1: Potential Method Amortization Invariant
$$
\hat{c}_i = c_i + \Phi(D_i) - \Phi(D_{i-1}). \text{ If } \Phi(D_n) \ge \Phi(D_0), \text{ then } \sum_{i=1}^n \hat{c}_i \ge \sum_{i=1}^n c_i.
$$
**Implications & Guarantees**: Total amortized cost upper bounds the true operational cost of any arbitrary sequence of n operations.

### Invariant 2: Max-Flow Min-Cut Duality Invariant
$$
\max |f| = \min_{(S,T)} c(S, T) \text{ where } S \cup T = V, s \in S, t \in T, S \cap T = \emptyset.
$$
**Implications & Guarantees**: The maximum volume of flow passing from source s to sink t equals the minimum total capacity of edges whose removal disconnects s from t.

### Invariant 3: 2-SAT Satisfiability Invariant
$$
\phi \in 2\text{-CNF is satisfiable} \iff \forall x, \text{SCC}(x) \ne \text{SCC}(\neg x) \text{ in the implication graph } G_\phi.
$$
**Implications & Guarantees**: Boolean satisfiability for 2-variable clauses is solvable in strictly linear O(V + E) time via Tarjan's SCC algorithm.

---

## 2. Core Mental Models

### Mental Model 1: Residual Networks & Augmenting Paths
Flow algorithms operate on residual graphs where backward edges represent the capability to undo previous flow decisions. Dinic's algorithm finds blocking flows in layered DAGs in O(V^2 E) time.

### Mental Model 2: The Lower Envelope & Convex Hull Trick
When optimizing dp[i] = min_{j < i}(dp[j] + m_j * x_i), each candidate j represents a line y = m_j * x + c_j. Querying the minimum at x_i corresponds to evaluating the lower envelope of lines. If slopes are monotonic, a deque maintains the hull in O(N) total time.

---

## 3. Idiomatic Code Examples

### Dinic's Algorithm for Maximum Network Flow
```python
from collections import deque
from typing import List

class Edge:
    __slots__ = ("to", "capacity", "flow", "rev")
    def __init__(self, to: int, capacity: int, flow: int, rev: int):
        self.to = to
        self.capacity = capacity
        self.flow = flow
        self.rev = rev

class DinicMaxFlow:
    """Computes Maximum Network Flow in O(V^2 E) using layered networks."""
    def __init__(self, num_nodes: int):
        self.n = num_nodes
        self.graph: List[List[Edge]] = [[] for _ in range(num_nodes)]
        self.level: List[int] = [-1] * num_nodes
        self.ptr: List[int] = [0] * num_nodes

    def add_edge(self, u: int, v: int, cap: int) -> None:
        forward = Edge(v, cap, 0, len(self.graph[v]))
        backward = Edge(u, 0, 0, len(self.graph[u]))
        self.graph[u].append(forward)
        self.graph[v].append(backward)

    def _bfs(self, s: int, t: int) -> bool:
        self.level = [-1] * self.n
        self.level[s] = 0
        q = deque([s])
        while q:
            u = q.popleft()
            for edge in self.graph[u]:
                if edge.capacity - edge.flow > 0 and self.level[edge.to] == -1:
                    self.level[edge.to] = self.level[u] + 1
                    q.append(edge.to)
        return self.level[t] != -1

    def _dfs(self, u: int, t: int, pushed: int) -> int:
        if pushed == 0 or u == t:
            return pushed
        for cid in range(self.ptr[u], len(self.graph[u])):
            self.ptr[u] = cid
            edge = self.graph[u][cid]
            tr = edge.to
            if self.level[u] + 1 != self.level[tr] or edge.capacity - edge.flow == 0:
                continue
            pushable = min(pushed, edge.capacity - edge.flow)
            tr_pushed = self._dfs(tr, t, pushable)
            if tr_pushed == 0:
                continue
            edge.flow += tr_pushed
            self.graph[tr][edge.rev].flow -= tr_pushed
            return tr_pushed
        return 0

    def max_flow(self, s: int, t: int) -> int:
        flow = 0
        while self._bfs(s, t):
            self.ptr = [0] * self.n
            while True:
                pushed = self._dfs(s, t, float("inf"))
                if pushed == 0:
                    break
                flow += pushed
        return flow
```
**Analysis**: Standard Dinic algorithm using BFS to build level graphs and DFS with current-arc pointers to find blocking flows.

---

## 4. Architectural Tradeoffs

### Dinic Algorithm vs Push-Relabel (FIFO)
Dinic is O(V^2 E) and operates on global layered networks via augmenting paths, making it simple to implement and exceptionally fast on sparse/unit networks (O(E sqrt(V))). Push-Relabel operates via local preflow pushes and relabeling in O(V^3) or O(V^2 sqrt(E)), which outperforms Dinic on dense networks with heavy back-capacities.

### Tarjan SCC vs Kosaraju Algorithm
Tarjan computes Strongly Connected Components in a single DFS pass using node low-link numbers and a stack. Kosaraju requires two full DFS traversals and graph transposition. Tarjan has lower constant factors and requires less auxiliary memory.

---

## 5. Common Failure Modes & Anti-Patterns

### Failure Mode 1: Residual Graph Infinite Looping
- **Root Cause**: Failing to check edge.capacity - edge.flow > 0 during augmenting path search can lead to traversal of saturated edges or infinite cycles in residual graphs with cycles.
- **Mitigation & Invariant Defense**: Strictly enforce residual capacity strictly greater than zero and level[v] == level[u] + 1 in BFS/DFS.

### Failure Mode 2: 2-SAT Variable Negation Indexing Collision
- **Root Cause**: Incorrect mapping of variable indices (e.g. mapping variable x to 2x and not-x to 2x+1) can cause overlapping nodes or erroneous self-implication cycles.
- **Mitigation & Invariant Defense**: Use standardized node mapping: variable i corresponds to 2*i, negation not-i corresponds to 2*i + 1.
