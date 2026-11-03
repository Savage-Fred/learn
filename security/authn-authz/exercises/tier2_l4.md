# Exercise TIER2_L4: OAuth 2.1 Authorization Code Flow with PKCE

**Objective**: Implement the complete client-side PKCE generation and server-side token exchange verification.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `google-zanzibar-2019`, `oauth-2-1-draft`
- **Applicable Citations**:
  - [Zanzibar: Google’s Consistent, Global Authorization System](https://www.usenix.org/conference/atc19/presentation/pang) (2019)
  - [The OAuth 2.1 Authorization Framework](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/) (2024)

---

## Problem Statement

Implement two functions: `generate_pkce_pair() -> Tuple[str, str]` (returning verifier and challenge), and `exchange_code_for_token(auth_code: str, code_verifier: str, stored_challenges: dict) -> dict`. The server must verify that the SHA256 hash of the verifier matches the stored code_challenge, invalidate the code immediately, and issue access + refresh tokens.

---

## Formal Constraints

- Code verifier: 43-128 characters of unreserved URL-safe characters.
- Code challenge: Base64URL(SHA256(code_verifier)).
- Code expiration: Authorization codes valid for max 60 seconds and single use only.

---

## Starter Code

```python
from typing import Tuple

def generate_pkce_pair() -> Tuple[str, str]:
    # TODO: Generate verifier and SHA256 challenge
    pass

def exchange_code_for_token(auth_code: str, code_verifier: str, stored_auth_codes: dict) -> dict:
    # TODO: Verify challenge, invalidate auth_code, return tokens
    pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Valid code_verifier matching stored challenge succeeds and returns access_token.
- [ ] **Test Case**: Replaying the same auth_code twice fails with 400 InvalidGrant.
- [ ] **Test Case**: Mismatched code_verifier fails with 400 InvalidGrant.

---

## Solution & Invariant Check

Generates cryptographically secure random bytes for verifier; computes SHA256; deletes auth_code on first exchange attempt.