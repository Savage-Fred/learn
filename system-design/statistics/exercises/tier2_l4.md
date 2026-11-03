# Exercise TIER2_L4: CUPED Variance Reduction Engine

**Objective**: Implement the CUPED variance reduction transformation on user engagement data and evaluate the reduction in confidence interval width.

---

## Problem Statement

Implement `CUPEDTransformer`. Accept pre-experiment metric array `X` and post-experiment metric array `Y`. Calculate optimal theta: `Cov(Y, X) / Var(X)`. Transform post-experiment metric to `Y_cuped`. Compare the standard error and confidence interval width of `Y` vs `Y_cuped`. Verify variance reduction matches theoretical `1 - rho^2`.

---

## Formal Constraints

- Input: 100,000 users with pre-experiment 14-day metric and post-experiment 14-day metric.
- Output: CUPED-adjusted metric, percentage variance reduction, and new p-value.
- Unbiasedness: Assert that mean difference between treatment and control is preserved.

---

## Starter Code

```python
import numpy as np

class CUPEDTransformer:
    def fit_transform(self, x_control: np.ndarray, y_control: np.ndarray,
                      x_treatment: np.ndarray, y_treatment: np.ndarray) -> dict:
        # TODO: Calculate pooled theta, compute Y_cuped, evaluate variance reduction
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: When correlation rho = 0.7, variance reduction is approximately 49% (1 - 0.7^2).
- [ ] **Test Case**: Point estimate of treatment effect matches unadjusted effect within numerical precision.
- [ ] **Test Case**: Confidence interval width is narrowed by factor of sqrt(1 - rho^2).

---

## Solution & Invariant Check

Compute pooled covariance across combined control and treatment sets to maximize estimation efficiency without bias.