# Topic: Master's-Level Algorithms

**Domain**: `leetcode`  
**Topic ID**: `algorithms`  
**Canonical Path**: `leetcode/algorithms/`

## Overview

Advanced algorithmic design and analysis covering amortized analysis (potential method), network flow duality, randomized tail bounds, advanced dynamic programming (Convex Hull Trick, D&C optimization), and graph decomposition (Tarjan SCC, 2-SAT, Heavy-Light Decomposition).

---

## Learning Objectives

- Prove algorithmic asymptotic bounds using the Potential Method of amortized analysis.
- Formulate and solve combinatorial optimization problems using Max-Flow Min-Cut and Push-Relabel algorithms.
- Analyze randomized algorithms and derive failure probability bounds using Markov, Chebyshev, and Chernoff/Hoeffding inequalities.
- Optimize dynamic programming transitions from O(N^2) to O(N log N) or O(N) using the Convex Hull Trick and Divide & Conquer optimization.
- Decompose complex dependency and tree queries using Tarjan Strongly Connected Components (SCC), 2-SAT, and Heavy-Light Decomposition (HLD).

## Prerequisite Knowledge Graph

- CLRS undergraduate algorithms (Dijkstra, BFS/DFS, basic Dynamic Programming, Master Theorem).
- Probability theory (expectation, variance, conditional probability).
- Graph theory fundamentals (directed graphs, trees, cuts).

---

## Role Track Relevance

### Track 1: FAANG SWE + AI Lab SWE (L5/L6)
- **Focus & Competencies**: Theoretical rigor, asymptotic proofs, network flow optimization, and distributed dispatching.

### Track 4: AI Lab Research Engineer (non-PhD) (L4/L5)
- **Focus & Competencies**: Optimal tensor placement, graph partitioning for distributed training, and randomized sampling algorithms.

---

## Company Profiles & Cultural Bars (The 7 Notable Companies)

### Google / GDM
- **Technical Focus**: CLRS-level theoretical proofs, formal asymptotic bounds, min-cost max-flow duality, and edge-case invariants.
- **Observable Evaluation Signals**:
  - Formal mathematical proofs
  - Clear algorithmic invariants
  - Flawless graph reductions

### OpenAI
- **Technical Focus**: Fast algorithmic implementation, applying flow/matching algorithms to practical token routing and cluster scheduling.
- **Observable Evaluation Signals**:
  - Clean, bug-free implementation
  - Quick edge-case identification
  - Practical complexity bounds

### Anthropic
- **Technical Focus**: High code taste in algorithmic implementations, modular graph structures, and transparent complexity justification.
- **Observable Evaluation Signals**:
  - Readable variable naming
  - Defensive graph cycle handling
  - Clean recursion/iteration

### Meta
- **Technical Focus**: Speed and precision: solving Hard problems (e.g. 2-SAT, max-flow) in under 35 minutes with working test cases.
- **Observable Evaluation Signals**:
  - Fast mental models
  - Immediate recurrence formulation
  - Bug-free execution

### Databricks
- **Technical Focus**: Query plan graph optimization, cost-based tree transformations, and dynamic programming over join orders.
- **Observable Evaluation Signals**:
  - Amortized complexity proofs
  - Bitmask optimization
  - Memory locality in graphs

### Netflix
- **Technical Focus**: Routing under dynamic capacity constraints, min-cost flow for streaming bitrate allocation across CDNs.
- **Observable Evaluation Signals**:
  - Trade-off analysis
  - Handling dynamic latency updates
  - Resilience to network partition

### Apple
- **Technical Focus**: Optimal resource scheduling under strict memory and energy constraints, exact versus approximate algorithms.
- **Observable Evaluation Signals**:
  - Space complexity minimization
  - Deterministic execution bounds
  - Numeric stability

---

## Standard 5-Artifact Topic Layout

1. **[Fundamentals](./fundamentals.md)**: Core axiomatic invariants, theoretical proofs, mental models, idiomatic code examples, architectural tradeoffs, and failure modes.
2. **[References (YAML)](./references.yaml)** & **[References (Markdown)](./references.md)**: Citable peer-reviewed literature (with DOIs/arXiv IDs), official standards/RFCs, foundational textbooks, and interview loop calibrations.
3. **[Evaluation Rubric](./rubric.md)**: L4 vs L5 vs L6 scoring criteria across the 5 dimensions (Decomposition, Technical Execution, Architecture, Resilience, Communication) matching `docs/ux-spec.md`.
4. **[Adaptive Exercises](./exercises/)**: Tiered problem sets spanning diagnostic starter, mid-level L4, senior L5, and staff L6.
5. **[Durable Learnings](./learnings/)**: Destination directory for user's durable notes and deep-dive captures.