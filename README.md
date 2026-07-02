# robobus benchmarks

Full-system benchmarks for **robobus** — a post-quantum, real-time robotics middleware:
a sub-microsecond shared-memory bus + CNSA 2.0 post-quantum crypto (FIPS 203 ML-KEM,
FIPS 204 ML-DSA) + PQC-hardened DDS-Security.

### 📊 Live site: **https://pq-cybarg.github.io/robobus-benchmarks/**

One portable, **capability-detecting** script measures every layer and records whatever a given
platform lacks as **SKIPPED** — so the *identical* script runs on macOS, Windows, every supported
Linux, Android and iOS. Re-run it on a target to add that platform's column.

```bash
python bench/run_benchmarks.py          # full run  -> bench/results/latest-<platform>.json
python bench/run_benchmarks.py --quick  # fast pass
python bench/render_report.py           # -> bench/reports/BENCHMARKS.md + bench/site/index.html
```

Optional backends unlock more rows: `cryptography` (AEAD, ECDH, classical signatures),
`liboqs-python` (ML-KEM, ML-DSA), `argon2-cffi` (Argon2id). None are required — missing ones just
produce SKIPPED rows.

## Read the layers (this is the whole point)

Latency is not one number. The stack spans nine orders of magnitude and each layer has its own
regime — conflating them is how benchmarks lie:

| Layer | Regime | Apple M5 baseline |
|---|---|---|
| Shared-memory bus op (amortized) | **nanoseconds** | 3.9 ns/op |
| Bus one-way IPC latency | **nanoseconds** | p50 83 ns (98%+ < 100 ns, RT) |
| Per-message AEAD (AES-256-GCM) | **ns/byte** | multi-GB/s |
| Key agreement / rekey (ECDH+ML-KEM) | **microseconds** | 129–142 µs |
| Full authenticated handshake | **µs → ~1 ms** | 598 µs (NIST-1) → 1.15 ms (CNSA 2.0) |
| DDS-Security handshake (w/ transport) | **milliseconds** | ~2.5 ms (RTPS round-trips) |

The runtime hot path is ns/GB-s. Handshakes are a **one-time** per-peer cost (sign-bound by
ML-DSA — ~212µs per lattice signature) amortized to zero over a session.

## Methodology notes (honest measurement)

- **Nanosecond timing.** `bench/native/nsbus.c` uses the high-resolution clock (mach 41.67 ns /
  `CLOCK_MONOTONIC_RAW`) plus **amortized batching** (time N ops in one read → sub-ns mean),
  because a single `clock_gettime(CLOCK_MONOTONIC)` read on macOS is only ~1 µs granular and would
  report sub-µs latencies as 0.
- **Warmup.** The one-way latency measurement discards a 20k-message warmup so `fork` / first-
  schedule / cold-cache / first-touch page-faults don't pollute the steady-state tail. The tool
  reports *where* the max sits (send-order position) so cold-start vs. mid-run jitter is visible.
- **RT hardening** (macOS time-constraint policy) squeezes the tail — e.g. p99.9 87 µs → 2.1 µs.
- **DDS handshakes** are reported as the *isolated* FSM window (begin → OK), not the ~100 ms full
  process (which is startup + SPDP discovery + teardown).

## CI

`.github/workflows/benchmarks.yml` runs the identical harness on GitHub's **ubuntu / macOS /
Windows** runners and refreshes this site. Those runners are **virtualized** (shared vCPUs, no RT);
each run self-labels as `virtualized` so its columns are for cross-platform coverage and relative
comparison — not bare-metal nanosecond claims.

---

Source & full project (private): `pq-cybarg/robobus`. MIT-licensed harness.
