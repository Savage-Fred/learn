# Domain: Privacy Architecture & Data Protection

**Directory**: `privacy-engineering/`  
**Platform Domain ID**: `privacy-engineering`

## Overview

Formal privacy guarantees, cryptographic privacy-enhancing technologies (PETs), confidential computing (TEEs), and modern differential privacy (DP-SGD, RDP, LDP) at enterprise scale.

---

## Priority Topics & Curriculum Index

### [PETs for AI](./pets-for-ai/)
- **Path**: `privacy-engineering/pets-for-ai/`
- **Focus**: Membership inference defense, training data extraction mitigation, CKKS homomorphic encryption, TEE remote attestation, and Secure Aggregation (SecAgg).
- **Artifacts**: [Fundamentals](./pets-for-ai/fundamentals.md) | [References](./pets-for-ai/references.md) | [Rubric](./pets-for-ai/rubric.md) | [Exercises](./pets-for-ai/exercises/) | [Learnings](./pets-for-ai/learnings/)

### [Modern Differential Privacy](./differential-privacy/)
- **Path**: `privacy-engineering/differential-privacy/`
- **Focus**: (ε, δ)-DP formal proofs, Laplace & Gaussian mechanisms, Rényi DP (RDP) linear composition, DP-SGD with Moments Accountant, and Local DP (LDP).
- **Artifacts**: [Fundamentals](./differential-privacy/fundamentals.md) | [References](./differential-privacy/references.md) | [Rubric](./differential-privacy/rubric.md) | [Exercises](./differential-privacy/exercises/) | [Learnings](./differential-privacy/learnings/)

---

## Target Role Tracks & Seniority Calibrations

### Track 2: FAANG Privacy Engineer + AI Labs (L6 (Staff))
Formal privacy budget governance, verifiable cryptographic attestation, compliance-to-architecture translation, and petabyte-scale privacy enforcement.

### Track 4: AI Lab Research Engineer (L4-L5)
Differentially private model fine-tuning (DP-SGD), gradient clipping, and encrypted inference latency optimization.

---

## Company Profiles & Cultural Bars

- **OpenAI**: Training data sanitization, memorization extraction defenses, and enterprise tenant data privacy isolation.
- **Google / GDM**: Android fleet telemetry differential privacy, federated learning with SecAgg, and formal epsilon accounting.
- **Anthropic**: Data retention minimization, synthetic data generation privacy guarantees, and verifiable audit logging.
- **Meta**: Massive differential privacy telemetry pipelines, advertising attribution with secure multi-party computation.
- **Databricks**: Clean rooms, differential privacy query engines for enterprise datasets, and zero-knowledge governance.
- **Netflix**: De-identification of viewing telemetry, differential privacy in recommendation model evaluation.
- **Apple**: On-device Local Differential Privacy, Private Cloud Compute (PCC) cryptographic attestation, and zero data retention verification.

---

## Standard 5-Artifact Contract

Every topic directory inside this domain adheres strictly to the canonical 5-artifact layout:
1. `README.md`: Scope, role alignment, company calibration, and topic navigation.
2. `fundamentals.md`: Core axiomatic invariants, proofs, idiomatic code, and failure modes.
3. `references.yaml` & `references.md`: Citable academic papers, RFCs, books, and verified interview loops.
4. `rubric.md`: Role-calibrated 5-dimension scoring criteria across L4, L5, and L6.
5. `exercises/`: Tiered adaptive problem sets (`tier1_starter.md`, `tier2_l4.md`, `tier3_l5.md`, `tier4_l6.md`).
6. `learnings/`: Git-committed destination for user's durable notes and deep-dive captures.