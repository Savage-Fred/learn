# Exercise TIER1_STARTER: HMAC-Signed Scoped Capability Token

**Objective**: Build an HMAC-SHA256 capability token issuer and validator that enforces method scoping and expiration.

---

## Problem Statement

Implement `mint_capability_token(secret_key: bytes, allowed_methods: List[str], ttl_seconds: int) -> str` and `verify_capability(token: str, secret_key: bytes, required_method: str) -> bool`. Token must serialize as Base64URL string containing payload and HMAC signature.

---

## Invariant Scaffolding & Guidance

- Token must be cryptographically signed with a secret key.
- Token payload contains token_id, allowed_methods, and expires_at.
- Validator must reject tokens if signature is invalid, method is not permitted, or token is expired.

---

## Starter Code

```python
from typing import List

def mint_capability_token(secret_key: bytes, allowed_methods: List[str], ttl_seconds: int) -> str:
    # TODO: Mint HMAC-signed token
    pass

def verify_capability(token_str: str, secret_key: bytes, required_method: str) -> bool:
    # TODO: Verify signature, expiration, and method permissions
    pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Token with allowed_methods=['read_file'] succeeds for 'read_file' and fails for 'delete_file'.
- [ ] **Test Case**: Expired token fails verification.
- [ ] **Test Case**: Tampered token payload fails signature verification.

---

## Solution & Invariant Check

Base64URL encoded JSON payload + HMAC-SHA256 digest; verifies signature using hmac.compare_digest; checks method in allowed list.