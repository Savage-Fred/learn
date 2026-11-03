# Domain: Systems, Cloud & AI Security

**Directory**: `security/`  
**Platform Domain ID**: `security`

## Overview

Zero-trust identity federation, relationship-based authorization (ReBAC/Zanzibar), empirical threat modeling for AI/LLMs, and sandboxed capability access models for autonomous agents.

---

## Priority Topics & Curriculum Index

### [Modern AuthN & AuthZ](./authn-authz/)
- **Path**: `security/authn-authz/`
- **Focus**: Cryptographic token validation (JWT, JWKS, EdDSA), OAuth 2.1 & PKCE, OIDC, WebAuthn/FIDO2, and Google Zanzibar ReBAC tuple evaluation.
- **Artifacts**: [Fundamentals](./authn-authz/fundamentals.md) | [References](./authn-authz/references.md) | [Rubric](./authn-authz/rubric.md) | [Exercises](./authn-authz/exercises/) | [Learnings](./authn-authz/learnings/)

### [Threat Modeling for Systems & AI](./threat-modeling/)
- **Path**: `security/threat-modeling/`
- **Focus**: Trust boundaries, STRIDE/PASTA/LINDDUN frameworks, OWASP LLM Top 10 (prompt injection, excessive agency), and CVSS v4.0 risk scoring.
- **Artifacts**: [Fundamentals](./threat-modeling/fundamentals.md) | [References](./threat-modeling/references.md) | [Rubric](./threat-modeling/rubric.md) | [Exercises](./threat-modeling/exercises/) | [Learnings](./threat-modeling/learnings/)

### [Access Models for Agents](./agent-access-models/)
- **Path**: `security/agent-access-models/`
- **Focus**: Confused deputy prevention, dynamic capability attenuation, RFC 8693 token exchange, microVM isolation (Firecracker), and HITL dual-control.
- **Artifacts**: [Fundamentals](./agent-access-models/fundamentals.md) | [References](./agent-access-models/references.md) | [Rubric](./agent-access-models/rubric.md) | [Exercises](./agent-access-models/exercises/) | [Learnings](./agent-access-models/learnings/)

---

## Target Role Tracks & Seniority Calibrations

### Track 3: FAANG + AI Labs Security Engineer (L4 (Mid), L5 (Senior), L6 (Staff))
Zero-trust boundary architecture, autonomous agent threat modeling, cryptographic credential delegation, and sandbox escaping defense.

### Track 1: FAANG SWE + AI Lab SWE (L5-L6)
Identity propagation across microservices, resilient token verification, and least-privilege service design.

---

## Company Profiles & Cultural Bars

- **OpenAI**: Agent sandboxing, tool-calling permission policies, red teaming, and ChatGPT Operator credential protection.
- **Google / GDM**: Global authorization infrastructure (Zanzibar), external consistency (Spanner timestamps), and BeyondCorp zero-trust perimeters.
- **Anthropic**: Constitutional AI boundaries, prompt injection mitigation, least-privilege tool execution, and defensive sandbox architecture.
- **Meta**: Massive multi-tenant authorization graphs, cryptographic session management, and automated vulnerability detection.
- **Databricks**: Multi-tenant cloud data isolation, fine-grained table/column access control, and customer-managed encryption keys.
- **Netflix**: Consoles and microservices zero-trust authorization with sub-millisecond p99 latency across distributed regions.
- **Apple**: Private Cloud Compute security invariants, cryptographic hardware verification, and end-to-end user privacy boundaries.

---

## Standard 5-Artifact Contract

Every topic directory inside this domain adheres strictly to the canonical 5-artifact layout:
1. `README.md`: Scope, role alignment, company calibration, and topic navigation.
2. `fundamentals.md`: Core axiomatic invariants, proofs, idiomatic code, and failure modes.
3. `references.yaml` & `references.md`: Citable academic papers, RFCs, books, and verified interview loops.
4. `rubric.md`: Role-calibrated 5-dimension scoring criteria across L4, L5, and L6.
5. `exercises/`: Tiered adaptive problem sets (`tier1_starter.md`, `tier2_l4.md`, `tier3_l5.md`, `tier4_l6.md`).
6. `learnings/`: Git-committed destination for user's durable notes and deep-dive captures.