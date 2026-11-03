# Exercise TIER1_STARTER: Cryptographic JWT Parser and Signature Validator

**Objective**: Build a secure JWT validator that parses headers, fetches JWKS public keys, verifies asymmetric signatures, and enforces claims.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `google-zanzibar-2019`, `oauth-2-1-draft`
- **Applicable Citations**:
  - [Zanzibar: Google’s Consistent, Global Authorization System](https://www.usenix.org/conference/atc19/presentation/pang) (2019)
  - [The OAuth 2.1 Authorization Framework](https://datatracker.ietf.org/doc/draft-ietf-oauth-v2-1/) (2024)

---

## Problem Statement

Implement `validate_jwt_token(token: str, jwks: dict, expected_iss: str, expected_aud: str) -> dict`. Parse header and payload; find matching key in `jwks` using `kid`; verify RS256 signature; assert `exp > now`, `iss == expected_iss`, and `aud == expected_aud`. Raise specific errors on verification failure.

---

## Invariant Scaffolding & Guidance

- Token must have exactly 3 dot-separated base64url segments.
- Algorithm in header must match allowed asymmetric algorithms (e.g. RS256).
- exp claim must be in the future; iss and aud must match expected strings.

---

## Starter Code

```python
def validate_jwt_token(token: str, jwks: dict, expected_iss: str, expected_aud: str) -> dict:
    # TODO: Implement secure token parsing and signature verification
    pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Valid token returns parsed payload dictionary.
- [ ] **Test Case**: Expired token raises TokenExpiredError.
- [ ] **Test Case**: Invalid signature or altered payload raises SignatureVerificationError.
- [ ] **Test Case**: Token with alg: none is rejected immediately.

---

## Solution & Invariant Check

Base64URL decodes header and payload; verifies signature using cryptography.hazmat RS256 public key; validates temporal claims.