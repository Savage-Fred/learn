# Exercise TIER1_STARTER: STRIDE Analysis of a 3-Tier Web Application

**Objective**: Perform a systematic STRIDE threat analysis on a standard web application architecture and define concrete mitigations.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `shostack-threat-modeling-2014`, `owasp-top-10-llm-2025`
- **Applicable Citations**:
  - [Threat Modeling: Designing for Security](https://www.wiley.com/en-us/Threat+Modeling%3A+Designing+for+Security-p-9781118809990) (2014)
  - [OWASP Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) (2025)

---

## Problem Statement

Given a web architecture where an untrusted Web Browser communicates via HTTPS with an NGINX reverse proxy, which routes to a Python FastAPI backend, which queries a PostgreSQL database: construct a structured STRIDE matrix. For each category (S, T, R, I, D, E), state the specific threat, vulnerable component, and standard architectural mitigation.

---

## Invariant Scaffolding & Guidance

- Identify trust boundaries between Client, Reverse Proxy, Application Server, and Database.
- Map each STRIDE category to at least one concrete threat across the boundaries.

---

## Starter Code

```python
# Return a structured list of threat models conforming to STRIDE
def stride_analysis():
    return [
        {"stride_category": "Spoofing", "threat": "...", "mitigation": "..."},
        {"stride_category": "Tampering", "threat": "...", "mitigation": "..."},
        {"stride_category": "Repudiation", "threat": "...", "mitigation": "..."},
        {"stride_category": "Information Disclosure", "threat": "...", "mitigation": "..."},
        {"stride_category": "Denial of Service", "threat": "...", "mitigation": "..."},
        {"stride_category": "Elevation of Privilege", "threat": "...", "mitigation": "..."},
    ]
```

---

## Verification Test Cases

- [ ] **Test Case**: Covers all 6 STRIDE categories with non-empty entries.
- [ ] **Test Case**: Mitigations reference industry-standard controls (e.g. mTLS, parameterization, audit logs, rate limits).
- [ ] **Test Case**: Correctly identifies the trust boundary crossed for each threat.

---

## Solution & Invariant Check

Spoofing: client identity spoofing mitigated by WebAuthn/mTLS; Tampering: MITM mitigated by TLS 1.3; Repudiation: unauthenticated transactions mitigated by immutable append-only audit logs; Info Disclosure: SQLi mitigated by ORM parameterization; DoS: API flooding mitigated by token bucket rate-limiting; EoP: role escalation mitigated by ReBAC/RBAC.