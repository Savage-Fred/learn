# Exercise TIER2_L4: Thread-Safe Decorator-Based Memoization Cache with TTL

**Objective**: Implement an idiomatic Python decorator supporting LRU caching with per-item TTL and thread safety.

---

## Problem Statement

Implement `@lru_cache_ttl(maxsize=128, ttl_seconds=60.0)`. When decorated over a function, repeated calls with identical arguments must return cached values if invoked within `ttl_seconds`. Expired items must be lazily evicted or purged upon capacity limits. Must support arbitrary hashable arguments (`*args`, `**kwargs`).

---

## Formal Constraints

- Time complexity: O(1) cache hits and evictions.
- Space complexity: O(N) where N is maximum cache capacity.
- Thread safety: Multiple concurrent reader/writer threads without corruption.

---

## Starter Code

```python
import time
from functools import wraps

def lru_cache_ttl(maxsize: int = 128, ttl_seconds: float = 60.0):
    def decorator(fn):
        # TODO: Implement thread-safe LRU with TTL
        @wraps(fn)
        def wrapper(*args, **kwargs):
            return fn(*args, **kwargs)
        return wrapper
    return decorator
```

---

## Verification Test Cases

- [ ] **Test Case**: Cache hit within TTL does not invoke wrapped function.
- [ ] **Test Case**: Expired item after TTL invokes wrapped function and refreshes timestamp.
- [ ] **Test Case**: Capacity overflow evicts least recently used item.
- [ ] **Test Case**: Concurrent calls from 10 threads produce consistent results without data races.

---

## Solution & Invariant Check

Maintains a dict of key -> (val, expiry, node) with a doubly-linked list for LRU ordering, guarded by a threading.Lock.