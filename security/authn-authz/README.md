# Topic: Modern AuthN & AuthZ

**Domain**: `security`  
**Topic ID**: `authn-authz`  
**Canonical Path**: `security/authn-authz/`

## Overview

Comprehensive security architecture covering authentication vs authorization, cryptographic token invariants (stateless JWT/CWT, JWKS rotation, RS256/EdDSA, replay protection), OAuth 2.1 with PKCE, OpenID Connect (OIDC), WebAuthn/FIDO2, and Google Zanzibar Relationship-Based Access Control (ReBAC).

---

## Learning Objectives

- Architect zero-trust authentication boundaries distinguishing identity verification (AuthN) from permission evaluation (AuthZ).
- Validate stateless JWT/CWT tokens enforcing asymmetric cryptographic verification, key rotation, audience/issuer checks, and replay defense.
- Implement OAuth 2.1 Authorization Code Flow with mandatory PKCE (code_verifier and code_challenge) and refresh token rotation.
- Design fine-grained access control models: Role-Based (RBAC), Attribute-Based (ABAC), and Relationship-Based Access Control (ReBAC).
- Implement a Zanzibar-style authorization engine using tuple evaluation, namespace configurations, and external consistency (Zookies) to solve the New-Enemy problem.

## Prerequisite Knowledge Graph

- Asymmetric cryptography fundamentals (public/private key pairs, digital signatures, hashing).
- HTTP protocol, headers, cookies, and TLS/mTLS handshakes.
- Basic distributed systems concepts (eventual consistency, network partitions).

---

## Role Track Relevance

### Track 3: FAANG + AI Labs Security Engineer (L4-L6)
- **Focus & Competencies**: Zero-trust identity federation, Zanzibar-scale authorization services, hardware token attestation, and cryptographically verified access control.

### Track 2: FAANG Privacy Engineer + AI Labs (L5-L6)
- **Focus & Competencies**: Data access governance, tenant boundary enforcement, and privacy-preserving authorization policies.

### Track 1: FAANG SWE + AI Lab SWE (L5/L6)
- **Focus & Competencies**: Identity propagation across microservices, resilient token verification, and low-latency authorization caching.

---

## Company Profiles & Cultural Bars (The 7 Notable Companies)

### Google / GDM
- **Technical Focus**: Global authorization infrastructure (Zanzibar), external consistency (Spanner timestamps), eliminating the New-Enemy problem, and BeyondCorp zero-trust perimeters.
- **Observable Evaluation Signals**:
  - Deep Zanzibar tuple model mastery
  - Zookies consistency proofs
  - Sub-millisecond latency evaluation

### Netflix
- **Technical Focus**: Zero-trust distributed authorization, evaluating high-throughput RPC checks with sub-millisecond p99 latency across multiple cloud regions.
- **Observable Evaluation Signals**:
  - Distributed caching of auth decisions
  - Stateless token validation
  - Graceful degradation under auth outage

### OpenAI
- **Technical Focus**: OAuth 2.1 authorization for plugin ecosystems, fine-grained tenant isolation, and cryptographic user delegation to AI agents.
- **Observable Evaluation Signals**:
  - PKCE token security
  - Scope containment
  - Replay attack defense

### Anthropic
- **Technical Focus**: High-taste security boundaries, defensive token parsing, least privilege principle, and formal authorization policy verification.
- **Observable Evaluation Signals**:
  - No ambient authority
  - Clean separation of AuthN/AuthZ
  - Comprehensive test coverage

### Meta
- **Technical Focus**: Massive scale social-graph authorization (TAO privacy rules), fast ReBAC evaluation, and automated permission auditing.
- **Observable Evaluation Signals**:
  - Graph traversal complexity
  - Cycle detection in group ACLs
  - Cache invalidation protocols

### Databricks
- **Technical Focus**: Multi-tenant cloud access control (Unity Catalog), table/column/row-level ABAC policies, and customer-managed KMS key binding.
- **Observable Evaluation Signals**:
  - Fine-grained ABAC policy engines
  - Audit log immutability
  - Tenant boundary isolation

### Apple
- **Technical Focus**: Hardware-backed authentication (WebAuthn/Secure Enclave), biometric credentials, and zero-knowledge identity tokens.
- **Observable Evaluation Signals**:
  - FIDO2 credential flows
  - Hardware attestation validation
  - Privacy-preserving identity proofs

---

## Standard 5-Artifact Topic Layout

1. **[Fundamentals](./fundamentals.md)**: Core axiomatic invariants, theoretical proofs, mental models, idiomatic code examples, architectural tradeoffs, and failure modes.
2. **[References (YAML)](./references.yaml)** & **[References (Markdown)](./references.md)**: Citable peer-reviewed literature (with DOIs/arXiv IDs), official standards/RFCs, foundational textbooks, and interview loop calibrations.
3. **[Evaluation Rubric](./rubric.md)**: L4 vs L5 vs L6 scoring criteria across the 5 dimensions (Decomposition, Technical Execution, Architecture, Resilience, Communication) matching `docs/ux-spec.md`.
4. **[Adaptive Exercises](./exercises/)**: Tiered problem sets spanning diagnostic starter, mid-level L4, senior L5, and staff L6.
5. **[Durable Learnings](./learnings/)**: Destination directory for user's durable notes and deep-dive captures.