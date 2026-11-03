# Exercise TIER2_L4: Thread-Safe Worker Pool with Graceful Shutdown in Rust

**Objective**: Implement a multi-threaded worker pool using std::sync::mpsc channels and Arc<Mutex<T>> with graceful shutdown on Drop.

---

## Problem Statement

Implement `ThreadPool::new(size: usize) -> ThreadPool`. Support `execute<F>(&self, f: F) where F: FnOnce() + Send + 'static`. Maintain an mpsc channel receiver wrapped in `Arc<Mutex<Receiver<Job>>>`. Implement `Drop` for ThreadPool that closes the channel and calls `join()` on all worker threads.

---

## Formal Constraints

- Worker pool size: Configurable N worker threads.
- Task execution: Support arbitrary FnOnce() + Send + 'static closures.
- Graceful shutdown: When WorkerPool is dropped, all queued jobs must finish and threads join cleanly.

---

## Starter Code

```python
use std::sync::{mpsc, Arc, Mutex};
use std::thread;

pub struct ThreadPool {
    workers: Vec<Worker>,
    sender: Option<mpsc::Sender<Job>>,
}

type Job = Box<dyn FnOnce() + Send + 'static>;

impl ThreadPool {
    pub fn new(size: usize) -> Self {
        // TODO: Initialize workers and channels
        unimplemented!()
    }

    pub fn execute<F>(&self, f: F)
    where
        F: FnOnce() + Send + 'static,
    {
        // TODO: Send job to worker queue
    }
}
```

---

## Verification Test Cases

- [ ] **Test Case**: Executes 100 concurrent computational tasks across 4 worker threads.
- [ ] **Test Case**: Dropping thread pool waits for all in-flight tasks to complete.
- [ ] **Test Case**: Panicking worker task does not poison the pool or hang the program.

---

## Solution & Invariant Check

Closes channel by dropping sender; workers receive RecvError and break loop; Drop joins thread handles.