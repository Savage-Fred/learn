# Exercise TIER3_L5: Encrypted Neural Network Inference via CKKS Homomorphic Encryption

**Objective**: Design an encrypted inference service that evaluates a linear model and polynomial activation function over CKKS-encrypted vectors without decrypting data.

---

## Problem Statement

Implement `EncryptedInferenceService`. Client encrypts input feature vector `x` under its public key. Server evaluates `y = W * x + b` followed by polynomial activation `y^2` using homomorphic addition, multiplication, and relinearization. Server returns encrypted ciphertext `c_out`. Client decrypts `c_out` with private key and verifies result matches plaintext calculation within epsilon tolerance.

---

## Formal Constraints

- Encryption scheme: CKKS approximate homomorphic encryption (simulated or via TenSEAL/SEAL).
- Polynomial approximation: Replace ReLU activation with square activation: f(x) = x^2.
- Noise budget: Ensure noise does not exhaust before final decryption.

---

## Starter Code

```python
class EncryptedInferenceService:
    def __init__(self, weights: np.ndarray, bias: np.ndarray):
        self.weights = weights
        self.bias = bias

    def evaluate_encrypted(self, encrypted_vector) -> object:
        # TODO: Homomorphic matrix-vector multiply and squaring
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Decrypted output matches plaintext dot product within 1e-4 numeric tolerance.
- [ ] **Test Case**: Server operates purely on ciphertext without access to client private key.
- [ ] **Test Case**: Noise scale remains within ciphertext modulus bounds.

---

## Solution & Invariant Check

Ciphertext-plaintext multiplication W * c_x; homomorphic addition + c_b; homomorphic squaring c * c with relinearization.