# Hard real-time: bounding the bus latency tail

The shared-memory bus is sub-microsecond in the common case, but "near-zero latency"
for hard real-time is about the **tail** (p99.9 / max), not the median. On a
general-purpose OS the tail is dominated by the scheduler and page faults, on macOS
this stack measures a p99.9 of **several milliseconds** under load. Bounding it needs a
real-time kernel plus isolation; this is a deployment/kernel concern, and the code +
harness to validate it live here.

## Why is p99 / max so high (and what fixes it)?

Two separate facts:

* **Nanosecond latency needs the native data plane, not Python.** Python's ~2.5 µs p50 is
  the *interpreter floor*, a receive is dozens of bytecodes + an allocation, which is µs
  no matter what. The **native C poller reaches the nanosecond target**; Python can't, and
  no amount of scheduling changes that.
* **The tail (p99/max) is OS scheduler jitter**, and *that* is what real-time hardening fixes.

Measured on this Apple-Silicon Mac (clock resolution ~1 µs, so p50/p99 reading "0" means
sub-microsecond, the deltas are in nanoseconds):

| path | p50 / p99 | <100 ns | max (worst case) |
|---|---|---|---|
| **native C poller** (`shm_bench.c`) | **<100 ns** | 99.6 % | 190 µs |
| **native C poller + RT** (`SHM_BENCH_RT=1`) | **<100 ns** | **99.8 %** | **8 µs** ← ~24× tighter tail |
| Python bus (busy-poll) | ~2.5 µs | n/a | 4–30 ms |
| Python bus + macOS RT (time-constraint) | ~2.8 µs | n/a | p99 **250–340 µs** (was 2.5–11 ms) |

So the fixes, in order of impact:

1. **Run the hot path in the native poller.** 99.8 % of messages < 100 ns. The Python API
   is for control/integration; the nanosecond data plane is C (or the Rust binding).
2. **Real-time schedule the poll thread.** This bounds the *tail*:
   * **macOS**, `THREAD_TIME_CONSTRAINT_POLICY` (the CoreAudio RT mechanism; works on Apple
     Silicon). `robobus.realtime.set_realtime()` applies it; the C poller does too under
     `SHM_BENCH_RT=1`. It cut the native max **190 µs → 8 µs** and the Python p99 **~10×**.
   * **Linux**, `SCHED_FIFO` + `mlockall` + **isolated core** (`isolcpus`/`nohz_full`) via
     `robobus.realtime` / `scripts/rt_latency.py --rt --core N`. A reader that owns an
     isolated core is never descheduled → single-/low-double-digit-µs *hard* bound.
3. **Software hygiene** (already in `bench_oneway`): busy-poll, `gc.disable()` during the
   loop (a GC pause is a ms-scale max), minimal per-sample allocation, warmup.
4. **Separate cores for producer and consumer**, the paced writer busy-waits a core.

Bottom line: **nanosecond is achieved (native poller, 99.8 % < 100 ns); real-time hardening
bounds the worst case** (macOS to single-digit µs, Linux-RT+isolcpus to a hard µs bound).
macOS is not a hard-RT OS, so its max still has rare µs outliers; Linux PREEMPT_RT removes
even those.

## Getting to 100 % (zero outliers), robustly, per platform

99.8 % < 100 ns is *best-effort on a general-purpose OS*. The last 0.2 %, the µs outliers, 
are **not** the scheduler you can see: they are hardware interrupts landing on the core, CPU
C-state wake-up, frequency/thermal transitions, and (on x86) firmware **SMIs** the OS can't
even observe. So a *hard* 100 % is obtained one of two ways: **own a core the OS can put
nothing else on**, or **remove the general-purpose OS from the hot path**. The robobus poller
already does its half, it is **OS-bypass**: a pure userspace busy-poll over mmap'd memory
with **zero syscalls in the hot loop** (`native/shm_bench.c`), memory-lockable, no allocation.
The rest is kernel config + hardware, and it differs by platform:

### Linux, the practical path to effectively 100 % (a hard, bounded worst case)
Give the poll thread a core that the kernel will never touch:
```
# kernel cmdline (isolate cores 2,3):
isolcpus=2,3 nohz_full=2,3 rcu_nocbs=2,3 irqaffinity=0,1 idle=poll intel_pstate=disable processor.max_cstate=1
```
```bash
tuned-adm profile realtime            # or set governor=performance, disable turbo/thermal drift
# steer every movable IRQ off 2,3; run the poller pinned there under SCHED_FIFO + mlockall:
python scripts/rt_latency.py --rt --core 3 --budget-us 5     # (or the C poller with SHM_BENCH_RT=1)
```
With a **PREEMPT_RT** kernel + a fully isolated core, nothing else is *runnable* on that CPU,
IRQs and RCU callbacks are elsewhere, and the core never changes frequency or sleeps, so the
poller cannot be preempted. In practice this is 100 % within a fixed ns bound (the only
remaining variance is last-level-cache / memory-bus, which is nanosecond-scale). This is how
industrial/robotics/HFT hard-RT is actually deployed. `robobus.realtime` (SCHED_FIFO +
`pin_cpu` + `mlockall`) provides the userspace half.

### Windows, best-effort (no hard guarantee)
`robobus.realtime.set_realtime()` sets `REALTIME_PRIORITY_CLASS` + `TIME_CRITICAL` +
1 ms timer + **MMCSS "Pro Audio"**, plus `pin_cpu()` (`SetThreadAffinityMask`) and
`lock_all_memory()` (working-set wiring). That gets you the same *tail-bounding* as macOS,
but Windows is not an RTOS, treat it as soft real-time.

### macOS, best-effort (no hard guarantee)
`THREAD_TIME_CONSTRAINT_POLICY` (shown above: max 190 µs → 8 µs). macOS has no core isolation
and no RT kernel, so rare µs outliers remain. Good enough for soft real-time; not certifiable.

### True, certifiable 100 %, take the GP OS out of the loop
For safety-critical/avionics-grade determinism, run the hot path where there is no
general-purpose scheduler at all: a **bare-metal isolated core**, an **RTOS** (Zephyr, QNX,
VxWorks, FreeRTOS), or an **FPGA / MCU coprocessor**. The robobus ring layout is a handful of
atomic loads over shared memory, it ports to a bare-metal poll loop unchanged (the wire
format in [PROTOCOL.md](PROTOCOL.md) is language- and OS-agnostic), so the same frames flow
between the RTOS core and the Linux/Python side. That is the only route to a *provable* 100 %.

**Summary:** robust hard-100 % = Linux PREEMPT_RT + isolated core (deploy) or an RTOS/bare-metal
core (certify). macOS/Windows give a bounded best-effort tail, not a guarantee, which is a
property of those kernels, not of robobus.

## What robobus provides

* `robobus.realtime`, `set_realtime()` (Linux `SCHED_FIFO`, macOS QoS), `pin_cpu(core)`
  (Linux affinity), `lock_all_memory()` (`mlockall`, no page-fault stalls).
* `scripts/rt_latency.py`, measures the bus one-way latency tail (p50/p99/**p99.9**/max)
  optionally under CPU/cache contention and with the hardening above, and **gates on a
  p99.9 budget** (exit non-zero if exceeded) so it can pass/fail in CI.

## The Linux setup that makes the tail bounded

1. **PREEMPT_RT kernel** (mainline since 6.12, or the `-rt` patchset). The harness prints
   `PREEMPT_RT=True/False` so a run is self-documenting.
2. **Isolate cores**, kernel cmdline: `isolcpus=2,3 nohz_full=2,3 rcu_nocbs=2,3`.
   Pin the bus reader there with `--core 3` (the writer/echo can share another isolated core).
3. **Privilege**, `SCHED_FIFO` + `mlockall` need `CAP_SYS_NICE` (run under `sudo` or grant
   the cap). The harness reports whether RT scheduling was actually acquired.
4. **Tune**, disable frequency scaling (`cpupower frequency-set -g performance`), and keep
   IRQs off the isolated cores (`irqaffinity=`).

## Running it

```bash
# on the PREEMPT_RT box, cores 2,3 isolated:
sudo python scripts/rt_latency.py --rt --core 3 --stress 4 --budget-us 50
# -> ... p99.9=<N> us   PASS/FAIL vs 50us
make rt-latency          # convenience wrapper (no gate)
```

Expected: on a correctly-configured PREEMPT_RT host with isolated cores, the bus p99.9
under load stays in the **single-to-low-double-digit microseconds**; the exact budget is
hardware-specific, so set `--budget-us` from a baseline run on your target.

## CI

`.github/workflows/ci.yml` has a `hard-rt` job that runs this **only** on a self-hosted
runner labelled `self-hosted, linux, realtime` (gated by the `HAVE_RT_RUNNER` repo
variable); it no-ops on GitHub-hosted runners, which are not real-time. Register a
PREEMPT_RT machine as a self-hosted runner to make the tail a merge gate.

## Honest limits

macOS and GitHub-hosted Linux cannot give hard-RT guarantees, the harness runs there
(and reports the tail) but the number is best-effort, not bounded. Hard real-time is a
property of the **kernel + isolation + hardware**, which is why this is validated on a
dedicated RT runner rather than asserted in the portable test suite.
