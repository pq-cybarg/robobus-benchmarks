/*
 * nsbus.c -- rigorous NANOSECOND-resolution benchmark of the shared-memory bus primitive.
 *
 * Motivation: a single clock_gettime(CLOCK_MONOTONIC) read on macOS is only ~1 us granular,
 * so per-message latencies below ~1 us read as 0. This tool fixes that two ways:
 *
 *   (1) a HIGH-RESOLUTION clock: mach_absolute_time() (Apple Silicon: 41.667 ns/tick) on
 *       Darwin, clock_gettime(CLOCK_MONOTONIC_RAW) elsewhere -- ~40 ns single-shot resolution.
 *
 *   (2) AMORTIZED batching for the mean: time N back-to-back ring ops under ONE pair of clock
 *       reads and divide by N. Clock-granularity-INDEPENDENT; resolves sub-ns means (e.g. 200M
 *       ops in 5.0 s -> 25.0 ns/op exactly). This is the correct way to report an operation
 *       faster than the clock's single-shot resolution.
 *
 * Two measurements:
 *   A. amortized single-core ring put+get  -> pure bus op cost (ns/op), sub-ns mean resolution.
 *   B. cross-process one-way latency (fork + shared mmap) -> real IPC latency distribution at
 *      high-res clock resolution, incl. the cache-coherence bounce and the preemption tail.
 *
 * Output: one JSON object on stdout (scientific notation). Portable across Darwin/Linux (POSIX
 * clock + mmap + fork). Not built on Windows (no fork/mmap) -- the harness skips it there.
 *
 * Build:  cc -O3 -std=c11 nsbus.c -o nsbus
 * Run:    ./nsbus [N_AMORTIZED] [N_ONEWAY]        (env NSBUS_RT=1 raises RT priority)
 */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <unistd.h>
#include <stdatomic.h>
#include <sys/mman.h>
#include <sys/wait.h>

#if defined(__APPLE__)
#include <mach/mach_time.h>
#include <mach/thread_act.h>
#include <mach/thread_policy.h>
#include <pthread.h>
static double NS_PER_TICK = 1.0;
static inline uint64_t rawclock(void){ return mach_absolute_time(); }
static void clock_init(void){ mach_timebase_info_data_t tb; mach_timebase_info(&tb);
    NS_PER_TICK = (double)tb.numer/(double)tb.denom; }
static const char* CLOCK_NAME = "mach_absolute_time";
#else
#include <time.h>
static double NS_PER_TICK = 1.0;
static inline uint64_t rawclock(void){ struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC_RAW, &ts);
    return (uint64_t)ts.tv_sec*1000000000ull + ts.tv_nsec; }
static void clock_init(void){ NS_PER_TICK = 1.0; }
static const char* CLOCK_NAME = "CLOCK_MONOTONIC_RAW";
#endif
static inline double ticks_to_ns(uint64_t t){ return (double)t * NS_PER_TICK; }

/* ---- minimal SPSC ring (seqlock-per-slot, the robobus pattern) --------------------- */
#define SLOTS 1024u
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

static int cmp_u64(const void* a, const void* b){
    uint64_t x=*(const uint64_t*)a, y=*(const uint64_t*)b; return (x>y)-(x<y); }

static void try_rt(void){
    if (!getenv("NSBUS_RT")) return;
#if defined(__APPLE__)
    thread_time_constraint_policy_data_t p;   /* the macOS RT lever (robobus/realtime.py) */
    p.period      = (uint32_t)(500000.0/NS_PER_TICK);  /* 500us */
    p.computation = (uint32_t)(300000.0/NS_PER_TICK);  /* 300us */
    p.constraint  = (uint32_t)(500000.0/NS_PER_TICK);  /* 500us */
    p.preemptible = 0;
    thread_policy_set(pthread_mach_thread_np(pthread_self()),
        THREAD_TIME_CONSTRAINT_POLICY, (thread_policy_t)&p, THREAD_TIME_CONSTRAINT_POLICY_COUNT);
#endif
}

int main(int argc, char** argv){
    clock_init();
    try_rt();
    uint64_t N_AMORT  = (argc>1)? strtoull(argv[1],0,10) : 50000000ull;
    uint64_t N_ONEWAY = (argc>2)? strtoull(argv[2],0,10) : 500000ull;

    /* ---- A. amortized single-core ring put+get (clock-independent mean) ------------- */
    ring_t* rA = mmap(0, sizeof(ring_t), PROT_READ|PROT_WRITE, MAP_SHARED|MAP_ANON, -1, 0);
    memset(rA, 0, sizeof(*rA));
    volatile uint64_t sink = 0;
    for (uint64_t i=0;i<100000;i++){ ring_put(rA,i,i,i); uint64_t s,p; ring_get(rA,i,&s,&p); sink+=p; }
    memset(rA,0,sizeof(*rA));
    uint64_t t0 = rawclock();
    for (uint64_t i=0;i<N_AMORT;i++){ ring_put(rA,i,i,i); uint64_t s,p; if(ring_get(rA,i,&s,&p)) sink+=p; }
    uint64_t t1 = rawclock();
    double amort_ns = ticks_to_ns(t1-t0);
    double ns_per_op = amort_ns / (double)N_AMORT;
    double ops_per_s = (double)N_AMORT / (amort_ns/1e9);

    /* ---- B. cross-process one-way latency distribution ----------------------------- */
    ring_t* rB = mmap(0, sizeof(ring_t), PROT_READ|PROT_WRITE, MAP_SHARED|MAP_ANON, -1, 0);
    memset(rB,0,sizeof(*rB));
    uint64_t* lat = mmap(0, sizeof(uint64_t)*N_ONEWAY, PROT_READ|PROT_WRITE, MAP_SHARED|MAP_ANON, -1, 0);
    atomic_uint_least64_t* done = mmap(0, sizeof(uint64_t), PROT_READ|PROT_WRITE, MAP_SHARED|MAP_ANON, -1, 0);
    atomic_store_explicit(done, 0, memory_order_relaxed);
    /* WARMUP: exchange W messages that are NOT recorded, so fork / first-schedule / cold-cache /
       first-touch page-fault costs do not pollute the steady-state distribution. The producer
       still touches every ring slot at least once during warmup (W >= SLOTS). */
    const uint64_t WARM = 20000;
    const uint64_t TOTAL = WARM + N_ONEWAY;
    pid_t pid = fork();
    if (pid == 0) { /* consumer */
        try_rt();
        for (uint64_t i=0;i<TOTAL;i++){
            uint64_t s,p;
            while (!ring_get(rB,i,&s,&p)) { /* spin */ }
            uint64_t d = rawclock() - s;
            if (i >= WARM) lat[i-WARM] = d;        /* record only steady-state */
            atomic_store_explicit(&rB->ridx, i+1, memory_order_release);  /* publish progress */
        }
        atomic_store_explicit(done,1,memory_order_release);
        _exit(0);
    }
    for (uint64_t i=0;i<TOTAL;i++){                 /* producer, lightly paced (~1us gap) */
        /* backpressure: never overwrite a slot the consumer hasn't read (bounded ring) */
        while (i - atomic_load_explicit(&rB->ridx, memory_order_acquire) >= SLOTS - 1) { /* wait */ }
        ring_put(rB, i, rawclock(), i);
        uint64_t spin = rawclock(); uint64_t gap=(uint64_t)(1000.0/NS_PER_TICK);
        while (rawclock()-spin < gap) {}
    }
    while (!atomic_load_explicit(done,memory_order_acquire)) {}
    waitpid(pid,0,0);

    /* find WHERE the max sits in send-order (was it early = cold-start, or distributed?) */
    uint64_t argmax=0, maxv=0;
    for (uint64_t i=0;i<N_ONEWAY;i++){ if (lat[i]>maxv){ maxv=lat[i]; argmax=i; } }
    double max_position = (double)argmax/(double)N_ONEWAY;   /* 0.0 = first msg, 1.0 = last */
    uint64_t* lt = malloc(sizeof(uint64_t)*N_ONEWAY);
    double sum=0; for (uint64_t i=0;i<N_ONEWAY;i++){ lt[i]=lat[i]; sum+=ticks_to_ns(lat[i]); }
    qsort(lt,N_ONEWAY,sizeof(uint64_t),cmp_u64);
    #define PCT(p) ticks_to_ns(lt[(uint64_t)((p)*(N_ONEWAY-1))])
    double mean = sum/(double)N_ONEWAY;
    uint64_t u100=0,u250=0,u500=0,u1us=0;
    for (uint64_t i=0;i<N_ONEWAY;i++){ double v=ticks_to_ns(lt[i]);
        if(v<100)u100++; if(v<250)u250++; if(v<500)u500++; if(v<1000)u1us++; }

    const char* rt = getenv("NSBUS_RT")?"on":"off";
    printf("{\n");
    printf("  \"clock\": {\"source\": \"%s\", \"ns_per_tick\": %.6e, \"single_shot_res_ns\": %.6e},\n",
        CLOCK_NAME, NS_PER_TICK, NS_PER_TICK);
    printf("  \"realtime\": \"%s\",\n", rt);
    printf("  \"amortized_ring_op\": {\"n\": %llu, \"ns_per_op\": %.6e, \"ops_per_s\": %.6e, \"sink\": %llu},\n",
        (unsigned long long)N_AMORT, ns_per_op, ops_per_s, (unsigned long long)sink);
    printf("  \"oneway_latency_ns\": {\"n\": %llu, \"min\": %.6e, \"p50\": %.6e, \"p90\": %.6e, "
           "\"p99\": %.6e, \"p999\": %.6e, \"max\": %.6e, \"mean\": %.6e, "
           "\"warmup_discarded\": %llu, \"max_index\": %llu, \"max_position_frac\": %.6e,\n",
        (unsigned long long)N_ONEWAY, PCT(0.0), PCT(0.50), PCT(0.90), PCT(0.99), PCT(0.999),
        ticks_to_ns(lt[N_ONEWAY-1]), mean,
        (unsigned long long)WARM, (unsigned long long)argmax, max_position);
    printf("    \"frac_under_100ns\": %.6e, \"frac_under_250ns\": %.6e, \"frac_under_500ns\": %.6e, "
           "\"frac_under_1us\": %.6e}\n",
        (double)u100/N_ONEWAY, (double)u250/N_ONEWAY, (double)u500/N_ONEWAY, (double)u1us/N_ONEWAY);
    printf("}\n");
    return 0;
}
