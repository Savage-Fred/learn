# Milestone 2 Review Gate Receipts

**PR**: [#3 Grounded Curricula & Content Seed](https://github.com/Savage-Fred/learn/pull/3)  
**Branch**: `feat/topic-curricula-seed` -> `feat/foundation-and-docs`  
**Reviewers**: Astra (`gpt-6-astra`), Sol (`gpt-6-sol`), Claude (`claude -p`)  
**Final Commit**: `8e04a34`  
**Date**: 2026-11-03  

---

## 1. Review Summary & Decision Log

| Reviewer | Tool / Model | Round 1 Verdict (`9fd2930`) | Round 2 Verdict (`91f59c3`) | Final Resolution (`8e04a34`) |
|---|---|---|---|---|
| **Astra** | `codex exec -c model="gpt-6-astra"` | Changes Requested (8 items) | Changes Requested (5 items) | **Fully Resolved & Passing** |
| **Sol** | `codex exec -c model="gpt-6-sol"` | *(Joined Round 2)* | Changes Requested (4 items) | **Fully Resolved & Passing** |
| **Claude** | `claude -p` | *(Joined Round 2)* | Changes Requested (6 blockers, 7 should-fix) | **Fully Resolved & Passing** |

---

## 2. Round 1 Audit Findings & Resolutions (Astra)

### Finding 1: Exercise Source Reference IDs
- **Observation**: Exercises had no explicit link to literature IDs in `references.yaml`.
- **Resolution**: Updated all 44 canonical exercise markdown files (`tier1_starter.md`, `tier2_l4.md`, `tier3_l5.md`, `tier4_l6.md`) with explicit `Source Reference IDs: ` lists referencing valid IDs.
- **Verification**: Enforced by `test_exercises_contain_all_four_tiers`.

### Finding 2: Google Zanzibar Publication Venue
- **Observation**: Cited as Google internal paper instead of official USENIX ATC 19 proceedings.
- **Resolution**: Updated `references.yaml` with USENIX ATC 19 title, venue, pages (`33--46`), and canonical URL.
- **Verification**: Enforced by `test_zanzibar_citation_publisher_fidelity`.

### Finding 3: SSRF Hostname Validation
- **Observation**: Raw URL regex string matching failed against IP literals, IPv6, and bypass encodings.
- **Resolution**: Replaced regex with DNS resolution checking `ipaddress.is_private`, `is_loopback`, `is_link_local`.
- **Verification**: Enforced by `test_concurrency_and_security_code_soundness`.

### Finding 4: Capability Caveat Fail-Closed Handling
- **Observation**: Unrecognized caveats in capability tokens defaulted to true.
- **Resolution**: Enforced strict fail-closed rejection: any unknown caveat fails verification immediately.
- **Verification**: Tested in `test_concurrency_and_security_code_soundness`.

### Finding 5: Rust Concurrency Safe Interfaces
- **Observation**: SPSC buffer implemented `Sync` while sharing safe `&self` push methods.
- **Resolution**: Separated into exclusive `SpscProducer` and `SpscConsumer` handles taking `&mut self`.
- **Verification**: Tested in `test_concurrency_and_security_code_soundness`.

### Finding 6: Secure Aggregation Cryptographic Invariants
- **Observation**: Zero-sum masks derived from public IDs lacked genuine confidentiality.
- **Resolution**: Replaced with modular Diffie-Hellman shared secret key exchange ($pk_j^{sk_i} \pmod p$).
- **Verification**: Tested in `test_concurrency_and_security_code_soundness`.

### Finding 7: Membership Inference Attack Advantage
- **Observation**: Defined as $|P_{in} - 0.5|$, yielding 50% advantage for constant guessing.
- **Resolution**: Corrected to standard True Positive Rate minus False Positive Rate: $\text{Adv} = \text{TPR} - \text{FPR}$.
- **Verification**: Enforced by `test_mathematical_invariants_rigor`.

### Finding 8: Rényi Differential Privacy Composition
- **Observation**: Adaptive composition was stated as an equality rather than an upper-bound inequality.
- **Resolution**: Corrected to inequality $\le \sum D_\alpha$.
- **Verification**: Enforced by `test_mathematical_invariants_rigor`.

---

## 3. Round 2 Cross-Agent Audit Findings & Final Resolutions (`8e04a34`)

### Finding 9: Duplicate Hyphenated Exercise Files (Claude)
- **Observation**: 44 duplicate files (`tier1-starter.md`, `tier2-intermediate.md`, `tier3-advanced.md`, `tier4-staff.md`) existed alongside canonical underscore files (`tier1_starter.md`, `tier2_l4.md`, `tier3_l5.md`, `tier4_l6.md`).
- **Resolution**: Executed `git rm` removing all 44 hyphenated files; modified generator in `/tmp/curricula_builder/build.py` to prevent creation and actively purge legacy files. Added automated unit test `test_no_hyphenated_exercise_files`.

### Finding 10: Zanzibar Complete Official Author List (Astra, Claude)
- **Observation**: `security/authn-authz/references.yaml` contained inaccurate authors ("Alex Chen", "Pratik Fimat", etc.) instead of the exact 14 authors from the USENIX ATC 19 paper.
- **Resolution**: Replaced author list with all 14 official authors from the USENIX publication:
  `Ruoming Pang`, `Ramon Caceres`, `Mike Burrows`, `Zhifeng Chen`, `Pratik Dave`, `Nathan Germer`, `Alexander Golynski`, `Kevin Graney`, `Nina Kang`, `Lea Kissner`, `Jeffrey L. Korn`, `Abhishek Parmar`, `Christina D. Richards`, `Mengzhi Wang`.
  Imported official USENIX ATC 19 BibTeX (`@inproceedings {234962, ...}`).
- **Verification**: Added author array equality assertion in `test_zanzibar_citation_publisher_fidelity`.

### Finding 11: CUPED WSDM 2013 Page Numbers (Claude)
- **Observation**: `system-design/statistics/references.yaml` listed pages `445--454` instead of official WSDM 2013 pages `123--132`.
- **Resolution**: Corrected citation BibTeX and metadata to `pages={123--132}`.
- **Verification**: Added check in `test_grounded_references_and_role_tracks`.

### Finding 12: Confused Deputy ACM Paper DOI (Claude)
- **Observation**: `security/agent-access-models/references.yaml` referenced ACM issue DOI `10.1145/54289.848243` instead of the specific paper DOI.
- **Resolution**: Updated canonical URL and DOI to `10.1145/54289.871709` (Norman Hardy, "The Confused Deputy: (or why capabilities might have been invented)").
- **Verification**: Added check in `test_grounded_references_and_role_tracks`.

### Finding 13: Complete Author Lists on Referenced Standards (Claude)
- **Observation**: Author lists were truncated without "et al." across several citations.
- **Resolution**: Updated author arrays and BibTeX to full official lists:
  - **RFC 8693**: Michael B. Jones, Anthony Nadalin, Brian Campbell, John Bradley, Chuck Mortimore.
  - **Carlini et al. 2021**: Nicholas Carlini, Florian Tramèr, Eric Wallace, Matthew Jagielski, Ariel Herbert-Voss, Katherine Lee, Adam Roberts, Tom Brown, Dawn Song, Úlfar Erlingsson, Alina Oprea.
  - **Bonawitz et al. 2017**: Keith Bonawitz, Vladimir Ivanov, Ben Kreuter, Antonio Marcedone, H. Brendan McMahan, Sarvar Patel, Daniel Ramage, Aaron Segal, Karn Seth.
  - **Herlihy & Shavit (2nd ed)**: Maurice Herlihy, Nir Shavit, Victor Luchangco, Michael Spear.

### Finding 14: Dual-Stack SSRF & DNS Rebinding (Astra, Sol, Claude)
- **Observation**: `gethostbyname_ex` was IPv4-only (allowing private IPv6 AAAA bypasses) and lacked socket pinning documentation to prevent Time-of-Check to Time-of-Use (TOCTOU) DNS rebinding.
- **Resolution**: Upgraded `is_private_or_loopback_destination` to dual-stack `socket.getaddrinfo(hostname, None, proto=socket.IPPROTO_TCP)`. Validates every IPv4 and IPv6 record against `is_private`, `is_loopback`, `is_link_local`, `is_multicast`, `is_reserved`, and `is_unspecified`. Documented mandatory socket connection pinning and HTTP redirect re-validation.
- **Verification**: Tested in `test_concurrency_and_security_code_soundness`.

### Finding 15: Threat Modeling L6 Attestation Grounding (Sol)
- **Observation**: `tier4_l6.md` in `security/threat-modeling` required NVIDIA H100 attestation and protected memory verification, but lacked a cited source for those specific claims.
- **Resolution**: Added official reference `nvidia-gpu-attestation-2023` ("NVIDIA Confidential Computing on Hopper Architecture: Deployment and Remote Attestation Guide") to `references.yaml` and linked it directly in `tier4_l6.md`.
- **Verification**: Added assertion in `test_grounded_references_and_role_tracks`.

### Finding 16: Non-`Sync` Rust Concurrency Handles (Astra, Claude)
- **Observation**: `SpscProducer` and `SpscConsumer` contained an `Arc<SpscRingBuffer>` field; because `SpscRingBuffer` implemented `Sync`, Rust auto-traits automatically implemented `Sync` for the handles.
- **Resolution**: Added `_marker: std::marker::PhantomData<std::cell::Cell<()>>` to both structs. Because `Cell` is `!Sync`, the handles are strictly `!Sync` (can be sent across threads via `Send`, but cannot be shared concurrently across threads). Added compile-time trait assertions.
- **Verification**: Verified in `test_concurrency_and_security_code_soundness`.

### Finding 17: Go Code Example Cleanliness (Claude)
- **Observation**: `system-design/go/fundamentals.md` imported `"time"` and `"errors"` without using them, causing Go compiler unused import failures.
- **Resolution**: Cleaned import list to strictly used packages (`"context"` and `"sync"`).
- **Verification**: Enforced in `test_concurrency_and_security_code_soundness`.

### Finding 18: SecAgg Pedagogical Disclaimer (Astra)
- **Observation**: The 31-bit Mersenne prime ($2^{31}-1$) in the SecAgg snippet is subject to discrete-log table recovery.
- **Resolution**: Added explicit code comments and conceptual disclaimers explaining that $2^{31}-1$ is used strictly for pedagogical illustration, and production systems must use RFC 3526 MODP groups (2048/3072-bit) or Curve25519 (X25519).

### Finding 19: Gaussian Mechanism Condition & RDP History Bound (Astra, Sol, Claude)
- **Observation**: The Gaussian noise standard analytic formula $\sigma \ge \frac{\Delta_2 f \sqrt{2\ln(1.25/\delta)}}{\epsilon}$ requires $\epsilon \in (0, 1)$ to guarantee the target $\delta$. Adaptive RDP composition requires bounding each step uniformly over all prior histories.
- **Resolution**: Updated `privacy-engineering/differential-privacy/fundamentals.md` to state the $\epsilon \in (0, 1)$ restriction and explain numerical calibration (Balle & Wang 2018) for $\epsilon \ge 1$. Formulated RDP adaptive composition with the uniform history supremum: $\sup_{a_{1:i-1}} D_\alpha(\mathcal{M}_i(D, a_{1:i-1}) \parallel \mathcal{M}_i(D', a_{1:i-1})) \le \varepsilon_i(\alpha) \implies D_\alpha(\mathcal{M}_{1:k}) \le \sum \varepsilon_i(\alpha)$ (Mironov 2017, Proposition 1).
- **Verification**: Tested in `test_mathematical_invariants_rigor`.

### Finding 20: Role Track Alignment (Claude)
- **Observation**: `security/authn-authz` and `security/threat-modeling` were missing Track 2 (Privacy Engineer), and `system-design/rust` was missing Track 3 (Security Engineer).
- **Resolution**: Added Track 2 to both security topics and Track 3 to Rust.
- **Verification**: Enforced in `test_grounded_references_and_role_tracks`.

### Finding 21: Interview Calibration Language & Tone (Claude)
- **Observation**: README links described "recent verified tier-1 interview calibrations" without public proof, and company calibrations contained unsourced claims (e.g. Netflix "billions of RPC checks").
- **Resolution**: Removed the word "verified" from all topic README reference links and toned down unverified operational metrics.

---

## 4. Verification Evidence

### Pytest Suite Execution
```bash
$ cd /home/will/dev/learn/.worktrees/curricula
$ .venv/bin/pytest app/tests/ -v
============================= test session starts ==============================
platform linux -- Python 3.13.12, pytest-9.2.0, pluggy-1.7.0 -- /home/will/dev/learn/.worktrees/curricula/.venv/bin/python3
rootdir: /home/will/dev/learn/.worktrees/curricula
configfile: pyproject.toml
plugins: anyio-4.16.0, asyncio-1.4.1.post1, cov-7.1.0
collected 23 items

app/tests/test_curricula_integrity.py::test_all_four_domains_exist_with_valid_readmes PASSED [  4%]
app/tests/test_curricula_integrity.py::test_all_eleven_priority_topics_exist_with_five_artifacts PASSED [  8%]
app/tests/test_curricula_integrity.py::test_references_yaml_schema_validity PASSED [ 13%]
app/tests/test_curricula_integrity.py::test_rubrics_cover_all_dimensions_and_levels PASSED [ 17%]
app/tests/test_curricula_integrity.py::test_exercises_contain_all_four_tiers PASSED [ 21%]
app/tests/test_curricula_integrity.py::test_no_hyphenated_exercise_files PASSED [ 26%]
app/tests/test_curricula_integrity.py::test_root_topic_aliases_and_symlinks_resolve PASSED [ 30%]
app/tests/test_curricula_integrity.py::test_zanzibar_citation_publisher_fidelity PASSED [ 34%]
app/tests/test_curricula_integrity.py::test_mathematical_invariants_rigor PASSED [ 39%]
app/tests/test_curricula_integrity.py::test_concurrency_and_security_code_soundness PASSED [ 43%]
app/tests/test_curricula_integrity.py::test_grounded_references_and_role_tracks PASSED [ 47%]
app/tests/test_foundation.py::test_app_package_imports_cleanly PASSED    [ 52%]
app/tests/test_foundation.py::test_settings_defaults PASSED              [ 56%]
app/tests/test_foundation.py::test_healthz_endpoint PASSED               [ 60%]
app/tests/test_foundation.py::test_api_status_endpoint PASSED            [ 65%]
app/tests/test_foundation.py::test_api_status_endpoint_auth_token_enforcement PASSED [ 69%]
app/tests/test_foundation.py::test_personal_state_store_resolves_outside_repository_by_default PASSED [ 73%]
app/tests/test_foundation.py::test_xdg_data_home_resolution PASSED       [ 78%]
app/tests/test_foundation.py::test_rejection_of_in_repo_data_dir PASSED  [ 82%]
app/tests/test_foundation.py::test_rejection_of_in_repo_data_dir_via_env PASSED [ 86%]
app/tests/test_foundation.py::test_rejection_of_in_repo_xdg_data_home_via_env PASSED [ 91%]
app/tests/test_foundation.py::test_api_status_endpoint_non_loopback_protects_data_dir PASSED [ 95%]
app/tests/test_foundation.py::test_clean_repository_invariant PASSED     [100%]

============================== 23 passed in 0.20s ==============================
```

### Opaque-Box E2E Runner Execution
```bash
$ python3 /home/will/dev/learn/tests_e2e/runner.py
================================================================================
        Savage-Fred/learn Independent Opaque-Box E2E Test Runner
================================================================================

▶ Running Tier 1: Feature Coverage (Happy-Path) (47 tests)
  ✔ Tier 1 Completed: 47/47 passed in 0.02s

▶ Running Tier 2: Boundary & Corner Cases (47 tests)
  ✔ Tier 2 Completed: 47/47 passed in 0.02s

▶ Running Tier 3: Cross-Feature Combinations (8 tests)
  ✔ Tier 3 Completed: 8/8 passed in 0.01s

▶ Running Tier 4: Real-World Multi-Turn Scenarios (5 tests)
  ✔ Tier 4 Completed: 5/5 passed in 0.00s

Total: 107/107 passed (0.08s)
✔ ALL 107 E2E TESTS PASSED CLEANLY (Exit Code: 0)
```
