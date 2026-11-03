# Core Fundamentals & Invariants: Rust for High-Performance Scalable Systems

This document articulates the axiomatic invariants, theoretical grounding, mental models, idiomatic code implementations, architectural tradeoffs, and failure modes governing this topic.

---

## 1. Axiomatic Core Invariants

### Invariant 1: Aliasing XOR Mutability Invariant
$$
\forall v, \quad (\text{Count}(\&v) \ge 0 \land \text{Count}(\&\text{mut } v) = 0) \lor (\text{Count}(\&v) = 0 \land \text{Count}(\&\text{mut } v) = 1).
$$
**Implications & Guarantees**: Prevents data races and iterator invalidation at compile time without runtime garbage collection or mutex locks.

### Invariant 2: Send and Sync Thread Invariants
$$
T: \text{Sync} \iff \&T: \text{Send}. \quad \text{Types implementing } \text{Send} \text{ can transfer ownership across thread boundaries; } \text{Sync} \text{ allows concurrent shared access}.
$$
**Implications & Guarantees**: Data race freedom is guaranteed at the type system level; attempting to share non-thread-safe types (e.g. Rc<T>) across threads fails at compile time.

### Invariant 3: Cancellation Safety Invariant in Tokio Select
$$
\forall f \in \text{Futures in } select!, \quad \text{Drop}(f) \text{ must not leave shared state inconsistent or drop unacknowledged messages}.
$$
**Implications & Guarantees**: Futures dropped before completing execution in tokio::select! must be structurally cancellation-safe or guarded by dedicated background tasks.

---

## 2. Core Mental Models

### Mental Model 1: Values, References, and the Lifetime Stack
Every value has a single owner. When the owner drops out of scope, its memory is deterministically freed (RAII). References (&T) borrow access without taking ownership, and the compiler's borrow checker ensures references never outlive the owned value via lifetime annotations ('a).

### Mental Model 2: Poll-Based Asynchronous Futures
Rust futures are lazy state machines that do nothing until polled by an executor (Tokio). futures::poll(cx) returns Poll::Ready(T) or Poll::Pending. Pin<&mut T> guarantees that futures containing self-referential pointers cannot be moved in memory while awaiting poll.

---

## 3. Idiomatic Code Examples

### Lock-Free Single-Producer Single-Consumer (SPSC) Ring Buffer in Rust
```rust
use std::sync::atomic::{AtomicUsize, Ordering};
use std::sync::Arc;
use std::cell::{UnsafeCell, Cell};
use std::marker::PhantomData;

struct SpscRingBuffer<T, const CAP: usize> {
    buffer: [UnsafeCell<Option<T>>; CAP],
    head: AtomicUsize, // Read pointer (Consumer)
    tail: AtomicUsize, // Write pointer (Producer)
}

// Invariant: The underlying buffer is Send and Sync, but direct access is private.
// Soundness is enforced by splitting into exclusive non-Sync Producer and Consumer handles.
unsafe impl<T: Send, const CAP: usize> Send for SpscRingBuffer<T, CAP> {}
unsafe impl<T: Send, const CAP: usize> Sync for SpscRingBuffer<T, CAP> {}

pub struct SpscProducer<T: Send, const CAP: usize> {
    buffer: Arc<SpscRingBuffer<T, CAP>>,
    _marker: PhantomData<Cell<()>>, // Cell is !Sync, ensuring SpscProducer is strictly !Sync
}

pub struct SpscConsumer<T: Send, const CAP: usize> {
    buffer: Arc<SpscRingBuffer<T, CAP>>,
    _marker: PhantomData<Cell<()>>, // Cell is !Sync, ensuring SpscConsumer is strictly !Sync
}

// Neither Producer nor Consumer implements Sync; they cannot be shared concurrently across threads
impl<T: Send, const CAP: usize> SpscProducer<T, CAP> {
    pub fn push(&mut self, item: T) -> Result<(), T> {
        let tail = self.buffer.tail.load(Ordering::Relaxed);
        let head = self.buffer.head.load(Ordering::Acquire); // Synchronize with consumer's head update

        if tail - head >= CAP {
            return Err(item); // Buffer full
        }

        let idx = tail & (CAP - 1);
        unsafe {
            *self.buffer.buffer[idx].get() = Some(item);
        }

        // Release order ensures the item write is visible before tail pointer advances
        self.buffer.tail.store(tail + 1, Ordering::Release);
        Ok(())
    }
}

impl<T: Send, const CAP: usize> SpscConsumer<T, CAP> {
    pub fn pop(&mut self) -> Option<T> {
        let head = self.buffer.head.load(Ordering::Relaxed);
        let tail = self.buffer.tail.load(Ordering::Acquire); // Synchronize with producer's tail update

        if head == tail {
            return None; // Buffer empty
        }

        let idx = head & (CAP - 1);
        let item = unsafe { (*self.buffer.buffer[idx].get()).take() };

        // Release order ensures the read/take is complete before head pointer advances
        self.buffer.head.store(head + 1, Ordering::Release);
        item
    }
}

pub fn make_spsc<T: Send, const CAP: usize>() -> (SpscProducer<T, CAP>, SpscConsumer<T, CAP>) {
    assert!(CAP > 0 && (CAP & (CAP - 1)) == 0, "Capacity must be power of two");
    let buf = Arc::new(SpscRingBuffer {
        buffer: std::array::from_fn(|_| UnsafeCell::new(None)),
        head: AtomicUsize::new(0),
        tail: AtomicUsize::new(0),
    });
    (
        SpscProducer { buffer: buf.clone(), _marker: PhantomData },
        SpscConsumer { buffer: buf, _marker: PhantomData },
    )
}

// Compile-time assertion verifying Send (movable across threads) without Sync (shareable across threads)
fn assert_send<T: Send>() {}
fn verify_soundness<T: Send, const CAP: usize>() {
    assert_send::<SpscProducer<T, CAP>>();
    assert_send::<SpscConsumer<T, CAP>>();
}
```
**Analysis**: Demonstrates sound lock-free SPSC queue splitting into exclusive non-Sync Producer and Consumer handles, using Acquire/Release atomic ordering.

---

## 4. Architectural Tradeoffs

### Arc<Mutex<T>> vs Lock-Free Atomics
Arc<Mutex<T>> is easy to reason about and eliminates data corruption, but incurs OS syscall latency when contended (futex sleeps) and risks priority inversion. Lock-free atomics with Acquire/Release orderings provide sub-microsecond non-blocking performance, but require meticulous safety proofs to prevent subtle memory reordering bugs across ARM/x86 architectures.

### Monomorphization vs Trait Objects (&dyn Trait)
Generics compile to specialized static machine code (monomorphization) with inlining and zero runtime overhead, but increase binary size (code bloat) and compile times. Dynamic trait objects (dyn Trait) compile once and use vtables (fat pointers), reducing binary size at the cost of dynamic dispatch and inability to inline.

---

## 5. Common Failure Modes & Anti-Patterns

### Failure Mode 1: Tokio Select Cancellation Leaks
- **Root Cause**: Calling tokio::select! over an async read stream and an async timer. If the timer fires, the read future is dropped mid-read, discarding bytes already pulled from the OS socket buffer into the dropped future.
- **Mitigation & Invariant Defense**: Pin the read stream outside the select! loop or use tokio_util::codec to frame messages atomically.

### Failure Mode 2: Memory Reordering via Relaxed Atomics
- **Root Cause**: Using Ordering::Relaxed on atomic flag updates allowing the CPU/compiler to reorder memory writes after the flag store, exposing uninitialized data to other threads.
- **Mitigation & Invariant Defense**: Always use Ordering::Release for publishing writes and Ordering::Acquire for consuming reads.
