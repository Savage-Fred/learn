# Exercise TIER1_STARTER: Laplace Mechanism for Counting Queries and Randomized Response

**Objective**: Build a calibrated Laplace noise generator from first principles and implement Warner's Randomized Response for binary surveys.

---

## Problem Statement

Implement `laplace_mechanism(true_count: int, epsilon: float) -> float` and `randomized_response_survey(true_answers: List[bool], p_truth: float = 0.5) -> float`. Prove that the randomized response estimator is unbiased and calculate its empirical variance.

---

## Invariant Scaffolding & Guidance

- Counting query sensitivity Delta_1 = 1.
- Laplace noise scale b = Delta_1 / epsilon.
- Randomized response: Coin 1 heads -> tell truth; tails -> flip Coin 2 (heads=Yes, tails=No).

---

## Starter Code

```python
import numpy as np

def laplace_mechanism(true_count: int, epsilon: float) -> float:
    # TODO: Sample Laplace noise with scale 1.0 / epsilon
    pass

def randomized_response_estimate(reported_answers: list, p_truth: float = 0.5) -> float:
    # TODO: Invert coin flip probabilities to estimate true proportion of Yes answers
    pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Mean of 10,000 Laplace evaluations on true_count=100 centered at 100.
- [ ] **Test Case**: Standard deviation of Laplace noise matches sqrt(2) / epsilon.
- [ ] **Test Case**: Randomized response correctly recovers true proportion (e.g. 70%) within confidence bounds.

---

## Solution & Invariant Check

Laplace noise sampled via inverse CDF: -b * sgn(U) * ln(1 - 2|U|); Randomized response estimated proportion = (p_yes - (1 - p_truth)/2) / p_truth.