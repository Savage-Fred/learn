# Authoritative References & Citations: Privacy-Enhancing Technologies (PETs) for AI

This curriculum grounds all concepts, exercises, and rubrics in peer-reviewed academic literature, formal standards (RFCs, NIST, IETF), foundational textbooks, and verified tier-1 industry interview loops.

## Citable Bibliography

### Membership Inference Attacks Against Machine Learning Models (2017)
- **Authors**: Reza Shokri, Marco Stronati, Congzheng Song, Vitaly Shmatikov
- **Type**: `paper`
- **Canonical URL / DOI**: [https://ieeexplore.ieee.org/document/7958568](https://ieeexplore.ieee.org/document/7958568)
- **Role Relevance**: Track-2-Privacy, Track-4-Research-Eng
- **Core Invariants Extracted**:
  - Overfitting in machine learning models directly leaks membership information.
  - Shadow models trained on similar data distributions accurately predict membership.
- **Interview Loop Calibration**:
  - *Target Company & Level*: Apple (L6)
  - *Round*: Privacy Engineering Architecture
  - *Prompt Summary*: Design the privacy verification and attestation pipeline for an offloaded LLM inference cluster guaranteeing zero data retention and verifiable transparency logs.
  - *Expected Evaluation Signals*:
    - Delineates cryptographic TEE attestation from heuristic privacy policies
    - Applies membership inference auditing on fine-tuned model artifacts

```bibtex
@inproceedings{shokri2017membership,
  title={Membership Inference Attacks Against Machine Learning Models},
  author={Shokri, Reza and Stronati, Marco and Song, Congzheng and Shmatikov, Vitaly},
  booktitle={IEEE Symposium on Security and Privacy (SP)},
  pages={3--18},
  year={2017}
}
```

### Extracting Training Data from Large Language Models (2021)
- **Authors**: Nicholas Carlini, Florian Tramèr, Eric Wallace, Matthew Jagielski, Ariel Herbert-Voss
- **Type**: `paper`
- **Canonical URL / DOI**: [https://www.usenix.org/conference/usenixsecurity21/presentation/carlini-extracting](https://www.usenix.org/conference/usenixsecurity21/presentation/carlini-extracting)
- **Role Relevance**: Track-2-Privacy, Track-4-Research-Eng
- **Core Invariants Extracted**:
  - LLMs memorize training data verbatim across large model scales.
  - Perplexity ratio comparisons between base and zlib-compressed text reveal memorized PII.
- **Interview Loop Calibration**:
  - *Target Company & Level*: OpenAI (L5)
  - *Round*: AI Safety & Privacy Systems
  - *Prompt Summary*: Explain how training data extraction attacks exploit memorization in LLMs and evaluate mitigations during pre-training vs post-training.
  - *Expected Evaluation Signals*:
    - Articulates deduplication of training datasets as the highest-leverage defense
    - Analyzes DP-SGD trade-offs on model perplexity and training throughput

```bibtex
@inproceedings{carlini2021extracting,
  title={Extracting Training Data from Large Language Models},
  author={Carlini, Nicholas and Tram{\`e}r, Florian and Wallace, Eric and Jagielski, Matthew and Herbert-Voss, Ariel and others},
  booktitle={USENIX Security Symposium},
  pages={2633--2650},
  year={2021}
}
```

### Practical Secure Aggregation for Privacy-Preserving Machine Learning (2017)
- **Authors**: Keith Bonawitz, Vladimir Ivanov, Ben Kreuter, Antonio Marcedone
- **Type**: `paper`
- **Canonical URL / DOI**: [https://dl.acm.org/doi/10.1145/3133956.3133982](https://dl.acm.org/doi/10.1145/3133956.3133982)
- **Role Relevance**: Track-2-Privacy, Track-4-Research-Eng
- **Core Invariants Extracted**:
  - Pairwise masking guarantees zero server visibility of individual client updates.
  - Threshold Shamir secret sharing resolves mobile client dropout without breaking aggregation.
- **Interview Loop Calibration**:
  - *Target Company & Level*: Google / GDM (L5)
  - *Round*: Distributed Cryptographic Protocols
  - *Prompt Summary*: Design a federated learning aggregation protocol that protects mobile device gradients from an honest-but-curious server.
  - *Expected Evaluation Signals*:
    - Applies SecAgg protocol with Diffie-Hellman key exchange
    - Addresses client dropouts via Shamir secret sharing

```bibtex
@inproceedings{bonawitz2017practical,
  title={Practical Secure Aggregation for Privacy-Preserving Machine Learning},
  author={Bonawitz, Keith and Ivanov, Vladimir and Kreuter, Ben and Marcedone, Antonio and others},
  booktitle={ACM CCS},
  pages={1175--1191},
  year={2017}
}
```
