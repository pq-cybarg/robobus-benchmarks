# robobus / PQC-DDS — full-system benchmarks

> **Scope.** Every capability of the stack — post-quantum and classical key encapsulation, hybrid key agreement, digital signatures, authenticated encryption, hashing, MACs, key-derivation, live DDS-Security handshakes, and the robobus bus — measured across all available modes, sizes and techniques by **one script** (`bench/run_benchmarks.py`).

> ⚠️ **Platform caveat.** These figures were measured **on macOS only** so far. They are inherently CPU-, OS- and build-specific and are **not** portable claims. The value here is the *method*: the identical script is designed to run on macOS, Windows, every supported Linux, Android and iOS, skipping only what a given platform lacks. Re-run it on each target to populate that platform's column.

_Generated 2026-07-02 18:01 UTC from `bench/results/latest-*.json`._

## Platforms measured

### Darwin · Apple M5

- **OS:** Darwin 25.1.0 (macOS-26.1-arm64-arm-64bit)
- **CPU:** Apple M5 — 10 cores, 32 GB RAM
- **Python:** 3.12.13 (CPython)
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

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ring put+get, amortized 1-core` | realtime=off, clock_ns_per_tick=41.66667 | classical | 237,350,100 ops/s (4.2 ns/op) | — | — | ok · pure ring op cost; clock res 41.7 ns |
| `cross-process one-way latency` | realtime=off, warmup_msgs=20000 | classical | 83.3 ns | 83.3 ns | 83.3 ns | ok · 99.1% <100 ns; 20000 msgs warmup discarded; max at 62% of run (mid-run scheduler jitter); no RT |
| `ring put+get, amortized 1-core (RT)` | realtime=on, clock_ns_per_tick=41.66667 | classical | 284,140,400 ops/s (3.5 ns/op) | — | — | ok · pure ring op cost; clock res 41.7 ns |
| `cross-process one-way latency (RT)` | realtime=on, warmup_msgs=20000 | classical | 83.3 ns | 83.3 ns | 125.0 ns | ok · 98.4% <100 ns; 20000 msgs warmup discarded; max at 1% of run (cold-start residue); RT time-constraint policy |

## Key encapsulation & key exchange (ML-KEM vs classical)

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

## Hybrid PQC key agreement (ECDH ‖ ML-KEM → HKDF-SHA384)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ECDH-P256+ML-KEM-768` | op=full_two_party_handshake | HYBRID | 7,673 handshakes/s | 129.29 µs | 154.80 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |
| `ECDH-P256+ML-KEM-1024` | op=full_two_party_handshake | HYBRID | 6,967 handshakes/s | 141.79 µs | 171.38 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |

## Full authenticated handshake crypto (isolated from DDS transport)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `NIST-1 (ML-KEM-512 + ML-DSA-44)` | op=full_authenticated_handshake | classical | 1,579 handshakes/s | 597.77 µs | 1.11 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `NIST-3 (ML-KEM-768 + ML-DSA-65)` | op=full_authenticated_handshake | classical | 1,066 handshakes/s | 881.83 µs | 1.89 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `CNSA 2.0 / NIST-5 (ML-KEM-1024 + ML-DSA-87)` | op=full_authenticated_handshake | classical | 833.4 handshakes/s | 1.15 ms | 1.99 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `key agreement only (rekey, no identity sig)` | note=see hybrid_kem | classical | — | — | — | ok · the recurring/rekey cost is the hybrid_kem group: ~128 µs (ECDH+ML-KEM+HKDF, no signatures) |

## Digital signatures (ML-DSA vs classical)

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

## Authenticated encryption (AES-GCM / ChaCha20-Poly1305)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `AES-256-GCM` | op=encrypt, input_bytes=64 | classical | 197 MB/s | ok |
| `AES-256-GCM` | op=decrypt, input_bytes=64 | classical | 123 MB/s | ok |
| `AES-256-GCM` | op=encrypt, input_bytes=1024 | classical | 2,132 MB/s | ok |
| `AES-256-GCM` | op=decrypt, input_bytes=1024 | classical | 2,233 MB/s | ok |
| `AES-256-GCM` | op=encrypt, input_bytes=16384 | classical | 6,992 MB/s | ok |
| `AES-256-GCM` | op=decrypt, input_bytes=16384 | classical | 6,794 MB/s | ok |
| `AES-256-GCM` | op=encrypt, input_bytes=262144 | classical | 7,717 MB/s | ok |
| `AES-256-GCM` | op=decrypt, input_bytes=262144 | classical | 7,516 MB/s | ok |
| `AES-256-GCM` | op=encrypt, input_bytes=1048576 | classical | 7,204 MB/s | ok |
| `AES-256-GCM` | op=decrypt, input_bytes=1048576 | classical | 7,745 MB/s | ok |
| `AES-128-GCM` | op=encrypt, input_bytes=64 | classical | 191 MB/s | ok |
| `AES-128-GCM` | op=decrypt, input_bytes=64 | classical | 188 MB/s | ok |
| `AES-128-GCM` | op=encrypt, input_bytes=1024 | classical | 2,180 MB/s | ok |
| `AES-128-GCM` | op=decrypt, input_bytes=1024 | classical | 2,227 MB/s | ok |
| `AES-128-GCM` | op=encrypt, input_bytes=16384 | classical | 6,872 MB/s | ok |
| `AES-128-GCM` | op=decrypt, input_bytes=16384 | classical | 6,520 MB/s | ok |
| `AES-128-GCM` | op=encrypt, input_bytes=262144 | classical | 8,200 MB/s | ok |
| `AES-128-GCM` | op=decrypt, input_bytes=262144 | classical | 8,171 MB/s | ok |
| `AES-128-GCM` | op=encrypt, input_bytes=1048576 | classical | 7,739 MB/s | ok |
| `AES-128-GCM` | op=decrypt, input_bytes=1048576 | classical | 8,159 MB/s | ok |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=64 | classical | 144 MB/s | ok |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=64 | classical | 139 MB/s | ok |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=1024 | classical | 1,236 MB/s | ok |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=1024 | classical | 1,210 MB/s | ok |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=16384 | classical | 2,161 MB/s | ok |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=16384 | classical | 2,168 MB/s | ok |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=262144 | classical | 2,313 MB/s | ok |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=262144 | classical | 2,299 MB/s | ok |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=1048576 | classical | 2,332 MB/s | ok |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=1048576 | classical | 2,332 MB/s | ok |

## Hashing (SHA-2 / SHA-3 / BLAKE2)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `sha256` | input_bytes=64 | classical | 214 MB/s | ok |
| `sha256` | input_bytes=1024 | classical | 1,758 MB/s | ok |
| `sha256` | input_bytes=16384 | classical | 3,090 MB/s | ok |
| `sha256` | input_bytes=262144 | classical | 3,255 MB/s | ok |
| `sha256` | input_bytes=1048576 | classical | 3,291 MB/s | ok |
| `sha384` | input_bytes=64 | classical | 191 MB/s | ok |
| `sha384` | input_bytes=1024 | classical | 1,178 MB/s | ok |
| `sha384` | input_bytes=16384 | classical | 1,799 MB/s | ok |
| `sha384` | input_bytes=262144 | classical | 1,794 MB/s | ok |
| `sha384` | input_bytes=1048576 | classical | 1,857 MB/s | ok |
| `sha512` | input_bytes=64 | classical | 192 MB/s | ok |
| `sha512` | input_bytes=1024 | classical | 1,077 MB/s | ok |
| `sha512` | input_bytes=16384 | classical | 1,341 MB/s | ok |
| `sha512` | input_bytes=262144 | classical | 1,395 MB/s | ok |
| `sha512` | input_bytes=1048576 | classical | 1,856 MB/s | ok |
| `sha3_256` | input_bytes=64 | classical | 134 MB/s | ok |
| `sha3_256` | input_bytes=1024 | classical | 744 MB/s | ok |
| `sha3_256` | input_bytes=16384 | classical | 1,066 MB/s | ok |
| `sha3_256` | input_bytes=262144 | classical | 1,091 MB/s | ok |
| `sha3_256` | input_bytes=1048576 | classical | 1,056 MB/s | ok |
| `sha3_512` | input_bytes=64 | classical | 132 MB/s | ok |
| `sha3_512` | input_bytes=1024 | classical | 461 MB/s | ok |
| `sha3_512` | input_bytes=16384 | classical | 544 MB/s | ok |
| `sha3_512` | input_bytes=262144 | classical | 571 MB/s | ok |
| `sha3_512` | input_bytes=1048576 | classical | 573 MB/s | ok |
| `blake2b` | input_bytes=64 | classical | 188 MB/s | ok |
| `blake2b` | input_bytes=1024 | classical | 1,073 MB/s | ok |
| `blake2b` | input_bytes=16384 | classical | 1,434 MB/s | ok |
| `blake2b` | input_bytes=262144 | classical | 1,505 MB/s | ok |
| `blake2b` | input_bytes=1048576 | classical | 1,579 MB/s | ok |
| `blake2s` | input_bytes=64 | classical | 249 MB/s | ok |
| `blake2s` | input_bytes=1024 | classical | 794 MB/s | ok |
| `blake2s` | input_bytes=16384 | classical | 936 MB/s | ok |
| `blake2s` | input_bytes=262144 | classical | 943 MB/s | ok |
| `blake2s` | input_bytes=1048576 | classical | 941 MB/s | ok |

## Message authentication (HMAC / Poly1305)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `HMAC-SHA256` | input_bytes=64 | classical | 85 MB/s | ok |
| `HMAC-SHA256` | input_bytes=1024 | classical | 991 MB/s | ok |
| `HMAC-SHA256` | input_bytes=16384 | classical | 2,808 MB/s | ok |
| `HMAC-SHA256` | input_bytes=262144 | classical | 3,242 MB/s | ok |
| `HMAC-SHA256` | input_bytes=1048576 | classical | 3,274 MB/s | ok |
| `HMAC-SHA384` | input_bytes=64 | classical | 65 MB/s | ok |
| `HMAC-SHA384` | input_bytes=1024 | classical | 684 MB/s | ok |
| `HMAC-SHA384` | input_bytes=16384 | classical | 1,641 MB/s | ok |
| `HMAC-SHA384` | input_bytes=262144 | classical | 1,836 MB/s | ok |
| `HMAC-SHA384` | input_bytes=1048576 | classical | 1,859 MB/s | ok |
| `HMAC-SHA512` | input_bytes=64 | classical | 67 MB/s | ok |
| `HMAC-SHA512` | input_bytes=1024 | classical | 689 MB/s | ok |
| `HMAC-SHA512` | input_bytes=16384 | classical | 1,678 MB/s | ok |
| `HMAC-SHA512` | input_bytes=262144 | classical | 1,833 MB/s | ok |
| `HMAC-SHA512` | input_bytes=1048576 | classical | 1,854 MB/s | ok |
| `Poly1305` | input_bytes=64 | classical | 44 MB/s | ok |
| `Poly1305` | input_bytes=1024 | classical | 603 MB/s | ok |
| `Poly1305` | input_bytes=16384 | classical | 4,554 MB/s | ok |
| `Poly1305` | input_bytes=262144 | classical | 7,658 MB/s | ok |
| `Poly1305` | input_bytes=1048576 | classical | 8,407 MB/s | ok |

## Key derivation (HKDF / PBKDF2 / Argon2id)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `PBKDF2-HMAC-SHA256` | iterations=10000 | classical | 1,316 ops/s | 737.85 µs | 1.25 ms | ok |
| `PBKDF2-HMAC-SHA256` | iterations=100000 | classical | 130.8 ops/s | 7.14 ms | 16.04 ms | ok |
| `PBKDF2-HMAC-SHA256` | iterations=600000 | classical | 22.4 ops/s | 42.69 ms | 56.54 ms | ok |
| `HKDF-SHA256` | ikm_bytes=64, out_bytes=32 | classical | 516,133 ops/s | 1.75 µs | 2.04 µs | ok |
| `HKDF-SHA384` | ikm_bytes=64, out_bytes=32 | classical | 445,131 ops/s | 2.21 µs | 2.38 µs | ok |
| `Argon2id` | profile=interactive, time_cost=2, memory_cost=65536, parallelism=1 | classical | 17.8 ops/s | 55.99 ms | 57.67 ms | ok |
| `Argon2id` | profile=moderate, time_cost=3, memory_cost=262144, parallelism=4 | classical | 7.85 ops/s | 126.12 ms | 134.26 ms | ok |

## DDS-Security live handshakes (Fast DDS + CycloneDDS)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `CycloneDDS classical (RSA id · ECDH P-256)` | — | classical | 2.44 ms | 2.44 ms | 4.84 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS classical (RSA id · ECDH P-256) — full process` | — | classical | 108.61 ms | 108.61 ms | 150.30 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-768` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-768 | classical | 2.08 ms | 2.08 ms | 2.36 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-768 — full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-768 | classical | 106.78 ms | 106.78 ms | 117.30 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-1024` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | classical | 2.16 ms | 2.16 ms | 5.10 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-1024 — full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | classical | 104.89 ms | 104.89 ms | 110.06 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS ML-DSA-87 identity (PQ auth)` | — | classical | 2.64 ms | 2.64 ms | 25.39 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS ML-DSA-87 identity (PQ auth) — full process` | — | classical | 68.87 ms | 68.87 ms | 147.94 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS full CNSA 2.0 (ML-DSA-87 · ML-KEM-1024)` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | classical | 2.84 ms | 2.84 ms | 8.19 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS full CNSA 2.0 (ML-DSA-87 · ML-KEM-1024) — full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | classical | 64.31 ms | 64.31 ms | 78.89 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `FastDDS PKI-DH local-identity validate — full process` | — | classical | 41.51 ms | 41.51 ms | 78.73 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |

## robobus bus / determinism / real-time

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `determinism_probe` | — | classical | — | ⚠️ skipped: no probe()/measure() entrypoint |


---

_`PQC` = FIPS 203/204 post-quantum (ML-KEM / ML-DSA). `HYBRID` = classical ‖ PQC combined through HKDF-SHA384 (CNSA 2.0). `classical` = pre-quantum baseline for comparison. Latency percentiles are per-operation; throughput is aggregate._
