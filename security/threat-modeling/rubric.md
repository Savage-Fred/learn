# Evaluation Rubric & Calibration Guide: Systems, Cloud & AI Threat Modeling

This rubric defines the scoring calibration for mock interview assessments, coding exercises, and technical design evaluations across five standardized dimensions.

## Seniority Level Overview

- **L4 (Mid-Level)**: Applies STRIDE to standard web services; identifies OWASP Top 10 vulnerabilities (SQLi, XSS, SSRF); understands basic trust boundaries.
- **L5 (Senior)**: Threat models complex distributed systems and autonomous AI agents; identifies indirect prompt injection and confused deputy risks; designs defense-in-depth mitigations; calculates CVSS v4.0 scores.
- **L6 (Staff / Principal)**: Leads enterprise-wide threat modeling; designs formal zero-trust architectures; models state-sponsored adversaries and frontier model exfiltration; sets organization-wide AI security policy.

---

## The 5 Scoring Dimensions

### Dimension 1: Problem Decomposition & Invariant Formulation (Weight: 20%)
*Ability to delineate trust boundaries, identify assets, and construct clear data flow diagrams (DFD).*

#### L4 (Mid-Level) Criteria
- Draws basic architecture with client, gateway, backend, and DB.
- Identifies primary trust boundary between public internet and internal network.

#### L5 (Senior) Criteria
- Identifies nuanced boundaries between multi-tenant workloads, microservices, and external third-party APIs.
- Delineates LLM instruction channel from untrusted context data.

#### L6 (Staff) Criteria
- Architects multi-layered security zones; models hardware vs kernel vs user space trust boundaries.

#### Observable Anti-Patterns
- ❌ **Monolithic Trust**: Treating the entire internal corporate network as a single trusted zone.

---

### Dimension 2: Technical Execution & Code Craftsmanship (Weight: 25%)
*Formulation of actionable, precise technical mitigations rather than generic advice.*

#### L4 (Mid-Level) Criteria
- Suggests standard library controls (parameterized queries, TLS, CORS headers).
- Implements basic input sanitization.

#### L5 (Senior) Criteria
- Specifies exact cryptographic schemes, eBPF network filtering rules, and token scoping invariants.
- Writes policy enforcement proxies in code.

#### L6 (Staff) Criteria
- Designs formal verification rules for authorization models and compiler-enforced memory safety.

#### Observable Anti-Patterns
- ❌ **Hand-Waving Mitigations**: Recommending 'use AI to detect bad prompts' without defining deterministic boundaries.

---

### Dimension 3: Systems Architecture & Trade-Off Rigor (Weight: 25%)
*Balancing security controls against user experience, developer velocity, and system latency.*

#### L4 (Mid-Level) Criteria
- Understands that encryption adds CPU and latency overhead.
- Acknowledges impact of rate-limiting on legitimate users.

#### L5 (Senior) Criteria
- Quantifies latency overhead of guardrail classifiers vs regex filters.
- Designs graceful degradation when security inspection services fail.

#### L6 (Staff) Criteria
- Architects frictionless security paradigms (zero-trust mTLS without developer overhead, transparent TEEs).

#### Observable Anti-Patterns
- ❌ **Security Nihilism**: Claiming systems cannot be secured against prompt injection so no controls should be applied.

---

### Dimension 4: Resilience, Security & Edge Case Posture (Weight: 15%)
*Anticipating bypasses, polyglot payloads, race conditions, and side-channel leakage.*

#### L4 (Mid-Level) Criteria
- Considers basic bypasses (URL encoding, case variation).
- Includes rate-limiting against brute force.

#### L5 (Senior) Criteria
- Anticipates multi-step indirect prompt injection (payload split across multiple retrieved documents).
- Designs dual-control gates for irreversible actions.

#### L6 (Staff) Criteria
- Models adversarial compromise of internal logging or build pipelines (SolarWinds-style attacks).

#### Observable Anti-Patterns
- ❌ **Perimeter-Only Defense**: Assuming external defenses will never be breached, leaving internal components unguarded.

---

### Dimension 5: Communication & Calibration Level (Weight: 15%)
*Clarity of risk communication, structured presentation, and empathy for engineering trade-offs.*

#### L4 (Mid-Level) Criteria
- Explains threats clearly in plain English.
- Receptive to interviewer feedback.

#### L5 (Senior) Criteria
- Presents threats prioritized by empirical exploitability and business impact.
- Communicates risk clearly to both engineering and executive audiences.

#### L6 (Staff) Criteria
- Commands executive presence; frames security as an enabler of business velocity.

#### Observable Anti-Patterns
- ❌ **Alarmist Doom-Saying**: Declaring every theoretical issue a critical blocker without risk calibration.

---

## Composite Scoring Calibration

- **Score 1.0 – 2.4 (Below Bar / Not Passing)**: Deficient in core invariants; misses basic correctness constraints; unhandled runtime exceptions.
- **Score 2.5 – 3.4 (L4 Mid-Level Standard)**: Produces working, clean code; identifies edge cases with standard test inputs; needs scaffolding for multi-node tradeoffs.
- **Score 3.5 – 4.4 (L5 Senior Bar - Strong Hire)**: Formulates mathematical/architectural invariants up front; anticipates distributed failure modes; proves time/space bounds.
- **Score 4.5 – 5.0 (L6 Staff Bar - Exceptional)**: Strategic problem reframing; anticipates cascading failure and adversarial vectors; balances cross-cutting organizational invariants.