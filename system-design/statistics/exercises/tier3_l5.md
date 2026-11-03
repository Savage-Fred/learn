# Exercise TIER3_L5: Sequential Testing Framework using Mixture SPRT

**Objective**: Implement a continuous monitoring framework using mixture Sequential Probability Ratio Test (mSPRT) allowing early stopping while strictly bounding Type I error.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `kohavi-controlled-experiments-2020`, `deng-cuped-2013`
- **Applicable Citations**:
  - [Trustworthy Online Controlled Experiments: A Practical Guide to A/B Testing](https://www.cambridge.org/core/books/trustworthy-online-controlled-experiments/D97B26382DEF7E123BEBF29C99026219) (2020)
  - [Improving the Sensitivity of Online Controlled Experiments by Utilizing Pre-Experiment Data](https://dl.acm.org/doi/10.1145/2433396.2433413) (2013)

---

## Problem Statement

Implement `MixtureSPRT(alpha=0.05, mixing_variance=1.0)`. As data streams in day by day, calculate the mixture likelihood ratio of treatment vs control. Return whether the test has reached statistical significance (allowing early stopping to ship or abort) or should continue running. Show that under the null hypothesis, false positive rate remains <= 5% across 30 days of daily checks.

---

## Formal Constraints

- Evaluation: Daily evaluation over 30 days without inflating false positive rate above 5%.
- Stopping rule: Stop immediately if likelihood ratio exceeds 1 / alpha boundary.

---

## Starter Code

```python
import numpy as np

class MixtureSPRT:
    def __init__(self, alpha: float = 0.05, mixing_variance: float = 1.0):
        self.alpha = alpha
        self.theta = mixing_variance

    def update_and_check(self, control_stream: np.ndarray, treatment_stream: np.ndarray) -> dict:
        # TODO: Compute Gaussian mixture likelihood ratio statistic
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Under strong positive effect, stops experiment on Day 4 instead of waiting for Day 30.
- [ ] **Test Case**: Under severe negative effect (regression), triggers emergency abort on Day 2.
- [ ] **Test Case**: Monte Carlo simulation of 1,000 null A/A tests verifies false positive rate <= 5% under continuous peeking.

---

## Solution & Invariant Check

Likelihood ratio Lambda_n = sqrt(V_n / (V_n + n*theta)) * exp( (n*theta * S_n^2) / (2 * V_n * (V_n + n*theta)) ); stop when Lambda_n >= 1 / alpha.