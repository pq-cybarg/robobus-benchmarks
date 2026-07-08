# Forcing the tail to ~100%: hardware & firmware workarounds

`docs/REALTIME.md` bounds the *scheduler* tail. This document goes deeper — the exotic
hardware/firmware tricks that attack the **last 0.2%** of µs outliers, so the native poller
approaches a *guaranteed* ns-scale worst case. The outliers come from four independent
layers; you have to beat all four. The robobus ring is already **OS-bypass** (userspace
busy-poll over mmap'd shared memory, zero syscalls in the hot loop), so what's left is
memory, CPU-state, and firmware jitter.

| Layer | Source of the outlier | The workaround | Ceiling |
|---|---|---|---|
| 1. OS preemption | scheduler, IRQs, RCU, timer tick | isolated core + PREEMPT_RT (REALTIME.md) | hard bound (Linux) |
| 2. Memory / cache | DRAM refresh, LLC eviction, TLB miss | **cache pseudo-lock**, **hedged channels**, huge pages | near-eliminated |
| 3. CPU state | C-state wake-up, freq/turbo, SMT | idle=poll, perf governor, UMWAIT/WFE | ns-scale |
| 4. Firmware | **SMIs** (invisible to the OS) | detect + BIOS suppression | platform-dependent |

## Layer 2 — the memory/DRAM tail (the deepest tricks)

Even with a core to yourself, a memory read can stall for hundreds of ns to µs when the
DRAM row is mid-**refresh** or the line was evicted from LLC. Two ways to beat it:

### (a) Intel Cache Pseudo-Locking (CAT / RDT / resctrl) — *never touch DRAM*
Intel **Cache Allocation Technology** + Linux **resctrl** can **pin a memory region into
L2/L3** so it is never evicted by any other core/thread — every access is a cache hit,
deterministic, and DRAM refresh becomes irrelevant. Load the ring into a pseudo-locked
region and the poll loop runs entirely from cache.
[[Intel: Introducing Cache Pseudo-Locking]](https://events19.linuxfoundation.org/wp-content/uploads/2017/11/Introducing-Cache-Pseudo-Locking-to-Reduce-Memory-Access-Latency-Reinette-Chatre-Intel.pdf),
[[kernel resctrl.rst]](https://www.kernel.org/doc/Documentation/x86/resctrl.rst).
Setup (model-specific — needs `cat_l2`/`cat_l3` in `/proc/cpuinfo`): see
`scripts/cache_pseudolock.sh`. Caveat: only some Intel SKUs expose it; not on AMD/ARM/Apple.

### (b) "TailSlayer" — hedge across independent DRAM channels (works everywhere)
When you *can't* lock cache, dodge the DRAM refresh stall instead. LaurieWired's
**TailSlayer** cut *worst-case* memory latency by **up to 93%** by **duplicating the working
set across memory-addressing boundaries so each copy lands on a different physical memory
channel with independent refresh timing**, then reading both copies on two cores and taking
whichever isn't mid-refresh
[[Tom's Hardware]](https://www.tomshardware.com/software/ambitious-hacker-reduces-worst-case-memory-latency-by-up-to-93-percent-but-with-severe-downsides-1960s-bottleneck-overcome-by-hedging-memory-accesses-to-avoid-running-into-dram-refresh-stalls).
Mapped to robobus: mirror the ring into two buffers placed a channel-stride apart (so they
map to different DRAM channels/ranks), have a hedge reader on a second isolated core, and
consume whichever slot resolves first. Cost: 2× memory bandwidth + a core — the "severe
downside" — but it directly kills the refresh-induced tail on Intel **and** ARM.

### (c) Cheaper memory wins (always do these)
* **Huge pages** (2 MiB / 1 GiB, `MAP_HUGETLB`) — the ring fits in one or two TLB entries, so
  no TLB-miss stalls on the hot path. Implemented in `native/shm_bench.c` (`SHM_BENCH_HUGE=1`).
* **Cache-line isolation** — keep the writer's cursor on its own 64 B line (no false sharing
  with reader-touched fields).
* **Non-temporal / streaming stores** (`movnti` / `_mm_stream`, ARM `STNP`) for the *payload*
  so it doesn't evict the hot cursor/seq lines from cache.
* **Prefetch** the next slot (`__builtin_prefetch`) a few iterations ahead.
* **NUMA locality** — allocate the ring on the same NUMA node as the poll core (`numactl
  --membind`), so reads never cross the interconnect.

## Layer 3 — CPU-state jitter

* **C-states** — an idle core takes µs to wake from a deep C-state. Force it awake:
  `idle=poll intel_idle.max_cstate=0 processor.max_cstate=1`. A busy-poller never idles, so
  this mostly matters for the *writer* side and for wakeups.
* **Frequency/turbo transitions** add latency — pin the clock: `cpupower frequency-set -g
  performance`, disable turbo, keep the die thermally steady.
* **SMT/hyperthreading** — a busy sibling steals the core's execution ports; isolate or
  disable the sibling of the poll core.
* **UMWAIT / UMONITOR / TPAUSE (x86)** — the low-power way to *busy-wait*. `UMONITOR` arms a
  cache line (the cursor); `UMWAIT` parks the core in the shallow **C0.1/C0.2** substate until
  the writer writes that line — near-instant wakeup, no power/thermal burn, and no sibling
  starvation (unlike a raw spin loop)
  [[UMWAIT — felixcloutier]](https://www.felixcloutier.com/x86/umwait),
  [[LWN: user wait instructions]](https://lwn.net/Articles/790812/). Available Tremont / Ice
  Lake+; AMD has `MONITORX/MWAITX`. **ARM equivalent:** `WFE` (wait-for-event) on an exclusive
  monitor of the cursor address; the writer's store + `SEV`/event-stream wakes it. This lets
  you keep ~spin-latency wakeup without pegging the core.

## Layer 4 — firmware SMIs (the classic hard-RT killer)

**System Management Interrupts** switch the CPU into SMM to run firmware code the OS cannot
see, preempt, or bound — a single SMI can stall a core for µs–ms
[[Linux Foundation RT wiki: SMI latency]](https://wiki.linuxfoundation.org/realtime/documentation/howto/debugging/smi-latency/start).

* **Detect** — `hwlatdetect` / the kernel `hwlat` tracer stops the machine, polls the TSC, and
  any gap with interrupts off *must* be an SMI
  [[kernel: Hardware Latency Detector]](https://www.kernel.org/doc/html/latest/trace/hwlat_detector.html),
  [[hwlatdetect(8)]](https://manpages.debian.org/testing/rt-tests/hwlatdetect.8.en.html). On
  x86 also read **`MSR_SMI_COUNT` (MSR 0x34)** before/after a run to count SMIs.
* **Reduce** — in BIOS/UEFI: enable the vendor "low-latency"/"determinism" profile, and disable
  **USB legacy emulation**, **hardware health/thermal polling**, and other periodic SMI sources.
  Some server platforms can get to ~0 SMIs; consumer/laptop firmware (incl. Apple) often can't,
  which is why certifiable determinism ultimately means an RTOS/bare-metal core with no SMM.

## Also: turn off the mitigations tax (trusted RT box)

Spectre/Meltdown mitigations add overhead to every syscall/context switch/indirect branch.
On a dedicated, physically-trusted RT machine, `mitigations=off` on the kernel cmdline removes
that variable cost (a real jitter source). Only on a box where the security trade-off is
acceptable.

## Per-platform: how close to 100 % you can actually get

| platform | isolate core | cache lock | UMWAIT/WFE | SMI-free | realistic result |
|---|---|---|---|---|---|
| **Linux x86 (Intel) + PREEMPT_RT** | ✅ isolcpus | ✅ CAT pseudo-lock | ✅ UMWAIT | BIOS-dependent | **effectively 100 %**, hard ns bound |
| **Linux ARM64 + PREEMPT_RT** | ✅ isolcpus | TCM (Cortex-R) / ✗ | ✅ WFE | usually clean | **effectively 100 %** |
| **Windows** | affinity only | ✗ | ✅ (x86) | ✗ | soft real-time (best-effort) |
| **macOS / Apple Silicon** | ✗ (no isolcpus) | ✗ | ✗ (no user WFE hook) | ✗ (SMC) | ~99.8 %, µs outliers remain |
| **RTOS / bare-metal / FPGA** | N/A (no GP OS) | SRAM/TCM | native | no SMM | **provable 100 %** |

**Bottom line:** a truly *guaranteed* 100 % is only reachable by removing the general-purpose
OS from the hot path (RTOS/bare-metal/FPGA). The best you can force on a general-purpose OS is
**Linux + PREEMPT_RT + isolated core + cache pseudo-lock (or TailSlayer hedging) + UMWAIT/WFE +
an SMI-clean BIOS**, which in practice yields no observable outliers over billions of messages —
"almost-guaranteed 100 %". Because the robobus wire format is OS/arch-agnostic
([PROTOCOL.md](PROTOCOL.md)), the same frames flow between that hardened core and everything else.

## Adaptive: probe the hardware, apply what it supports

Because every trick here is hardware-specific, robobus **detects capabilities at runtime and
adapts** rather than hard-coding any of them — `robobus.determinism`:

```
$ robobus determinism                     # report what THIS machine supports + recommendations
$ python -c "from robobus.determinism import optimize; print(optimize(core=3))"
```

`capabilities()` probes CPU vendor/arch, `waitpkg` (UMWAIT), CAT/resctrl (cache pseudo-lock),
`isolcpus`, PREEMPT_RT, huge pages, NUMA nodes, macOS time-constraint, spare cores (TailSlayer).
`optimize()` then applies the best available combination — pin to an isolated core *if one
exists*, RT policy, `mlockall` — and returns the rest as actionable recommendations. The native
poller is adaptive too: it picks the spin primitive at compile+runtime (`PAUSE` on x86,
`YIELD` on ARM) and reports `+umwait-capable` / `+wfe-capable` when the CPU exposes the
low-power monitor-wait.

## What robobus implements vs. what is deployment/BIOS

* **Implemented (code):** OS-bypass busy-poll (no hot-loop syscalls); **adaptive capability
  probe + apply** (`robobus.determinism`); `robobus.realtime` (SCHED_FIFO / macOS
  time-constraint / Windows REALTIME+MMCSS, `pin_cpu`, `mlockall`); the C poller's RT policy
  (`SHM_BENCH_RT=1`) and arch-adaptive spin hint (`PAUSE`/`YIELD`) with runtime WAITPKG/WFE
  detection.
* **Deployment (scripts/docs):** the kernel cmdline recipe (REALTIME.md),
  `scripts/cache_pseudolock.sh` (resctrl CAT pseudo-lock), `scripts/rt_latency.py` gate, and the
  SMI-detection + BIOS checklist above.
* **Advanced / opt-in:** full UMWAIT/WFE monitor-wait, huge-page ring, and the TailSlayer
  dual-channel hedge reader are documented here with the exact instructions/APIs; enable per the
  capability report on hardware that supports them.
* **Not software:** SMI suppression (BIOS), memory-channel placement for TailSlayer (board/BIOS),
  and true certifiable 100 % (RTOS/FPGA).

## Sources
- Tom's Hardware — LaurieWired "TailSlayer" (hedge DRAM channels, up to 93% worst-case): https://www.tomshardware.com/software/ambitious-hacker-reduces-worst-case-memory-latency-by-up-to-93-percent-but-with-severe-downsides-1960s-bottleneck-overcome-by-hedging-memory-accesses-to-avoid-running-into-dram-refresh-stalls
- Intel — Introducing Cache Pseudo-Locking: https://events19.linuxfoundation.org/wp-content/uploads/2017/11/Introducing-Cache-Pseudo-Locking-to-Reduce-Memory-Access-Latency-Reinette-Chatre-Intel.pdf
- Linux kernel — resctrl / Intel RDT: https://www.kernel.org/doc/Documentation/x86/resctrl.rst
- UMWAIT — Felix Cloutier x86 reference: https://www.felixcloutier.com/x86/umwait
- LWN — x86 user wait instructions (UMWAIT/UMONITOR/TPAUSE): https://lwn.net/Articles/790812/
- Linux kernel — Hardware Latency Detector: https://www.kernel.org/doc/html/latest/trace/hwlat_detector.html
- hwlatdetect(8) manpage: https://manpages.debian.org/testing/rt-tests/hwlatdetect.8.en.html
- Linux Foundation RT wiki — SMI latency debugging: https://wiki.linuxfoundation.org/realtime/documentation/howto/debugging/smi-latency/start
- Red Hat — Optimizing RHEL for Real Time (hardware/firmware latency): https://docs.redhat.com/en/documentation/red_hat_enterprise_linux_for_real_time/9/html/optimizing_rhel_9_for_real_time_for_low_latency_operation/assembly_running-and-interpreting-hardware-and-firmware-latency-tests_optimizing-rhel9-for-real-time-for-low-latency-operation
