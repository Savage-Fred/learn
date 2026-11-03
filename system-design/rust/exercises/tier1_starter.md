# Exercise TIER1_STARTER: Custom Safe Linked List with Iterator Protocol in Rust

**Objective**: Build a memory-safe singly linked list in safe Rust implementing standard Iterator and Drop traits.

---

## Problem Statement

Implement `LinkedList<T>` in safe Rust. Support `push(&mut self, elem: T)`, `pop(&mut self) -> Option<T>`, `peek(&self) -> Option<&T>`, and implement `IntoIterator` and `Iterator`. Implement custom `Drop` that iteratively pops nodes to prevent call stack overflow on large lists.

---

## Invariant Scaffolding & Guidance

- Node ownership is represented via Option<Box<Node<T>>>.
- Iteration borrows references without consuming the list (&list).
- Drop must iteratively deallocate nodes to avoid stack overflow recursion.

---

## Starter Code

```python
pub struct LinkedList<T> {
    head: Option<Box<Node<T>>>,
}

struct Node<T> {
    elem: T,
    next: Option<Box<Node<T>>>,
}

impl<T> LinkedList<T> {
    pub fn new() -> Self {
        LinkedList { head: None }
    }

    pub fn push(&mut self, elem: T) {
        // TODO: Push to front
    }

    pub fn pop(&mut self) -> Option<T> {
        // TODO: Pop from front
        None
    }
}
```

---

## Verification Test Cases

- [ ] **Test Case**: Pushing 1, 2, 3 and popping returns 3, 2, 1.
- [ ] **Test Case**: Iteration over list references yields correct sequence.
- [ ] **Test Case**: Dropping a 1,000,000-node list does not cause a stack overflow.

---

## Solution & Invariant Check

Uses Option::take to swap out nodes without violating borrow checker; Drop runs while let Some(_) = self.pop() loop.