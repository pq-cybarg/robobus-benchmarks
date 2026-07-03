#ifndef ROBOBUS_CBMC_ATOMIC_SHIM_H
#define ROBOBUS_CBMC_ATOMIC_SHIM_H
/* cbmc (6.x) has no model for clang's __c11_atomic_* builtins, so <stdatomic.h> operations become
 * no-body external calls: stores are dropped and loads return a nondeterministic value. For the
 * SEQUENTIAL correctness proof the atomics are semantically plain load/store (single-threaded
 * reasoning), so we model them as exactly that. This is sound for the roundtrip / torn-read-
 * rejection / memory-safety / backpressure properties. Concurrent interleavings are a separate
 * concern, covered by PROP_concurrent and by the SymbiYosys/k-induction proof of the RTL ring. */
#include <stdint.h>
typedef uint_least64_t atomic_uint_least64_t;
#define memory_order_relaxed 0
#define memory_order_consume 1
#define memory_order_acquire 2
#define memory_order_release 3
#define memory_order_acq_rel 4
#define memory_order_seq_cst 5
#define atomic_store_explicit(p, v, mo) (*(p) = (v))
#define atomic_load_explicit(p, mo)     (*(p))
#define atomic_thread_fence(mo)         ((void)0)
#endif
