/*
 * ring.h -- the robobus SPSC shared-memory bus primitive, as a single-source-of-truth header.
 *
 * This is the EXACT ring that nsbus.c benchmarks AND that bench/formal/nsbus_ring_proof.c
 * formally verifies with cbmc. Keeping one definition means the numbers we publish and the
 * proof we publish are about the same code -- not a paraphrase of it.
 *
 * Design: a bounded single-producer/single-consumer ring of 64-byte slots, each guarded by a
 * per-slot seqlock. The writer stamps the sequence odd (writing), fences, writes the payload,
 * then stamps it even (ready); the reader validates the sequence before and after copying the
 * payload and rejects any read that raced a write (torn read). Wrapping unsigned arithmetic on
 * the 64-bit position is intentional -- the low bits index the ring, the whole word is the
 * monotonic generation.
 *
 * Pure: depends only on <stdint.h> + <stdatomic.h>. No OS, no clock, no allocation -- which is
 * precisely why cbmc can reason about it exhaustively.
 */
#ifndef ROBOBUS_RING_H
#define ROBOBUS_RING_H

#include <stdint.h>
#ifdef __CPROVER__
#include "cbmc_atomic_shim.h"     /* cbmc has no __c11_atomic_* model; use a sequential-equivalent */
#else
#include <stdatomic.h>
#endif

/* SLOTS is overridable (-DSLOTS=...) so the cbmc proof can use a small ring: the seqlock logic
 * is per-slot and size-independent, and SLOTS must always be a power of two. */
#ifndef SLOTS
#define SLOTS 1024u
#endif
#define SLOTMASK (SLOTS-1u)
typedef struct { atomic_uint_least64_t seq; uint64_t stamp; uint64_t payload; char pad[40]; } slot_t; /* 64B */
typedef struct { atomic_uint_least64_t widx; char p0[56];
                 atomic_uint_least64_t ridx; char p1[56]; slot_t s[SLOTS]; } ring_t;

static inline void ring_put(ring_t* r, uint64_t w, uint64_t stamp, uint64_t payload){
    slot_t* sl = &r->s[w & SLOTMASK];
    atomic_store_explicit(&sl->seq, (w<<1)|1u, memory_order_relaxed);   /* odd = writing */
    atomic_thread_fence(memory_order_release);
    sl->stamp = stamp; sl->payload = payload;
    atomic_store_explicit(&sl->seq, (w+1)<<1, memory_order_release);    /* even = ready */
    atomic_store_explicit(&r->widx, w+1, memory_order_release);
}
static inline int ring_get(ring_t* r, uint64_t rpos, uint64_t* stamp, uint64_t* payload){
    slot_t* sl = &r->s[rpos & SLOTMASK];
    uint64_t s1 = atomic_load_explicit(&sl->seq, memory_order_acquire);
    if (s1 != ((rpos+1)<<1)) return 0;                                 /* not yet published */
    *stamp = sl->stamp; *payload = sl->payload;
    atomic_thread_fence(memory_order_acquire);
    return atomic_load_explicit(&sl->seq, memory_order_relaxed) == s1; /* unchanged => consistent */
}

#endif /* ROBOBUS_RING_H */
