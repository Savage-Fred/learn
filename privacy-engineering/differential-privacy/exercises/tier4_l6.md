# Exercise TIER4_L6: Petabyte-Scale Differential Privacy Budget Management Gateway

**Objective**: Architect a centralized privacy budget management service for enterprise analytics that enforces hierarchical privacy budgets, detects composition exhaustion, and generates verifiable privacy proofs.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `dwork-roth-dp-2014`, `abadi-dpsgd-2016`, `mironov-rdp-2017`
- **Applicable Citations**:
  - [The Algorithmic Foundations of Differential Privacy](https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf) (2014)
  - [Deep Learning with Differential Privacy](https://dl.acm.org/doi/10.1145/2976749.2978318) (2016)
  - [Rényi Differential Privacy](https://ieeexplore.ieee.org/document/8049725) (2017)

---

## Problem Statement

Design and architect `PrivacyBudgetGateway`. When an analyst submits an SQL aggregation query with requested epsilon, the gateway checks their team's remaining privacy budget. If approved, it reserves the budget, executes the query, injects Laplace or Gaussian noise calibrated to the query's sensitivity, records the spent epsilon in an immutable audit ledger, and returns the noisy result. If the budget would be exceeded, the query is rejected with `PrivacyBudgetExhaustedError`.

---

## Formal Constraints

- Scale: 10,000 concurrent data analysts querying 1PB data warehouse.
- Governance: Hard cap on annual total budget (epsilon_total <= 5.0, delta_total <= 1e-6) per user cohort.
- Auditability: Cryptographically signed ledger proofs of remaining privacy budget.

---

## Starter Code

```python
class PrivacyBudgetGateway:
    def __init__(self, total_epsilon: float = 5.0, total_delta: float = 1e-6):
        self.total_epsilon = total_epsilon
        self.total_delta = total_delta
        # TODO: Initialize budget ledger and concurrency locks

    def execute_private_query(self, team_id: str, query_sql: str, requested_epsilon: float) -> dict:
        """Reserve budget, inject noise, log transaction, return result."""
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Consecutive queries decrement team's remaining budget until cap is reached.
- [ ] **Test Case**: Attempting to exceed total_epsilon rejects query and leaves budget unchanged.
- [ ] **Test Case**: Concurrent queries from multiple analysts execute with thread-safe atomic budget deduction.

---

## Solution & Invariant Check

Atomic compare-and-swap on remaining budget; advanced composition tracking; query plan parser extracting L1/L2 sensitivity from SQL GROUP BY and WHERE clauses.