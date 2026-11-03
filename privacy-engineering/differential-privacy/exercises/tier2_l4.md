# Exercise TIER2_L4: DP-SGD Gradient Clipping and Gaussian Perturbation in PyTorch

**Objective**: Implement per-sample gradient clipping and calibrated Gaussian noise injection inside a custom PyTorch training loop.

---

## Problem Statement

Implement `train_dp_epoch(model, optimizer, data_loader, max_grad_norm: float, noise_multiplier: float)`. In each step, compute per-sample gradients, clip their L2 norms to `max_grad_norm`, sum them, add calibrated Gaussian noise, and update weights. Assert that model parameters update without error and noise scales properly with C.

---

## Formal Constraints

- Dataset: Synthetic classification or MNIST batch.
- Clipping: Strictly enforce L2 norm bound ||g_i||_2 <= C for every sample i.
- Noise: Inject Gaussian noise N(0, sigma^2 C^2 I) where sigma is noise multiplier.

---

## Starter Code

```python
import torch
import torch.nn as nn

def train_dp_epoch(model: nn.Module, 
                   optimizer: torch.optim.Optimizer, 
                   data_loader: torch.utils.data.DataLoader, 
                   max_grad_norm: float, 
                   noise_multiplier: float) -> float:
    # TODO: Implement per-sample clipping and noisy gradient descent
    pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Per-sample gradient norm never exceeds max_grad_norm before summation.
- [ ] **Test Case**: Setting noise_multiplier=0 matches standard non-private training with gradient clipping.
- [ ] **Test Case**: Loss converges on linearly separable dataset under modest noise.

---

## Solution & Invariant Check

Calculates per-sample norm; scales sample_grad by min(1.0, C / norm); adds torch.randn_like(grad) * (noise_multiplier * C).