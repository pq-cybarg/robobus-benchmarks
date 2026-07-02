# Real-time & Determinism

The mean bus latency is nanoseconds; the engineering challenge is the **tail**. A single preempted
message turns a 83 ns p50 into a µs-scale p99.9. This page is how that tail is bounded and measured
honestly.

## Measuring nanoseconds correctly

A single `clock_gettime(CLOCK_MONOTONIC)` read on macOS is only ~1 µs granular, so naive
measurement reports sub-µs latencies as **0**. `bench/native/nsbus.c` fixes this two ways:

1. **High-resolution clock** — `mach_absolute_time()` (Apple Silicon: **41.67 ns/tick**) or
   `CLOCK_MONOTONIC_RAW` elsewhere.
2. **Amortized batching** — time N ops under one clock read and divide → sub-ns *mean* resolution,
   independent of clock granularity. (This is how "3.9 ns/op" is a real number, not a rounding of 0.)

**Warmup matters.** The one-way measurement discards a 20 000-message warmup so `fork` /
first-schedule / cold-cache / first-touch page-faults don't pollute the steady-state tail — and it
records *where* the max sits in send-order, so cold-start (position ≈ 0) is distinguishable from
mid-run scheduler jitter (random position). Empirically, after warmup the residual max lands
mid-run → it's genuine preemption, not cold-start; warmup alone cut p99.9 from ~87 µs to ~8.6 µs.

## Bounding the tail

| Lever | Platform | Effect |
|---|---|---|
| Time-constraint scheduling policy | macOS (Mach) | p99.9 87 µs → **2.1 µs**, max 202 µs → 37 µs |
| `SCHED_FIFO` + `mlockall` + CPU pin | Linux | removes scheduler + paging jitter |
| PREEMPT_RT | Linux-RT | bounded worst-case (hard-RT) |
| Cache pseudo-lock (Intel CAT) | Linux/Intel | eviction-free working set |
| UMWAIT / WFE wait | x86 / ARM | low-power spin without cache thrash |
| DRAM-channel hedging, SMI suppression | firmware | shave rare µs spikes |

The adaptive `robobus determinism` probe detects which levers a host supports (umwait, wfe,
core-isolation, PREEMPT_RT, cache-pseudolock, hugepages, time-constraint, constant-TSC, …) and
chooses the wait strategy accordingly — so the same code adapts from a laptop to an isolated RT core.

## Honest limits

- **Bare-metal only for the tightest tail.** macOS gives soft-RT (time-constraint); hard-RT bounds
  need Linux PREEMPT_RT on isolated cores.
- **Virtualized environments (CI, cloud) are not RT.** The benchmark harness self-labels
  `virtualized` runs (GitHub Actions ubuntu/macos/windows) so their tails aren't mistaken for
  bare-metal — good for coverage and relative comparison, not absolute nanosecond claims.
- **The mean is nanoseconds; the guarantee is about the tail.** See [Benchmarks](Benchmarks) for
  the full distributions (p50/p90/p99/p99.9/max, with and without RT).
