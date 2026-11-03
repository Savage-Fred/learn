# Evaluation Rubric & Calibration Guide: Access Models for Autonomous Agents

This rubric defines the scoring calibration for mock interview assessments, coding exercises, and technical design evaluations across five standardized dimensions.

## Seniority Level Overview

- **L4 (Mid-Level)**: Understands least privilege; uses short-lived API keys; implements basic tool schema validation and permission checks in code.
- **L5 (Senior)**: Architects dynamic capability attenuation; designs RFC 8693 token exchange for agent delegation; configures container sandboxes (gVisor/Firecracker); implements HITL dual-control.
- **L6 (Staff / Principal)**: Designs enterprise-wide autonomous agent execution platforms; proves formal capability invariants; architects multi-tenant microVM sandboxes with eBPF egress enforcement and hardware attestation.

---

## The 5 Scoring Dimensions

### Dimension 1: Problem Decomposition & Invariant Formulation (Weight: 20%)
*Formulation of capability boundaries, delegation invariants, and non-ambient authority.*

#### L4 (Mid-Level) Criteria
- Identifies risks of giving agent full database or cloud credentials.
- Lists tools requiring restricted permissions.

#### L5 (Senior) Criteria
- Formulates monotonic privilege attenuation invariant.
- Separates user identity from ephemeral agent delegation tokens.

#### L6 (Staff) Criteria
- Proves elimination of confused deputy vulnerabilities using capability security theory.

#### Observable Anti-Patterns
- ❌ **Ambient Credential Storage**: Placing global admin credentials in agent process environment variables.

---

### Dimension 2: Technical Execution & Code Craftsmanship (Weight: 25%)
*Implementation of token chaining, HMAC verification, sandbox lifecycle, and eBPF filters.*

#### L4 (Mid-Level) Criteria
- Implements token verification with expiration checks.
- Validates input parameter types.

#### L5 (Senior) Criteria
- Implements chained HMAC caveats with constant-time verification.
- Manages ephemeral sandbox lifecycles cleanly.

#### L6 (Staff) Criteria
- Writes kernel-level seccomp/eBPF network egress filters blocking link-local and internal subnets.

#### Observable Anti-Patterns
- ❌ **Unvalidated Sandbox Escapes**: Running untrusted agent Python scripts via bare subprocess.Popen(shell=True).

---

### Dimension 3: Systems Architecture & Trade-Off Rigor (Weight: 25%)
*Evaluating performance overhead of sandboxes (startup latency, memory) vs security isolation.*

#### L4 (Mid-Level) Criteria
- Understands differences between Docker and virtual machines.
- Calculates token lifetime trade-offs.

#### L5 (Senior) Criteria
- Compares warm microVM pools vs on-demand cold starts.
- Quantifies memory footprint of 10,000 concurrent agent sandboxes.

#### L6 (Staff) Criteria
- Architects hybrid tiered execution: fast WebAssembly for read tools, isolated microVMs for untrusted code.

#### Observable Anti-Patterns
- ❌ **Ignoring Sandbox Boot Latency**: Assuming standard heavy VMs (30s boot) can handle real-time interactive user turns.

---

### Dimension 4: Resilience, Security & Edge Case Posture (Weight: 15%)
*Handling sandbox crashes, OOM kills, network partition during token exchange, and prompt hijacking.*

#### L4 (Mid-Level) Criteria
- Sets timeouts on tool execution.
- Catches tool execution exceptions.

#### L5 (Senior) Criteria
- Cleans up leaked sandboxes and dangling network namespaces on worker crashes.
- Guards against fork-bombs and memory exhaustion.

#### L6 (Staff) Criteria
- Designs tamper-proof audit trails recording cryptographically signed proofs of agent authorization.

#### Observable Anti-Patterns
- ❌ **Unbounded Egress**: Allowing sandboxes unrestricted outbound internet access, enabling reverse shells.

---

### Dimension 5: Communication & Calibration Level (Weight: 15%)
*Clarity of capability concepts, risk framing, and collaborative problem solving.*

#### L4 (Mid-Level) Criteria
- Explains sandbox concepts clearly.
- Follows guidance on security best practices.

#### L5 (Senior) Criteria
- Articulates capability theory and confused deputy mechanics with precision.
- Frames security solutions around developer ergonomics.

#### L6 (Staff) Criteria
- Drives high-level security architecture discussions with executive presence.

#### Observable Anti-Patterns
- ❌ **Buzzword Bingo**: Listing security tools (eBPF, Wasm, gVisor) without explaining how they enforce invariants.

---

## Composite Scoring Calibration

- **Score 1.0 – 2.4 (Below Bar / Not Passing)**: Deficient in core invariants; misses basic correctness constraints; unhandled runtime exceptions.
- **Score 2.5 – 3.4 (L4 Mid-Level Standard)**: Produces working, clean code; identifies edge cases with standard test inputs; needs scaffolding for multi-node tradeoffs.
- **Score 3.5 – 4.4 (L5 Senior Bar - Strong Hire)**: Formulates mathematical/architectural invariants up front; anticipates distributed failure modes; proves time/space bounds.
- **Score 4.5 – 5.0 (L6 Staff Bar - Exceptional)**: Strategic problem reframing; anticipates cascading failure and adversarial vectors; balances cross-cutting organizational invariants.