# robobus / PQC-DDS — full-system benchmarks

> **Scope.** Every capability of the stack — post-quantum and classical key encapsulation, hybrid key agreement, digital signatures, authenticated encryption, hashing, MACs, key-derivation, live DDS-Security handshakes, and the robobus bus — measured across all available modes, sizes and techniques by **one script** (`bench/run_benchmarks.py`).

> ⚠️ **Platform caveat.** These figures were measured **on macOS only** so far. They are inherently CPU-, OS- and build-specific and are **not** portable claims. The value here is the *method*: the identical script is designed to run on macOS, Windows, every supported Linux, Android and iOS, skipping only what a given platform lacks. Re-run it on each target to populate that platform's column.

_Generated 2026-07-02 21:18 UTC from `bench/results/latest-*.json`._

## Platforms measured

### Darwin · Apple M5

- **OS:** Darwin 25.1.0 (macOS-26.1-arm64-arm-64bit)
- **CPU:** Apple M5 — 10 cores, 32 GB RAM
- **Python:** 3.12.13 (CPython)
- **Crypto backends:** cryptography 49.0.0, oqs 0.15.0, argon2 25.1.0, psutil 7.2.2
- **Fidelity tier:** 3-baremetal-partial (real hardware, some noise controls)
- **Uncontrolled noise:** macOS: no core isolation / governor control (soft-RT only)

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
| `ring put+get, amortized 1-core` | realtime=off, clock_ns_per_tick=41.66667 | classical | 295,033,800 ops/s (3.4 ns/op) | — | — | ok · pure ring op cost; clock res 41.7 ns |
| `cross-process one-way latency` | realtime=off, warmup_msgs=20000 | classical | 83.3 ns | 83.3 ns | 48.00 µs | ok · 94.2% <100 ns; 20000 msgs warmup discarded; max at 18% of run (mid-run scheduler jitter); no RT |
| `ring put+get, amortized 1-core (RT)` | realtime=on, clock_ns_per_tick=41.66667 | classical | 272,456,300 ops/s (3.7 ns/op) | — | — | ok · pure ring op cost; clock res 41.7 ns |
| `cross-process one-way latency (RT)` | realtime=on, warmup_msgs=20000 | classical | 83.3 ns | 83.3 ns | 166.7 ns | ok · 98.4% <100 ns; 20000 msgs warmup discarded; max at 20% of run (mid-run scheduler jitter); RT time-constraint policy |

## Key encapsulation & key exchange (ML-KEM vs classical)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `X25519` | op=keygen | classical | 73,063 ops/s | 13.38 µs | 16.29 µs | ok |
| `X25519` | op=derive | classical | 65,010 ops/s | 15.21 µs | 17.17 µs | ok |
| `ECDH-P256` | op=keygen | classical | 161,461 ops/s | 6.04 µs | 6.58 µs | ok |
| `ECDH-P256` | op=derive | classical | 40,876 ops/s | 24.12 µs | 27.04 µs | ok |
| `ML-KEM-512` | op=keygen | PQC | 116,973 ops/s | 8.33 µs | 10.21 µs | ok |
| `ML-KEM-512` | op=encapsulate | PQC | 108,717 ops/s | 9.00 µs | 11.42 µs | ok |
| `ML-KEM-512` | op=decapsulate | PQC | 135,919 ops/s | 7.21 µs | 8.75 µs | ok |
| `ML-KEM-768` | op=keygen | PQC | 75,373 ops/s | 11.71 µs | 13.29 µs | ok |
| `ML-KEM-768` | op=encapsulate | PQC | 61,046 ops/s | 12.46 µs | 107.40 µs | ok |
| `ML-KEM-768` | op=decapsulate | PQC | 90,040 ops/s | 10.92 µs | 13.58 µs | ok |
| `ML-KEM-1024` | op=keygen | PQC | 62,611 ops/s | 15.92 µs | 19.21 µs | ok |
| `ML-KEM-1024` | op=encapsulate | PQC | 59,803 ops/s | 16.38 µs | 20.79 µs | ok |
| `ML-KEM-1024` | op=decapsulate | PQC | 61,754 ops/s | 16.00 µs | 19.42 µs | ok |

## Hybrid PQC key agreement (ECDH ‖ ML-KEM → HKDF-SHA384)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ECDH-P256+ML-KEM-768` | op=full_two_party_handshake | HYBRID | 7,811 handshakes/s | 125.96 µs | 150.96 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |
| `ECDH-P256+ML-KEM-1024` | op=full_two_party_handshake | HYBRID | 7,040 handshakes/s | 140.88 µs | 161.17 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |

## Full authenticated handshake crypto (isolated from DDS transport)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `NIST-1 (ML-KEM-512 + ML-DSA-44)` | op=full_authenticated_handshake | HYBRID | 1,609 handshakes/s | 599.04 µs | 1.15 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `NIST-3 (ML-KEM-768 + ML-DSA-65)` | op=full_authenticated_handshake | HYBRID | 1,076 handshakes/s | 889.21 µs | 1.69 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `CNSA 2.0 / NIST-5 (ML-KEM-1024 + ML-DSA-87)` | op=full_authenticated_handshake | HYBRID | 836.8 handshakes/s | 1.15 ms | 1.96 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `key agreement only (rekey, no identity sig)` | note=see hybrid_kem | classical | — | — | — | ok · the recurring/rekey cost is the hybrid_kem group: ~128 µs (ECDH+ML-KEM+HKDF, no signatures) |

## Digital signatures (ML-DSA vs classical)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `Ed25519` | op=keygen | classical | 72,859 ops/s | 13.54 µs | 16.25 µs | ok |
| `Ed25519` | op=sign | classical | 67,893 ops/s | 14.50 µs | 19.50 µs | ok |
| `Ed25519` | op=verify | classical | 28,608 ops/s | 34.08 µs | 40.04 µs | ok |
| `ECDSA-P256` | op=sign | classical | 80,079 ops/s | 12.42 µs | 14.71 µs | ok |
| `ECDSA-P256` | op=verify | classical | 30,694 ops/s | 32.04 µs | 39.96 µs | ok |
| `RSA-3072-PSS` | op=sign | classical | 1,062 ops/s | 919.02 µs | 1.23 ms | ok |
| `RSA-3072-PSS` | op=verify | classical | 47,439 ops/s | 21.00 µs | 25.62 µs | ok |
| `ML-DSA-44` | op=keygen | PQC | 30,570 ops/s | 32.33 µs | 39.84 µs | ok |
| `ML-DSA-44` | op=sign | PQC | 7,670 ops/s | 101.27 µs | 435.07 µs | ok |
| `ML-DSA-44` | op=verify | PQC | 27,940 ops/s | 36.38 µs | 40.92 µs | ok |
| `ML-DSA-65` | op=keygen | PQC | 16,024 ops/s | 60.96 µs | 71.00 µs | ok |
| `ML-DSA-65` | op=sign | PQC | 4,600 ops/s | 174.44 µs | 714.04 µs | ok |
| `ML-DSA-65` | op=verify | PQC | 17,958 ops/s | 55.42 µs | 63.54 µs | ok |
| `ML-DSA-87` | op=keygen | PQC | 11,734 ops/s | 84.04 µs | 96.17 µs | ok |
| `ML-DSA-87` | op=sign | PQC | 3,703 ops/s | 219.42 µs | 829.30 µs | ok |
| `ML-DSA-87` | op=verify | PQC | 11,277 ops/s | 87.42 µs | 102.25 µs | ok |

## Authenticated encryption (AES-GCM / ChaCha20-Poly1305)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `AES-256-GCM` | op=encrypt, input_bytes=64 | QR | 197 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=64 | QR | 195 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=encrypt, input_bytes=1024 | QR | 2,261 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=1024 | QR | 2,247 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=encrypt, input_bytes=16384 | QR | 6,949 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=16384 | QR | 6,899 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=encrypt, input_bytes=262144 | QR | 8,158 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=262144 | QR | 8,096 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=encrypt, input_bytes=1048576 | QR | 8,168 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=1048576 | QR | 8,009 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-128-GCM` | op=encrypt, input_bytes=64 | classical | 195 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=64 | classical | 185 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=encrypt, input_bytes=1024 | classical | 2,238 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=1024 | classical | 2,217 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=encrypt, input_bytes=16384 | classical | 6,688 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=16384 | classical | 5,649 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=encrypt, input_bytes=262144 | classical | 8,254 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=262144 | classical | 8,218 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=encrypt, input_bytes=1048576 | classical | 8,189 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=1048576 | classical | 8,176 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=64 | QR | 144 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=64 | QR | 138 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=1024 | QR | 1,055 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=1024 | QR | 1,079 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=16384 | QR | 1,962 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=16384 | QR | 1,725 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=262144 | QR | 2,235 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=262144 | QR | 2,238 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=1048576 | QR | 2,197 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=1048576 | QR | 2,325 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

## Hashing (SHA-2 / SHA-3 / BLAKE2)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `sha256` | input_bytes=64 | classical | 220 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha256` | input_bytes=1024 | classical | 1,773 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha256` | input_bytes=16384 | classical | 3,098 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha256` | input_bytes=262144 | classical | 3,273 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha256` | input_bytes=1048576 | classical | 3,173 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=64 | QR | 185 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=1024 | QR | 1,187 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=16384 | QR | 1,780 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=262144 | QR | 1,851 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=1048576 | QR | 1,868 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=64 | QR | 183 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=1024 | QR | 1,187 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=16384 | QR | 1,794 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=262144 | QR | 1,731 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=1048576 | QR | 1,859 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha3_256` | input_bytes=64 | classical | 136 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_256` | input_bytes=1024 | classical | 742 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_256` | input_bytes=16384 | classical | 1,067 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_256` | input_bytes=262144 | classical | 1,076 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_256` | input_bytes=1048576 | classical | 1,069 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=64 | QR | 132 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=1024 | QR | 463 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=16384 | QR | 567 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=262144 | QR | 593 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=1048576 | QR | 587 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `blake2b` | input_bytes=64 | QR | 220 MB/s | ok |
| `blake2b` | input_bytes=1024 | QR | 1,201 MB/s | ok |
| `blake2b` | input_bytes=16384 | QR | 1,544 MB/s | ok |
| `blake2b` | input_bytes=262144 | QR | 1,578 MB/s | ok |
| `blake2b` | input_bytes=1048576 | QR | 1,590 MB/s | ok |
| `blake2s` | input_bytes=64 | classical | 236 MB/s | ok |
| `blake2s` | input_bytes=1024 | classical | 739 MB/s | ok |
| `blake2s` | input_bytes=16384 | classical | 871 MB/s | ok |
| `blake2s` | input_bytes=262144 | classical | 800 MB/s | ok |
| `blake2s` | input_bytes=1048576 | classical | 764 MB/s | ok |

## Message authentication (HMAC / Poly1305)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `HMAC-SHA256` | input_bytes=64 | classical | 77 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA256` | input_bytes=1024 | classical | 888 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA256` | input_bytes=16384 | classical | 2,723 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA256` | input_bytes=262144 | classical | 2,902 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA256` | input_bytes=1048576 | classical | 3,134 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=64 | QR | 64 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=1024 | QR | 644 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=16384 | QR | 1,598 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=262144 | QR | 1,849 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=1048576 | QR | 1,839 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=64 | QR | 65 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=1024 | QR | 696 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=16384 | QR | 1,632 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=262144 | QR | 1,842 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=1048576 | QR | 1,866 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `Poly1305` | input_bytes=64 | QR | 42 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=1024 | QR | 599 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=16384 | QR | 4,966 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=262144 | QR | 8,236 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=1048576 | QR | 8,534 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

## Key derivation (HKDF / PBKDF2 / Argon2id)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `PBKDF2-HMAC-SHA256` | iterations=10000 | classical | 1,445 ops/s | 689.94 µs | 730.01 µs | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `PBKDF2-HMAC-SHA256` | iterations=100000 | classical | 140.8 ops/s | 6.94 ms | 10.04 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `PBKDF2-HMAC-SHA256` | iterations=600000 | classical | 22.7 ops/s | 44.19 ms | 45.06 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `HKDF-SHA256` | ikm_bytes=64, out_bytes=32 | classical | 580,396 ops/s | 1.67 µs | 1.83 µs | ok · extract-then-expand KDF — HIGH-entropy inputs (RFC 5869) |
| `HKDF-SHA384` | ikm_bytes=64, out_bytes=32 | QR | 477,434 ops/s | 1.96 µs | 2.50 µs | ok · extract-then-expand KDF — HIGH-entropy inputs (RFC 5869) |
| `Argon2id` | profile=interactive, time_cost=2, memory_cost=65536, parallelism=1 | QR | 15.6 ops/s | 63.20 ms | 77.21 ms | ok · memory-hard passphrase KDF — LOW-entropy inputs, GPU/ASIC-resistant |
| `Argon2id` | profile=moderate, time_cost=3, memory_cost=262144, parallelism=4 | QR | 9.47 ops/s | 105.24 ms | 108.44 ms | ok · memory-hard passphrase KDF — LOW-entropy inputs, GPU/ASIC-resistant |

## DDS-Security live handshakes (Fast DDS + CycloneDDS)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `CycloneDDS classical (RSA id · ECDH P-256)` | — | classical | 1.97 ms | 1.97 ms | 5.99 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS classical (RSA id · ECDH P-256) — full process` | — | classical | 105.30 ms | 105.30 ms | 281.52 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-768` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-768 | HYBRID | 2.04 ms | 2.04 ms | 3.52 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-768 — full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-768 | HYBRID | 101.79 ms | 101.79 ms | 134.79 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-1024` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | HYBRID | 1.99 ms | 1.99 ms | 2.18 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-1024 — full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | HYBRID | 98.95 ms | 98.95 ms | 112.49 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS ML-DSA-87 identity (PQ auth)` | — | PQC | 2.30 ms | 2.30 ms | 4.40 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS ML-DSA-87 identity (PQ auth) — full process` | — | PQC | 59.72 ms | 59.72 ms | 64.67 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS full CNSA 2.0 (ML-DSA-87 · ML-KEM-1024)` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | HYBRID | 2.55 ms | 2.55 ms | 7.62 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS full CNSA 2.0 (ML-DSA-87 · ML-KEM-1024) — full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | HYBRID | 59.30 ms | 59.30 ms | 67.62 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `FastDDS PKI-DH local-identity validate — full process` | — | classical | 37.70 ms | 37.70 ms | 86.47 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |

## GPU offload — swapover cost & throughput crossover (scalability, not latency)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `dispatch+sync swapover (unified memory)` | backend=mlx.core, gpu=Apple M5 (Apple GPU / Metal) | classical | 198.08 µs | 198.08 µs | 655.16 µs | ok · irreducible per-offload cost; unified memory (no PCIe). vs 83 ns bus hop / 12 µs ML-KEM — GPU disqualified for the latency path |
| `throughput vs CPU` | batch_elems=4096, backend=mlx.core | classical | — | — | — | ok · CPU wins (swapover not amortized); batch=4,096 f32 = 16 KiB |
| `throughput vs CPU` | batch_elems=65536, backend=mlx.core | classical | — | — | — | ok · CPU wins (swapover not amortized); batch=65,536 f32 = 256 KiB |
| `throughput vs CPU` | batch_elems=262144, backend=mlx.core | classical | — | — | — | ok · CPU wins (swapover not amortized); batch=262,144 f32 = 1024 KiB |
| `throughput vs CPU` | batch_elems=1048576, backend=mlx.core | classical | — | — | — | ok · GPU wins; batch=1,048,576 f32 = 4096 KiB |
| `throughput vs CPU` | batch_elems=4194304, backend=mlx.core | classical | — | — | — | ok · GPU wins; batch=4,194,304 f32 = 16384 KiB |
| `throughput vs CPU` | batch_elems=16777216, backend=mlx.core | classical | — | — | — | ok · GPU wins; batch=16,777,216 f32 = 65536 KiB |
| `crossover batch (GPU starts winning)` | backend=mlx.core | classical | — | — | — | ok · GPU offload pays off above ~1,048,576 f32 elems (~4096 KiB). At 1 KiB/stream that is ~4,096 concurrent streams — i.e. GPU is a SWARM/MESH/high-density-electrode scalability tool, not a per-node one |

## robobus bus / determinism / real-time

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `determinism_probe` | — | classical | — | ⚠️ skipped: no probe()/measure() entrypoint |


---

**Classes.** `PQC` = post-quantum *asymmetric* (FIPS 203 ML-KEM / FIPS 204 ML-DSA), replacing quantum-broken RSA/ECC. `HYBRID` = classical ⊕ PQC (CNSA 2.0 transition, e.g. ECDH ‖ ML-KEM → HKDF-SHA384). `QR` = quantum-**resistant** symmetric/hash (AES-256, ChaCha20-Poly1305, SHA-384/512, SHA3, KMAC, Argon2id) — Grover only square-roots symmetric search, so these keep their margins and are part of CNSA 2.0; *not* PQC (an asymmetric term), but *not* classical either. `classical` = quantum-broken asymmetric (RSA/ECDH/ECDSA/Ed25519) or sub-strength symmetric (AES-128, SHA-256 collision). Latency percentiles are per-operation; throughput is aggregate._
