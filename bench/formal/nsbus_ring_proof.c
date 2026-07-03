/*
 * nsbus_ring_proof.c -- MACHINE-CHECKED correctness proof of the robobus SPSC ring.
 *
 * This is the C counterpart to the SymbiYosys/k-induction proof of the RTL ring (bench/hdl):
 * there we prove the hardware FIFO; here we prove the *actual C* that nsbus.c benchmarks, by
 * including the same bench/native/ring.h -- no paraphrase, the real ring_put/ring_get.
 *
 * cbmc explores ALL executions (all nondeterministic inputs, and -- for the concurrent harness --
 * all thread interleavings) up to the given bound and either proves the assertions hold or prints
 * a concrete counterexample. Each PROP_* function is an independent proof obligation; run one per
 * cbmc invocation via --function (see run_formal.py).
 *
 * What is proven:
 *   PROP_safety        -- ring_put/ring_get never index out of bounds, never deref a bad pointer,
 *                         for an ARBITRARY 64-bit position and arbitrary ring contents.
 *   PROP_roundtrip     -- publishing position w then consuming w returns EXACTLY the stamp+payload
 *                         written, and reports success. (protocol liveness + data integrity)
 *   PROP_reject_writing-- a reader that meets a slot mid-write (odd sequence) rejects it.
 *   PROP_reject_stale  -- a reader that meets a slot holding a DIFFERENT generation rejects it.
 *   PROP_backpressure  -- while the live window is smaller than the ring (the producer's
 *                         backpressure guard), no two live positions ever alias the same slot.
 *   PROP_concurrent    -- under ALL interleavings of a concurrent writer and reader on one slot,
 *                         a successful read never returns a torn (inconsistent) stamp/payload pair.
 *
 * Note on arithmetic: the seqlock deliberately relies on WRAPPING unsigned 64-bit arithmetic
 * (position is a monotonic generation; low bits index the ring). Unsigned wrap is defined in C
 * and intentional here, so the unsigned-overflow check is deliberately NOT enabled for these
 * proofs (see run_formal.py); every other safety check IS.
 */
#include "ring.h"

uint64_t nondet_u64(void);

/* ---- PROP_safety: no OOB / no bad deref for any position, any ring ---------------------
 * cbmc's --bounds-check + --pointer-check turn every array access and dereference in
 * ring_put/ring_get into an implicit assertion; proving this function proves memory safety. */
void PROP_safety(void){
    static ring_t r;                       /* arbitrary contents modelled below */
    r.s[nondet_u64() & SLOTMASK].seq = nondet_u64();   /* ring may hold anything */
    uint64_t w = nondet_u64();
    ring_put(&r, w, nondet_u64(), nondet_u64());
    uint64_t s, p;
    (void)ring_get(&r, w, &s, &p);
}

/* ---- PROP_roundtrip: put(w) then get(w) yields EXACTLY what was written ---------------- */
void PROP_roundtrip(void){
    static ring_t r;                       /* fresh ring: all sequences 0 (even, generation 0) */
    uint64_t w       = nondet_u64();
    uint64_t stamp   = nondet_u64();
    uint64_t payload = nondet_u64();
    ring_put(&r, w, stamp, payload);
    uint64_t s, p;
    int ok = ring_get(&r, w, &s, &p);
    __CPROVER_assert(ok == 1, "ROUNDTRIP: get() after put() on the same position succeeds");
    __CPROVER_assert(s == stamp && p == payload,
                     "ROUNDTRIP: get() returns exactly the stamp/payload that put() wrote");
}

/* ---- PROP_reject_writing: odd sequence (writer in progress) is rejected ---------------- */
void PROP_reject_writing(void){
    static ring_t r;
    uint64_t w = nondet_u64();
    slot_t* sl = &r.s[w & SLOTMASK];
    atomic_store_explicit(&sl->seq, (w << 1) | 1u, memory_order_relaxed);  /* odd => writing */
    uint64_t s, p;
    int ok = ring_get(&r, w, &s, &p);
    __CPROVER_assert(ok == 0, "REJECT: reader rejects a slot that is being written (odd sequence)");
}

/* ---- PROP_reject_stale: a different published generation in the slot is rejected ------- *
 * The reader compares the RAW seq word (seq == (rpos+1)<<1). Because seq = generation<<1, the low
 * bit is the writing flag and the effective generation is 63-bit — two positions 2^63 apart would
 * alias (a non-issue: 2^63 messages ~= 292 years at 1 GHz). So we model the slot holding ANY even
 * (published, not mid-write) seq that is NOT position w's expected seq, and require rejection. */
void PROP_reject_stale(void){
    static ring_t r;
    uint64_t w          = nondet_u64();
    uint64_t stored_seq = nondet_u64();
    __CPROVER_assume((stored_seq & 1u) == 0u);            /* even => a completed publication */
    __CPROVER_assume(stored_seq != ((w + 1) << 1));       /* but NOT position w's generation */
    slot_t* sl = &r.s[w & SLOTMASK];
    atomic_store_explicit(&sl->seq, stored_seq, memory_order_relaxed);
    uint64_t s, p;
    int ok = ring_get(&r, w, &s, &p);
    __CPROVER_assert(ok == 0, "REJECT: reader rejects a slot whose published generation != w");
}

/* ---- PROP_backpressure: a sub-ring live window never aliases a slot -------------------- *
 * The producer waits while (i - ridx >= SLOTS-1), so every live position b satisfies
 * b - ridx < SLOTS-1. For any two live positions a<b the ring index is position & SLOTMASK;
 * because 0 < b-a < SLOTS and SLOTS is a power of two, a and b map to distinct slots. */
void PROP_backpressure(void){
    uint64_t ridx = nondet_u64();
    uint64_t a    = nondet_u64();
    uint64_t b    = nondet_u64();
    __CPROVER_assume(ridx <= a && a < b);          /* a, b both live (>= read cursor), a before b */
    __CPROVER_assume(b - ridx < SLOTS - 1);        /* producer backpressure bounds the window */
    __CPROVER_assert((a & SLOTMASK) != (b & SLOTMASK),
                     "BACKPRESSURE: distinct live positions never share a ring slot");
}

/* ---- PROP_concurrent: no torn read under ALL writer/reader interleavings --------------- *
 * One writer publishes the fixed pair (0xA5A5.., 0x5A5A..) at a fixed position; one reader
 * consumes it. cbmc explores every interleaving of the two threads (SC model). Whenever the
 * reader reports success, the pair it returns MUST be the exact pair the writer wrote -- never
 * a half-updated (torn) combination. This is the seqlock's core guarantee. */
#ifdef PROP_CONCURRENT
#include <pthread.h>
#define CPOS 7u
#define CSTAMP   0xA5A5A5A5A5A5A5A5ull
#define CPAYLOAD 0x5A5A5A5A5A5A5A5Aull
static ring_t g;
static void* cwriter(void* _){ (void)_; ring_put(&g, CPOS, CSTAMP, CPAYLOAD); return 0; }
static void* creader(void* _){ (void)_;
    uint64_t s, p;
    if (ring_get(&g, CPOS, &s, &p)) {
        __CPROVER_assert(s == CSTAMP && p == CPAYLOAD,
                         "CONCURRENT: a successful read is never torn (pair is consistent)");
    }
    return 0;
}
void PROP_concurrent(void){
    pthread_t tw, tr;
    pthread_create(&tw, 0, cwriter, 0);
    pthread_create(&tr, 0, creader, 0);
    pthread_join(tw, 0);
    pthread_join(tr, 0);
}
#endif
