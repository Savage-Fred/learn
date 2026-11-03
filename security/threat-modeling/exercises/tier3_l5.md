# Exercise TIER3_L5: Defense-in-Depth for an Autonomous Customer Support Agent

**Objective**: Formulate a comprehensive security architecture for an autonomous agent with database refund and email sending tools, mitigating prompt injection and SSRF.

---

## Problem Statement

Design the end-to-end security architecture for an autonomous customer support agent. Customer submits arbitrary text in chat. The agent can invoke tools: `issue_refund(order_id, amount)` and `send_email(to, subject, body)`. Specify: (1) Prompt boundary segregation, (2) Parameter validation and business policy invariants, (3) SSRF and payload injection defenses, and (4) Human-in-the-loop escalation rules for anomalies.

---

## Formal Constraints

- Agent capabilities: Query customer orders, issue refunds up to $500, send confirmation emails.
- Risk profile: Customer chat input is completely untrusted and adversarial.

---

## Starter Code

```python
class CustomerSupportAgentSecurity:
    def validate_incoming_message(self, message: str) -> bool:
        pass

    def authorize_tool_call(self, customer_id: str, tool_name: str, args: dict) -> bool:
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Rejects prompt injection attempting to refund an order owned by a different customer.
- [ ] **Test Case**: Caps refund at maximum $500 threshold and triggers supervisor review for > $100.
- [ ] **Test Case**: Sanitizes email body to prevent HTML injection / phishing links.

---

## Solution & Invariant Check

Tool calls strictly validate that order_id belongs to authenticated customer_id; refunds > $100 require human supervisor approval; email recipient forced to customer's verified account email.