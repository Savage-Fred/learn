# Exercise TIER3_L5: Rényi Differential Privacy (RDP) Accountant

**Objective**: Build an analytical RDP privacy accountant that tracks cumulative privacy loss across training epochs and converts to (ε, δ)-DP.

---

## Problem Statement

Implement `RDPAccountant(sample_rate: float, noise_multiplier: float)`. Support `step(num_steps: int = 1)` and `get_epsilon(target_delta: float = 1e-5) -> float`. Track RDP accumulation across 1,000 training steps and output final calibrated epsilon.

---

## Formal Constraints

- Orders: Evaluate Rényi divergence across orders alpha in range [1.5, 64].
- Composition: Linear addition of RDP bounds for Gaussian mechanisms with subsampling.
- Conversion: Enforce epsilon(delta) = min_{alpha} (RDP(alpha) + ln(1/delta) / (alpha - 1)).

---

## Starter Code

```python
import numpy as np

class RDPAccountant:
    def __init__(self, sample_rate: float, noise_multiplier: float):
        self.q = sample_rate
        self.sigma = noise_multiplier
        self.alphas = np.linspace(1.5, 64, 100)
        self.rdp = np.zeros_like(self.alphas)

    def step(self, steps: int = 1) -> None:
        # TODO: Accumulate RDP for subsampled Gaussian mechanism
        pass

    def get_epsilon(self, target_delta: float = 1e-5) -> float:
        # TODO: Convert RDP to optimal (epsilon, delta)-DP
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: RDP accumulates strictly linearly with number of steps.
- [ ] **Test Case**: Yields epsilon ~ 1.5 - 3.0 for 1,000 steps with noise_multiplier=1.0 and q=0.01.
- [ ] **Test Case**: Conversion formula satisfies epsilon = min_alpha (rdp(alpha) + log(1/delta)/(alpha-1)).

---

## Solution & Invariant Check

Gaussian RDP bound alpha / (2 * sigma^2); subsampling amplification theorem; optimal alpha minimization over grid.