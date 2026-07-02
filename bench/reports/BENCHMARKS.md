# robobus / PQC-DDS — full-system benchmarks

> **Scope.** Every capability of the stack — post-quantum and classical key encapsulation, hybrid key agreement, digital signatures, authenticated encryption, hashing, MACs, key-derivation, live DDS-Security handshakes, and the robobus bus — measured across all available modes, sizes and techniques by **one script** (`bench/run_benchmarks.py`).

> ⚠️ **Platform caveat.** These figures were measured **on macOS only** so far. They are inherently CPU-, OS- and build-specific and are **not** portable claims. The value here is the *method*: the identical script is designed to run on macOS, Windows, every supported Linux, Android and iOS, skipping only what a given platform lacks. Re-run it on each target to populate that platform's column.

_Generated 2026-07-02 20:19 UTC from `bench/results/latest-*.json`._

## Platforms measured

### Darwin · Apple M1 (Virtual)

- **OS:** Darwin 24.6.0 (macOS-15.7.7-arm64-arm-64bit)
- **CPU:** Apple M1 (Virtual) — 3 cores, 7 GB RAM
- **Python:** 3.12.10 (CPython)
- **Crypto backends:** cryptography 49.0.0, oqs 0.15.0, argon2 25.1.0, psutil 7.2.2

### Darwin · Apple M5

- **OS:** Darwin 25.1.0 (macOS-26.1-arm64-arm-64bit)
- **CPU:** Apple M5 — 10 cores, 32 GB RAM
- **Python:** 3.12.13 (CPython)
- **Crypto backends:** cryptography 49.0.0, oqs 0.15.0, argon2 25.1.0, psutil 7.2.2

### Linux · x86_64

- **OS:** Linux 6.17.0-1018-azure (Linux-6.17.0-1018-azure-x86_64-with-glibc2.39)
- **CPU:** x86_64 — 2 cores, 15 GB RAM
- **Python:** 3.12.13 (CPython)
- **Crypto backends:** cryptography 49.0.0, oqs 0.15.0, argon2 25.1.0, psutil 7.2.2

### Windows · AMD64

- **OS:** Windows 2025Server (Windows-2025Server-10.0.26100-SP0)
- **CPU:** AMD64 Family 25 Model 1 Stepping 1, AuthenticAMD — 2 cores, 15 GB RAM
- **Python:** 3.12.10 (CPython)
- **Crypto backends:** cryptography 49.0.0, oqs 0.15.0, argon2 25.1.0, psutil 7.2.2

## How to reproduce

```bash
# one script, every platform — measures what it can, skips the rest with a reason
python bench/run_benchmarks.py            # full run
python bench/run_benchmarks.py --quick    # fast pass
python bench/render_report.py             # regenerate this report + the HTML site
```

Optional backends unlock more rows: `cryptography` (AEAD, ECDH, classical signatures), `oqs`/liboqs (ML-KEM, ML-DSA), `argon2-cffi` (Argon2id). Absent backends produce **SKIPPED** rows — never a crash — which is exactly how the same script stays valid on constrained platforms (e.g. stock Android/iOS Python).

## Shared-memory bus — nanosecond latency (native SPSC ring)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ring put+get, amortized 1-core` | realtime=off, clock_ns_per_tick=41.66667 | classical | 131,354,300 ops/s (7.6 ns/op) | — | — | ok · pure ring op cost; clock res 41.7 ns |
| `cross-process one-way latency` | realtime=off, warmup_msgs=20000 | classical | 83.3 ns | 83.3 ns | 1.07 ms | ok · 51.8% <100 ns; 20000 msgs warmup discarded; max at 31% of run (mid-run scheduler jitter); no RT |
| `ring put+get, amortized 1-core (RT)` | realtime=on, clock_ns_per_tick=41.66667 | classical | 80,145,540 ops/s (12.5 ns/op) | — | — | ok · pure ring op cost; clock res 41.7 ns |
| `cross-process one-way latency (RT)` | realtime=on, warmup_msgs=20000 | classical | 83.3 ns | 83.3 ns | 985.29 µs | ok · 55.2% <100 ns; 20000 msgs warmup discarded; max at 58% of run (mid-run scheduler jitter); RT time-constraint policy |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ring put+get, amortized 1-core` | realtime=off, clock_ns_per_tick=41.66667 | classical | 237,350,100 ops/s (4.2 ns/op) | — | — | ok · pure ring op cost; clock res 41.7 ns |
| `cross-process one-way latency` | realtime=off, warmup_msgs=20000 | classical | 83.3 ns | 83.3 ns | 83.3 ns | ok · 99.1% <100 ns; 20000 msgs warmup discarded; max at 62% of run (mid-run scheduler jitter); no RT |
| `ring put+get, amortized 1-core (RT)` | realtime=on, clock_ns_per_tick=41.66667 | classical | 284,140,400 ops/s (3.5 ns/op) | — | — | ok · pure ring op cost; clock res 41.7 ns |
| `cross-process one-way latency (RT)` | realtime=on, warmup_msgs=20000 | classical | 83.3 ns | 83.3 ns | 125.0 ns | ok · 98.4% <100 ns; 20000 msgs warmup discarded; max at 1% of run (cold-start residue); RT time-constraint policy |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ring put+get, amortized 1-core` | realtime=off, clock_ns_per_tick=1.0 | classical | 483,752,400 ops/s (2.1 ns/op) | — | — | ok · pure ring op cost; clock res 1.0 ns |
| `cross-process one-way latency` | realtime=off, warmup_msgs=20000 | classical | 72.0 ns | 72.0 ns | 93.0 ns | ok · 99.0% <100 ns; 20000 msgs warmup discarded; max at 9% of run (mid-run scheduler jitter); no RT |
| `ring put+get, amortized 1-core (RT)` | realtime=on, clock_ns_per_tick=1.0 | classical | 479,194,800 ops/s (2.1 ns/op) | — | — | ok · pure ring op cost; clock res 1.0 ns |
| `cross-process one-way latency (RT)` | realtime=on, warmup_msgs=20000 | classical | 71.0 ns | 71.0 ns | 90.0 ns | ok · 99.1% <100 ns; 20000 msgs warmup discarded; max at 35% of run (mid-run scheduler jitter); RT time-constraint policy |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `ring_op_amortized` | — | classical | — | ⚠️ skipped: no fork/mmap on Windows |
| `oneway_latency` | — | classical | — | ⚠️ skipped: no fork/mmap on Windows |

## Key encapsulation & key exchange (ML-KEM vs classical)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `X25519` | op=keygen | classical | 7,575 ops/s | 100.17 µs | 555.01 µs | ok |
| `X25519` | op=derive | classical | 4,837 ops/s | 176.46 µs | 670.82 µs | ok |
| `ECDH-P256` | op=keygen | classical | 34,758 ops/s | 18.29 µs | 237.37 µs | ok |
| `ECDH-P256` | op=derive | classical | 17,849 ops/s | 47.92 µs | 182.29 µs | ok |
| `ML-KEM-512` | op=keygen | PQC | 57,995 ops/s | 15.88 µs | 48.55 µs | ok |
| `ML-KEM-512` | op=encapsulate | PQC | 46,070 ops/s | 16.88 µs | 110.05 µs | ok |
| `ML-KEM-512` | op=decapsulate | PQC | 75,094 ops/s | 12.00 µs | 33.50 µs | ok |
| `ML-KEM-768` | op=keygen | PQC | 45,005 ops/s | 20.17 µs | 26.54 µs | ok |
| `ML-KEM-768` | op=encapsulate | PQC | 34,765 ops/s | 22.62 µs | 105.68 µs | ok |
| `ML-KEM-768` | op=decapsulate | PQC | 40,283 ops/s | 18.46 µs | 119.58 µs | ok |
| `ML-KEM-1024` | op=keygen | PQC | 31,667 ops/s | 28.88 µs | 90.50 µs | ok |
| `ML-KEM-1024` | op=encapsulate | PQC | 32,009 ops/s | 30.08 µs | 53.19 µs | ok |
| `ML-KEM-1024` | op=decapsulate | PQC | 37,381 ops/s | 26.71 µs | 36.67 µs | ok |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `X25519` | op=keygen | classical | 73,043 ops/s | 13.21 µs | 16.58 µs | ok |
| `X25519` | op=derive | classical | 63,927 ops/s | 15.29 µs | 40.01 µs | ok |
| `ECDH-P256` | op=keygen | classical | 159,199 ops/s | 6.08 µs | 21.26 µs | ok |
| `ECDH-P256` | op=derive | classical | 38,950 ops/s | 24.29 µs | 29.71 µs | ok |
| `ML-KEM-512` | op=keygen | PQC | 60,963 ops/s | 8.50 µs | 27.43 µs | ok |
| `ML-KEM-512` | op=encapsulate | PQC | 72,479 ops/s | 9.04 µs | 9.46 µs | ok |
| `ML-KEM-512` | op=decapsulate | PQC | 52,007 ops/s | 7.71 µs | 75.54 µs | ok |
| `ML-KEM-768` | op=keygen | PQC | 31,470 ops/s | 28.21 µs | 123.40 µs | ok |
| `ML-KEM-768` | op=encapsulate | PQC | 48,368 ops/s | 28.62 µs | 106.50 µs | ok |
| `ML-KEM-768` | op=decapsulate | PQC | 89,024 ops/s | 10.96 µs | 13.38 µs | ok |
| `ML-KEM-1024` | op=keygen | PQC | 62,057 ops/s | 15.83 µs | 18.79 µs | ok |
| `ML-KEM-1024` | op=encapsulate | PQC | 59,386 ops/s | 16.54 µs | 19.79 µs | ok |
| `ML-KEM-1024` | op=decapsulate | PQC | 61,113 ops/s | 15.88 µs | 20.08 µs | ok |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `X25519` | op=keygen | classical | 27,590 ops/s | 35.39 µs | 47.22 µs | ok |
| `X25519` | op=derive | classical | 27,782 ops/s | 35.33 µs | 44.18 µs | ok |
| `ECDH-P256` | op=keygen | classical | 63,685 ops/s | 15.03 µs | 26.96 µs | ok |
| `ECDH-P256` | op=derive | classical | 18,383 ops/s | 53.45 µs | 63.50 µs | ok |
| `ML-KEM-512` | op=keygen | PQC | 45,425 ops/s | 21.09 µs | 36.16 µs | ok |
| `ML-KEM-512` | op=encapsulate | PQC | 43,149 ops/s | 22.25 µs | 37.73 µs | ok |
| `ML-KEM-512` | op=decapsulate | PQC | 64,669 ops/s | 14.94 µs | 25.34 µs | ok |
| `ML-KEM-768` | op=keygen | PQC | 35,081 ops/s | 27.47 µs | 42.99 µs | ok |
| `ML-KEM-768` | op=encapsulate | PQC | 34,427 ops/s | 28.04 µs | 43.51 µs | ok |
| `ML-KEM-768` | op=decapsulate | PQC | 44,226 ops/s | 21.89 µs | 35.07 µs | ok |
| `ML-KEM-1024` | op=keygen | PQC | 28,843 ops/s | 33.47 µs | 48.79 µs | ok |
| `ML-KEM-1024` | op=encapsulate | PQC | 27,935 ops/s | 34.54 µs | 50.33 µs | ok |
| `ML-KEM-1024` | op=decapsulate | PQC | 32,908 ops/s | 29.66 µs | 40.52 µs | ok |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `X25519` | op=keygen | classical | 23,817 ops/s | 40.40 µs | 67.80 µs | ok |
| `X25519` | op=derive | classical | 24,700 ops/s | 39.30 µs | 55.99 µs | ok |
| `ECDH-P256` | op=keygen | classical | 49,926 ops/s | 19.00 µs | 39.10 µs | ok |
| `ECDH-P256` | op=derive | classical | 17,640 ops/s | 55.30 µs | 75.81 µs | ok |
| `ML-KEM-512` | op=keygen | PQC | 5,127 ops/s | 188.00 µs | 243.43 µs | ok |
| `ML-KEM-512` | op=encapsulate | PQC | 4,106 ops/s | 236.40 µs | 283.11 µs | ok |
| `ML-KEM-512` | op=decapsulate | PQC | 3,329 ops/s | 290.30 µs | 415.31 µs | ok |
| `ML-KEM-768` | op=keygen | PQC | 3,271 ops/s | 297.10 µs | 355.85 µs | ok |
| `ML-KEM-768` | op=encapsulate | PQC | 2,785 ops/s | 348.40 µs | 447.32 µs | ok |
| `ML-KEM-768` | op=decapsulate | PQC | 2,324 ops/s | 420.90 µs | 509.10 µs | ok |
| `ML-KEM-1024` | op=keygen | PQC | 2,274 ops/s | 429.35 µs | 505.94 µs | ok |
| `ML-KEM-1024` | op=encapsulate | PQC | 2,006 ops/s | 486.90 µs | 582.10 µs | ok |
| `ML-KEM-1024` | op=decapsulate | PQC | 1,718 ops/s | 572.60 µs | 623.15 µs | ok |

## Hybrid PQC key agreement (ECDH ‖ ML-KEM → HKDF-SHA384)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ECDH-P256+ML-KEM-768` | op=full_two_party_handshake | HYBRID | 4,271 handshakes/s | 227.54 µs | 295.83 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |
| `ECDH-P256+ML-KEM-1024` | op=full_two_party_handshake | HYBRID | 3,408 handshakes/s | 274.67 µs | 814.96 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ECDH-P256+ML-KEM-768` | op=full_two_party_handshake | HYBRID | 7,673 handshakes/s | 129.29 µs | 154.80 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |
| `ECDH-P256+ML-KEM-1024` | op=full_two_party_handshake | HYBRID | 6,967 handshakes/s | 141.79 µs | 171.38 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ECDH-P256+ML-KEM-768` | op=full_two_party_handshake | HYBRID | 3,213 handshakes/s | 301.88 µs | 387.55 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |
| `ECDH-P256+ML-KEM-1024` | op=full_two_party_handshake | HYBRID | 3,041 handshakes/s | 321.04 µs | 364.96 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ECDH-P256+ML-KEM-768` | op=full_two_party_handshake | HYBRID | 699.7 handshakes/s | 1.37 ms | 2.29 ms | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |
| `ECDH-P256+ML-KEM-1024` | op=full_two_party_handshake | HYBRID | 554.0 handshakes/s | 1.79 ms | 2.02 ms | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |

## Full authenticated handshake crypto (isolated from DDS transport)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `NIST-1 (ML-KEM-512 + ML-DSA-44)` | op=full_authenticated_handshake | HYBRID | 770.0 handshakes/s | 1.16 ms | 4.31 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `NIST-3 (ML-KEM-768 + ML-DSA-65)` | op=full_authenticated_handshake | HYBRID | 528.5 handshakes/s | 1.67 ms | 4.08 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `CNSA 2.0 / NIST-5 (ML-KEM-1024 + ML-DSA-87)` | op=full_authenticated_handshake | HYBRID | 362.8 handshakes/s | 2.37 ms | 5.86 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `key agreement only (rekey, no identity sig)` | note=see hybrid_kem | classical | — | — | — | ok · the recurring/rekey cost is the hybrid_kem group: ~128 µs (ECDH+ML-KEM+HKDF, no signatures) |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `NIST-1 (ML-KEM-512 + ML-DSA-44)` | op=full_authenticated_handshake | HYBRID | 1,579 handshakes/s | 597.77 µs | 1.11 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `NIST-3 (ML-KEM-768 + ML-DSA-65)` | op=full_authenticated_handshake | HYBRID | 1,066 handshakes/s | 881.83 µs | 1.89 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `CNSA 2.0 / NIST-5 (ML-KEM-1024 + ML-DSA-87)` | op=full_authenticated_handshake | HYBRID | 833.4 handshakes/s | 1.15 ms | 1.99 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `key agreement only (rekey, no identity sig)` | note=see hybrid_kem | classical | — | — | — | ok · the recurring/rekey cost is the hybrid_kem group: ~128 µs (ECDH+ML-KEM+HKDF, no signatures) |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `NIST-1 (ML-KEM-512 + ML-DSA-44)` | op=full_authenticated_handshake | HYBRID | 1,404 handshakes/s | 692.08 µs | 941.07 µs | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `NIST-3 (ML-KEM-768 + ML-DSA-65)` | op=full_authenticated_handshake | HYBRID | 1,045 handshakes/s | 928.84 µs | 1.37 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `CNSA 2.0 / NIST-5 (ML-KEM-1024 + ML-DSA-87)` | op=full_authenticated_handshake | HYBRID | 842.9 handshakes/s | 1.16 ms | 1.54 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `key agreement only (rekey, no identity sig)` | note=see hybrid_kem | classical | — | — | — | ok · the recurring/rekey cost is the hybrid_kem group: ~128 µs (ECDH+ML-KEM+HKDF, no signatures) |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `NIST-1 (ML-KEM-512 + ML-DSA-44)` | op=full_authenticated_handshake | HYBRID | 149.2 handshakes/s | 6.53 ms | 10.72 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `NIST-3 (ML-KEM-768 + ML-DSA-65)` | op=full_authenticated_handshake | HYBRID | 86.1 handshakes/s | 11.77 ms | 18.24 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `CNSA 2.0 / NIST-5 (ML-KEM-1024 + ML-DSA-87)` | op=full_authenticated_handshake | HYBRID | 65.0 handshakes/s | 15.21 ms | 19.80 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `key agreement only (rekey, no identity sig)` | note=see hybrid_kem | classical | — | — | — | ok · the recurring/rekey cost is the hybrid_kem group: ~128 µs (ECDH+ML-KEM+HKDF, no signatures) |

## Digital signatures (ML-DSA vs classical)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `Ed25519` | op=keygen | classical | 7,217 ops/s | 100.62 µs | 481.10 µs | ok |
| `Ed25519` | op=sign | classical | 8,800 ops/s | 102.17 µs | 385.35 µs | ok |
| `Ed25519` | op=verify | classical | 4,411 ops/s | 214.33 µs | 666.24 µs | ok |
| `ECDSA-P256` | op=sign | classical | 34,345 ops/s | 27.71 µs | 39.33 µs | ok |
| `ECDSA-P256` | op=verify | classical | 14,988 ops/s | 66.00 µs | 78.67 µs | ok |
| `RSA-3072-PSS` | op=sign | classical | 324.2 ops/s | 2.85 ms | 6.45 ms | ok |
| `RSA-3072-PSS` | op=verify | classical | 14,279 ops/s | 61.83 µs | 260.95 µs | ok |
| `ML-DSA-44` | op=keygen | PQC | 14,481 ops/s | 59.79 µs | 202.98 µs | ok |
| `ML-DSA-44` | op=sign | PQC | 3,697 ops/s | 214.79 µs | 1.07 ms | ok |
| `ML-DSA-44` | op=verify | PQC | 13,591 ops/s | 62.54 µs | 253.64 µs | ok |
| `ML-DSA-65` | op=keygen | PQC | 8,427 ops/s | 107.25 µs | 305.36 µs | ok |
| `ML-DSA-65` | op=sign | PQC | 2,715 ops/s | 287.56 µs | 1.24 ms | ok |
| `ML-DSA-65` | op=verify | PQC | 10,210 ops/s | 95.27 µs | 244.79 µs | ok |
| `ML-DSA-87` | op=keygen | PQC | 6,755 ops/s | 147.27 µs | 173.58 µs | ok |
| `ML-DSA-87` | op=sign | PQC | 2,053 ops/s | 393.21 µs | 1.48 ms | ok |
| `ML-DSA-87` | op=verify | PQC | 5,668 ops/s | 156.33 µs | 479.10 µs | ok |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `Ed25519` | op=keygen | classical | 72,604 ops/s | 13.54 µs | 16.75 µs | ok |
| `Ed25519` | op=sign | classical | 67,552 ops/s | 14.67 µs | 17.96 µs | ok |
| `Ed25519` | op=verify | classical | 28,494 ops/s | 34.42 µs | 42.92 µs | ok |
| `ECDSA-P256` | op=sign | classical | 77,119 ops/s | 12.42 µs | 15.71 µs | ok |
| `ECDSA-P256` | op=verify | classical | 30,270 ops/s | 32.62 µs | 47.25 µs | ok |
| `RSA-3072-PSS` | op=sign | classical | 1,083 ops/s | 914.48 µs | 1.23 ms | ok |
| `RSA-3072-PSS` | op=verify | classical | 46,882 ops/s | 20.96 µs | 25.54 µs | ok |
| `ML-DSA-44` | op=keygen | PQC | 30,451 ops/s | 32.71 µs | 39.12 µs | ok |
| `ML-DSA-44` | op=sign | PQC | 7,562 ops/s | 102.54 µs | 436.84 µs | ok |
| `ML-DSA-44` | op=verify | PQC | 27,658 ops/s | 35.54 µs | 40.83 µs | ok |
| `ML-DSA-65` | op=keygen | PQC | 16,036 ops/s | 61.46 µs | 73.09 µs | ok |
| `ML-DSA-65` | op=sign | PQC | 4,699 ops/s | 169.88 µs | 724.15 µs | ok |
| `ML-DSA-65` | op=verify | PQC | 17,877 ops/s | 55.46 µs | 62.29 µs | ok |
| `ML-DSA-87` | op=keygen | PQC | 11,741 ops/s | 84.00 µs | 96.67 µs | ok |
| `ML-DSA-87` | op=sign | PQC | 3,859 ops/s | 211.96 µs | 804.87 µs | ok |
| `ML-DSA-87` | op=verify | PQC | 11,263 ops/s | 87.96 µs | 100.33 µs | ok |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `Ed25519` | op=keygen | classical | 27,515 ops/s | 35.59 µs | 45.35 µs | ok |
| `Ed25519` | op=sign | classical | 25,589 ops/s | 37.83 µs | 56.99 µs | ok |
| `Ed25519` | op=verify | classical | 8,421 ops/s | 117.16 µs | 128.61 µs | ok |
| `ECDSA-P256` | op=sign | classical | 33,867 ops/s | 28.48 µs | 42.74 µs | ok |
| `ECDSA-P256` | op=verify | classical | 13,484 ops/s | 72.32 µs | 87.61 µs | ok |
| `RSA-3072-PSS` | op=sign | classical | 472.8 ops/s | 2.01 ms | 4.04 ms | ok |
| `RSA-3072-PSS` | op=verify | classical | 19,964 ops/s | 48.91 µs | 61.81 µs | ok |
| `ML-DSA-44` | op=keygen | PQC | 22,811 ops/s | 42.61 µs | 57.76 µs | ok |
| `ML-DSA-44` | op=sign | PQC | 11,491 ops/s | 70.62 µs | 245.45 µs | ok |
| `ML-DSA-44` | op=verify | PQC | 22,443 ops/s | 43.39 µs | 56.67 µs | ok |
| `ML-DSA-65` | op=keygen | PQC | 14,660 ops/s | 65.72 µs | 112.70 µs | ok |
| `ML-DSA-65` | op=sign | PQC | 6,849 ops/s | 118.53 µs | 429.92 µs | ok |
| `ML-DSA-65` | op=verify | PQC | 15,115 ops/s | 64.69 µs | 78.31 µs | ok |
| `ML-DSA-87` | op=keygen | PQC | 9,920 ops/s | 98.61 µs | 114.81 µs | ok |
| `ML-DSA-87` | op=sign | PQC | 6,020 ops/s | 144.59 µs | 415.71 µs | ok |
| `ML-DSA-87` | op=verify | PQC | 10,128 ops/s | 96.58 µs | 112.29 µs | ok |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `Ed25519` | op=keygen | classical | 23,742 ops/s | 40.90 µs | 59.54 µs | ok |
| `Ed25519` | op=sign | classical | 22,571 ops/s | 43.10 µs | 62.24 µs | ok |
| `Ed25519` | op=verify | classical | 8,200 ops/s | 119.40 µs | 146.17 µs | ok |
| `ECDSA-P256` | op=sign | classical | 30,442 ops/s | 31.20 µs | 57.20 µs | ok |
| `ECDSA-P256` | op=verify | classical | 12,831 ops/s | 75.30 µs | 109.73 µs | ok |
| `RSA-3072-PSS` | op=sign | classical | 482.4 ops/s | 2.04 ms | 2.89 ms | ok |
| `RSA-3072-PSS` | op=verify | classical | 18,018 ops/s | 53.50 µs | 82.50 µs | ok |
| `ML-DSA-44` | op=keygen | PQC | 2,236 ops/s | 438.90 µs | 492.09 µs | ok |
| `ML-DSA-44` | op=sign | PQC | 620.8 ops/s | 1.28 ms | 4.39 ms | ok |
| `ML-DSA-44` | op=verify | PQC | 1,938 ops/s | 504.90 µs | 590.32 µs | ok |
| `ML-DSA-65` | op=keygen | PQC | 1,265 ops/s | 774.80 µs | 828.93 µs | ok |
| `ML-DSA-65` | op=sign | PQC | 459.6 ops/s | 1.49 ms | 6.62 ms | ok |
| `ML-DSA-65` | op=verify | PQC | 1,216 ops/s | 813.50 µs | 879.95 µs | ok |
| `ML-DSA-87` | op=keygen | PQC | 773.0 ops/s | 1.29 ms | 1.40 ms | ok |
| `ML-DSA-87` | op=sign | PQC | 308.1 ops/s | 2.71 ms | 7.49 ms | ok |
| `ML-DSA-87` | op=verify | PQC | 733.4 ops/s | 1.36 ms | 1.48 ms | ok |

## Authenticated encryption (AES-GCM / ChaCha20-Poly1305)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `AES-256-GCM` | op=encrypt, input_bytes=64 | QR | 76 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=64 | QR | 79 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=encrypt, input_bytes=1024 | QR | 824 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=1024 | QR | 767 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=encrypt, input_bytes=65536 | QR | 3,827 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=65536 | QR | 4,501 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-128-GCM` | op=encrypt, input_bytes=64 | classical | 62 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=64 | classical | 66 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=encrypt, input_bytes=1024 | classical | 922 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=1024 | classical | 1,000 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=encrypt, input_bytes=65536 | classical | 5,877 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=65536 | classical | 5,389 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=64 | QR | 59 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=64 | QR | 55 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=1024 | QR | 543 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=1024 | QR | 582 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=65536 | QR | 1,581 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=65536 | QR | 1,476 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `AES-256-GCM` | op=encrypt, input_bytes=64 | QR | 197 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=64 | QR | 123 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=encrypt, input_bytes=1024 | QR | 2,132 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=1024 | QR | 2,233 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=encrypt, input_bytes=16384 | QR | 6,992 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=16384 | QR | 6,794 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=encrypt, input_bytes=262144 | QR | 7,717 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=262144 | QR | 7,516 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=encrypt, input_bytes=1048576 | QR | 7,204 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=1048576 | QR | 7,745 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-128-GCM` | op=encrypt, input_bytes=64 | classical | 191 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=64 | classical | 188 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=encrypt, input_bytes=1024 | classical | 2,180 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=1024 | classical | 2,227 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=encrypt, input_bytes=16384 | classical | 6,872 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=16384 | classical | 6,520 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=encrypt, input_bytes=262144 | classical | 8,200 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=262144 | classical | 8,171 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=encrypt, input_bytes=1048576 | classical | 7,739 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=1048576 | classical | 8,159 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=64 | QR | 144 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=64 | QR | 139 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=1024 | QR | 1,236 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=1024 | QR | 1,210 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=16384 | QR | 2,161 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=16384 | QR | 2,168 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=262144 | QR | 2,313 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=262144 | QR | 2,299 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=1048576 | QR | 2,332 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=1048576 | QR | 2,332 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `AES-256-GCM` | op=encrypt, input_bytes=64 | QR | 72 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=64 | QR | 73 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=encrypt, input_bytes=1024 | QR | 819 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=1024 | QR | 835 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=encrypt, input_bytes=65536 | QR | 3,601 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=65536 | QR | 3,602 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-128-GCM` | op=encrypt, input_bytes=64 | classical | 72 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=64 | classical | 73 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=encrypt, input_bytes=1024 | classical | 837 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=1024 | classical | 850 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=encrypt, input_bytes=65536 | classical | 3,854 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=65536 | classical | 3,859 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=64 | QR | 59 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=64 | QR | 60 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=1024 | QR | 661 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=1024 | QR | 654 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=65536 | QR | 2,029 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=65536 | QR | 2,050 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `AES-256-GCM` | op=encrypt, input_bytes=64 | QR | 52 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=64 | QR | 52 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=encrypt, input_bytes=1024 | QR | 652 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=1024 | QR | 663 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=encrypt, input_bytes=65536 | QR | 3,468 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=65536 | QR | 3,466 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-128-GCM` | op=encrypt, input_bytes=64 | classical | 52 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=64 | classical | 52 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=encrypt, input_bytes=1024 | classical | 662 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=1024 | classical | 670 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=encrypt, input_bytes=65536 | classical | 3,696 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=65536 | classical | 3,705 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=64 | QR | 45 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=64 | QR | 45 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=1024 | QR | 543 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=1024 | QR | 541 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=65536 | QR | 1,869 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=65536 | QR | 2,020 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

## Hashing (SHA-2 / SHA-3 / BLAKE2)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `sha256` | input_bytes=64 | classical | 116 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha256` | input_bytes=1024 | classical | 1,000 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha256` | input_bytes=65536 | classical | 2,197 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=64 | QR | 95 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=1024 | QR | 687 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=65536 | QR | 1,340 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=64 | QR | 116 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=1024 | QR | 784 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=65536 | QR | 1,322 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha3_256` | input_bytes=64 | classical | 77 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_256` | input_bytes=1024 | classical | 429 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_256` | input_bytes=65536 | classical | 626 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=64 | QR | 77 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=1024 | QR | 262 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=65536 | QR | 325 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `blake2b` | input_bytes=64 | QR | 105 MB/s | ok |
| `blake2b` | input_bytes=1024 | QR | 600 MB/s | ok |
| `blake2b` | input_bytes=65536 | QR | 919 MB/s | ok |
| `blake2s` | input_bytes=64 | classical | 152 MB/s | ok |
| `blake2s` | input_bytes=1024 | classical | 488 MB/s | ok |
| `blake2s` | input_bytes=65536 | classical | 572 MB/s | ok |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `sha256` | input_bytes=64 | classical | 214 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha256` | input_bytes=1024 | classical | 1,758 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha256` | input_bytes=16384 | classical | 3,090 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha256` | input_bytes=262144 | classical | 3,255 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha256` | input_bytes=1048576 | classical | 3,291 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=64 | QR | 191 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=1024 | QR | 1,178 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=16384 | QR | 1,799 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=262144 | QR | 1,794 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=1048576 | QR | 1,857 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=64 | QR | 192 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=1024 | QR | 1,077 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=16384 | QR | 1,341 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=262144 | QR | 1,395 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=1048576 | QR | 1,856 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha3_256` | input_bytes=64 | classical | 134 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_256` | input_bytes=1024 | classical | 744 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_256` | input_bytes=16384 | classical | 1,066 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_256` | input_bytes=262144 | classical | 1,091 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_256` | input_bytes=1048576 | classical | 1,056 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=64 | QR | 132 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=1024 | QR | 461 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=16384 | QR | 544 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=262144 | QR | 571 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=1048576 | QR | 573 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `blake2b` | input_bytes=64 | QR | 188 MB/s | ok |
| `blake2b` | input_bytes=1024 | QR | 1,073 MB/s | ok |
| `blake2b` | input_bytes=16384 | QR | 1,434 MB/s | ok |
| `blake2b` | input_bytes=262144 | QR | 1,505 MB/s | ok |
| `blake2b` | input_bytes=1048576 | QR | 1,579 MB/s | ok |
| `blake2s` | input_bytes=64 | classical | 249 MB/s | ok |
| `blake2s` | input_bytes=1024 | classical | 794 MB/s | ok |
| `blake2s` | input_bytes=16384 | classical | 936 MB/s | ok |
| `blake2s` | input_bytes=262144 | classical | 943 MB/s | ok |
| `blake2s` | input_bytes=1048576 | classical | 941 MB/s | ok |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `sha256` | input_bytes=64 | classical | 65 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha256` | input_bytes=1024 | classical | 646 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha256` | input_bytes=65536 | classical | 1,549 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=64 | QR | 54 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=1024 | QR | 385 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=65536 | QR | 749 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=64 | QR | 54 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=1024 | QR | 397 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=65536 | QR | 747 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha3_256` | input_bytes=64 | classical | 49 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_256` | input_bytes=1024 | classical | 296 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_256` | input_bytes=65536 | classical | 425 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=64 | QR | 49 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=1024 | QR | 185 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=65536 | QR | 240 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `blake2b` | input_bytes=64 | QR | 82 MB/s | ok |
| `blake2b` | input_bytes=1024 | QR | 519 MB/s | ok |
| `blake2b` | input_bytes=65536 | QR | 738 MB/s | ok |
| `blake2s` | input_bytes=64 | classical | 87 MB/s | ok |
| `blake2s` | input_bytes=1024 | classical | 369 MB/s | ok |
| `blake2s` | input_bytes=65536 | classical | 465 MB/s | ok |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `sha256` | input_bytes=64 | classical | 57 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha256` | input_bytes=1024 | classical | 583 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha256` | input_bytes=65536 | classical | 1,539 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=64 | QR | 49 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=1024 | QR | 377 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=65536 | QR | 740 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=64 | QR | 48 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=1024 | QR | 377 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=65536 | QR | 739 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha3_256` | input_bytes=64 | classical | 44 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_256` | input_bytes=1024 | classical | 282 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_256` | input_bytes=65536 | classical | 422 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=64 | QR | 44 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=1024 | QR | 180 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=65536 | QR | 235 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `blake2b` | input_bytes=64 | QR | 70 MB/s | ok |
| `blake2b` | input_bytes=1024 | QR | 418 MB/s | ok |
| `blake2b` | input_bytes=65536 | QR | 590 MB/s | ok |
| `blake2s` | input_bytes=64 | classical | 78 MB/s | ok |
| `blake2s` | input_bytes=1024 | classical | 289 MB/s | ok |
| `blake2s` | input_bytes=65536 | classical | 355 MB/s | ok |

## Message authentication (HMAC / Poly1305)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `HMAC-SHA256` | input_bytes=64 | classical | 47 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA256` | input_bytes=1024 | classical | 518 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA256` | input_bytes=65536 | classical | 1,830 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=64 | QR | 37 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=1024 | QR | 389 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=65536 | QR | 1,219 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=64 | QR | 41 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=1024 | QR | 440 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=65536 | QR | 1,337 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `Poly1305` | input_bytes=64 | QR | 13 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=1024 | QR | 217 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=65536 | QR | 3,889 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `HMAC-SHA256` | input_bytes=64 | classical | 85 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA256` | input_bytes=1024 | classical | 991 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA256` | input_bytes=16384 | classical | 2,808 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA256` | input_bytes=262144 | classical | 3,242 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA256` | input_bytes=1048576 | classical | 3,274 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=64 | QR | 65 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=1024 | QR | 684 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=16384 | QR | 1,641 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=262144 | QR | 1,836 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=1048576 | QR | 1,859 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=64 | QR | 67 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=1024 | QR | 689 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=16384 | QR | 1,678 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=262144 | QR | 1,833 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=1048576 | QR | 1,854 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `Poly1305` | input_bytes=64 | QR | 44 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=1024 | QR | 603 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=16384 | QR | 4,554 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=262144 | QR | 7,658 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=1048576 | QR | 8,407 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `HMAC-SHA256` | input_bytes=64 | classical | 30 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA256` | input_bytes=1024 | classical | 373 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA256` | input_bytes=65536 | classical | 1,500 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=64 | QR | 20 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=1024 | QR | 230 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=65536 | QR | 662 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=64 | QR | 22 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=1024 | QR | 244 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=65536 | QR | 732 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `Poly1305` | input_bytes=64 | QR | 19 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=1024 | QR | 290 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=65536 | QR | 4,934 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `HMAC-SHA256` | input_bytes=64 | classical | 23 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA256` | input_bytes=1024 | classical | 299 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA256` | input_bytes=65536 | classical | 1,430 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=64 | QR | 18 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=1024 | QR | 206 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=65536 | QR | 708 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=64 | QR | 18 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=1024 | QR | 205 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=65536 | QR | 709 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `Poly1305` | input_bytes=64 | QR | 12 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=1024 | QR | 180 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=65536 | QR | 4,216 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

## Key derivation (HKDF / PBKDF2 / Argon2id)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `PBKDF2-HMAC-SHA256` | iterations=10000 | classical | 412.1 ops/s | 2.20 ms | 5.78 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `PBKDF2-HMAC-SHA256` | iterations=100000 | classical | 41.5 ops/s | 24.02 ms | 32.03 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `PBKDF2-HMAC-SHA256` | iterations=600000 | classical | 6.10 ops/s | 162.91 ms | 169.01 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `HKDF-SHA256` | ikm_bytes=64, out_bytes=32 | classical | 160,201 ops/s | 4.88 µs | 31.71 µs | ok · extract-then-expand KDF — HIGH-entropy inputs (RFC 5869) |
| `HKDF-SHA384` | ikm_bytes=64, out_bytes=32 | QR | 159,283 ops/s | 5.38 µs | 16.75 µs | ok · extract-then-expand KDF — HIGH-entropy inputs (RFC 5869) |
| `Argon2id` | profile=interactive, time_cost=2, memory_cost=65536, parallelism=1 | QR | 8.94 ops/s | 112.94 ms | 117.63 ms | ok · memory-hard passphrase KDF — LOW-entropy inputs, GPU/ASIC-resistant |
| `Argon2id` | profile=moderate, time_cost=3, memory_cost=262144, parallelism=4 | QR | 3.72 ops/s | 266.07 ms | 290.84 ms | ok · memory-hard passphrase KDF — LOW-entropy inputs, GPU/ASIC-resistant |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `PBKDF2-HMAC-SHA256` | iterations=10000 | classical | 1,316 ops/s | 737.85 µs | 1.25 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `PBKDF2-HMAC-SHA256` | iterations=100000 | classical | 130.8 ops/s | 7.14 ms | 16.04 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `PBKDF2-HMAC-SHA256` | iterations=600000 | classical | 22.4 ops/s | 42.69 ms | 56.54 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `HKDF-SHA256` | ikm_bytes=64, out_bytes=32 | classical | 516,133 ops/s | 1.75 µs | 2.04 µs | ok · extract-then-expand KDF — HIGH-entropy inputs (RFC 5869) |
| `HKDF-SHA384` | ikm_bytes=64, out_bytes=32 | QR | 445,131 ops/s | 2.21 µs | 2.38 µs | ok · extract-then-expand KDF — HIGH-entropy inputs (RFC 5869) |
| `Argon2id` | profile=interactive, time_cost=2, memory_cost=65536, parallelism=1 | QR | 17.8 ops/s | 55.99 ms | 57.67 ms | ok · memory-hard passphrase KDF — LOW-entropy inputs, GPU/ASIC-resistant |
| `Argon2id` | profile=moderate, time_cost=3, memory_cost=262144, parallelism=4 | QR | 7.85 ops/s | 126.12 ms | 134.26 ms | ok · memory-hard passphrase KDF — LOW-entropy inputs, GPU/ASIC-resistant |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `PBKDF2-HMAC-SHA256` | iterations=10000 | classical | 341.7 ops/s | 2.92 ms | 3.08 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `PBKDF2-HMAC-SHA256` | iterations=100000 | classical | 34.3 ops/s | 29.13 ms | 29.68 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `PBKDF2-HMAC-SHA256` | iterations=600000 | classical | 5.72 ops/s | 174.86 ms | 174.96 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `HKDF-SHA256` | ikm_bytes=64, out_bytes=32 | classical | 224,425 ops/s | 4.12 µs | 4.58 µs | ok · extract-then-expand KDF — HIGH-entropy inputs (RFC 5869) |
| `HKDF-SHA384` | ikm_bytes=64, out_bytes=32 | QR | 170,166 ops/s | 5.43 µs | 5.83 µs | ok · extract-then-expand KDF — HIGH-entropy inputs (RFC 5869) |
| `Argon2id` | profile=interactive, time_cost=2, memory_cost=65536, parallelism=1 | QR | 13.6 ops/s | 73.31 ms | 73.94 ms | ok · memory-hard passphrase KDF — LOW-entropy inputs, GPU/ASIC-resistant |
| `Argon2id` | profile=moderate, time_cost=3, memory_cost=262144, parallelism=4 | QR | 6.00 ops/s | 166.58 ms | 167.34 ms | ok · memory-hard passphrase KDF — LOW-entropy inputs, GPU/ASIC-resistant |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `PBKDF2-HMAC-SHA256` | iterations=10000 | classical | 200.0 ops/s | 5.00 ms | 5.09 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `PBKDF2-HMAC-SHA256` | iterations=100000 | classical | 20.0 ops/s | 50.12 ms | 50.32 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `PBKDF2-HMAC-SHA256` | iterations=600000 | classical | 3.33 ops/s | 300.80 ms | 301.35 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `HKDF-SHA256` | ikm_bytes=64, out_bytes=32 | classical | 173,096 ops/s | 5.30 µs | 9.11 µs | ok · extract-then-expand KDF — HIGH-entropy inputs (RFC 5869) |
| `HKDF-SHA384` | ikm_bytes=64, out_bytes=32 | QR | 140,541 ops/s | 6.70 µs | 8.00 µs | ok · extract-then-expand KDF — HIGH-entropy inputs (RFC 5869) |
| `Argon2id` | profile=interactive, time_cost=2, memory_cost=65536, parallelism=1 | QR | 10.4 ops/s | 96.51 ms | 96.81 ms | ok · memory-hard passphrase KDF — LOW-entropy inputs, GPU/ASIC-resistant |
| `Argon2id` | profile=moderate, time_cost=3, memory_cost=262144, parallelism=4 | QR | 4.51 ops/s | 221.02 ms | 222.48 ms | ok · memory-hard passphrase KDF — LOW-entropy inputs, GPU/ASIC-resistant |

## DDS-Security live handshakes (Fast DDS + CycloneDDS)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `CycloneDDS` | — | classical | — | ⚠️ skipped: CycloneDDS PQC test binary not built on this platform |
| `FastDDS` | — | classical | — | ⚠️ skipped: Fast DDS PKI-DH test binary not built on this platform |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `CycloneDDS classical (RSA id · ECDH P-256)` | — | classical | 2.44 ms | 2.44 ms | 4.84 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS classical (RSA id · ECDH P-256) — full process` | — | classical | 108.61 ms | 108.61 ms | 150.30 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-768` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-768 | HYBRID | 2.08 ms | 2.08 ms | 2.36 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-768 — full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-768 | HYBRID | 106.78 ms | 106.78 ms | 117.30 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-1024` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | HYBRID | 2.16 ms | 2.16 ms | 5.10 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-1024 — full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | HYBRID | 104.89 ms | 104.89 ms | 110.06 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS ML-DSA-87 identity (PQ auth)` | — | PQC | 2.64 ms | 2.64 ms | 25.39 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS ML-DSA-87 identity (PQ auth) — full process` | — | PQC | 68.87 ms | 68.87 ms | 147.94 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS full CNSA 2.0 (ML-DSA-87 · ML-KEM-1024)` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | HYBRID | 2.84 ms | 2.84 ms | 8.19 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS full CNSA 2.0 (ML-DSA-87 · ML-KEM-1024) — full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | HYBRID | 64.31 ms | 64.31 ms | 78.89 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `FastDDS PKI-DH local-identity validate — full process` | — | classical | 41.51 ms | 41.51 ms | 78.73 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `CycloneDDS` | — | classical | — | ⚠️ skipped: CycloneDDS PQC test binary not built on this platform |
| `FastDDS` | — | classical | — | ⚠️ skipped: Fast DDS PKI-DH test binary not built on this platform |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `CycloneDDS` | — | classical | — | ⚠️ skipped: CycloneDDS PQC test binary not built on this platform |
| `FastDDS` | — | classical | — | ⚠️ skipped: Fast DDS PKI-DH test binary not built on this platform |

## robobus bus / determinism / real-time

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `determinism_probe` | — | classical | — | ⚠️ skipped: package import failed: No module named 'robobus' |
| `bus_latency` | — | classical | — | ⚠️ skipped: package import failed: No module named 'robobus' |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `determinism_probe` | — | classical | — | ⚠️ skipped: no probe()/measure() entrypoint |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `determinism_probe` | — | classical | — | ⚠️ skipped: package import failed: No module named 'robobus' |
| `bus_latency` | — | classical | — | ⚠️ skipped: package import failed: No module named 'robobus' |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `determinism_probe` | — | classical | — | ⚠️ skipped: package import failed: No module named 'robobus' |
| `bus_latency` | — | classical | — | ⚠️ skipped: package import failed: No module named 'robobus' |


---

**Classes.** `PQC` = post-quantum *asymmetric* (FIPS 203 ML-KEM / FIPS 204 ML-DSA), replacing quantum-broken RSA/ECC. `HYBRID` = classical ⊕ PQC (CNSA 2.0 transition, e.g. ECDH ‖ ML-KEM → HKDF-SHA384). `QR` = quantum-**resistant** symmetric/hash (AES-256, ChaCha20-Poly1305, SHA-384/512, SHA3, KMAC, Argon2id) — Grover only square-roots symmetric search, so these keep their margins and are part of CNSA 2.0; *not* PQC (an asymmetric term), but *not* classical either. `classical` = quantum-broken asymmetric (RSA/ECDH/ECDSA/Ed25519) or sub-strength symmetric (AES-128, SHA-256 collision). Latency percentiles are per-operation; throughput is aggregate._
