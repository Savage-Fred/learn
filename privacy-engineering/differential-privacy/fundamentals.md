# Core Fundamentals & Invariants: Modern Differential Privacy

This document articulates the axiomatic invariants, theoretical grounding, mental models, idiomatic code implementations, architectural tradeoffs, and failure modes governing this topic.

---

## 1. Axiomatic Core Invariants

### Invariant 1: (ε, δ)-Differential Privacy Definition Invariant
$$
\forall D \sim D' (\|D - D'\|_1 \le 1), \forall S \subseteq \text{Range}(\mathcal{M}), \quad \Pr[\mathcal{M}(D) \in S] \le e^\epsilon \Pr[\mathcal{M}(D') \in S] + \delta.
$$
**Implications & Guarantees**: The presence or absence of any single individual in the dataset cannot significantly shift the probability distribution of query outputs.

### Invariant 2: Gaussian Mechanism Parameterization Invariant
$$
\mathcal{M}(D) = f(D) + \mathcal{N}(0, \sigma^2 I), \quad \sigma \ge \frac{\Delta_2 f \sqrt{2 \ln(1.25 / \delta)}}{\epsilon} \implies (\epsilon, \delta)\text{-DP}.
$$
**Implications & Guarantees**: L2 sensitivity governs Gaussian noise calibration, enabling tighter composition than Laplace noise under vector-valued outputs.

### Invariant 3: Rényi Differential Privacy (RDP) Additive Composition
$$
D_\alpha(\mathcal{M}_1 \circ \mathcal{M}_2(D) \parallel \mathcal{M}_1 \circ \mathcal{M}_2(D')) = D_\alpha(\mathcal{M}_1(D) \parallel \mathcal{M}_1(D')) + D_\alpha(\mathcal{M}_2(D) \parallel \mathcal{M}_2(D')).
$$
**Implications & Guarantees**: RDP composes strictly linearly across thousands of training steps, converted back to (ε, δ)-DP to report formal privacy guarantees.

---

## 2. Core Mental Models

### Mental Model 1: The Privacy Loss Random Variable
Privacy loss is a random variable L = ln(Pr[M(D)=o] / Pr[M(D')=o]). Pure ε-DP bounds the worst-case maximum of L by ε. Approximate (ε, δ)-DP allows an exponentially small probability δ that L exceeds ε. RDP bounds the Rényi divergence (moments) of L, allowing tight Gaussian tail bounds.

### Mental Model 2: Central vs Local Differential Privacy
In Central DP, users trust a central server with raw data, and the server adds noise to aggregate outputs (error O(1/ε)). In Local DP (LDP), each user adds noise locally before transmitting to the server (error O(sqrt(N)/ε)). LDP provides immunity against untrusted servers at the cost of requiring massive sample sizes (N > 10M).

---

## 3. Idiomatic Code Examples

### DP-SGD Gradient Clipping and Gaussian Noise Injection in PyTorch
```python
import torch
import torch.nn as nn
from typing import List

def dp_sgd_step(model: nn.Module, 
                loss_fn: nn.Module, 
                batch_inputs: torch.Tensor, 
                batch_targets: torch.Tensor, 
                max_grad_norm: float, 
                noise_multiplier: float, 
                learning_rate: float) -> float:
    """Executes a single DP-SGD training step with per-sample clipping."""
    batch_size = batch_inputs.shape[0]
    per_sample_grads: List[List[torch.Tensor]] = []

    # 1. Compute per-sample gradients
    for i in range(batch_size):
        model.zero_grad()
        out = model(batch_inputs[i:i+1])
        loss = loss_fn(out, batch_targets[i:i+1])
        loss.backward()
        
        sample_grad = [p.grad.detach().clone() for p in model.parameters() if p.grad is not None]
        per_sample_grads.append(sample_grad)

    # 2. Clip each sample's gradient norm to max_grad_norm
    clipped_grads = [torch.zeros_like(p) for p in model.parameters()]
    for sample_grad in per_sample_grads:
        total_norm = torch.sqrt(sum(torch.sum(g ** 2) for g in sample_grad))
        clip_coef = min(1.0, max_grad_norm / (total_norm.item() + 1e-6))
        for j, g in enumerate(sample_grad):
            clipped_grads[j] += g * clip_coef

    # 3. Add calibrated Gaussian noise and update parameters
    model.zero_grad()
    with torch.no_grad():
        for p, clipped_g in zip(model.parameters(), clipped_grads):
            # Noise sigma = noise_multiplier * max_grad_norm
            noise_std = noise_multiplier * max_grad_norm
            noise = torch.randn_like(clipped_g) * noise_std
            # Summed gradient + noise averaged over batch
            noisy_grad = (clipped_g + noise) / batch_size
            p.sub_(learning_rate * noisy_grad)

    return float(loss.item())
```
**Analysis**: Implements the foundational Abadi et al. DP-SGD algorithm: per-sample gradient computation, L2 norm clipping, Gaussian perturbation, and parameter update.

---

## 4. Architectural Tradeoffs

### Epsilon (ε) Privacy vs Model Utility
A smaller epsilon (ε < 1.0) provides provably strong privacy guarantees against membership inference, but requires adding heavy noise, degrading model accuracy and perplexity. A larger epsilon (ε > 8.0) yields near-unperturbed model utility, but increases vulnerability to targeted memorization extraction.

### Standard Composition vs Rényi DP (RDP) Accounting
Standard composition linearly adds epsilons: k steps yield k*ε, causing the privacy budget to exhaust in ~10 iterations. Advanced composition scales with sqrt(k*ln(1/δ))*ε. RDP accounts for Gaussian convolutions analytically, allowing 10,000+ training epochs under ε < 3.0.

---

## 5. Common Failure Modes & Anti-Patterns

### Failure Mode 1: Floating-Point Side-Channel Vulnerability (Mironov Attack)
- **Root Cause**: Implementing the Laplace mechanism using standard IEEE 754 floating-point sampling creates irregular gap distributions in output values, allowing an adversary to distinguish neighboring datasets with 100% certainty despite mathematical DP proofs.
- **Mitigation & Invariant Defense**: Use snapping mechanisms or discrete integer noise (Discrete Laplace / Skellam mechanism).

### Failure Mode 2: Batch-Level Instead of Per-Sample Gradient Clipping
- **Root Cause**: Clipping the average batch gradient instead of individual per-sample gradients violates the sensitivity bound: an outlier sample can still dominate the gradient direction.
- **Mitigation & Invariant Defense**: Strictly enforce per-sample gradient norm clipping prior to summation.
