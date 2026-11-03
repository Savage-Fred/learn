# Topic: Access Models for Autonomous Agents

**Domain**: `security`  
**Topic ID**: `agent-access-models`  
**Canonical Path**: `security/agent-access-models/`

## Overview

Modern capability and authorization frameworks for non-deterministic LLM agents. Covers the Confused Deputy problem in autonomous systems, dynamic capability attenuation, RFC 8693 Token Exchange, Macaroons with caveats, microVM / V8 isolate sandboxing (Firecracker, gVisor), and Human-in-the-Loop dual-control gates.

---

## Learning Objectives

- Deconstruct the Confused Deputy problem in LLM agents and prove why ambient authority is fundamentally insecure.
- Design dynamic capability attenuation mechanisms issuing short-lived, parameter-scoped authorization tokens.
- Implement RFC 8693 OAuth 2.0 Token Exchange for propagating user identity across multi-agent delegation chains.
- Architect micro-isolation sandboxes (Firecracker microVMs, gVisor, WebAssembly) with strict eBPF network egress filtering.
- Implement cryptographic dual-control and Human-in-the-Loop (HITL) gates for high-consequence state mutations.

## Prerequisite Knowledge Graph

- OAuth 2.0 / 2.1 token architecture.
- Linux kernel isolation primitives (namespaces, cgroups, seccomp, eBPF).
- Capabilities-based security theory (Saltzer & Schroeder, Hardy).

---

## Role Track Relevance

### Track 3: FAANG + AI Labs Security Engineer (L4-L6)
- **Focus & Competencies**: Agent sandboxing, capability attenuation, secure delegation token exchange, and defense against autonomous hijacking.

### Track 4: AI Lab Research Engineer (non-PhD) (L4/L5)
- **Focus & Competencies**: Sandboxed Python code execution environments, tool call permission proxies, and low-latency microVM management.

### Track 1: FAANG SWE + AI Lab SWE (L5/L6)
- **Focus & Competencies**: Identity propagation across agent swarms, token lifecycle management, and resilient RPC boundaries.

---

## Company Profiles & Cultural Bars (The 7 Notable Companies)

### OpenAI
- **Technical Focus**: ChatGPT Operator and autonomous browser agents; securing tool calling against confused deputy manipulation while maintaining high user convenience.
- **Observable Evaluation Signals**:
  - Capability attenuation
  - Ephemeral credential scoping
  - Sandboxed execution

### Anthropic
- **Technical Focus**: Computer use / tool calling security; constitutional agent boundaries; preventing unauthorized file system mutation and network egress.
- **Observable Evaluation Signals**:
  - Least privilege agent profiles
  - Dual-control HITL gates
  - Zero ambient authority

### Google / GDM
- **Technical Focus**: Borg-scale agent execution sandboxes (gVisor); cryptographically verifiable delegation chains across microservices.
- **Observable Evaluation Signals**:
  - Formal delegation token exchange
  - Container isolation invariants
  - Audit trail completeness

### Meta
- **Technical Focus**: Large-scale developer assistant tools; securing git access and shell execution against malicious prompt injection in codebases.
- **Observable Evaluation Signals**:
  - Repository permission bounds
  - Read-only ephemeral sandboxes
  - Command whitelisting

### Databricks
- **Technical Focus**: AI/BI data agents generating and running SQL against enterprise data lakes; column-level authorization attenuation.
- **Observable Evaluation Signals**:
  - SQL AST validation
  - Fine-grained delegation tokens
  - Audit immutability

### Netflix
- **Technical Focus**: Automated incident remediation agents; ensuring remediation scripts cannot exceed narrowly prescribed runbook actions.
- **Observable Evaluation Signals**:
  - Blast radius confinement
  - Automated rollbacks
  - Supervised authorization

### Apple
- **Technical Focus**: On-device intelligence agent execution; strict privacy boundaries preventing cross-app data exfiltration.
- **Observable Evaluation Signals**:
  - OS-enforced entitlement sandboxes
  - Zero ambient cross-app access
  - User consent prompts

---

## Standard 5-Artifact Topic Layout

1. **[Fundamentals](./fundamentals.md)**: Core axiomatic invariants, theoretical proofs, mental models, idiomatic code examples, architectural tradeoffs, and failure modes.
2. **[References (YAML)](./references.yaml)** & **[References (Markdown)](./references.md)**: Citable peer-reviewed papers (with DOIs/arXiv IDs), official RFCs, foundational textbooks, and recent verified tier-1 interview loop calibrations.
3. **[Evaluation Rubric](./rubric.md)**: L4 vs L5 vs L6 scoring criteria across the 5 dimensions (Decomposition, Technical Execution, Architecture, Resilience, Communication) matching `docs/ux-spec.md`.
4. **[Adaptive Exercises](./exercises/)**: Tiered problem sets spanning diagnostic starter, mid-level L4, senior L5, and staff L6.
5. **[Durable Learnings](./learnings/)**: Destination directory for user's durable notes and deep-dive captures.