# Exercise TIER2_L4: Agent Policy Evaluation Proxy with Parameter Constraints

**Objective**: Build a policy evaluation proxy that intercepts agent tool calls and enforces parameter schemas, rate limits, and allowed actions.

---

## Problem Statement

Implement `AgentToolProxy`. When the agent requests a tool call via `invoke(tool_name: str, arguments: dict) -> dict`, the proxy checks against session rate limits, validates argument types against registered JSON schemas, checks shell commands against dangerous patterns, and executes the underlying tool only if policy passes.

---

## Formal Constraints

- Validation: Schema enforcement for tool arguments.
- Rate limiting: Maximum 10 tool invocations per minute per agent session.
- Safety: Prohibits system commands matching blacklist (e.g. 'rm -rf', 'curl | bash').

---

## Starter Code

```python
class AgentToolProxy:
    def __init__(self, allowed_schemas: dict, rate_limit_rpm: int = 10):
        self.schemas = allowed_schemas
        self.rate_limit_rpm = rate_limit_rpm
        # TODO: Initialize rate limiting tracking

    def invoke(self, session_id: str, tool_name: str, args: dict):
        # TODO: Enforce policy, rate limits, and argument validation
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Valid tool call executes and returns tool output.
- [ ] **Test Case**: Exceeding 10 calls in 60 seconds raises RateLimitExceeded error.
- [ ] **Test Case**: Command injection attempt ('cat file; rm -rf /') is blocked and raises SecurityViolation.

---

## Solution & Invariant Check

Sliding-window counter for session rate limits; regex check for command chaining characters (; && || | ` $); schema type validation.