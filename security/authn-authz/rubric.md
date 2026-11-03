# Evaluation Rubric & Calibration Guide: Modern AuthN & AuthZ

This rubric defines the scoring calibration for mock interview assessments, coding exercises, and technical design evaluations across five standardized dimensions.

## Seniority Level Overview

- **L4 (Mid-Level)**: Understands difference between AuthN and AuthZ; validates JWT signatures using standard libraries; implements basic OAuth 2.0 flows and RBAC permission tables.
- **L5 (Senior)**: Architects OAuth 2.1 with PKCE and token rotation; designs ReBAC authorization models; proves prevention of the New-Enemy problem; implements JWKS key rotation pipelines.
- **L6 (Staff / Principal)**: Deploys global zero-trust authorization systems handling billions of checks per second; designs formal policy verification engines; proves external consistency under network partitions.

---

## The 5 Scoring Dimensions

### Dimension 1: Problem Decomposition & Invariant Formulation (Weight: 20%)
*Formulation of identity, token, and authorization boundary invariants.*

#### L4 (Mid-Level) Criteria
- Distinguishes user identity (who) from permissions (what).
- Identifies token expiration and audience verification requirements.

#### L5 (Senior) Criteria
- Formulates mathematical invariant of PKCE challenge verification.
- Models permissions as an ACL graph with defined reachability invariants.

#### L6 (Staff) Criteria
- Proves why causal consistency is insufficient to prevent ACL leaks without external consistency (Zanzibar Zookies).

#### Observable Anti-Patterns
- ❌ **Confusing AuthN with AuthZ**: Assuming a valid signature implies permission to perform arbitrary actions.

---

### Dimension 2: Technical Execution & Code Craftsmanship (Weight: 25%)
*Correct, secure implementation of cryptographic verification, token parsing, and policy evaluation.*

#### L4 (Mid-Level) Criteria
- Parses JWT headers and verifies signatures without disabling validation flags.
- Correctly handles HTTP Authorization headers.

#### L5 (Senior) Criteria
- Implements constant-time string comparison to prevent timing attacks.
- Handles JWKS cache expiration and key rotation gracefully.

#### L6 (Staff) Criteria
- Implements high-performance graph reachability engine with memoization and cycle detection.

#### Observable Anti-Patterns
- ❌ **Skipping Signature Verification**: Decoding JWT payloads using jwt.decode(verify=False).

---

### Dimension 3: Systems Architecture & Trade-Off Rigor (Weight: 25%)
*Evaluation of centralized vs decentralized token validation, caching, and revocation.*

#### L4 (Mid-Level) Criteria
- Understands stateless token vs database session trade-offs.
- Calculates token lifetime impacts.

#### L5 (Senior) Criteria
- Architects hybrid JWT + revocation list with Bloom filter caching.
- Designs low-latency authorization proxies.

#### L6 (Staff) Criteria
- Quantifies p99 latency impact of distributed consensus (Spanner/Paxos) in authorization paths.

#### Observable Anti-Patterns
- ❌ **Unbounded Re-Auth Traffic**: Forcing downstream microservices to query central identity provider on every sub-call.

---

### Dimension 4: Resilience, Security & Edge Case Posture (Weight: 15%)
*Defenses against token replay, algorithm confusion, key compromise, and cyclic group denial-of-service.*

#### L4 (Mid-Level) Criteria
- Validates exp, iss, and aud claims.
- Handles expired tokens cleanly with 401 Unauthorized.

#### L5 (Senior) Criteria
- Guards against alg: none and HMAC-RSA key substitution attacks.
- Detects cyclic group memberships in authorization trees.

#### L6 (Staff) Criteria
- Designs emergency key revocation and instantaneous credential termination protocols.

#### Observable Anti-Patterns
- ❌ **Accepting Any Public Key**: Using public keys extracted from unauthenticated token headers without matching trusted JWKS.

---

### Dimension 5: Communication & Calibration Level (Weight: 15%)
*Precision of technical security terminology, threat modeling communication, and executive clarity.*

#### L4 (Mid-Level) Criteria
- Clearly explains authentication steps.
- Receptive to security edge-case prompts.

#### L5 (Senior) Criteria
- Articulates cryptographic guarantees and failure scenarios crisply.
- Justifies protocol choices with industry RFC standards.

#### L6 (Staff) Criteria
- Communicates security posture with executive presence; translates business risks into technical controls.

#### Observable Anti-Patterns
- ❌ **Vague Hand-Waving**: Saying 'we just encrypt it' without specifying algorithms, key management, or verification steps.

---

## Composite Scoring Calibration

- **Score 1.0 – 2.4 (Below Bar / Not Passing)**: Deficient in core invariants; misses basic correctness constraints; unhandled runtime exceptions.
- **Score 2.5 – 3.4 (L4 Mid-Level Standard)**: Produces working, clean code; identifies edge cases with standard test inputs; needs scaffolding for multi-node tradeoffs.
- **Score 3.5 – 4.4 (L5 Senior Bar - Strong Hire)**: Formulates mathematical/architectural invariants up front; anticipates distributed failure modes; proves time/space bounds.
- **Score 4.5 – 5.0 (L6 Staff Bar - Exceptional)**: Strategic problem reframing; anticipates cascading failure and adversarial vectors; balances cross-cutting organizational invariants.