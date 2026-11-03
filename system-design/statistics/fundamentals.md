# Core Fundamentals & Invariants: Statistics for Data Analysis & Experimentation

This document articulates the axiomatic invariants, theoretical grounding, mental models, idiomatic code implementations, architectural tradeoffs, and failure modes governing this topic.

---

## 1. Axiomatic Core Invariants

### Invariant 1: Type I / Type II Error Trade-Off Invariant
$$
\alpha = \Pr[\text{Reject } H_0 \mid H_0 \text{ is True}], \quad \beta = \Pr[\text{Fail to Reject } H_0 \mid H_1 \text{ is True}]. \quad \text{Sample size } n \approx \frac{16 \sigma^2}{\Delta^2} \text{ for } \alpha=0.05, 1-\beta=0.80.
$$
**Implications & Guarantees**: Sample size scales quadratically with reciprocal effect size; detecting 50% smaller effects requires 4x the sample size.

### Invariant 2: CUPED Variance Reduction Invariant
$$
Y_{cuped} = Y - \theta (X - \mathbb{E}[X]), \quad \theta = \frac{\text{Cov}(Y, X)}{\text{Var}(X)}, \quad \text{Var}(Y_{cuped}) = \text{Var}(Y) (1 - \rho_{XY}^2).
$$
**Implications & Guarantees**: Using pre-experiment data X correlated with metric Y strictly reduces variance by factor 1 - rho^2 without introducing estimator bias.

### Invariant 3: Continuous Monitoring (Peeking) Bias Invariant
$$
\lim_{T \to \infty} \Pr[\exists t \le T : |Z_t| > z_{\alpha/2} \mid H_0] = 1.
$$
**Implications & Guarantees**: Continuously checking a standard fixed-horizon p-value over time will reject the null hypothesis with probability approaching 100% even when no effect exists.

---

## 2. Core Mental Models

### Mental Model 1: The Two-Sided Marketplace SUTVA Violation
If an experiment subsidizes drivers in group A (treatment), riders hail them faster, depriving control drivers in group B of rides. This violates SUTVA (Stable Unit Treatment Value Assumption). Mitigate using cluster randomization (geographic zones) or switchback experiments (alternating time windows).

### Mental Model 2: Alpha Spending and Sequential Testing
Instead of testing at a single fixed horizon, alpha is distributed across the experiment lifecycle using an alpha spending function (e.g. O'Brien-Fleming or Pocock), or Wald's SPRT (Sequential Probability Ratio Test), allowing early stopping for overwhelming success or failure.

---

## 3. Idiomatic Code Examples

### CUPED Variance Reduction and Benjamini-Hochberg FDR Control
```python
import numpy as np
from typing import List, Tuple

def apply_cuped(y_pre: np.ndarray, y_post: np.ndarray) -> np.ndarray:
    """Computes CUPED-adjusted post-experiment metric."""
    cov = np.cov(y_post, y_pre)[0, 1]
    var_pre = np.var(y_pre, ddof=1)
    if var_pre == 0:
        return y_post
    theta = cov / var_pre
    mean_pre = np.mean(y_pre)
    return y_post - theta * (y_pre - mean_pre)

def benjamini_hochberg(p_values: List[float], fdr_q: float = 0.05) -> List[Tuple[float, bool]]:
    """Enforces False Discovery Rate (FDR) control on multiple hypothesis tests."""
    m = len(p_values)
    # Sort p-values with original indices
    sorted_indices = np.argsort(p_values)
    sorted_p = np.array(p_values)[sorted_indices]
    
    # Critical threshold: (i / m) * q
    thresholds = (np.arange(1, m + 1) / m) * fdr_q
    significant = sorted_p <= thresholds
    
    # Find largest k where p_k <= (k/m)*q
    max_sig_idx = -1
    for i in range(m - 1, -1, -1):
        if significant[i]:
            max_sig_idx = i
            break
            
    is_sig_sorted = np.zeros(m, dtype=bool)
    if max_sig_idx >= 0:
        is_sig_sorted[:max_sig_idx + 1] = True
        
    # Re-order back to original order
    results = [False] * m
    for orig_idx, sig_flag in zip(sorted_indices, is_sig_sorted):
        results[orig_idx] = bool(sig_flag)
        
    return [(p, sig) for p, sig in zip(p_values, results)]
```
**Analysis**: Demonstrates CUPED theta calculation to remove pre-experiment variance, and Benjamini-Hochberg FDR thresholding across m parallel hypothesis tests.

---

## 4. Architectural Tradeoffs

### CUPED vs Longer Experiment Duration
CUPED reduces metric variance by 30-50% if a strong pre-experiment feature exists (e.g. past 30 days streaming hours), effectively cutting required sample size by half without extending experiment duration. However, it requires joining pre-experiment logs and cannot be applied to entirely new user cohorts.

### Fixed Horizon vs Sequential Testing (SPRT)
Fixed horizon tests are mathematically simpler and have maximum power at the designated sample size, but cannot be monitored continuously. Sequential testing allows continuous monitoring and early stopping for catastrophic regressions, but suffers a slight loss in power at the final sample size.

---

## 5. Common Failure Modes & Anti-Patterns

### Failure Mode 1: The Peeking Problem
- **Root Cause**: Dashboard operators monitor experiment p-values daily and stop the experiment the moment p < 0.05 is observed, inflating true false positive rate from 5% to 30%+.
- **Mitigation & Invariant Defense**: Enforce sequential testing bounds (mSPRT), lock dashboards until pre-determined sample size is reached, or use alpha spending functions.

### Failure Mode 2: Survivorship and Selection Bias in Logged Data
- **Root Cause**: Calculating metrics only on users who triggered a specific event during the experiment, ignoring users who dropped out before triggering.
- **Mitigation & Invariant Defense**: Always analyze on an Intent-to-Treat (ITT) basis over all randomized units.
