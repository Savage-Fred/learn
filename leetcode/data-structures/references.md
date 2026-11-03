# Authoritative References & Citations: Advanced Data Structures & Indexing

This curriculum grounds all concepts, exercises, and rubrics in peer-reviewed academic literature, formal standards (RFCs, NIST, IETF), foundational textbooks, and verified tier-1 industry interview loops.

## Citable Bibliography

### The Art of Multiprocessor Programming (2020)
- **Authors**: Maurice Herlihy, Nir Shavit, Victor Luchangco, Michael Spear
- **Type**: `book`
- **Canonical URL / DOI**: [https://www.sciencedirect.com/book/9780124159501/the-art-of-multiprocessor-programming](https://www.sciencedirect.com/book/9780124159501/the-art-of-multiprocessor-programming)
- **Role Relevance**: Track-1-SWE, Track-4-Research-Eng
- **Core Invariants Extracted**:
  - Lock-free Michael-Scott queues maintain consistency via cooperative CAS advancement.
  - ABA mitigation requires hazard pointers or epoch-based reclamation.
- **Interview Loop Calibration**:
  - *Target Company & Level*: Databricks (L5)
  - *Round*: Concurrency & Memory Systems
  - *Prompt Summary*: Implement an in-memory B+ Tree with optimistic lock coupling (latch crabbing) for high-concurrency read-heavy workloads.
  - *Expected Evaluation Signals*:
    - Articulates difference between reader-writer locks and lock crabbing
    - Avoids deadlocks during root-node splits

```bibtex
@book{herlihy2020art,
  title={The Art of Multiprocessor Programming},
  author={Herlihy, Maurice and Shavit, Nir and Luchangco, Victor and Spear, Michael},
  year={2020},
  edition={2nd},
  publisher={Morgan Kaufmann}
}
```

### Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs (2018)
- **Authors**: Yury A. Malkov, Dmitry A. Yashunin
- **Type**: `paper`
- **Canonical URL / DOI**: [https://ieeexplore.ieee.org/document/8594632](https://ieeexplore.ieee.org/document/8594632)
- **Role Relevance**: Track-1-SWE, Track-4-Research-Eng
- **Core Invariants Extracted**:
  - Multi-layer proximity graphs enable logarithmic O(log N) nearest neighbor search.
  - Heuristic edge selection maintains small-world navigability across high clustering.
- **Interview Loop Calibration**:
  - *Target Company & Level*: OpenAI (L5)
  - *Round*: Vector Search Systems
  - *Prompt Summary*: Design an approximate nearest neighbor index serving 10,000 queries per second over 50 million 1536-dimensional vectors.
  - *Expected Evaluation Signals*:
    - Proposes HNSW or IVF-PQ with quantitative RAM analysis
    - Explains trade-off between recall, index build time, and query latency

```bibtex
@article{malkov2018efficient,
  title={Efficient and robust approximate nearest neighbor search using Hierarchical Navigable Small World graphs},
  author={Malkov, Yury A and Yashunin, Dmitry A},
  journal={IEEE Transactions on Pattern Analysis and Machine Intelligence},
  volume={42},
  number={4},
  pages={824--836},
  year={2018},
  publisher={IEEE}
}
```
