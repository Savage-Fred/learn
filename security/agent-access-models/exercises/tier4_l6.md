# Exercise TIER4_L6: Multi-Tenant Ephemeral MicroVM Sandbox Platform

**Objective**: Architect a production-grade sandboxed execution platform for autonomous agent swarms running untrusted code with eBPF egress filtering and sub-100ms startup.

---

## Problem Statement

Design and architect `AgentSandboxPlatform`. Manage a pool of warm microVMs. When an agent requests code execution, lease an ephemeral microVM, mount a temporary scratch workspace, execute the payload under strict CPU/RAM cgroups, stream stdout/stderr, enforce eBPF egress blocking against private IP ranges, and destroy the microVM on completion.

---

## Formal Constraints

- Startup latency: < 50ms warm sandbox acquisition.
- Isolation: MicroVM (Firecracker) or kernel-isolated container (gVisor) with read-only rootfs.
- Egress policy: Default-deny; allow-listed external domains only via eBPF or forward proxy; zero access to cloud metadata (169.254.169.254).

---

## Starter Code

```python
class AgentSandboxPlatform:
    def __init__(self, pool_size: int = 10, memory_limit_mb: int = 256):
        self.pool_size = pool_size
        self.memory_limit_mb = memory_limit_mb
        # TODO: Initialize warm pool of microVM / container instances

    def execute_payload(self, agent_id: str, code_payload: str, timeout_seconds: int = 10) -> dict:
        """Acquire warm sandbox, execute payload with egress filters, recycle VM."""
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Executes Python data science script and returns correct stdout within memory limit.
- [ ] **Test Case**: Attempting network call to 169.254.169.254 is rejected with NetworkUnreachable.
- [ ] **Test Case**: Fork bomb or infinite loop terminated cleanly after timeout_seconds without affecting other tenants.

---

## Solution & Invariant Check

Pre-warmed pool of microVMs; seccomp profile disables ptrace and raw sockets; network namespace routed through veth pair with eBPF egress filter blocking RFC1918 and link-local ranges; cgroups enforce 256MB hard limit.