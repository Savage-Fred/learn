# Evaluation Rubric & Calibration Guide: Master's-Level Algorithms

This rubric defines the scoring calibration for mock interview assessments, coding exercises, and technical design evaluations across five standardized dimensions.

## Seniority Level Overview

- **L4 (Mid-Level)**: Solves standard LeetCode Medium problems in 25-30 minutes; formulates correct DP state transitions; implements BFS/DFS and topological sort without hesitation.
- **L5 (Senior)**: Solves LeetCode Hard in 35-40 minutes; formulates potential functions for amortized analysis; solves network flow reductions and proves invariant correctness.
- **L6 (Staff / Principal)**: Formulates non-trivial reductions (e.g. 2-SAT, min-cut, CHT optimization); devises novel graph approximations; anticipates numeric stability and hardware cache locality in algorithms.

---

## The 5 Scoring Dimensions

### Dimension 1: Problem Decomposition & Invariant Formulation (Weight: 20%)
*Ability to formulate mathematical reductions and invariants (e.g. flow conservation, cut capacity, topological order).*

#### L4 (Mid-Level) Criteria
- Identifies standard graph or DP patterns from problem prompt.
- States base cases and termination conditions correctly.

#### L5 (Senior) Criteria
- Identifies network flow or 2-SAT reductions independently.
- Formulates formal DP recurrence and proves optimal substructure.

#### L6 (Staff) Criteria
- Proves duality bounds; formulates problem as convex hull lower envelope or min-cut partition.

#### Observable Anti-Patterns
- ❌ **Greedy Fallacy**: Applying a greedy heuristic without proving the matroid or exchange property.

---

### Dimension 2: Technical Execution & Code Craftsmanship (Weight: 25%)
*Clean, bug-free implementation of complex algorithmic structures (residual graphs, bitmasks, pointer coupling).*

#### L4 (Mid-Level) Criteria
- Writes clean, compilable code without syntax errors.
- Correctly manages index boundaries and off-by-one errors.

#### L5 (Senior) Criteria
- Implements Dinic or Tarjan cleanly with minimal auxiliary memory.
- Uses current-arc optimization and recursion stack safety.

#### L6 (Staff) Criteria
- Produces vectorized or iterative implementations avoiding recursion limits.
- Zero unnecessary object allocations in hot algorithmic loops.

#### Observable Anti-Patterns
- ❌ **Off-By-One Index Chaos**: Conflating 0-indexed and 1-indexed graph nodes leading to out-of-bounds panics.

---

### Dimension 3: Systems Architecture & Trade-Off Rigor (Weight: 25%)
*Rigorous analysis of time/space complexity and practical hardware performance.*

#### L4 (Mid-Level) Criteria
- Accurately calculates Big-O time and space complexity.
- Compares recursion depth to maximum call stack limits.

#### L5 (Senior) Criteria
- Differentiates between worst-case, average-case, and amortized complexity.
- Analyzes graph density impact on Dinic vs Push-Relabel.

#### L6 (Staff) Criteria
- Evaluates cache line locality of adjacency matrices vs compressed sparse rows (CSR).
- Explains practical convergence bounds of randomized algorithms.

#### Observable Anti-Patterns
- ❌ **Hand-Waving Complexity**: Guessing O(N log N) without analyzing inner loop dependencies.

---

### Dimension 4: Resilience, Security & Edge Case Posture (Weight: 15%)
*Handling of disconnected graphs, self-loops, negative cycles, and integer overflow.*

#### L4 (Mid-Level) Criteria
- Checks for empty inputs, single-node graphs, and disconnected components.
- Handles non-existent paths gracefully.

#### L5 (Senior) Criteria
- Detects and handles negative cycles and capacity saturation.
- Guards against 32-bit signed integer overflow in flow/cost accumulation.

#### L6 (Staff) Criteria
- Proves algorithm termination under pathological adversarial graph topologies.

#### Observable Anti-Patterns
- ❌ **Infinite Recursion on Cycles**: Failing to mark visited nodes before recursive DFS calls.

---

### Dimension 5: Communication & Calibration Level (Weight: 15%)
*Structured explanation of the solution, mathematical clarity, and responsiveness.*

#### L4 (Mid-Level) Criteria
- Clearly explains the step-by-step approach before coding.
- Walks through a dry-run test case accurately.

#### L5 (Senior) Criteria
- Explains why alternative approaches (e.g. pure DP vs network flow) fail or are suboptimal.
- Speaks fluently using formal mathematical concepts.

#### L6 (Staff) Criteria
- Engages with interviewer as a peer researcher; quickly adapts to modified constraints.

#### Observable Anti-Patterns
- ❌ **Silent Coding**: Writing code for 20 minutes without articulating intent or invariants.

---

## Composite Scoring Calibration

- **Score 1.0 – 2.4 (Below Bar / Not Passing)**: Deficient in core invariants; misses basic correctness constraints; unhandled runtime exceptions.
- **Score 2.5 – 3.4 (L4 Mid-Level Standard)**: Produces working, clean code; identifies edge cases with standard test inputs; needs scaffolding for multi-node tradeoffs.
- **Score 3.5 – 4.4 (L5 Senior Bar - Strong Hire)**: Formulates mathematical/architectural invariants up front; anticipates distributed failure modes; proves time/space bounds.
- **Score 4.5 – 5.0 (L6 Staff Bar - Exceptional)**: Strategic problem reframing; anticipates cascading failure and adversarial vectors; balances cross-cutting organizational invariants.