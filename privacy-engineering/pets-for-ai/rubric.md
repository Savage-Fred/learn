# Evaluation Rubric & Calibration Guide: Privacy-Enhancing Technologies (PETs) for AI

This rubric defines the scoring calibration for mock interview assessments, coding exercises, and technical design evaluations across five standardized dimensions.

## Seniority Level Overview

- **L4 (Mid-Level)**: Understands basic privacy principles (PII identification, GDPR basics); executes shadow-model membership inference attacks; implements Shamir's Secret Sharing.
- **L5 (Senior)**: Architects Secure Aggregation protocols handling client dropouts; implements homomorphic inference prototypes (CKKS); analyzes TEE remote attestation chains; designs SISA unlearning pipelines.
- **L6 (Staff / Principal)**: Deploys enterprise-scale confidential computing infrastructure (Private Cloud Compute); sets organization-wide privacy guarantees; navigates complex cross-border regulatory compliance.

---

## The 5 Scoring Dimensions

### Dimension 1: Problem Decomposition & Invariant Formulation (Weight: 20%)
*Formulation of privacy threat models (honest-but-curious vs malicious adversary), zero-sum invariants, and attestation proofs.*

#### L4 (Mid-Level) Criteria
- Distinguishes data in transit, data at rest, and data in use.
- Identifies memorization risks in ML models.

#### L5 (Senior) Criteria
- Formulates mathematical invariant of Secure Aggregation zero-sum cancellation.
- Defines formal adversary capabilities (e.g. colluding clients, curious server).

#### L6 (Staff) Criteria
- Proves cryptographic boundaries under side-channel and microarchitectural hardware attacks.

#### Observable Anti-Patterns
- ❌ **Compliance as Security**: Assuming GDPR legal contracts substitute for technical cryptographic privacy invariants.

---

### Dimension 2: Technical Execution & Code Craftsmanship (Weight: 25%)
*Clean, secure implementation of cryptographic primitives, Shamir secret sharing, and PyTorch training hooks.*

#### L4 (Mid-Level) Criteria
- Implements basic Shamir polynomial evaluation over finite fields.
- Calculates MIA accuracy and ROC-AUC correctly.

#### L5 (Senior) Criteria
- Handles client dropout recovery in SecAgg with threshold secret reconstruction.
- Implements CKKS polynomial approximations for non-linear activations.

#### L6 (Staff) Criteria
- Produces verified hardware attestation verification code parsing X.509 certificate chains and TPM/SEV quote measurements.

#### Observable Anti-Patterns
- ❌ **Insecure Randomness**: Using random.random() instead of secrets or cryptographic PRNG for cryptographic key generation.

---

### Dimension 3: Systems Architecture & Trade-Off Rigor (Weight: 25%)
*Evaluating computational overhead of cryptographic PETs vs hardware enclaves vs statistical noise.*

#### L4 (Mid-Level) Criteria
- Understands that encryption slows down processing speed.
- Calculates bandwidth overhead of sending masks.

#### L5 (Senior) Criteria
- Compares multiplicative depth constraints in CKKS vs communication rounds in SMPC.
- Quantifies network bandwidth of pairwise secret sharing for 10,000 clients.

#### L6 (Staff) Criteria
- Architects hybrid confidential computing pipelines balancing TEE GPU attestation against distributed inference throughput.

#### Observable Anti-Patterns
- ❌ **Ignoring FHE Multiplicative Depth**: Attempting to evaluate a 50-layer deep ResNet under FHE without bootstrapping or polynomial approximations.

---

### Dimension 4: Resilience, Security & Edge Case Posture (Weight: 15%)
*Handling client dropouts, malicious server collusion, poisoned model updates, and rollback attacks.*

#### L4 (Mid-Level) Criteria
- Validates client payload shapes and types.
- Handles network disconnects during upload.

#### L5 (Senior) Criteria
- Guards against client sybil attacks in federated aggregation.
- Validates hardware attestation freshness against replay attacks using nonces.

#### L6 (Staff) Criteria
- Designs Byzantine-resilient secure aggregation rejecting poisoned gradient updates without viewing individual updates.

#### Observable Anti-Patterns
- ❌ **Missing Nonce in Attestation**: Accepting static hardware attestation quotes, enabling replay attacks by a compromised hypervisor.

---

### Dimension 5: Communication & Calibration Level (Weight: 15%)
*Precision of cryptographic terminology, regulatory-to-system translation, and executive presence.*

#### L4 (Mid-Level) Criteria
- Explains membership inference concepts clearly.
- Follows guidance on cryptographic protocols.

#### L5 (Senior) Criteria
- Articulates mathematical guarantees and failure modes with confidence.
- Explains why data anonymization fails against linkage attacks.

#### L6 (Staff) Criteria
- Commands authority on frontier AI privacy architecture and international regulatory frameworks.

#### Observable Anti-Patterns
- ❌ **Over-Claiming Privacy**: Claiming a system is '100% anonymous and private' without formal mathematical definitions.

---

## Composite Scoring Calibration

- **Score 1.0 – 2.4 (Below Bar / Not Passing)**: Deficient in core invariants; misses basic correctness constraints; unhandled runtime exceptions.
- **Score 2.5 – 3.4 (L4 Mid-Level Standard)**: Produces working, clean code; identifies edge cases with standard test inputs; needs scaffolding for multi-node tradeoffs.
- **Score 3.5 – 4.4 (L5 Senior Bar - Strong Hire)**: Formulates mathematical/architectural invariants up front; anticipates distributed failure modes; proves time/space bounds.
- **Score 4.5 – 5.0 (L6 Staff Bar - Exceptional)**: Strategic problem reframing; anticipates cascading failure and adversarial vectors; balances cross-cutting organizational invariants.