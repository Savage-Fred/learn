# Evaluation Rubric & Calibration Guide: Modern Differential Privacy

This rubric defines the scoring calibration for mock interview assessments, coding exercises, and technical design evaluations across five standardized dimensions.

## Seniority Level Overview

- **L4 (Mid-Level)**: Understands (ε, δ)-DP definition; implements Laplace mechanism for numeric queries; calculates L1 sensitivity for counting and mean queries; runs basic randomized response.
- **L5 (Senior)**: Implements DP-SGD with per-sample clipping in PyTorch; calculates Gaussian noise scales; tracks privacy budgets using RDP accountants; designs Local DP protocols.
- **L6 (Staff / Principal)**: Architects enterprise-wide privacy budget management platforms; proves formal DP theorems; optimizes DP-SGD backpropagation (Ghost Clipping); manages fleet-wide telemetry DP budgets.

---

## The 5 Scoring Dimensions

### Dimension 1: Problem Decomposition & Invariant Formulation (Weight: 20%)
*Formulation of neighborhood relations, global sensitivity bounds, and privacy loss definitions.*

#### L4 (Mid-Level) Criteria
- Defines neighboring datasets (add/remove vs substitute).
- Calculates sensitivity Delta = 1 for count queries.

#### L5 (Senior) Criteria
- Differentiates L1 vs L2 sensitivity.
- Formulates RDP composition invariants and conversion bounds.

#### L6 (Staff) Criteria
- Proves tight privacy lower bounds using reconstruction attack reductions.

#### Observable Anti-Patterns
- ❌ **Confusing Sensitivity with Data Magnitude**: Assuming sensitivity is the maximum value in the dataset rather than the maximum change induced by adding/removing one record.

---

### Dimension 2: Technical Execution & Code Craftsmanship (Weight: 25%)
*Clean, mathematically sound implementation of clipping, noise injection, and accounting algorithms.*

#### L4 (Mid-Level) Criteria
- Implements Laplace sampling using inverted CDF or NumPy.
- Avoids negative counts in post-processing.

#### L5 (Senior) Criteria
- Implements per-sample gradient clipping without memory explosion.
- Uses cryptographic or secure PRNG for noise generation.

#### L6 (Staff) Criteria
- Optimizes DP-SGD memory consumption via Ghost Clipping or vectorized per-sample gradient hooks.

#### Observable Anti-Patterns
- ❌ **Batch Clipping Fallacy**: Applying torch.nn.utils.clip_grad_norm_ on accumulated batch gradients instead of per-sample gradients.

---

### Dimension 3: Systems Architecture & Trade-Off Rigor (Weight: 25%)
*Analyzing privacy budget consumption, batch sizing impacts, and query planner integrations.*

#### L4 (Mid-Level) Criteria
- Understands that every query consumes privacy budget.
- Calculates cumulative epsilon under simple addition.

#### L5 (Senior) Criteria
- Analyzes amplified privacy guarantees under Poisson subsampling.
- Quantifies trade-off between clipping threshold C and noise scale sigma.

#### L6 (Staff) Criteria
- Architects distributed privacy budget ledger with transactional rollback and composition alarms.

#### Observable Anti-Patterns
- ❌ **Infinite Budget Fallacy**: Treating epsilon as a renewable resource without bounding cumulative queries over time.

---

### Dimension 4: Resilience, Security & Edge Case Posture (Weight: 15%)
*Defending against floating-point timing attacks, reconstruction attacks, and empty-set edge cases.*

#### L4 (Mid-Level) Criteria
- Handles empty datasets safely.
- Ensures delta is strictly smaller than 1/N.

#### L5 (Senior) Criteria
- Guards against floating-point side-channel vulnerabilities (Mironov attack) using discretization.
- Monitors privacy budget exhaustion.

#### L6 (Staff) Criteria
- Defends against auxiliary data correlation and reconstruction attacks on high-dimensional statistics.

#### Observable Anti-Patterns
- ❌ **Unbounded Delta**: Setting delta >= 1/N, effectively allowing the mechanism to reveal entire user records with probability delta.

---

### Dimension 5: Communication & Calibration Level (Weight: 15%)
*Clarity of formal mathematical arguments, intuitive trade-off explanation, and regulatory alignment.*

#### L4 (Mid-Level) Criteria
- Explains what epsilon means in plain English to non-technical stakeholders.
- Follows guidance on parameter calibration.

#### L5 (Senior) Criteria
- Articulates difference between local and central DP with clarity.
- Justifies parameter choices (C, sigma, batch_size) with mathematical rigor.

#### L6 (Staff) Criteria
- Frames differential privacy as a strategic enabler of data sharing and regulatory compliance.

#### Observable Anti-Patterns
- ❌ **Epsilon Mysticism**: Claiming arbitrary numbers (e.g. ε=50) provide meaningful privacy without analyzing probability ratio bounds.

---

## Composite Scoring Calibration

- **Score 1.0 – 2.4 (Below Bar / Not Passing)**: Deficient in core invariants; misses basic correctness constraints; unhandled runtime exceptions.
- **Score 2.5 – 3.4 (L4 Mid-Level Standard)**: Produces working, clean code; identifies edge cases with standard test inputs; needs scaffolding for multi-node tradeoffs.
- **Score 3.5 – 4.4 (L5 Senior Bar - Strong Hire)**: Formulates mathematical/architectural invariants up front; anticipates distributed failure modes; proves time/space bounds.
- **Score 4.5 – 5.0 (L6 Staff Bar - Exceptional)**: Strategic problem reframing; anticipates cascading failure and adversarial vectors; balances cross-cutting organizational invariants.