# Authoritative References & Citations: Modern AuthN & AuthZ

This curriculum grounds all concepts, exercises, and rubrics in peer-reviewed academic literature, formal standards (RFCs, NIST, IETF), foundational textbooks, and verified tier-1 industry interview loops.

## Citable Bibliography

### Zanzibar: Google’s Consistent, Global Authorization System (2019)
- **Authors**: Ruoming Pang, Ramon Caceres, Mike Burrows, Zhifeng Chen, Pratik Dave, Nathan Germer, Alexander Golynski, Kevin Graney, Nina Kang, Lea Kissner, Jeffrey L. Korn, Abhishek Parmar, Christina D. Richards, Mengzhi Wang
- **Type**: `paper`
- **Canonical URL / DOI**: [https://www.usenix.org/conference/atc19/presentation/pang](https://www.usenix.org/conference/atc19/presentation/pang)
- **Role Relevance**: Track-3-Security, Track-1-SWE
- **Core Invariants Extracted**:
  - External consistency eliminates the New-Enemy problem using Spanner timestamps and Zookies.
  - Relationship tuples define directed graph reachability for fine-grained permissions.
  - Leopard indexing layer caches set-reachability to guarantee sub-millisecond evaluation.
- **Interview Loop Calibration**:
  - *Target Company & Level*: Google / GDM (L6)
  - *Round*: Distributed Systems & Security Architecture
  - *Prompt Summary*: Design a globally distributed authorization system providing 99.999% availability, sub-millisecond latency, and external consistency for document ACL updates.
  - *Expected Evaluation Signals*:
    - Articulates the New-Enemy problem and snapshot consistency bounds
    - Designs hierarchical caching and graph cycle detection

```bibtex
@inproceedings {234962,
	author = {Ruoming Pang and Ramon Caceres and Mike Burrows and Zhifeng Chen and Pratik Dave and Nathan Germer and Alexander Golynski and Kevin Graney and Nina Kang and Lea Kissner and Jeffrey L. Korn and Abhishek Parmar and Christina D. Richards and Mengzhi Wang},
	title = {Zanzibar: {Google{\textquoteright}s} Consistent, Global Authorization System},
	booktitle = {2019 USENIX Annual Technical Conference (USENIX ATC 19)},
	year = {2019},
	isbn = {978-1-939133-03-8},
	address = {Renton, WA},
	pages = {33--46},
	url = {https://www.usenix.org/conference/atc19/presentation/pang},
	publisher = {USENIX Association},
	month = jul
}
```

### The OAuth 2.1 Authorization Framework (2024)
- **Authors**: Dick Hardt, Aaron Parecki, Torsten Lodderstedt
- **Type**: `rfc`
- **Canonical URL / DOI**: [https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/)
- **Role Relevance**: Track-3-Security, Track-1-SWE
- **Core Invariants Extracted**:
  - PKCE is mandatory for all OAuth clients (confidential and public).
  - Implicit grant and resource owner password credentials are deprecated.
  - Refresh token rotation must invalidate previous tokens upon single use.
- **Interview Loop Calibration**:
  - *Target Company & Level*: OpenAI (L5)
  - *Round*: Systems Security
  - *Prompt Summary*: Design the authentication and authorization flow for third-party developer integrations connecting to user accounts via OAuth 2.1.
  - *Expected Evaluation Signals*:
    - Mandates PKCE with code_challenge and code_verifier
    - Enforces refresh token rotation and token revocation endpoints

```bibtex
@misc{oauth21draft,
  title={The OAuth 2.1 Authorization Framework},
  author={Hardt, Dick and Parecki, Aaron and Lodderstedt, Torsten},
  year={2024},
  publisher={IETF OAuth Working Group}
}
```
