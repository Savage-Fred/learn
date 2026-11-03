# Evaluation Rubric & Calibration Guide: Statistics for Data Analysis & Experimentation

This rubric defines the scoring calibration for mock interview assessments, coding exercises, and technical design evaluations across five standardized dimensions.

## Seniority Level Overview

- **L4 (Mid-Level)**: Calculates sample sizes using basic formulas; understands p-values, t-tests, and Type I/II errors; identifies sample ratio mismatches (SRM).
- **L5 (Senior)**: Implements CUPED variance reduction; designs sequential testing frameworks avoiding peeking bias; applies Benjamini-Hochberg FDR control; designs cluster-randomized switchback experiments.
- **L6 (Staff / Principal)**: Architects enterprise-scale experimentation infrastructure; addresses multi-sided network interference; designs automated metric pipelines with synthetic controls and causal inference.

---

## The 5 Scoring Dimensions

### Dimension 1: Problem Decomposition & Invariant Formulation (Weight: 20%)
*Formulation of hypotheses, statistical invariants, and sample size requirements.*

#### L4 (Mid-Level) Criteria
- States null and alternative hypotheses clearly.
- Calculates required sample size for given alpha and beta.

#### L5 (Senior) Criteria
- Identifies SUTVA assumptions and potential violations up front.
- Formulates mathematical variance reduction invariants (CUPED).

#### L6 (Staff) Criteria
- Proves asymptotic convergence bounds; models network interference using graph spillover models.

#### Observable Anti-Patterns
- ❌ **Ignoring Sample Ratio Mismatch**: Analyzing experiment metrics when the traffic split diverges from 50/50 (SRM).

---

### Dimension 2: Technical Execution & Code Craftsmanship (Weight: 25%)
*Correct statistical computation, avoiding data leakage, and clean vectorized implementations.*

#### L4 (Mid-Level) Criteria
- Computes t-statistic and p-value correctly using NumPy/SciPy.
- Winsorizes outliers appropriately.

#### L5 (Senior) Criteria
- Implements CUPED theta calculation without lookahead bias.
- Writes correct Benjamini-Hochberg thresholding logic.

#### L6 (Staff) Criteria
- Produces distributed single-pass covariance calculations for billions of rows.

#### Observable Anti-Patterns
- ❌ **Lookahead Data Leakage**: Using post-experiment data to compute pre-experiment CUPED baselines.

---

### Dimension 3: Systems Architecture & Trade-Off Rigor (Weight: 25%)
*Designing high-throughput logging, telemetry aggregation, and experiment assignment services.*

#### L4 (Mid-Level) Criteria
- Understands how hashing (e.g. Murmur3) assigns users to treatment/control.
- Calculates experiment duration based on traffic.

#### L5 (Senior) Criteria
- Designs low-latency bucketing service at the API gateway.
- Compares switchback time-window durations vs wash-out periods.

#### L6 (Staff) Criteria
- Architects real-time streaming metric pipeline computing rolling mixture SPRT statistics.

#### Observable Anti-Patterns
- ❌ **Synchronous Experiment Assignment**: Making blocking database queries to assign a user to an experiment variant on every HTTP request.

---

### Dimension 4: Resilience, Security & Edge Case Posture (Weight: 15%)
*Handling heavy-tailed distributions, bot traffic, metric cannibalization, and holiday seasonality.*

#### L4 (Mid-Level) Criteria
- Removes bot traffic and extreme outliers.
- Validates sanity of logging timestamps.

#### L5 (Senior) Criteria
- Uses non-parametric bootstrap when normality assumptions are violated by extreme skew.
- Monitors guardrail metrics to prevent business cannibalization.

#### L6 (Staff) Criteria
- Designs automated rollback tripwires triggered by sequential testing boundary breaches.

#### Observable Anti-Patterns
- ❌ **Overfitting to Skewed Outliers**: Computing raw arithmetic means on heavy-tailed revenue metrics without trimming.

---

### Dimension 5: Communication & Calibration Level (Weight: 15%)
*Ability to communicate statistical findings clearly to business and product leadership.*

#### L4 (Mid-Level) Criteria
- Explains p-value and confidence interval in plain English.
- Does not claim causality without control groups.

#### L5 (Senior) Criteria
- Articulates risk of false discoveries in multi-metric dashboards.
- Explains why statistical significance does not equal practical business significance.

#### L6 (Staff) Criteria
- Guides executive decisions under ambiguous or conflicting metric movements.

#### Observable Anti-Patterns
- ❌ **P-Hacking**: Re-segmenting data post-hoc until a subgroup shows p < 0.05 and claiming victory.

---

## Composite Scoring Calibration

- **Score 1.0 – 2.4 (Below Bar / Not Passing)**: Deficient in core invariants; misses basic correctness constraints; unhandled runtime exceptions.
- **Score 2.5 – 3.4 (L4 Mid-Level Standard)**: Produces working, clean code; identifies edge cases with standard test inputs; needs scaffolding for multi-node tradeoffs.
- **Score 3.5 – 4.4 (L5 Senior Bar - Strong Hire)**: Formulates mathematical/architectural invariants up front; anticipates distributed failure modes; proves time/space bounds.
- **Score 4.5 – 5.0 (L6 Staff Bar - Exceptional)**: Strategic problem reframing; anticipates cascading failure and adversarial vectors; balances cross-cutting organizational invariants.