# Exercise TIER3_L5: RFC 8693 OAuth 2.0 Token Exchange for Multi-Agent Workflows

**Objective**: Implement an RFC 8693 token exchange service that attenuates user tokens into scoped, ephemeral subagent tokens.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `hardy-confused-deputy-1988`, `rfc-8693-token-exchange`
- **Applicable Citations**:
  - [The Confused Deputy: (or why capabilities might have been invented)](https://dl.acm.org/doi/10.1145/54289.848243) (1988)
  - [RFC 8693: OAuth 2.0 Token Exchange](https://datatracker.ietf.org/doc/html/rfc8693) (2020)

---

## Problem Statement

Implement `TokenExchangeService`. Support `exchange_token(subject_token: str, actor_token: str, requested_scope: List[str], ttl_seconds: int) -> str`. Validate both tokens, ensure requested_scope is a subset of subject_token scope, and mint a new JWT with `act` (actor) claim representing the subagent delegation chain.

---

## Formal Constraints

- Token exchange: Client presents user session token and requests down-scoped token.
- Claims: Downstream token must include subject_token (user) and actor_token (calling agent).
- Scope monotonicity: Requested scope must be a strict subset of user token scope.

---

## Starter Code

```python
class TokenExchangeService:
    def __init__(self, signing_key: bytes, jwks: dict):
        self.key = signing_key
        self.jwks = jwks

    def exchange_token(self, subject_token: str, actor_token: str, 
                       requested_scope: list, ttl_seconds: int = 300) -> str:
        # TODO: Validate tokens, assert scope subset, mint attenuated token with act claim
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Valid exchange produces new token with attenuated scope and nested 'act' claim.
- [ ] **Test Case**: Attempting to escalate scope (requesting 'admin' when user token only has 'read') raises ScopeEscalationError.
- [ ] **Test Case**: Invalid or expired subject token raises AuthenticationError.

---

## Solution & Invariant Check

Verifies both JWTs; checks set(requested_scope).issubset(set(subject_scope)); mints JWT with sub=user, act={'sub': actor_id}, scope=requested_scope.