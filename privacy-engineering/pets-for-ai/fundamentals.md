# Core Fundamentals & Invariants: Privacy-Enhancing Technologies (PETs) for AI

This document articulates the axiomatic invariants, theoretical grounding, mental models, idiomatic code implementations, architectural tradeoffs, and failure modes governing this topic.

---

## 1. Axiomatic Core Invariants

### Invariant 1: Membership Inference Distinguishability Invariant
$$
\mathcal{A}_{MIA}(x, y; \theta) \text{ exploits } \mathcal{L}(f_\theta(x), y) \sim \mathcal{D}_{train} \text{ vs } \mathcal{D}_{test}. \quad \text{Advantage } \text{Adv} = 2 |\Pr[\text{Guess} = 1 \mid \text{In}] - 0.5|.
$$
**Implications & Guarantees**: Models that overfit display higher prediction confidence and lower loss on training records, enabling an adversary to distinguish members from non-members with high statistical confidence.

### Invariant 2: Homomorphic Addition and Multiplication Invariant (CKKS)
$$
\text{Dec}(c_1 \oplus c_2) \approx m_1 + m_2, \quad \text{Dec}(c_1 \otimes c_2) \approx m_1 \cdot m_2 \text{ within noise budget } B.
$$
**Implications & Guarantees**: Enables evaluation of polynomial activation functions directly over encrypted ciphertexts without decrypting data, bounded by multiplicative depth.

### Invariant 3: Secure Aggregation Zero-Sum Mask Invariant
$$
\sum_{i=1}^N y_i = \sum_{i=1}^N \left( x_i + \sum_{j > i} s_{i,j} - \sum_{j < i} s_{j,i} \right) = \sum_{i=1}^N x_i.
$$
**Implications & Guarantees**: Individual client vectors x_i are completely obscured by pairwise Diffie-Hellman masks s_{i,j}, but masks cancel out identically when summed across all surviving clients.

---

## 2. Core Mental Models

### Mental Model 1: The Spectrum of Privacy Technologies
Heuristic masking (anonymization, redaction) is fragile against linking attacks. Cryptographic PETs (SMPC, FHE, TEEs) protect data in use and computation. Statistical PETs (Differential Privacy) protect the output and bounding information leakage. True defense-in-depth combines cryptographic execution with differential privacy guarantees.

### Mental Model 2: Cryptographic Remote Attestation
Before sending sensitive data or model weights to a cloud server, the client challenges the hardware enclave (Intel SGX, AMD SEV, NVIDIA H100). The enclave signs a cryptographic measurement (SHA-256 hash of its initial memory and boot state) using a key fused into the hardware silicon, verifiable against the chipmaker's public PKI.

---

## 3. Idiomatic Code Examples

### Secure Aggregation with Pairwise Diffie-Hellman Zero-Sum Masks
```python
import numpy as np
import hashlib
from typing import List, Dict

class SecAggClient:
    def __init__(self, client_id: int, total_clients: int, private_seed: int):
        self.id = client_id
        self.total = total_clients
        self.private_seed = private_seed

    def generate_shared_mask(self, peer_id: int) -> np.ndarray:
        # Deterministic pairwise seed from shared secret
        low, high = min(self.id, peer_id), max(self.id, peer_id)
        seed_bytes = hashlib.sha256(f"shared:{low}:{high}".encode("utf-8")).digest()
        seed_int = int.from_bytes(seed_bytes[:4], "big")
        rng = np.random.default_rng(seed_int)
        # Random mask vector of dimension 4
        mask = rng.normal(0, 10.0, size=4)
        # Invariant: If self.id < peer_id, add mask; if self.id > peer_id, subtract mask
        return mask if self.id < peer_id else -mask

    def mask_gradient(self, raw_gradient: np.ndarray) -> np.ndarray:
        masked = raw_gradient.copy()
        for peer_id in range(self.total):
            if peer_id != self.id:
                masked += self.generate_shared_mask(peer_id)
        return masked

class SecAggServer:
    def aggregate(self, masked_vectors: List[np.ndarray]) -> np.ndarray:
        # Summing all masked vectors cancels all pairwise masks identically
        return np.sum(masked_vectors, axis=0)
```
**Analysis**: Demonstrates the core algebraic zero-sum invariant of Secure Aggregation: pairwise masks cancel out completely in the sum.

---

## 4. Architectural Tradeoffs

### Homomorphic Encryption (FHE/CKKS) vs Hardware TEEs
FHE provides mathematical security guarantees against arbitrary hardware physical compromise, but incurs a 1000x-10000x compute and memory overhead, limiting it to small models or linear operations. TEEs execute native unencrypted code at near-native speed on modern CPUs/GPUs, but rely on silicon manufacturer security and are vulnerable to physical side-channel and microarchitectural attacks (Spectre/Meltdown).

### Exact Machine Unlearning vs SISA Sharded Training
Exact machine unlearning requires retraining the entire model from scratch without the deleted user data (100% compliant, but computationally prohibitive for large foundation models). SISA (Sharded, Isolated, Sliced, Aggregated) trains independent models on data shards; deleting a user requires retraining only the single affected shard model and re-aggregating.

---

## 5. Common Failure Modes & Anti-Patterns

### Failure Mode 1: Client Dropout in Naive Secure Aggregation
- **Root Cause**: If a mobile client drops off the network after sending its masked gradient, its pairwise masks with other clients do not cancel out, permanently corrupting the aggregate model update.
- **Mitigation & Invariant Defense**: Use Shamir's secret sharing on client private seeds (Bonawitz et al. protocol), allowing surviving clients to reconstruct and subtract the dropped client's masks.

### Failure Mode 2: TEE Side-Channel Memory Access Leakage
- **Root Cause**: Although enclave memory is encrypted on the RAM bus, an untrusted host OS can monitor page fault patterns or cache line contention (Spectre-SGX), reconstructing private encryption keys or model weights.
- **Mitigation & Invariant Defense**: Use constant-time algorithms, oblivious RAM (ORAM), and hardware architectures with hardware-enforced memory encryption and cache partitioning.
