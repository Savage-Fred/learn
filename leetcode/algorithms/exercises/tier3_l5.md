# Exercise TIER3_L5: 2-SAT Boolean Satisfiability Solver

**Objective**: Build a linear-time 2-SAT solver reducing 2-CNF clauses to an implication graph and finding a valid truth assignment.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `clrs-4th-ed-2022`, `kleinberg-tardos-2005`
- **Applicable Citations**:
  - [Introduction to Algorithms](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/) (2022)
  - [Algorithm Design](https://www.pearson.com/en-us/subject-catalog/p/algorithm-design/P200000003260) (2005)

---

## Problem Statement

Implement `solve_2sat(num_vars: int, clauses: List[Tuple[int, int]]) -> Optional[List[bool]]`. Each clause (x, y) represents (x OR y), where negative integers represent negation (e.g. -1 is NOT x1). If satisfiable, return a valid truth assignment for variables 1..num_vars. If unsatisfiable, return None.

---

## Formal Constraints

- Variables: Up to 100,000 Boolean variables.
- Clauses: Up to 500,000 2-CNF clauses.
- Time complexity: O(V + E) strictly linear.

---

## Starter Code

```python
from typing import List, Tuple, Optional

def solve_2sat(num_vars: int, clauses: List[Tuple[int, int]]) -> Optional[List[bool]]:
    # TODO: Build implication graph, run Tarjan SCC, verify x and not-x in different SCCs
    pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Trivial satisfiable clause (1, 2) and (-1, 2) assigns True to x2.
- [ ] **Test Case**: Unsatisfiable contradiction (1, 1), (-1, -1) returns None.
- [ ] **Test Case**: Large random 2-SAT instance with 50,000 variables and 100,000 clauses runs in under 1 second.

---

## Solution & Invariant Check

Clause (u OR v) translates to (~u -> v) and (~v -> u). Satisfiable iff SCC(x) != SCC(~x). Assignment truth value: if SCC(x) > SCC(~x) (topological reverse order) then True else False.