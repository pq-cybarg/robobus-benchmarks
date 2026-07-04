/*
 * nsbus.c -- rigorous NANOSECOND-resolution benchmark of the shared-memory bus primitive.
 *
 * Motivation: a single coarse clock read (macOS clock_gettime ~1 us; Windows GetTickCount ~15 ms)
 * reads sub-us latencies as 0. This tool fixes that two ways:
 *   (1) a HIGH-RESOLUTION clock: mach_absolute_time (Darwin), QueryPerformanceCounter (Windows),
 *       clock_gettime(CLOCK_MONOTONIC_RAW) (Linux) -- ~10-40 ns single-shot resolution.
 *   (2) AMORTIZED batching for the mean: time N back-to-back ring ops under ONE pair of clock reads
 *       and divide by N -- clock-granularity-independent, resolves sub-ns means.
 *
 * THREE measurements (all portable across Darwin / Linux / Windows):
 *   A. amortized single-core ring put+get           -> pure bus op cost (ns/op), sub-ns mean.
 *   B. cross-PROCESS one-way latency                 -> real IPC latency distribution incl. the
 *      (POSIX fork+mmap; Windows CreateProcess+CreateFileMapping)  cache-coherence bounce + tail.
 *   C. cross-THREAD (two threads, one ring) one-way  -> same cache-line bounce WITHOUT the process/
 *      latency (portable everywhere, incl. Windows)     IPC machinery -- the load-bearing hop cost.
 *
 * Output: one JSON object on stdout (scientific notation).
 *
 * Build:  POSIX  cc -O3 -std=c11 nsbus.c -o nsbus
 *         Windows clang -O3 -std=c11 nsbus.c -o nsbus.exe -lwinmm -lavrt   (clang for C11 <stdatomic.h>)
 * Run:    ./nsbus [N_AMORTIZED] [N_ONEWAY]           (env NSBUS_RT=1 raises RT priority)
 */
#if !defined(_WIN32)
#define _GNU_SOURCE          /* CLOCK_MONOTONIC_RAW + SCHED_FIFO on Linux; harmless elsewhere */
#endif
#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdatomic.h>

/* ============================ platform: high-resolution clock ============================ */
#if defined(_WIN32)
  #define WIN32_LEAN_AND_MEAN
  #include <windows.h>
  #include <timeapi.h>    /* timeBeginPeriod (winmm) -- excluded by WIN32_LEAN_AND_MEAN */
  #include <avrt.h>       /* MMCSS: AvSetMmThreadCharacteristics / AvSetMmThreadPriority */
  #include <process.h>    /* _beginthreadex */
  static double NS_PER_TICK = 1.0;
  static inline uint64_t rawclock(void){ LARGE_INTEGER c; QueryPerformanceCounter(&c); return (uint64_t)c.QuadPart; }
  static void clock_init(void){ LARGE_INTEGER f; QueryPerformanceFrequency(&f); NS_PER_TICK = 1.0e9/(double)f.QuadPart; }
  static const char* CLOCK_NAME = "QueryPerformanceCounter";
#elif defined(__APPLE__)
  #include <mach/mach_time.h>
  #include <mach/thread_act.h>
  #include <mach/thread_policy.h>
  #include <pthread.h>
  #include <sys/qos.h>
  #include <sys/mman.h>
  #include <unistd.h>
  #include <sys/wait.h>
  static double NS_PER_TICK = 1.0;
  static inline uint64_t rawclock(void){ return mach_absolute_time(); }
  static void clock_init(void){ mach_timebase_info_data_t tb; mach_timebase_info(&tb);
      NS_PER_TICK = (double)tb.numer/(double)tb.denom; }
  static const char* CLOCK_NAME = "mach_absolute_time";
#else
  #include <time.h>
  #include <pthread.h>
  #include <sched.h>
  #include <unistd.h>
  #include <sys/mman.h>
  #include <sys/wait.h>
  static double NS_PER_TICK = 1.0;
  static inline uint64_t rawclock(void){ struct timespec ts;
      clock_gettime(CLOCK_MONOTONIC_RAW, &ts);
      return (uint64_t)ts.tv_sec*1000000000ull + ts.tv_nsec; }
  static void clock_init(void){ NS_PER_TICK = 1.0; }
  static const char* CLOCK_NAME = "CLOCK_MONOTONIC_RAW";
#endif
static inline double ticks_to_ns(uint64_t t){ return (double)t * NS_PER_TICK; }

/* the SPSC ring (seqlock-per-slot) -- one source of truth, also cbmc-verified (bench/formal). */
#include "ring.h"

/* ============================ portable page-aligned local alloc ============================ */
/* zeroed, page-aligned memory for the ring (needs >=64B alignment) + the latency array. */
static void* local_alloc(size_t n){
#if defined(_WIN32)
    return VirtualAlloc(NULL, n, MEM_COMMIT|MEM_RESERVE, PAGE_READWRITE);   /* zeroed */
#else
    void* p = mmap(0, n, PROT_READ|PROT_WRITE, MAP_PRIVATE|MAP_ANON, -1, 0);
    return (p==MAP_FAILED)? NULL : p;
#endif
}

/* ============================ RT / jitter suppression, per OS ============================ */
static void stabilize(void){
    if (!getenv("NSBUS_RT")) return;
#if defined(_WIN32)
    /* Windows RT levers: 1 ms timer resolution (timeBeginPeriod), time-critical priority, and MMCSS
     * ("Pro Audio") which gives a glitch-resistant scheduling class analogous to macOS time-constraint. */
    timeBeginPeriod(1);
    SetThreadPriority(GetCurrentThread(), THREAD_PRIORITY_TIME_CRITICAL);
    SetPriorityClass(GetCurrentProcess(), HIGH_PRIORITY_CLASS);
    DWORD idx = 0; HANDLE h = AvSetMmThreadCharacteristicsA("Pro Audio", &idx);
    if (h) AvSetMmThreadPriority(h, AVRT_PRIORITY_CRITICAL);
#elif defined(__APPLE__)
    pthread_set_qos_class_self_np(QOS_CLASS_USER_INTERACTIVE, 0);       /* pin to P-cores */
    double per_us = getenv("NSBUS_RT_PERIOD_US") ? atof(getenv("NSBUS_RT_PERIOD_US")) : 500.0;
    double cmp_us = getenv("NSBUS_RT_COMPUTE_US") ? atof(getenv("NSBUS_RT_COMPUTE_US")) : 300.0;
    thread_time_constraint_policy_data_t p;
    p.period      = (uint32_t)(per_us*1000.0/NS_PER_TICK);
    p.computation = (uint32_t)(cmp_us*1000.0/NS_PER_TICK);
    p.constraint  = (uint32_t)(per_us*1000.0/NS_PER_TICK);
    p.preemptible = 0;
    thread_policy_set(pthread_mach_thread_np(pthread_self()),
        THREAD_TIME_CONSTRAINT_POLICY, (thread_policy_t)&p, THREAD_TIME_CONSTRAINT_POLICY_COUNT);
#else
    /* Linux: request SCHED_FIFO where permitted; full determinism needs isolcpus/nohz_full. */
    struct sched_param sp; sp.sched_priority = 80;
    (void)!sched_setscheduler(0, SCHED_FIFO, &sp);
#endif
}

static int cmp_u64(const void* a, const void* b){
    uint64_t x=*(const uint64_t*)a, y=*(const uint64_t*)b; return (x>y)-(x<y); }

/* The consumer half of one-way latency: spin-read every position, timestamp the delta, record the
 * steady-state window. Shared by the two-thread path, the POSIX fork child, and the Win32 child. */
static void consumer_loop(ring_t* r, uint64_t* lat, atomic_uint_least64_t* done,
                          uint64_t total, uint64_t warm){
    stabilize();
    for (uint64_t i=0;i<total;i++){
        uint64_t s,p;
        while (!ring_get(r,i,&s,&p)) { /* spin */ }
        uint64_t d = rawclock() - s;
        if (i >= warm) lat[i-warm] = d;
        atomic_store_explicit(&r->ridx, i+1, memory_order_release);
    }
    atomic_store_explicit(done,1,memory_order_release);
}

/* The producer half: paced (~1 us busy-gap) publish with ring backpressure. */
static void producer_loop(ring_t* r, atomic_uint_least64_t* done, uint64_t total){
    for (uint64_t i=0;i<total;i++){
        while (i - atomic_load_explicit(&r->ridx, memory_order_acquire) >= SLOTS - 1) { /* wait */ }
        ring_put(r, i, rawclock(), i);
        uint64_t spin = rawclock(); uint64_t gap=(uint64_t)(1000.0/NS_PER_TICK);
        while (rawclock()-spin < gap) {}
    }
    while (!atomic_load_explicit(done,memory_order_acquire)) {}
}

/* Compute + print one latency JSON block (percentiles, fractions, spike/jitter) from lat[0..n). */
static void emit_lat_block(const char* key, uint64_t* lat, uint64_t n_oneway, uint64_t warm){
    const uint64_t COOL = (n_oneway > 128) ? 64 : 0;    /* drop teardown-race tail */
    const uint64_t N = n_oneway - COOL;
    uint64_t argmax=0, maxv=0;
    for (uint64_t i=0;i<N;i++){ if (lat[i]>maxv){ maxv=lat[i]; argmax=i; } }
    double max_position = (double)argmax/(double)N;
    uint64_t* lt = (uint64_t*)malloc(sizeof(uint64_t)*N);
    double sum=0; for (uint64_t i=0;i<N;i++){ lt[i]=lat[i]; sum+=ticks_to_ns(lat[i]); }
    qsort(lt,N,sizeof(uint64_t),cmp_u64);
    #define PCT(p) ticks_to_ns(lt[(uint64_t)((p)*(N-1))])
    double mean = sum/(double)N;
    uint64_t u100=0,u250=0,u500=0,u1us=0;
    for (uint64_t i=0;i<N;i++){ double v=ticks_to_ns(lt[i]);
        if(v<100)u100++; if(v<250)u250++; if(v<500)u500++; if(v<1000)u1us++; }
    const double SPIKE_NS = 1000.0;
    uint64_t spikes=0, stable_max=0;
    for (uint64_t i=0;i<N;i++){ if (ticks_to_ns(lt[i])>SPIKE_NS) spikes++; else if (lt[i]>stable_max) stable_max=lt[i]; }
    double p50ns = PCT(0.50);
    double jitter = (p50ns>0)? PCT(0.99)/p50ns : 0.0;
    printf("  \"%s\": {\"n\": %llu, \"min\": %.6e, \"p50\": %.6e, \"p90\": %.6e, "
           "\"p99\": %.6e, \"p999\": %.6e, \"p9999\": %.6e, \"max\": %.6e, \"mean\": %.6e, "
           "\"warmup_discarded\": %llu, \"cooldown_discarded\": %llu, \"max_index\": %llu, "
           "\"max_position_frac\": %.6e, \"frac_under_100ns\": %.6e, \"frac_under_250ns\": %.6e, "
           "\"frac_under_500ns\": %.6e, \"frac_under_1us\": %.6e, \"spike_thresh_ns\": %.6e, "
           "\"spike_count\": %llu, \"spike_rate\": %.6e, \"stable_max_ns\": %.6e, "
           "\"jitter_p99_over_p50\": %.6e}",
        key, (unsigned long long)N, PCT(0.0), PCT(0.50), PCT(0.90), PCT(0.99), PCT(0.999), PCT(0.9999),
        ticks_to_ns(lt[N-1]), mean, (unsigned long long)warm, (unsigned long long)COOL,
        (unsigned long long)argmax, max_position, (double)u100/N, (double)u250/N, (double)u500/N,
        (double)u1us/N, SPIKE_NS, (unsigned long long)spikes, (double)spikes/(double)N,
        ticks_to_ns(stable_max), jitter);
    free(lt);
    #undef PCT
}

/* ============================ thread abstraction (measurement C) ============================ */
typedef struct { ring_t* r; uint64_t* lat; atomic_uint_least64_t* done; uint64_t total, warm; } cargs_t;
#if defined(_WIN32)
static unsigned __stdcall thr_consumer(void* a){ cargs_t* c=(cargs_t*)a; consumer_loop(c->r,c->lat,c->done,c->total,c->warm); return 0; }
#else
static void* thr_consumer(void* a){ cargs_t* c=(cargs_t*)a; consumer_loop(c->r,c->lat,c->done,c->total,c->warm); return 0; }
#endif

/* =============================== Windows cross-process child ================================ */
#if defined(_WIN32)
/* map a named shared region (creator makes it, child opens it) */
static void* shm_map(const char* name, size_t sz, int create, HANDLE* out){
    HANDLE h = create
        ? CreateFileMappingA(INVALID_HANDLE_VALUE, NULL, PAGE_READWRITE, (DWORD)(sz>>32), (DWORD)(sz&0xffffffff), name)
        : OpenFileMappingA(FILE_MAP_ALL_ACCESS, FALSE, name);
    if (!h) return NULL;
    void* p = MapViewOfFile(h, FILE_MAP_ALL_ACCESS, 0, 0, sz);
    *out = h; return p;
}
/* consumer-mode re-exec: nsbus.exe --consumer <tag> <total> <warm> <n_oneway> */
static int run_consumer(int argc, char** argv){
    if (argc < 6) return 2;
    const char* tag = argv[2];
    uint64_t total = strtoull(argv[3],0,10), warm = strtoull(argv[4],0,10), n_oneway = strtoull(argv[5],0,10);
    char rn[256], ln[256], dn[256];
    snprintf(rn,sizeof rn,"nsbus_ring_%s",tag); snprintf(ln,sizeof ln,"nsbus_lat_%s",tag); snprintf(dn,sizeof dn,"nsbus_done_%s",tag);
    HANDLE hr,hl,hd;
    ring_t* r = (ring_t*)shm_map(rn, sizeof(ring_t), 0, &hr);
    uint64_t* lat = (uint64_t*)shm_map(ln, sizeof(uint64_t)*n_oneway, 0, &hl);
    atomic_uint_least64_t* done = (atomic_uint_least64_t*)shm_map(dn, 64, 0, &hd);
    if (!r||!lat||!done) return 3;
    clock_init();
    consumer_loop(r, lat, done, total, warm);
    return 0;
}
#endif

int main(int argc, char** argv){
#if defined(_WIN32)
    if (argc>1 && strcmp(argv[1],"--consumer")==0) return run_consumer(argc, argv);
#endif
    clock_init();
    stabilize();
    uint64_t N_AMORT  = (argc>1)? strtoull(argv[1],0,10) : 50000000ull;
    uint64_t N_ONEWAY = (argc>2)? strtoull(argv[2],0,10) : 500000ull;
    const uint64_t WARM = 20000, TOTAL = WARM + N_ONEWAY;

    /* ---- A. amortized single-core ring put+get (portable local alloc) ---- */
    ring_t* rA = (ring_t*)local_alloc(sizeof(ring_t));
    volatile uint64_t sink = 0;
    for (uint64_t i=0;i<100000;i++){ ring_put(rA,i,i,i); uint64_t s,p; ring_get(rA,i,&s,&p); sink+=p; }
    memset(rA,0,sizeof(*rA));
    uint64_t t0 = rawclock();
    for (uint64_t i=0;i<N_AMORT;i++){ ring_put(rA,i,i,i); uint64_t s,p; if(ring_get(rA,i,&s,&p)) sink+=p; }
    uint64_t t1 = rawclock();
    double amort_ns = ticks_to_ns(t1-t0);
    double ns_per_op = amort_ns / (double)N_AMORT;
    double ops_per_s = (double)N_AMORT / (amort_ns/1e9);

    /* ---- C. cross-THREAD one-way latency (portable: two threads, one in-process ring) ---- */
    ring_t* rC = (ring_t*)local_alloc(sizeof(ring_t));
    uint64_t* latC = (uint64_t*)local_alloc(sizeof(uint64_t)*N_ONEWAY);
    atomic_uint_least64_t* doneC = (atomic_uint_least64_t*)local_alloc(64);
    atomic_store_explicit(doneC, 0, memory_order_relaxed);
    cargs_t ca = { rC, latC, doneC, TOTAL, WARM };
#if defined(_WIN32)
    HANDLE th = (HANDLE)_beginthreadex(NULL,0,thr_consumer,&ca,0,NULL);
    producer_loop(rC, doneC, TOTAL);
    WaitForSingleObject(th, INFINITE); CloseHandle(th);
#else
    pthread_t th; pthread_create(&th, NULL, thr_consumer, &ca);
    producer_loop(rC, doneC, TOTAL);
    pthread_join(th, NULL);
#endif

    /* ---- B. cross-PROCESS one-way latency ---- */
    ring_t* rB; uint64_t* latB; atomic_uint_least64_t* doneB; int have_B = 1;
#if defined(_WIN32)
    /* Windows: named shared memory + CreateProcess a --consumer child. */
    char tag[64]; snprintf(tag,sizeof tag,"%lu", (unsigned long)GetCurrentProcessId());
    char rn[256], ln[256], dn[256];
    snprintf(rn,sizeof rn,"nsbus_ring_%s",tag); snprintf(ln,sizeof ln,"nsbus_lat_%s",tag); snprintf(dn,sizeof dn,"nsbus_done_%s",tag);
    HANDLE hr,hl,hd;
    rB = (ring_t*)shm_map(rn, sizeof(ring_t), 1, &hr);
    latB = (uint64_t*)shm_map(ln, sizeof(uint64_t)*N_ONEWAY, 1, &hl);
    doneB = (atomic_uint_least64_t*)shm_map(dn, 64, 1, &hd);
    atomic_store_explicit(doneB, 0, memory_order_relaxed);
    char exe[MAX_PATH]; GetModuleFileNameA(NULL, exe, MAX_PATH);
    char cmd[1024];
    snprintf(cmd,sizeof cmd,"\"%s\" --consumer %s %llu %llu %llu", exe, tag,
             (unsigned long long)TOTAL,(unsigned long long)WARM,(unsigned long long)N_ONEWAY);
    STARTUPINFOA si; PROCESS_INFORMATION pi; ZeroMemory(&si,sizeof si); si.cb=sizeof si; ZeroMemory(&pi,sizeof pi);
    if (CreateProcessA(NULL, cmd, NULL, NULL, FALSE, 0, NULL, NULL, &si, &pi)) {
        producer_loop(rB, doneB, TOTAL);
        WaitForSingleObject(pi.hProcess, INFINITE);
        CloseHandle(pi.hProcess); CloseHandle(pi.hThread);
    } else { have_B = 0; }
#else
    /* POSIX: MAP_SHARED anonymous memory inherited across fork(). */
    rB   = (ring_t*)mmap(0, sizeof(ring_t), PROT_READ|PROT_WRITE, MAP_SHARED|MAP_ANON, -1, 0);
    latB = (uint64_t*)mmap(0, sizeof(uint64_t)*N_ONEWAY, PROT_READ|PROT_WRITE, MAP_SHARED|MAP_ANON, -1, 0);
    doneB= (atomic_uint_least64_t*)mmap(0, 64, PROT_READ|PROT_WRITE, MAP_SHARED|MAP_ANON, -1, 0);
    atomic_store_explicit(doneB, 0, memory_order_relaxed);
    if (getenv("NSBUS_RT")) { mlock(rB, sizeof(ring_t)); mlock(latB, sizeof(uint64_t)*N_ONEWAY); }
    pid_t pid = fork();
    if (pid == 0) { consumer_loop(rB, latB, doneB, TOTAL, WARM); _exit(0); }
    producer_loop(rB, doneB, TOTAL);
    waitpid(pid,0,0);
#endif

    /* ---- emit JSON ---- */
    const char* rt = getenv("NSBUS_RT")?"on":"off";
    printf("{\n");
    printf("  \"clock\": {\"source\": \"%s\", \"ns_per_tick\": %.6e, \"single_shot_res_ns\": %.6e},\n",
        CLOCK_NAME, NS_PER_TICK, NS_PER_TICK);
    printf("  \"realtime\": \"%s\", \"platform_ipc\": \"%s\",\n", rt,
#if defined(_WIN32)
        "CreateProcess+CreateFileMapping"
#else
        "fork+mmap(MAP_SHARED)"
#endif
        );
    printf("  \"amortized_ring_op\": {\"n\": %llu, \"ns_per_op\": %.6e, \"ops_per_s\": %.6e, \"sink\": %llu},\n",
        (unsigned long long)N_AMORT, ns_per_op, ops_per_s, (unsigned long long)sink);
    emit_lat_block("twothread_latency_ns", latC, N_ONEWAY, WARM); printf(",\n");
    if (have_B) { emit_lat_block("oneway_latency_ns", latB, N_ONEWAY, WARM); printf("\n"); }
    else        { printf("  \"oneway_latency_ns\": null\n"); }
    printf("}\n");
    return 0;
}
