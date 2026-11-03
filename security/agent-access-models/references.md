# Authoritative References & Citations: Access Models for Autonomous Agents

This curriculum grounds all concepts, exercises, and rubrics in peer-reviewed academic literature, formal standards (RFCs, NIST, IETF), foundational textbooks, and verified tier-1 industry interview loops.

## Citable Bibliography

### The Confused Deputy: (or why capabilities might have been invented) (1988)
- **Authors**: Norm Hardy
- **Type**: `paper`
- **Canonical URL / DOI**: [https://dl.acm.org/doi/10.1145/54289.871709](https://dl.acm.org/doi/10.1145/54289.871709)
- **Role Relevance**: Track-3-Security, Track-1-SWE
- **Core Invariants Extracted**:
  - Ambient authority inevitably leads to the confused deputy vulnerability.
  - Capabilities bundle designation and authority into an unforgeable token.
- **Interview Loop Calibration**:
  - *Target Company & Level*: OpenAI (L6)
  - *Round*: Agent Platform Security Architecture
  - *Prompt Summary*: Design the access control and sandboxing layer for ChatGPT Operator / web-browsing agent executing arbitrary web interactions while authenticated to user services.
  - *Expected Evaluation Signals*:
    - Identifies confused deputy risks when agent visits adversarial third-party web pages
    - Specifies per-domain cookie/session sandboxing and explicit user confirmation for state mutations

```bibtex
@article{hardy1988confused,
  title={The Confused Deputy: (or why capabilities might have been invented)},
  author={Hardy, Norm},
  journal={ACM SIGOPS Operating Systems Review},
  volume={22},
  number={4},
  pages={36--38},
  year={1988}
}
```

### RFC 8693: OAuth 2.0 Token Exchange (2020)
- **Authors**: Michael B. Jones, Anthony Nadalin, Brian Campbell, John Bradley, Chuck Mortimore
- **Type**: `rfc`
- **Canonical URL / DOI**: [https://datatracker.ietf.org/doc/html/rfc8693](https://datatracker.ietf.org/doc/html/rfc8693)
- **Role Relevance**: Track-3-Security, Track-1-SWE
- **Core Invariants Extracted**:
  - Allows clients to exchange an existing security token for a new token with attenuated scope.
  - Tracks actor (the deputy) and subject (the original principal) in token claims.
- **Interview Loop Calibration**:
  - *Target Company & Level*: Google / GDM (L5)
  - *Round*: Identity & Delegation Architecture
  - *Prompt Summary*: Design an identity propagation protocol where a user delegates a task to an autonomous orchestrator, which invokes subagents.
  - *Expected Evaluation Signals*:
    - Applies RFC 8693 with subject_token and actor_token claims
    - Enforces monotonic scope down-scoping

```bibtex
@misc{rfc8693,
  title={OAuth 2.0 Token Exchange},
  author={Jones, Michael B and Nadalin, Anthony and Campbell, Brian and Bradley, John and Mortimore, Chuck},
  year={2020},
  publisher={IETF RFC 8693}
}
```
