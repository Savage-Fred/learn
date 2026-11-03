# Topic: Privacy-Enhancing Technologies (PETs) for AI

**Domain**: `privacy-engineering`  
**Topic ID**: `pets-for-ai`  
**Canonical Path**: `privacy-engineering/pets-for-ai/`

## Overview

Advanced cryptographic and system-level privacy engineering for machine learning and AI systems. Covers adversarial privacy attacks (Membership Inference, Training Data Extraction, Model Inversion), Secure Multi-Party Computation (SMPC, Beaver triples), Homomorphic Encryption (CKKS/BFV), Confidential Computing (TEEs, Apple Private Cloud Compute remote attestation), Federated Learning with Secure Aggregation (SecAgg), and Machine Unlearning (SISA).

---

## Learning Objectives

- Quantify and execute empirical privacy attacks on machine learning models (Membership Inference Attacks, training data extraction).
- Implement Secure Multi-Party Computation (SMPC) protocols (Shamir secret sharing, Beaver multiplication triples) for private collaborative analytics.
- Design encrypted inference pipelines using CKKS Homomorphic Encryption for evaluating neural networks over encrypted ciphertexts.
- Architect hardware-isolated Confidential Computing systems utilizing Trusted Execution Environments (TEEs) and cryptographic remote attestation.
- Implement Federated Learning with Secure Aggregation (SecAgg) and Machine Unlearning architectures (SISA) complying with GDPR 'Right to be Forgotten'.

## Prerequisite Knowledge Graph

- Machine learning foundations (PyTorch, neural network training loops, loss functions).
- Applied cryptography (public key encryption, secret sharing, digital signatures).
- Hardware architecture basics (memory isolation, CPU enclaves).

---

## Role Track Relevance

### Track 2: FAANG Privacy Engineer + AI Labs (L6 Staff)
- **Focus & Competencies**: Cryptographic privacy architectures, PETs deployment, regulatory-to-system translation (GDPR/EU AI Act), and large-scale data governance.

### Track 4: AI Lab Research Engineer (non-PhD) (L4/L5)
- **Focus & Competencies**: Encrypted inference acceleration, private collaborative training pipelines, and confidential GPU compute attestation.

---

## Company Profiles & Cultural Bars (The 7 Notable Companies)

### Apple
- **Technical Focus**: Private Cloud Compute (PCC) architecture; remote cryptographic attestation; verifiable transparency logs; zero data retention guarantees for offloaded AI inference.
- **Observable Evaluation Signals**:
  - Hardware TEE verification
  - Cryptographic root of trust
  - Zero data retention verification

### Google / GDM
- **Technical Focus**: Federated Learning at scale (Gboard); Secure Aggregation (SecAgg) protocol resilience under high mobile client dropout; confidential computing in GCP.
- **Observable Evaluation Signals**:
  - SecAgg protocol design
  - Handling mobile client dropouts
  - Federated analytics

### OpenAI
- **Technical Focus**: Training data sanitization; memorization extraction defenses; preventing confidential enterprise data leakage via fine-tuned model outputs.
- **Observable Evaluation Signals**:
  - Deduplication at scale
  - Prefix extraction probing
  - Auditing model weights

### Anthropic
- **Technical Focus**: Data retention minimization; synthetic data generation with formal privacy bounds; verifiable transparency and deletion logging.
- **Observable Evaluation Signals**:
  - Machine unlearning strategies
  - Clean privacy invariants
  - Defensive system boundaries

### Meta
- **Technical Focus**: Private advertising attribution using Secure Multi-Party Computation (SMPC); high-throughput private set intersection (PSI).
- **Observable Evaluation Signals**:
  - SMPC protocol efficiency
  - Oblivious transfer overhead
  - Scalable batching

### Databricks
- **Technical Focus**: Clean rooms for enterprise data collaboration; multi-party computation over cloud data lakes; zero-knowledge governance.
- **Observable Evaluation Signals**:
  - Tenant isolation
  - Query rewriting for privacy
  - Audit log immutability

### Netflix
- **Technical Focus**: De-identification of viewing telemetry; protecting subscriber privacy against linking attacks on viewing histories.
- **Observable Evaluation Signals**:
  - k-anonymity limits
  - L-diversity and t-closeness
  - Noise addition trade-offs

---

## Standard 5-Artifact Topic Layout

1. **[Fundamentals](./fundamentals.md)**: Core axiomatic invariants, theoretical proofs, mental models, idiomatic code examples, architectural tradeoffs, and failure modes.
2. **[References (YAML)](./references.yaml)** & **[References (Markdown)](./references.md)**: Citable peer-reviewed papers (with DOIs/arXiv IDs), official RFCs, foundational textbooks, and recent verified tier-1 interview loop calibrations.
3. **[Evaluation Rubric](./rubric.md)**: L4 vs L5 vs L6 scoring criteria across the 5 dimensions (Decomposition, Technical Execution, Architecture, Resilience, Communication) matching `docs/ux-spec.md`.
4. **[Adaptive Exercises](./exercises/)**: Tiered problem sets spanning diagnostic starter, mid-level L4, senior L5, and staff L6.
5. **[Durable Learnings](./learnings/)**: Destination directory for user's durable notes and deep-dive captures.