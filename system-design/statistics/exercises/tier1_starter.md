# Exercise TIER1_STARTER: Two-Sample T-Test, Sample Ratio Mismatch (SRM) & Bonferroni Correction

**Objective**: Build a statistical testing utility from first principles that checks for Sample Ratio Mismatch and conducts two-sample hypothesis tests with Bonferroni correction.

---

## Problem Statement

Implement `evaluate_experiment_batch(control_data: list, treatment_data: list, expected_ratio: float = 0.5, alpha: float = 0.05) -> dict`. First test for SRM using chi-squared test. If SRM fails (p < 0.001), raise SRMDetectedError. Otherwise compute difference in means, 95% confidence interval, p-value, and apply Bonferroni correction for k concurrent metrics.

---

## Invariant Scaffolding & Guidance

- Chi-squared test for SRM checks if observed counts match expected traffic split.
- Bonferroni adjusts significance threshold: alpha_adj = alpha / k.
- Two-sample t-statistic = (mean_T - mean_C) / sqrt(var_T/n_T + var_C/n_C).

---

## Starter Code

```python
from typing import List, Dict

def evaluate_experiment_batch(control_metrics: Dict[str, List[float]], 
                              treatment_metrics: Dict[str, List[float]], 
                              alpha: float = 0.05) -> dict:
    # TODO: Check SRM, compute two-sample t-test for each metric, apply Bonferroni
    pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Detects SRM when traffic split is 4,000 control vs 6,000 treatment (expected 5,000/5,000).
- [ ] **Test Case**: Computes accurate difference in means and p-values matching SciPy ttest_ind.
- [ ] **Test Case**: Correctly inflates critical p-value threshold under 10 concurrent metrics.

---

## Solution & Invariant Check

SRM: chi2 = sum((obs - exp)^2 / exp); t_stat = (m1 - m2) / sqrt(s1^2/n1 + s2^2/n2); df via Welch-Satterthwaite formula.