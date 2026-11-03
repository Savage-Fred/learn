# Topic: Statistics for Data Analysis & Experimentation

**Domain**: `system-design`  
**Topic ID**: `statistics`  
**Canonical Path**: `system-design/statistics/`

## Overview

Rigorous statistical inference, internet-scale A/B testing platforms, variance reduction via CUPED, sequential testing (Wald's SPRT, mixture SPRT), multiple testing correction (Bonferroni, Benjamini-Hochberg FDR), bootstrap resampling, and causal inference under network interference.

---

## Learning Objectives

- Formulate statistical hypotheses, calculate required sample sizes for specified statistical power (1 - beta), and control Type I error rates.
- Apply multiple hypothesis testing corrections (Bonferroni and Benjamini-Hochberg False Discovery Rate control) to multi-variant experiments.
- Implement CUPED (Controlled-experiment Using Pre-Experiment Data) variance reduction to accelerate experiment runtime by 30-50%.
- Eliminate the 'peeking problem' (continuous monitoring bias) using sequential testing frameworks (Wald's SPRT and mixture SPRT).
- Address Stable Unit Treatment Value Assumption (SUTVA) violations caused by marketplace network interference using cluster randomization and switchback experiments.

## Prerequisite Knowledge Graph

- Probability theory (random variables, expectation, variance, central limit theorem).
- Linear regression and ordinary least squares (OLS).
- Basic Python data manipulation (NumPy, SciPy).

---

## Role Track Relevance

### Track 1: FAANG SWE + AI Lab SWE (L5/L6)
- **Focus & Competencies**: Large-scale experimentation platform architecture, low-latency metric logging, and automated outlier detection.

### Track 4: AI Lab Research Engineer (non-PhD) (L4/L5)
- **Focus & Competencies**: Statistical significance of LLM benchmark evaluations, confidence intervals on benchmark scores, and bootstrapping win-rates.

---

## Company Profiles & Cultural Bars (The 7 Notable Companies)

### Netflix
- **Technical Focus**: Personalized recommendation experimentation, network interference across shared streaming bandwidth, switchback testing, and low-latency metrics estimation.
- **Observable Evaluation Signals**:
  - CUPED variance reduction
  - Cluster randomization
  - Sequential testing to stop bad tests fast

### Meta
- **Technical Focus**: Massive two-sided marketplace experimentation, social graph network spillover, thousands of concurrent A/B tests, and automated FDR control.
- **Observable Evaluation Signals**:
  - Benjamini-Hochberg FDR
  - Back-of-the-envelope sample size sizing
  - Detecting metric cannibalization

### Google / GDM
- **Technical Focus**: Mathematical rigor, rigorous null hypothesis statistical testing (NHST), non-parametric bootstrap estimation, and telemetry outlier rejection.
- **Observable Evaluation Signals**:
  - Formal statistical derivation
  - Understanding asymptotic normality assumptions
  - Defensive winsorization

### OpenAI
- **Technical Focus**: Statistical evaluation of model generations, ELO rating confidence intervals, bootstrap win-rate estimations, and human preference ranking variance.
- **Observable Evaluation Signals**:
  - Bootstrap resampling
  - Bradley-Terry model estimation
  - Power analysis for eval sample sizes

### Databricks
- **Technical Focus**: Distributed statistical computing, approximate quantile estimation (t-digest), and scalable covariance computations over billions of rows.
- **Observable Evaluation Signals**:
  - Distributed covariance aggregation
  - Approximate quantiles
  - Efficient data passes

### Apple
- **Technical Focus**: Privacy-preserving experimentation, differential privacy noise injection into A/B metrics, and on-device metric aggregation.
- **Observable Evaluation Signals**:
  - Adding Laplace noise to test statistics
  - Locally private mean estimation
  - Sample size inflation under noise

### Anthropic
- **Technical Focus**: Statistical significance in model alignment evaluations, win-rate estimation under constitutional AI principles, and rigorous confidence intervals.
- **Observable Evaluation Signals**:
  - Bootstrap win-rate estimation
  - Hypothesis testing on human preference rankings
  - Defensive sample size validation

---

## Standard 5-Artifact Topic Layout

1. **[Fundamentals](./fundamentals.md)**: Core axiomatic invariants, theoretical proofs, mental models, idiomatic code examples, architectural tradeoffs, and failure modes.
2. **[References (YAML)](./references.yaml)** & **[References (Markdown)](./references.md)**: Citable peer-reviewed papers (with DOIs/arXiv IDs), official RFCs, foundational textbooks, and recent verified tier-1 interview loop calibrations.
3. **[Evaluation Rubric](./rubric.md)**: L4 vs L5 vs L6 scoring criteria across the 5 dimensions (Decomposition, Technical Execution, Architecture, Resilience, Communication) matching `docs/ux-spec.md`.
4. **[Adaptive Exercises](./exercises/)**: Tiered problem sets spanning diagnostic starter, mid-level L4, senior L5, and staff L6.
5. **[Durable Learnings](./learnings/)**: Destination directory for user's durable notes and deep-dive captures.