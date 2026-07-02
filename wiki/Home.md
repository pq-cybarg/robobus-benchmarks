# robobus

**Post-quantum, real-time robotics middleware** — a hardened ROS 1 + ROS 2 + LabStreamingLayer
stack built around a **sub-microsecond shared-memory bus**, **CNSA 2.0 post-quantum cryptography**
(FIPS 203 ML-KEM + FIPS 204 ML-DSA), and **PQC-hardened DDS-Security** for both Fast DDS and
Eclipse Cyclone DDS.

> ⚠️ Benchmarks were measured **on macOS (Apple M5)** so far. They are CPU/OS/build-specific and
> are not portable claims — the value is the *method*: one script runs everywhere and each platform
> reports what it can.

## Pages

- **[Benchmarks](Benchmarks)** — full-system numbers across every layer (nanosecond bus → µs PQC →
  GB/s AEAD → live DDS handshakes). Live HTML: https://pq-cybarg.github.io/robobus-benchmarks/
- **[Architecture](Architecture)** — the shared-memory bus + the three-runtime fabric.
- **[PQC DDS-Security](PQC-DDS-Security)** — hybrid ECDH+ML-KEM key agreement + ML-DSA-87 identity
  signatures for Fast DDS & Cyclone DDS.
- **[Real-time & Determinism](Real-Time-and-Determinism)** — how the nanosecond tail is bounded.

## The one thing to understand: read the latency layers

Latency is not a single number — the stack spans nine orders of magnitude, and conflating the
layers is how benchmarks mislead. On Apple M5 (bare metal):

| Layer | Regime | Result |
|---|---|---|
| Shared-memory bus op (amortized) | **nanoseconds** | 3.9 ns/op (~254M ops/s) |
| Bus one-way IPC latency | **nanoseconds** | p50 83 ns · 98%+ < 100 ns (RT) |
| Per-message AEAD (AES-256-GCM) | **ns/byte** | multi-GB/s |
| Key agreement / rekey (ECDH+ML-KEM) | **microseconds** | 129–142 µs |
| Full authenticated handshake | **µs → ~1 ms** | 598 µs (NIST-1) → 1.15 ms (CNSA 2.0) |
| DDS-Security handshake (w/ transport) | **milliseconds** | ~2.5 ms (RTPS round-trips) |

The **runtime hot path is ns/GB-s**. Handshakes are a **one-time** per-peer cost (sign-bound by
ML-DSA — ~212 µs per lattice signature) amortized to zero over a session. Milliseconds only appear
in one-time setup + DDS transport, never in the steady state.

## Reproduce

```bash
python bench/run_benchmarks.py     # full run  (capability-detecting; skips what a platform lacks)
python bench/render_report.py      # -> bench/reports/BENCHMARKS.md + bench/site/index.html
```

The identical script is designed to run on macOS, Windows, every supported Linux, Android and iOS,
and in CI (`.github/workflows/benchmarks.yml` — ubuntu/macos/windows runners, self-labelled
*virtualized*).
