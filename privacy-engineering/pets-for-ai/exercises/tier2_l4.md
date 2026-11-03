# Exercise TIER2_L4: Secure Aggregation with Shamir's Secret Sharing for 5 Simulated Clients

**Objective**: Implement the complete Secure Aggregation protocol using Diffie-Hellman pairwise masking and Shamir's Secret Sharing to handle 1 client dropout.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `shokri-mia-2017`, `carlini-extracting-training-data-2021`, `bonawitz-secagg-2017`
- **Applicable Citations**:
  - [Membership Inference Attacks Against Machine Learning Models](https://ieeexplore.ieee.org/document/7958568) (2017)
  - [Extracting Training Data from Large Language Models](https://www.usenix.org/conference/usenixsecurity21/presentation/carlini-extracting) (2021)
  - [Practical Secure Aggregation for Privacy-Preserving Machine Learning](https://dl.acm.org/doi/10.1145/3133956.3133982) (2017)

---

## Problem Statement

Implement `simulate_secure_aggregation(clients: list, dropped_client_id: int) -> np.ndarray`. Clients generate pairwise masks and share Shamir secret shares of their seeds. When client `dropped_client_id` drops out, the server collects secret shares of the dropped client's seed from surviving clients, reconstructs the missing masks, subtracts them, and outputs the exact sum of gradients of surviving clients.

---

## Formal Constraints

- Clients: 5 mobile clients, each holding a 10-dimensional gradient vector.
- Dropout tolerance: 1 client drops out before sending masked gradient.
- Zero-knowledge: The server must learn nothing about individual client vectors.

---

## Starter Code

```python
class SecureAggregationSimulation:
    def run_protocol(self, client_gradients: dict, dropped_client: int) -> np.ndarray:
        # TODO: Execute pairwise masking, Shamir share distribution, dropout recovery
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Aggregate vector matches exact mathematical sum of 4 surviving client gradients.
- [ ] **Test Case**: Server memory dump contains only masked values and reconstructed seeds of dropped clients.
- [ ] **Test Case**: No individual gradient of surviving clients is revealed.

---

## Solution & Invariant Check

Pairwise zero-sum masks cancel for surviving pairs; Shamir Lagrange interpolation reconstructs dropped client's masks to subtract them from aggregate.