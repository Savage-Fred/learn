# Exercise TIER4_L6: Frontier Model Weight Hosting Threat Model & Exfiltration Mitigations

**Objective**: Develop a comprehensive threat model for hosting frontier AI model weights on multi-cloud GPU infrastructure against state-sponsored adversaries and insider threats.

---

## Problem Statement

Architect the security infrastructure protecting model weights stored in cloud storage and loaded into GPU memory. Detail: (1) Cryptographic key management and envelope encryption (KMS + hardware security modules), (2) Confidential Computing and TEE remote attestation before decryption, (3) Ephemeral GPU memory scrubbing on pod eviction, (4) Out-of-band network exfiltration detection (eBPF egress watermarking), and (5) Dual-custody multi-party approvals for weight export.

---

## Formal Constraints

- Asset: Proprietary frontier model weights worth > $100M.
- Adversary: Advanced Persistent Threat (APT) with cloud provider insider capabilities and compromised developer credentials.
- Availability SLA: 99.99% inference serving availability across 10,000 H100 GPUs.

---

## Starter Code

```python
class ModelWeightSecurityArchitecture:
    def verify_gpu_enclave(self, node_attestation_report: bytes) -> bool:
        """Verify NVIDIA H100 Confidential Computing attestation report."""
        pass

    def authorize_weight_decryption(self, session_credentials: list) -> bytes:
        """Enforce m-of-n Shamir secret sharing / dual-custody authorization."""
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Rejects weight decryption if node attestation signature does not match NVIDIA root of trust.
- [ ] **Test Case**: Blocks weight exfiltration via eBPF egress bandwidth throttling and alert generation.
- [ ] **Test Case**: Proves zero plaintext weights touch unencrypted NVMe or non-volatile storage.

---

## Solution & Invariant Check

Weights encrypted at rest with per-cluster ephemeral keys; decrypted directly into H100 protected memory only after remote attestation verification; network egress completely disabled on GPU worker nodes.