# Topic: Systems, Cloud & AI Threat Modeling

**Domain**: `security`  
**Topic ID**: `threat-modeling`  
**Canonical Path**: `security/threat-modeling/`

## Overview

Rigorous threat modeling methodology for cloud infrastructure and frontier AI agent architectures. Covers trust boundaries, STRIDE, PASTA, LINDDUN, OWASP LLM Top 10 (prompt injection, excessive agency, tool poisoning), and CVSS v4.0 risk scoring.

---

## Learning Objectives

- Deconstruct complex software architectures into trust zones, data flows, and perimeter boundaries.
- Apply STRIDE, PASTA, and LINDDUN frameworks to uncover architectural security and privacy flaws.
- Analyze frontier AI threat vectors: Direct vs Indirect Prompt Injection, Model Inversion, and Excessive Agency.
- Formulate defense-in-depth mitigations establishing cryptographic trust and input sanitization at boundaries.
- Calculate quantitative risk ratings using CVSS v4.0 and prioritize mitigation roadmaps.

## Prerequisite Knowledge Graph

- Web application architecture (reverse proxies, API gateways, databases).
- Basic security terminology (spoofing, tampering, privilege escalation).
- Familiarity with Large Language Model APIs and autonomous tool calling.

---

## Role Track Relevance

### Track 3: FAANG + AI Labs Security Engineer (L4-L6)
- **Focus & Competencies**: Systematic threat modeling, AI agent attack surfaces, jailbreak defenses, and least-privilege cloud boundaries.

### Track 2: FAANG Privacy Engineer + AI Labs (L5-L6)
- **Focus & Competencies**: Privacy threat modeling (LINDDUN), data flow trust boundaries, and telemetry exfiltration vectors.

### Track 1: FAANG SWE + AI Lab SWE (L5/L6)
- **Focus & Competencies**: Secure architectural decomposition, input validation invariants, and threat boundary enforcement.

---

## Company Profiles & Cultural Bars (The 7 Notable Companies)

### Anthropic
- **Technical Focus**: Rigorous threat modeling of autonomous coding agents with tool execution and shell access; indirect prompt injection vectors and constitutional boundaries.
- **Observable Evaluation Signals**:
  - Clear separation of data vs control plane
  - Sandboxing defense-in-depth
  - Comprehensive threat enumeration

### OpenAI
- **Technical Focus**: ChatGPT Operator and agent tools threat modeling; preventing confused deputy attacks and credential exfiltration via web browsing.
- **Observable Evaluation Signals**:
  - SSRF mitigations
  - Attenuated tool credentials
  - Human-in-the-loop triggers

### Google / GDM
- **Technical Focus**: BeyondCorp perimeter-less architectures, supply-chain threat modeling (SLSA), and model weight exfiltration mitigations.
- **Observable Evaluation Signals**:
  - Formal trust boundary diagrams
  - Threat categorization using STRIDE
  - Quantitative CVSS scoring

### Meta
- **Technical Focus**: Massive multi-tenant infrastructure threat analysis, preventing horizontal privilege escalation in internal developer tools.
- **Observable Evaluation Signals**:
  - Data flow tracing
  - Rate-limiting defenses
  - Automated threat detection

### Databricks
- **Technical Focus**: Data lake clean room threat models, side-channel leakage across co-located cloud tenants, and SQL injection in query planners.
- **Observable Evaluation Signals**:
  - Tenant isolation boundaries
  - Side-channel mitigation
  - Least privilege execution

### Netflix
- **Technical Focus**: Chaos engineering for security, testing automated failure recovery under active adversary simulation.
- **Observable Evaluation Signals**:
  - Failure domain blast radius
  - Resilience under credential compromise
  - Security telemetry

### Apple
- **Technical Focus**: Private Cloud Compute threat modeling, hardware attestation guarantees against physical tampering and cloud provider insider threats.
- **Observable Evaluation Signals**:
  - Cryptographic boundary verification
  - Zero data retention proofs
  - Transparency logs

---

## Standard 5-Artifact Topic Layout

1. **[Fundamentals](./fundamentals.md)**: Core axiomatic invariants, theoretical proofs, mental models, idiomatic code examples, architectural tradeoffs, and failure modes.
2. **[References (YAML)](./references.yaml)** & **[References (Markdown)](./references.md)**: Citable peer-reviewed literature (with DOIs/arXiv IDs), official standards/RFCs, foundational textbooks, and interview loop calibrations.
3. **[Evaluation Rubric](./rubric.md)**: L4 vs L5 vs L6 scoring criteria across the 5 dimensions (Decomposition, Technical Execution, Architecture, Resilience, Communication) matching `docs/ux-spec.md`.
4. **[Adaptive Exercises](./exercises/)**: Tiered problem sets spanning diagnostic starter, mid-level L4, senior L5, and staff L6.
5. **[Durable Learnings](./learnings/)**: Destination directory for user's durable notes and deep-dive captures.