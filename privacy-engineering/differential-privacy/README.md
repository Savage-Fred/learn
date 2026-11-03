# Topic: Modern Differential Privacy

**Domain**: `privacy-engineering`  
**Topic ID**: `differential-privacy`  
**Canonical Path**: `privacy-engineering/differential-privacy/`

## Overview

Rigorous mathematical formulation and system deployment of Differential Privacy. Covers (ε, δ)-DP definitions, sensitivity calculations, Laplace and Gaussian mechanisms, Rényi Differential Privacy (RDP) linear composition, Differentially Private Stochastic Gradient Descent (DP-SGD with Moments Accountant), and Local Differential Privacy (LDP) at internet scale.

---

## Learning Objectives

- Prove (ε, δ)-differential privacy guarantees for randomized mechanisms over neighboring datasets.
- Calculate global L1 and L2 sensitivities and calibrate Laplace and Gaussian noise scales.
- Compose privacy budgets across multiple sequential queries using standard composition, Advanced Composition, and Rényi DP (RDP).
- Implement DP-SGD in PyTorch with per-sample gradient clipping, Gaussian noise addition, and Moments Accountant tracking.
- Design and analyze Local Differential Privacy (LDP) randomized response protocols for large-scale client device telemetry.

## Prerequisite Knowledge Graph

- Mathematical analysis (calculus, probability distributions, variance, tail bounds).
- Machine learning optimization (gradient descent, backpropagation).
- Basic linear algebra (norms, vectors, matrices).

---

## Role Track Relevance

### Track 2: FAANG Privacy Engineer + AI Labs (L6 Staff)
- **Focus & Competencies**: Formal privacy budget governance, verifiable privacy accounting, telemetry pipeline design, and regulatory privacy defense.

### Track 4: AI Lab Research Engineer (non-PhD) (L4/L5)
- **Focus & Competencies**: DP-SGD fine-tuning of foundation models, gradient clipping overhead reduction, and privacy-utility trade-off optimization.

---

## Company Profiles & Cultural Bars (The 7 Notable Companies)

### Google / GDM
- **Technical Focus**: Android fleet telemetry differential privacy (RAPPOR), DP-SGD fine-tuning of language models, and formal epsilon accounting.
- **Observable Evaluation Signals**:
  - Formal DP mathematical proofs
  - Moments accountant derivation
  - Fleet telemetry aggregation

### Apple
- **Technical Focus**: Local Differential Privacy on iOS/macOS for popular emoji and search word tracking; formal privacy budget renewal policies.
- **Observable Evaluation Signals**:
  - Randomized response protocols
  - Local vs Central DP trade-offs
  - Annual budget management

### OpenAI
- **Technical Focus**: Differentially private fine-tuning of frontier models; evaluating privacy leakage bounds on customer fine-tuned weights.
- **Observable Evaluation Signals**:
  - DP-SGD training speedups
  - Per-sample gradient clipping efficiency
  - Perplexity penalty minimization

### Meta
- **Technical Focus**: Differential privacy in ad attribution and conversion modeling; private SQL query engines over petabyte warehouse data.
- **Observable Evaluation Signals**:
  - Hierarchical budget allocation
  - Differential privacy in SQL planners
  - Noise calibration on heavy-tailed metrics

### Databricks
- **Technical Focus**: Differentially private data clean rooms; automated epsilon spending limits on user analytical queries.
- **Observable Evaluation Signals**:
  - Budget tracking per analyst
  - Composition exhaustion alerts
  - Laplace mechanism integration

### Netflix
- **Technical Focus**: Differential privacy in recommendation evaluation; preventing de-anonymization of subscriber rating histories.
- **Observable Evaluation Signals**:
  - Sensitivity bounding on sparse matrices
  - Utility vs privacy optimization

### Anthropic
- **Technical Focus**: Formal privacy budget bounds on model fine-tuning data, differential privacy in synthetic training data generation, and verifiable transparency logging.
- **Observable Evaluation Signals**:
  - Rényi Differential Privacy accounting
  - Data retention minimization
  - Verifiable privacy guarantees

---

## Standard 5-Artifact Topic Layout

1. **[Fundamentals](./fundamentals.md)**: Core axiomatic invariants, theoretical proofs, mental models, idiomatic code examples, architectural tradeoffs, and failure modes.
2. **[References (YAML)](./references.yaml)** & **[References (Markdown)](./references.md)**: Citable peer-reviewed literature (with DOIs/arXiv IDs), official standards/RFCs, foundational textbooks, and interview loop calibrations.
3. **[Evaluation Rubric](./rubric.md)**: L4 vs L5 vs L6 scoring criteria across the 5 dimensions (Decomposition, Technical Execution, Architecture, Resilience, Communication) matching `docs/ux-spec.md`.
4. **[Adaptive Exercises](./exercises/)**: Tiered problem sets spanning diagnostic starter, mid-level L4, senior L5, and staff L6.
5. **[Durable Learnings](./learnings/)**: Destination directory for user's durable notes and deep-dive captures.