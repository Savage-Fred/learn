# Exercise TIER1_STARTER: Custom Iterable and Context Manager Pipeline

**Objective**: Build a memory-safe custom stream reader class implementing __iter__, __next__, __enter__, and __exit__ protocols.

## Grounded Sources & Curriculum References
- **Source Reference IDs**: `ramalho-fluent-python-2022`, `pep-544-protocols`, `slatkin-effective-python-2019`
- **Applicable Citations**:
  - [Fluent Python: Clear, Concise, and Effective Programming](https://www.oreilly.com/library/view/fluent-python-2nd/9781492056348/) (2022)
  - [PEP 544 – Protocols: Structural subtyping (static duck typing)](https://peps.python.org/pep-0544/) (2018)
  - [Effective Python: 90 Specific Ways to Write Better Python](https://effectivepython.com/) (2019)

---

## Problem Statement

Implement a class `BoundedBatchReader` that accepts an iterable of items and a batch size. It must support `with` context management (closing underlying resource) and iterable iteration yielding lists of items of maximum size `batch_size`. The reader must maintain O(1) auxiliary memory relative to the underlying dataset.

---

## Invariant Scaffolding & Guidance

- __iter__ must return self; __next__ must raise StopIteration when exhausted.
- __enter__ must return the resource; __exit__ must ensure resource closure even on exception.

---

## Starter Code

```python
class BoundedBatchReader:
    def __init__(self, source_iterable, batch_size: int):
        self.source = source_iterable
        self.batch_size = batch_size
        self._iterator = None

    def __enter__(self):
        # TODO: initialize iterator
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: cleanup
        pass

    def __iter__(self):
        # TODO: implement iterator protocol
        return self

    def __next__(self):
        # TODO: yield batch of size batch_size
        pass
```

---

## Verification Test Cases

- [ ] **Test Case**: Verify normal iteration over 10 items with batch_size 3 yields 4 batches: [3, 3, 3, 1].
- [ ] **Test Case**: Verify context manager cleans up even if exception is raised inside context.
- [ ] **Test Case**: Verify StopIteration is raised once underlying iterator is exhausted.

---

## Solution & Invariant Check

The class wraps iter(source) without loading elements into memory upfront; slices items via itertools.islice in __next__.