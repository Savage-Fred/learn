# Authoritative References & Citations: Systems, Cloud & AI Threat Modeling

This curriculum grounds all concepts, exercises, and rubrics in peer-reviewed academic literature, formal standards (RFCs, NIST, IETF), foundational textbooks, and verified tier-1 industry interview loops.

## Citable Bibliography

### Threat Modeling: Designing for Security (2014)
- **Authors**: Adam Shostack
- **Type**: `book`
- **Canonical URL / DOI**: [https://www.wiley.com/en-us/Threat+Modeling%3A+Designing+for+Security-p-9781118809990](https://www.wiley.com/en-us/Threat+Modeling%3A+Designing+for+Security-p-9781118809990)
- **Role Relevance**: Track-3-Security, Track-1-SWE
- **Core Invariants Extracted**:
  - Security controls must be applied at trust boundaries.
  - STRIDE maps architectural components to specific threat classes.
- **Interview Loop Calibration**:
  - *Target Company & Level*: Google / GDM (L5)
  - *Round*: Threat Modeling & Security Design
  - *Prompt Summary*: Perform a comprehensive STRIDE analysis of a distributed multi-tenant document storage system.
  - *Expected Evaluation Signals*:
    - Identifies trust boundaries accurately
    - Maps threats systematically across all STRIDE dimensions

```bibtex
@book{shostack2014threat,
  title={Threat Modeling: Designing for Security},
  author={Shostack, Adam},
  year={2014},
  publisher={John Wiley \& Sons}
}
```

### OWASP Top 10 for Large Language Model Applications (2025)
- **Authors**: OWASP GenAI Security Project
- **Type**: `tech_blog`
- **Canonical URL / DOI**: [https://owasp.org/www-project-top-10-for-large-language-model-applications/](https://owasp.org/www-project-top-10-for-large-language-model-applications/)
- **Role Relevance**: Track-3-Security, Track-1-SWE
- **Core Invariants Extracted**:
  - LLM01: Prompt Injection (Direct and Indirect).
  - LLM06: Excessive Agency and unsafe tool invocation.
- **Interview Loop Calibration**:
  - *Target Company & Level*: Anthropic (L5)
  - *Round*: AI Safety & Systems Security
  - *Prompt Summary*: Threat model an autonomous coding agent with git push and terminal access. Identify injection vectors and propose sandboxing controls.
  - *Expected Evaluation Signals*:
    - Identifies indirect prompt injection via untrusted pull request comments or READMEs
    - Specifies microVM or gVisor sandbox with network egress restrictions

```bibtex
@misc{owaspllm2025,
  title={OWASP Top 10 for Large Language Model Applications},
  author={{OWASP Foundation}},
  year={2025},
  url={https://owasp.org/www-project-top-10-for-large-language-model-applications/}
}
```
