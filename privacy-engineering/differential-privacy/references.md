# Authoritative References & Citations: Modern Differential Privacy

This curriculum grounds all concepts, exercises, and rubrics in peer-reviewed academic literature, formal standards (RFCs, NIST, IETF), foundational textbooks, and verified tier-1 industry interview loops.

## Citable Bibliography

### The Algorithmic Foundations of Differential Privacy (2014)
- **Authors**: Cynthia Dwork, Aaron Roth
- **Type**: `book`
- **Canonical URL / DOI**: [https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf](https://www.cis.upenn.edu/~aaroth/Papers/privacybook.pdf)
- **Role Relevance**: Track-2-Privacy, Track-4-Research-Eng
- **Core Invariants Extracted**:
  - Definition of (ε, δ)-Differential Privacy.
  - Laplace mechanism calibrated to L1 sensitivity.
  - Post-processing invariance: Any computation on a DP output remains DP.
- **Interview Loop Calibration**:
  - *Target Company & Level*: Google / GDM (L6)
  - *Round*: Privacy Theory & Systems Architecture
  - *Prompt Summary*: Prove that the Laplace mechanism satisfies pure ε-differential privacy, and derive the optimal noise scale for counting queries.
  - *Expected Evaluation Signals*:
    - Formal proof using probability density ratio bounds
    - Calculates sensitivity of counting queries as Delta = 1

```bibtex
@book{dwork2014algorithmic,
  title={The Algorithmic Foundations of Differential Privacy},
  author={Dwork, Cynthia and Roth, Aaron},
  year={2014},
  publisher={Foundations and Trends in Theoretical Computer Science}
}
```

### Deep Learning with Differential Privacy (2016)
- **Authors**: Martin Abadi, Andy Chu, Ian Goodfellow, H. Brendan McMahan, Ilya Mironov, Kunal Talwar, Li Zhang
- **Type**: `paper`
- **Canonical URL / DOI**: [https://dl.acm.org/doi/10.1145/2976749.2978318](https://dl.acm.org/doi/10.1145/2976749.2978318)
- **Role Relevance**: Track-2-Privacy, Track-4-Research-Eng
- **Core Invariants Extracted**:
  - Per-sample gradient clipping bounds L2 sensitivity to C.
  - Moments Accountant bounds cumulative privacy loss under Gaussian perturbation.
- **Interview Loop Calibration**:
  - *Target Company & Level*: OpenAI (L5)
  - *Round*: Research Engineering & Privacy Systems
  - *Prompt Summary*: Design the training pipeline for differentially private fine-tuning of an LLM, explaining per-sample gradient clipping memory optimization.
  - *Expected Evaluation Signals*:
    - Articulates why standard backpropagation computes batch-averaged gradients
    - Explains Ghost Clipping or Opacus micro-batching optimizations

```bibtex
@inproceedings{abadi2016deep,
  title={Deep Learning with Differential Privacy},
  author={Abadi, Martin and Chu, Andy and Goodfellow, Ian and McMahan, H Brendan and Mironov, Ilya and Talwar, Kunal and Zhang, Li},
  booktitle={ACM CCS},
  pages={308--318},
  year={2016}
}
```

### Rényi Differential Privacy (2017)
- **Authors**: Ilya Mironov
- **Type**: `paper`
- **Canonical URL / DOI**: [https://ieeexplore.ieee.org/document/8049725](https://ieeexplore.ieee.org/document/8049725)
- **Role Relevance**: Track-2-Privacy, Track-4-Research-Eng
- **Core Invariants Extracted**:
  - Rényi divergence of order alpha enables strict additive composition.
  - Conversion from (alpha, D_alpha)-RDP to (ε, δ)-DP provides optimal tail bounds.
- **Interview Loop Calibration**:
  - *Target Company & Level*: Apple (L6)
  - *Round*: Advanced Privacy Foundations
  - *Prompt Summary*: Explain why Rényi Differential Privacy provides strictly tighter composition bounds than Advanced Composition for Gaussian mechanisms.
  - *Expected Evaluation Signals*:
    - Proves linear additivity of Rényi divergence under independent mechanisms
    - Calculates conversion back to (ε, δ)-DP

```bibtex
@inproceedings{mironov2017renyi,
  title={R\'enyi Differential Privacy},
  author={Mironov, Ilya},
  booktitle={IEEE Computer Security Foundations Symposium (CSF)},
  pages={263--275},
  year={2017}
}
```
