# Core Fundamentals & Invariants: Pythonic Coding Patterns

This document articulates the axiomatic invariants, theoretical grounding, mental models, idiomatic code implementations, architectural tradeoffs, and failure modes governing this topic.

---

## 1. Axiomatic Core Invariants

### Invariant 1: Python Data Model Protocol Invariant
$$
Any object O satisfies protocol P if O implements the required dunder methods: \forall m \in \text{Methods}(P), \text{hasattr}(O, m) \land \text{callable}(\text{getattr}(O, m)). Subclassing is neither required nor idiomatic.
$$
**Implications & Guarantees**: Enables structural duck typing at runtime and compile-time verification via typing.Protocol.

### Invariant 2: Generator Memory Bound Invariant
$$
\forall N \in \mathbb{N}, \text{MemoryUsage}(\text{Stream}(N)) = O(1) \text{ auxiliary space under lazy generator evaluation}.
$$
**Implications & Guarantees**: Pipelines composed of generator expressions and itertools produce items on demand without loading full sequences into heap memory.

### Invariant 3: Asyncio Single-Threaded Non-Preemption Invariant
$$
\text{Coroutine execution between two } await \text{ expressions is strictly atomic with respect to other coroutines in the same thread}.
$$
**Implications & Guarantees**: Concurrency bugs arise exclusively across await boundaries; blocking synchronous system calls freeze the entire event loop.

---

## 2. Core Mental Models

### Mental Model 1: Everything is a Protocol, Not a Hierarchy
Rather than forcing rigid inheritance hierarchies (e.g., inheriting from abstract base classes), Python favors capabilities indicated by dunder protocols (__iter__, __enter__, __getitem__). Design interfaces around structural protocols.

### Mental Model 2: CPython Memory Arenas & Object Lifecycles
CPython manages memory via reference counting for immediate cleanup and a generational cyclic GC for circular references. Objects <= 512 bytes use PyMalloc pools and arenas. Custom classes without __slots__ carry a ~150-byte __dict__ overhead.

---

## 3. Idiomatic Code Examples

### Structural Protocol & Thread-Safe LRU Cache Decorator
```python
from typing import Protocol, TypeVar, runtime_checkable, Generic, Dict, Optional
import threading

T_co = TypeVar("T_co", covariant=True)

@runtime_checkable
class Streamable(Protocol[T_co]):
    def read_chunk(self, size: int) -> bytes: ...
    def is_eof(self) -> bool: ...

class Node:
    __slots__ = ("key", "val", "prev", "next")
    def __init__(self, key: str, val: bytes):
        self.key: str = key
        self.val: bytes = val
        self.prev: Optional["Node"] = None
        self.next: Optional["Node"] = None

class ThreadSafeBoundedCache:
    """O(1) LRU Cache with strict slots and reentrant thread locking."""
    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("Capacity must be positive")
        self.capacity = capacity
        self.lookup: Dict[str, Node] = {}
        self.head = Node("__head__", b"")
        self.tail = Node("__tail__", b"")
        self.head.next = self.tail
        self.tail.prev = self.head
        self._lock = threading.RLock()

    def _remove(self, node: Node) -> None:
        p, n = node.prev, node.next
        if p and n:
            p.next = n
            n.prev = p

    def _add_to_front(self, node: Node) -> None:
        first = self.head.next
        node.next = first
        node.prev = self.head
        if first:
            first.prev = node
        self.head.next = node

    def get(self, key: str) -> Optional[bytes]:
        with self._lock:
            node = self.lookup.get(key)
            if not node:
                return None
            self._remove(node)
            self._add_to_front(node)
            return node.val

    def put(self, key: str, val: bytes) -> None:
        with self._lock:
            if key in self.lookup:
                self._remove(self.lookup[key])
            node = Node(key, val)
            self.lookup[key] = node
            self._add_to_front(node)
            if len(self.lookup) > self.capacity:
                lru = self.tail.prev
                if lru and lru is not self.head:
                    self._remove(lru)
                    del self.lookup[lru.key]
```
**Analysis**: Demonstrates PEP 544 Protocol, __slots__ for memory optimization, and an O(1) doubly linked list LRU cache guarded by threading.RLock.

---

## 4. Architectural Tradeoffs

### __slots__ vs Dynamic Attribute Flexibility
Using __slots__ reduces instance memory by ~60-70% and speeds up attribute access by ~20%, but disables dynamic runtime attribute injection and requires explicit inheritance handling.

### Asyncio Coroutines vs Multiprocessing Workers
Asyncio handles 100k+ concurrent I/O-bound network connections with minimal stack overhead, but cannot parallelize CPU-bound tensor computations across multi-core systems due to CPython's GIL. Multiprocessing provides true CPU parallelism at the cost of IPC serialization and process fork overhead.

---

## 5. Common Failure Modes & Anti-Patterns

### Failure Mode 1: Async Event Loop Starvation
- **Root Cause**: Invoking a synchronous, blocking function (e.g. time.sleep, requests.get, or heavy regex) inside an async def coroutine pauses the single-threaded event loop for all concurrent connections.
- **Mitigation & Invariant Defense**: Offload blocking operations to loop.run_in_executor(None, func) or use non-blocking async libraries (httpx, aiofiles).

### Failure Mode 2: Mutable Default Arguments
- **Root Cause**: Default argument expressions in Python functions are evaluated once at function definition time, resulting in shared state across all function invocations.
- **Mitigation & Invariant Defense**: Use def func(val=None): if val is None: val = [] idiom.
