# Authoritative References & Citations: Master's-Level Algorithms

This curriculum grounds all concepts, exercises, and rubrics in peer-reviewed academic literature, formal standards (RFCs, NIST, IETF), foundational textbooks, and verified tier-1 industry interview loops.

## Citable Bibliography

### Introduction to Algorithms (2022)
- **Authors**: Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest, Clifford Stein
- **Type**: `book`
- **Canonical URL / DOI**: [https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/](https://mitpress.mit.edu/9780262046305/introduction-to-algorithms/)
- **Role Relevance**: Track-1-SWE, Track-4-Research-Eng
- **Core Invariants Extracted**:
  - Potential method amortized analysis guarantees operational upper bounds.
  - Max-Flow Min-Cut Theorem establishes linear programming duality in graphs.
- **Interview Loop Calibration**:
  - *Target Company & Level*: Google / GDM (L5)
  - *Round*: Algorithmic Rigor
  - *Prompt Summary*: Given a directed graph of server capacities and network latencies, find the minimum-cost maximum-flow under dynamic edge cost updates.
  - *Expected Evaluation Signals*:
    - Formal proof of flow conservation and capacity constraints
    - Correct asymptotic runtime derivation in terms of V and E

```bibtex
@book{clrs2022algorithms,
  title={Introduction to Algorithms},
  author={Cormen, Thomas H and Leiserson, Charles E and Rivest, Ronald L and Stein, Clifford},
  year={2022},
  edition={4th},
  publisher={MIT Press}
}
```

### Algorithm Design (2005)
- **Authors**: Jon Kleinberg, Éva Tardos
- **Type**: `book`
- **Canonical URL / DOI**: [https://www.pearson.com/en-us/subject-catalog/p/algorithm-design/P200000003260](https://www.pearson.com/en-us/subject-catalog/p/algorithm-design/P200000003260)
- **Role Relevance**: Track-1-SWE, Track-4-Research-Eng
- **Core Invariants Extracted**:
  - Bipartite matching and baseball elimination reduce to Max-Flow.
  - Reduction from 3-SAT to independent set proves NP-completeness.
- **Interview Loop Calibration**:
  - *Target Company & Level*: Meta (L5)
  - *Round*: Speed Coding
  - *Prompt Summary*: Solve maximum bipartite matching with worker preferences and task capacities.
  - *Expected Evaluation Signals*:
    - Reduces problem to max-flow with source/sink supernodes
    - Implements working Dinic or Ford-Fulkerson within 30 minutes

```bibtex
@book{kleinberg2005algorithm,
  title={Algorithm Design},
  author={Kleinberg, Jon and Tardos, \'Eva},
  year={2005},
  publisher={Addison-Wesley}
}
```
