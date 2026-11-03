# Exercise TIER4_L6: Zero-Copy Multi-Worker Shared Memory IPC Ring Buffer

**Objective**: Architect a zero-copy shared memory IPC ring buffer for streaming PyTorch tensor chunks between multiple worker processes without serialization overhead.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `ramalho-fluent-python-2022`, `pep-544-protocols`, `slatkin-effective-python-2019`
- **Applicable Citations**:
  - [Fluent Python: Clear, Concise, and Effective Programming](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/) (2022)
  - [PEP 544 – Protocols: Structural subtyping (static duck typing)](https://peps.python.org/pep-0544/) (2018)
  - [Effective Python: 90 Specific Ways to Write Better Python](https://effectivepython.com/) (2019)

---

## Problem Statement

Design and implement `SharedMemoryRingBuffer`. The producer writes high-dimensional float32 arrays into pre-allocated shared memory slots. Multiple consumer worker processes read batches with zero serialization overhead. Implement lock-free sequence pointers, consumer heartbeat liveness tracking, and automatic lease recovery if a consumer terminates unexpectedly.

---

## Formal Constraints

- Memory overhead: Zero-copy using multiprocessing.shared_memory and memoryview.
- Concurrency: Lock-free atomic sequence numbering using shared atomic integers or POSIX semaphores.
- Crash resilience: If a worker process crashes abruptly (SIGKILL), the ring buffer must detect dead workers and recover without deadlocking producers.

---

## Starter Code

```python
from multiprocessing import shared_memory
import numpy as np

class SharedMemoryRingBuffer:
    def __init__(self, name: str, slot_count: int, slot_size_bytes: int, create: bool = False):
        self.name = name
        self.slot_count = slot_count
        self.slot_size_bytes = slot_size_bytes
        # TODO: Setup shared memory block and control structures

    def write_tensor(self, array: np.ndarray) -> int:
        """Write array directly into next available ring buffer slot."""
        pass

    def read_tensor(self, slot_id: int) -> np.ndarray:
        """Read array using memoryview without copying bytes."""
        pass

    def recover_dead_consumers(self) -> None:
        """Detect crashed consumers and advance sequence markers."""
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Producer and 4 consumers transfer 1GB of tensor data with zero memory copies.
- [ ] **Test Case**: Kill consumer worker with SIGKILL; assert producer continues writing without deadlock.
- [ ] **Test Case**: Verify memoryview references do not leak or corrupt underlying buffer slots.

---

## Solution & Invariant Check

Pre-allocates a single contiguous multiprocessing.shared_memory.SharedMemory block divided into header metadata (atomic sequence counters, heartbeat timestamps) and fixed-stride payload slots.