# Exercise TIER2_L4: Bipartite Maximum Matching via Dinic's Algorithm

**Objective**: Formulate maximum bipartite matching as a network flow problem and solve it using Dinic's algorithm.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `clrs-4th-ed-2022`, `kleinberg-tardos-2005`
- **Applicable Citations**:
  - [Introduction to Algorithms](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) (2022)
  - [Algorithm Design](https://www.pearson.com/en-us/subject-catalog/p/algorithm-design/P200000003260) (2005)

---

## Problem Statement

Implement `max_bipartite_matching(workers, tasks, compatibilities) -> int`. Construct a flow network with a source supernode connected to all workers, workers connected to compatible tasks with unit capacity, and all tasks connected to a sink supernode with unit capacity. Return the maximum number of matched worker-task pairs.

---

## Formal Constraints

- Nodes: Up to 1,000 workers and 1,000 tasks.
- Edges: Up to 10,000 capability links.
- Time complexity: O(E * sqrt(V)) for unit network flow.

---

## Starter Code

```python
from typing import List, Tuple

def max_bipartite_matching(num_workers: int, num_tasks: int, edges: List[Tuple[int, int]]) -> int:
    # TODO: Construct flow network and invoke Dinic max flow
    pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Complete bipartite graph matching all workers.
- [ ] **Test Case**: Bottle-necked matching where multiple workers contend for a single task.
- [ ] **Test Case**: Zero compatible edges returns 0.

---

## Solution & Invariant Check

Source -> workers with cap 1; tasks -> sink with cap 1; cross edges with cap 1; compute max flow.