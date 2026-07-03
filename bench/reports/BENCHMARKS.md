# robobus / PQC-DDS — full-system benchmarks

> **Scope.** Every capability of the stack — post-quantum and classical key encapsulation, hybrid key agreement, digital signatures, authenticated encryption, hashing, MACs, key-derivation, live DDS-Security handshakes, and the robobus bus — measured across all available modes, sizes and techniques by **one script** (`bench/run_benchmarks.py`).

> ⚠️ **Platform caveat.** These figures were measured **on macOS only** so far. They are inherently CPU-, OS- and build-specific and are **not** portable claims. The value here is the *method*: the identical script is designed to run on macOS, Windows, every supported Linux, Android and iOS, skipping only what a given platform lacks. Re-run it on each target to populate that platform's column.

_Generated 2026-07-03 16:57 UTC from `bench/results/latest-*.json`._

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
- **Fidelity tier:** 3-baremetal-partial (real hardware, some noise controls)
- **Uncontrolled noise:** macOS: no core isolation / governor control (soft-RT only)

### formal · cbmc 6.9.0 bounded model checker

- **OS:** formal machine-checked (cbmc 6.9.0 (bit-precise SAT/SMT decision procedure))
- **CPU:** cbmc 6.9.0 bounded model checker — 1 cores
- **Python:** n/a (cbmc)
- **Crypto backends:** cbmc 6.9.0
- **Fidelity tier:** formal (exhaustive proof, not measurement)

### HDL-sim · RTL @ 200 MHz (icarus)

- **OS:** HDL-sim cycle-exact (cocotb/icarus cycle-accurate simulation)
- **CPU:** RTL @ 200 MHz (icarus) — 1 cores
- **Python:** n/a (cocotb)
- **Crypto backends:** cocotb 2.0.1, icarus present
- **Fidelity tier:** 6/7-hdl-sim (cycle-exact RTL, no hardware)

### Linux · armv7l

- **EMULATED ISA (linux/arm/v7, QEMU):** correctness/portability only — timing is NOT cycle-accurate under emulation and is not measured.
- **OS:** Linux 6.12.76-linuxkit (Linux-6.12.76-linuxkit-armv7l-with-glibc2.41)
- **CPU:** armv7l — 10 cores
- **Python:** 3.13.5 (CPython)
- **Crypto backends:** cryptography 43.0.0
- **Absent on this host (SKIPPED):** oqs, argon2, psutil
- **Fidelity tier:** 2-baremetal-untuned (real hardware, default OS noise)
- **Measurement conditions:** isolcpus=none, pinned=False
- **Uncontrolled noise:** no isolated cores (isolcpus=) -> scheduler + IRQ noise

### Linux · i686

- **EMULATED ISA (linux/386, QEMU):** correctness/portability only — timing is NOT cycle-accurate under emulation and is not measured.
- **OS:** Linux 6.12.76-linuxkit (Linux-6.12.76-linuxkit-i686-with-glibc2.41)
- **CPU:** i686 — 10 cores
- **Python:** 3.13.5 (CPython)
- **Crypto backends:** cryptography 43.0.0
- **Absent on this host (SKIPPED):** oqs, argon2, psutil
- **Fidelity tier:** 2-baremetal-untuned (real hardware, default OS noise)
- **Measurement conditions:** isolcpus=none, pinned=False
- **Uncontrolled noise:** no isolated cores (isolcpus=) -> scheduler + IRQ noise

### Linux · ppc64le

- **EMULATED ISA (linux/ppc64le, QEMU):** correctness/portability only — timing is NOT cycle-accurate under emulation and is not measured.
- **OS:** Linux 6.12.76-linuxkit (Linux-6.12.76-linuxkit-ppc64le-with-glibc2.41)
- **CPU:** ppc64le — 10 cores
- **Python:** 3.13.5 (CPython)
- **Crypto backends:** cryptography 43.0.0
- **Absent on this host (SKIPPED):** oqs, argon2, psutil
- **Fidelity tier:** 2-baremetal-untuned (real hardware, default OS noise)
- **Measurement conditions:** isolcpus=none, pinned=False
- **Uncontrolled noise:** no isolated cores (isolcpus=) -> scheduler + IRQ noise

### Linux · riscv64

- **EMULATED ISA (linux/riscv64, QEMU):** correctness/portability only — timing is NOT cycle-accurate under emulation and is not measured.
- **OS:** Linux 6.12.76-linuxkit (Linux-6.12.76-linuxkit-riscv64-with-glibc2.41)
- **CPU:** riscv64 — 10 cores
- **Python:** 3.13.5 (CPython)
- **Crypto backends:** cryptography 43.0.0
- **Absent on this host (SKIPPED):** oqs, argon2, psutil
- **Fidelity tier:** 2-baremetal-untuned (real hardware, default OS noise)
- **Measurement conditions:** isolcpus=none, pinned=False
- **Uncontrolled noise:** no isolated cores (isolcpus=) -> scheduler + IRQ noise

### Linux · s390x

- **EMULATED ISA (linux/s390x, QEMU):** correctness/portability only — timing is NOT cycle-accurate under emulation and is not measured.
- **OS:** Linux 6.12.76-linuxkit (Linux-6.12.76-linuxkit-s390x-with-glibc2.41)
- **CPU:** s390x — 10 cores
- **Python:** 3.13.5 (CPython)
- **Crypto backends:** cryptography 43.0.0
- **Absent on this host (SKIPPED):** oqs, argon2, psutil
- **Fidelity tier:** 2-baremetal-untuned (real hardware, default OS noise)
- **Measurement conditions:** isolcpus=none, pinned=False
- **Uncontrolled noise:** no isolated cores (isolcpus=) -> scheduler + IRQ noise

### Linux · x86_64

- **OS:** Linux 6.17.0-1018-azure (Linux-6.17.0-1018-azure-x86_64-with-glibc2.39)
- **CPU:** x86_64 — 2 cores, 15 GB RAM
- **Python:** 3.12.13 (CPython)
- **Crypto backends:** cryptography 49.0.0, oqs 0.15.0, argon2 25.1.0, psutil 7.2.2
- **Fidelity tier:** 1-virtualized (GitHub-hosted VM — coverage only)
- **Measurement conditions:** SMT=on, isolcpus=none, pinned=False
- **Uncontrolled noise:** SMT/hyperthreading active (sibling-core contention); no isolated cores (isolcpus=) -> scheduler + IRQ noise

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

## Portability / correctness — emulated ISAs (QEMU; timing NOT measured, by design)

**Linux · armv7l**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `KAT sha256` | arch=armv7l | — | — | ok · Merkle-Damgard — length-extendable (key via HMAC) · known-answer vector matches |
| `KAT sha384` | arch=armv7l | — | — | ok · Merkle-Damgard — length-extendable (key via HMAC) · known-answer vector matches |
| `KAT sha512` | arch=armv7l | — | — | ok · Merkle-Damgard — length-extendable (key via HMAC) · known-answer vector matches |
| `KAT sha3_256` | arch=armv7l | — | — | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 · known-answer vector matches |
| `KAT sha3_512` | arch=armv7l | — | — | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 · known-answer vector matches |
| `KAT HMAC-SHA256` | arch=armv7l | — | — | ok · nested MAC — keys a Merkle-Damgard hash safely · RFC vector |
| `struct pack/unpack (wire format)` | host_byteorder=little, arch=armv7l | — | — | ok · little+big-endian round-trip on a little-endian host |
| `AES-256-GCM seal/open round-trip` | arch=armv7l | — | — | ok · Grover → ~128-bit quantum security · encrypt then decrypt |
| `ECDH-P256 shared-secret agreement` | arch=armv7l | — | — | ok · both parties derive the same key |
| `Ed25519 sign/verify` | arch=armv7l | — | — | ok · signature verifies |
| `ML-KEM/ML-DSA round-trips (oqs)` | arch=armv7l | — | — | ⚠️ skipped: liboqs/oqs not built here (ModuleNotFoundError); ML-KEM/ML-DSA use fixed byte encodings (FIPS 203/204) over SHA-3/SHAKE, whose KATs pass above |

**Linux · i686**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `KAT sha256` | arch=i686 | — | — | ok · Merkle-Damgard — length-extendable (key via HMAC) · known-answer vector matches |
| `KAT sha384` | arch=i686 | — | — | ok · Merkle-Damgard — length-extendable (key via HMAC) · known-answer vector matches |
| `KAT sha512` | arch=i686 | — | — | ok · Merkle-Damgard — length-extendable (key via HMAC) · known-answer vector matches |
| `KAT sha3_256` | arch=i686 | — | — | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 · known-answer vector matches |
| `KAT sha3_512` | arch=i686 | — | — | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 · known-answer vector matches |
| `KAT HMAC-SHA256` | arch=i686 | — | — | ok · nested MAC — keys a Merkle-Damgard hash safely · RFC vector |
| `struct pack/unpack (wire format)` | host_byteorder=little, arch=i686 | — | — | ok · little+big-endian round-trip on a little-endian host |
| `AES-256-GCM seal/open round-trip` | arch=i686 | — | — | ok · Grover → ~128-bit quantum security · encrypt then decrypt |
| `ECDH-P256 shared-secret agreement` | arch=i686 | — | — | ok · both parties derive the same key |
| `Ed25519 sign/verify` | arch=i686 | — | — | ok · signature verifies |
| `ML-KEM/ML-DSA round-trips (oqs)` | arch=i686 | — | — | ⚠️ skipped: liboqs/oqs not built here (ModuleNotFoundError); ML-KEM/ML-DSA use fixed byte encodings (FIPS 203/204) over SHA-3/SHAKE, whose KATs pass above |

**Linux · ppc64le**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `KAT sha256` | arch=ppc64le | — | — | ok · Merkle-Damgard — length-extendable (key via HMAC) · known-answer vector matches |
| `KAT sha384` | arch=ppc64le | — | — | ok · Merkle-Damgard — length-extendable (key via HMAC) · known-answer vector matches |
| `KAT sha512` | arch=ppc64le | — | — | ok · Merkle-Damgard — length-extendable (key via HMAC) · known-answer vector matches |
| `KAT sha3_256` | arch=ppc64le | — | — | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 · known-answer vector matches |
| `KAT sha3_512` | arch=ppc64le | — | — | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 · known-answer vector matches |
| `KAT HMAC-SHA256` | arch=ppc64le | — | — | ok · nested MAC — keys a Merkle-Damgard hash safely · RFC vector |
| `struct pack/unpack (wire format)` | host_byteorder=little, arch=ppc64le | — | — | ok · little+big-endian round-trip on a little-endian host |
| `AES-256-GCM seal/open round-trip` | arch=ppc64le | — | — | ok · Grover → ~128-bit quantum security · encrypt then decrypt |
| `ECDH-P256 shared-secret agreement` | arch=ppc64le | — | — | ok · both parties derive the same key |
| `Ed25519 sign/verify` | arch=ppc64le | — | — | ok · signature verifies |
| `ML-KEM/ML-DSA round-trips (oqs)` | arch=ppc64le | — | — | ⚠️ skipped: liboqs/oqs not built here (ModuleNotFoundError); ML-KEM/ML-DSA use fixed byte encodings (FIPS 203/204) over SHA-3/SHAKE, whose KATs pass above |

**Linux · riscv64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `KAT sha256` | arch=riscv64 | — | — | ok · Merkle-Damgard — length-extendable (key via HMAC) · known-answer vector matches |
| `KAT sha384` | arch=riscv64 | — | — | ok · Merkle-Damgard — length-extendable (key via HMAC) · known-answer vector matches |
| `KAT sha512` | arch=riscv64 | — | — | ok · Merkle-Damgard — length-extendable (key via HMAC) · known-answer vector matches |
| `KAT sha3_256` | arch=riscv64 | — | — | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 · known-answer vector matches |
| `KAT sha3_512` | arch=riscv64 | — | — | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 · known-answer vector matches |
| `KAT HMAC-SHA256` | arch=riscv64 | — | — | ok · nested MAC — keys a Merkle-Damgard hash safely · RFC vector |
| `struct pack/unpack (wire format)` | host_byteorder=little, arch=riscv64 | — | — | ok · little+big-endian round-trip on a little-endian host |
| `AES-256-GCM seal/open round-trip` | arch=riscv64 | — | — | ok · Grover → ~128-bit quantum security · encrypt then decrypt |
| `ECDH-P256 shared-secret agreement` | arch=riscv64 | — | — | ok · both parties derive the same key |
| `Ed25519 sign/verify` | arch=riscv64 | — | — | ok · signature verifies |
| `ML-KEM/ML-DSA round-trips (oqs)` | arch=riscv64 | — | — | ⚠️ skipped: liboqs/oqs not built here (ModuleNotFoundError); ML-KEM/ML-DSA use fixed byte encodings (FIPS 203/204) over SHA-3/SHAKE, whose KATs pass above |

**Linux · s390x**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `KAT sha256` | arch=s390x | — | — | ok · Merkle-Damgard — length-extendable (key via HMAC) · known-answer vector matches |
| `KAT sha384` | arch=s390x | — | — | ok · Merkle-Damgard — length-extendable (key via HMAC) · known-answer vector matches |
| `KAT sha512` | arch=s390x | — | — | ok · Merkle-Damgard — length-extendable (key via HMAC) · known-answer vector matches |
| `KAT sha3_256` | arch=s390x | — | — | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 · known-answer vector matches |
| `KAT sha3_512` | arch=s390x | — | — | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 · known-answer vector matches |
| `KAT HMAC-SHA256` | arch=s390x | — | — | ok · nested MAC — keys a Merkle-Damgard hash safely · RFC vector |
| `struct pack/unpack (wire format)` | host_byteorder=big, arch=s390x | — | — | ok · little+big-endian round-trip on a big-endian host |
| `AES-256-GCM seal/open round-trip` | arch=s390x | — | — | ok · Grover → ~128-bit quantum security · encrypt then decrypt |
| `ECDH-P256 shared-secret agreement` | arch=s390x | — | — | ok · both parties derive the same key |
| `Ed25519 sign/verify` | arch=s390x | — | — | ok · signature verifies |
| `ML-KEM/ML-DSA round-trips (oqs)` | arch=s390x | — | — | ⚠️ skipped: liboqs/oqs not built here (ModuleNotFoundError); ML-KEM/ML-DSA use fixed byte encodings (FIPS 203/204) over SHA-3/SHAKE, whose KATs pass above |

## Formal verification — machine-checked proofs of the C bus ring (cbmc) & RTL (SymbiYosys)

**formal · cbmc 6.9.0 bounded model checker**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `PROP_safety` | tool=cbmc, ring_slots=8 | — | — | ok · ring_put/ring_get never index out of bounds or deref a bad pointer, for ANY 64-bit position |
| `PROP_roundtrip` | tool=cbmc, ring_slots=8 | — | — | ok · put(w) then get(w) returns EXACTLY the stamp+payload written, and reports success |
| `PROP_reject_writing` | tool=cbmc, ring_slots=8 | — | — | ok · a reader meeting a slot mid-write (odd sequence) rejects it — no torn read |
| `PROP_reject_stale` | tool=cbmc, ring_slots=8 | — | — | ok · a reader meeting a slot holding a different published generation rejects it |
| `PROP_backpressure` | tool=cbmc, ring_slots=1024 | — | — | ok · within the producer's backpressure window (< ring size) no two live positions alias a slot |

## Shared-memory bus — nanosecond latency (native SPSC ring)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ring put+get, amortized 1-core` | realtime=off, clock_ns_per_tick=41.66667 | — | 131,354,300 ops/s (7.6 ns/op) | — | — | ok · pure ring op cost; clock res 41.7 ns |
| `cross-process one-way latency` | realtime=off, warmup_msgs=20000 | — | 83.3 ns | 83.3 ns | 1.07 ms | ok · 51.8% <100 ns; 20000 msgs warmup discarded; max at 31% of run (mid-run scheduler jitter); no RT |
| `ring put+get, amortized 1-core (RT)` | realtime=on, clock_ns_per_tick=41.66667 | — | 80,145,540 ops/s (12.5 ns/op) | — | — | ok · pure ring op cost; clock res 41.7 ns |
| `cross-process one-way latency (RT)` | realtime=on, warmup_msgs=20000 | — | 83.3 ns | 83.3 ns | 985.29 µs | ok · 55.2% <100 ns; 20000 msgs warmup discarded; max at 58% of run (mid-run scheduler jitter); RT time-constraint policy |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ring put+get, amortized 1-core` | realtime=off, clock_ns_per_tick=41.66667 | — | 295,033,800 ops/s (3.4 ns/op) | — | — | ok · pure ring op cost; clock res 41.7 ns |
| `cross-process one-way latency` | realtime=off, warmup_msgs=20000 | — | 83.3 ns | 83.3 ns | 48.00 µs | ok · 94.2% <100 ns; 20000 msgs warmup discarded; max at 18% of run (mid-run scheduler jitter); no RT |
| `ring put+get, amortized 1-core (RT)` | realtime=on, clock_ns_per_tick=41.66667 | — | 272,456,300 ops/s (3.7 ns/op) | — | — | ok · pure ring op cost; clock res 41.7 ns |
| `cross-process one-way latency (RT)` | realtime=on, warmup_msgs=20000 | — | 83.3 ns | 83.3 ns | 166.7 ns | ok · 98.4% <100 ns; 20000 msgs warmup discarded; max at 20% of run (mid-run scheduler jitter); RT time-constraint policy |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ring put+get, amortized 1-core` | realtime=off, clock_ns_per_tick=1.0 | — | 482,587,900 ops/s (2.1 ns/op) | — | — | ok · pure ring op cost; clock res 1.0 ns |
| `cross-process one-way latency` | realtime=off, warmup_msgs=20000 | — | 88.0 ns | 88.0 ns | 128.0 ns | ok · 98.4% <100 ns; 20000 msgs warmup discarded; max at 92% of run (mid-run scheduler jitter); no RT |
| `ring put+get, amortized 1-core (RT)` | realtime=on, clock_ns_per_tick=1.0 | — | 488,773,700 ops/s (2.0 ns/op) | — | — | ok · pure ring op cost; clock res 1.0 ns |
| `cross-process one-way latency (RT)` | realtime=on, warmup_msgs=20000 | — | 88.0 ns | 88.0 ns | 188.0 ns | ok · 98.2% <100 ns; 20000 msgs warmup discarded; max at 5% of run (mid-run scheduler jitter); RT time-constraint policy |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `ring_op_amortized` | — | — | — | ⚠️ skipped: no fork/mmap on Windows |
| `oneway_latency` | — | — | — | ⚠️ skipped: no fork/mmap on Windows |

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

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `X25519` | op=keygen | classical | 27,477 ops/s | 35.48 µs | 49.29 µs | ok |
| `X25519` | op=derive | classical | 27,777 ops/s | 35.33 µs | 44.15 µs | ok |
| `ECDH-P256` | op=keygen | classical | 61,784 ops/s | 15.62 µs | 27.75 µs | ok |
| `ECDH-P256` | op=derive | classical | 18,135 ops/s | 53.83 µs | 65.87 µs | ok |
| `ML-KEM-512` | op=keygen | PQC | 45,375 ops/s | 21.17 µs | 36.27 µs | ok |
| `ML-KEM-512` | op=encapsulate | PQC | 43,520 ops/s | 22.08 µs | 36.94 µs | ok |
| `ML-KEM-512` | op=decapsulate | PQC | 64,422 ops/s | 15.00 µs | 25.49 µs | ok |
| `ML-KEM-768` | op=keygen | PQC | 34,894 ops/s | 27.61 µs | 42.92 µs | ok |
| `ML-KEM-768` | op=encapsulate | PQC | 34,174 ops/s | 28.18 µs | 44.01 µs | ok |
| `ML-KEM-768` | op=decapsulate | PQC | 44,172 ops/s | 22.00 µs | 32.87 µs | ok |
| `ML-KEM-1024` | op=keygen | PQC | 28,701 ops/s | 33.51 µs | 49.86 µs | ok |
| `ML-KEM-1024` | op=encapsulate | PQC | 28,009 ops/s | 34.40 µs | 49.81 µs | ok |
| `ML-KEM-1024` | op=decapsulate | PQC | 32,929 ops/s | 29.62 µs | 40.65 µs | ok |

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
| `ECDH-P256+ML-KEM-768` | op=full_two_party_handshake | HYBRID | 7,811 handshakes/s | 125.96 µs | 150.96 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |
| `ECDH-P256+ML-KEM-1024` | op=full_two_party_handshake | HYBRID | 7,040 handshakes/s | 140.88 µs | 161.17 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ECDH-P256+ML-KEM-768` | op=full_two_party_handshake | HYBRID | 3,209 handshakes/s | 303.07 µs | 358.25 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |
| `ECDH-P256+ML-KEM-1024` | op=full_two_party_handshake | HYBRID | 3,018 handshakes/s | 323.48 µs | 367.47 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ECDH-P256+ML-KEM-768` | op=full_two_party_handshake | HYBRID | 699.7 handshakes/s | 1.37 ms | 2.29 ms | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |
| `ECDH-P256+ML-KEM-1024` | op=full_two_party_handshake | HYBRID | 554.0 handshakes/s | 1.79 ms | 2.02 ms | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |

## Full authenticated handshake crypto (isolated from DDS transport)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `NIST-1 (ML-KEM-512 + ML-DSA-44)` | op=full_authenticated_handshake | — | 770.0 handshakes/s | 1.16 ms | 4.31 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `NIST-3 (ML-KEM-768 + ML-DSA-65)` | op=full_authenticated_handshake | — | 528.5 handshakes/s | 1.67 ms | 4.08 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `CNSA 2.0 / NIST-5 (ML-KEM-1024 + ML-DSA-87)` | op=full_authenticated_handshake | — | 362.8 handshakes/s | 2.37 ms | 5.86 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `key agreement only (rekey, no identity sig)` | note=see hybrid_kem | — | — | — | — | ok · the recurring/rekey cost is the hybrid_kem group: ~128 µs (ECDH+ML-KEM+HKDF, no signatures) |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `NIST-1 (ML-KEM-512 + ML-DSA-44)` | op=full_authenticated_handshake | — | 1,609 handshakes/s | 599.04 µs | 1.15 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `NIST-3 (ML-KEM-768 + ML-DSA-65)` | op=full_authenticated_handshake | — | 1,076 handshakes/s | 889.21 µs | 1.69 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `CNSA 2.0 / NIST-5 (ML-KEM-1024 + ML-DSA-87)` | op=full_authenticated_handshake | — | 836.8 handshakes/s | 1.15 ms | 1.96 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `key agreement only (rekey, no identity sig)` | note=see hybrid_kem | — | — | — | — | ok · the recurring/rekey cost is the hybrid_kem group: ~128 µs (ECDH+ML-KEM+HKDF, no signatures) |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `NIST-1 (ML-KEM-512 + ML-DSA-44)` | op=full_authenticated_handshake | — | 1,379 handshakes/s | 703.20 µs | 993.54 µs | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `NIST-3 (ML-KEM-768 + ML-DSA-65)` | op=full_authenticated_handshake | — | 1,020 handshakes/s | 950.04 µs | 1.36 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `CNSA 2.0 / NIST-5 (ML-KEM-1024 + ML-DSA-87)` | op=full_authenticated_handshake | — | 857.0 handshakes/s | 1.14 ms | 1.65 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `key agreement only (rekey, no identity sig)` | note=see hybrid_kem | — | — | — | — | ok · the recurring/rekey cost is the hybrid_kem group: ~128 µs (ECDH+ML-KEM+HKDF, no signatures) |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `NIST-1 (ML-KEM-512 + ML-DSA-44)` | op=full_authenticated_handshake | — | 149.2 handshakes/s | 6.53 ms | 10.72 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `NIST-3 (ML-KEM-768 + ML-DSA-65)` | op=full_authenticated_handshake | — | 86.1 handshakes/s | 11.77 ms | 18.24 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `CNSA 2.0 / NIST-5 (ML-KEM-1024 + ML-DSA-87)` | op=full_authenticated_handshake | — | 65.0 handshakes/s | 15.21 ms | 19.80 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `key agreement only (rekey, no identity sig)` | note=see hybrid_kem | — | — | — | — | ok · the recurring/rekey cost is the hybrid_kem group: ~128 µs (ECDH+ML-KEM+HKDF, no signatures) |

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

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `Ed25519` | op=keygen | classical | 27,375 ops/s | 35.73 µs | 46.47 µs | ok |
| `Ed25519` | op=sign | classical | 25,862 ops/s | 37.90 µs | 47.57 µs | ok |
| `Ed25519` | op=verify | classical | 8,389 ops/s | 117.55 µs | 129.66 µs | ok |
| `ECDSA-P256` | op=sign | classical | 33,444 ops/s | 28.83 µs | 43.92 µs | ok |
| `ECDSA-P256` | op=verify | classical | 13,395 ops/s | 72.87 µs | 88.64 µs | ok |
| `RSA-3072-PSS` | op=sign | classical | 490.9 ops/s | 2.01 ms | 2.62 ms | ok |
| `RSA-3072-PSS` | op=verify | classical | 19,769 ops/s | 49.46 µs | 62.22 µs | ok |
| `ML-DSA-44` | op=keygen | PQC | 22,761 ops/s | 42.59 µs | 58.90 µs | ok |
| `ML-DSA-44` | op=sign | PQC | 11,192 ops/s | 73.12 µs | 265.49 µs | ok |
| `ML-DSA-44` | op=verify | PQC | 22,444 ops/s | 43.24 µs | 57.79 µs | ok |
| `ML-DSA-65` | op=keygen | PQC | 14,871 ops/s | 65.46 µs | 81.91 µs | ok |
| `ML-DSA-65` | op=sign | PQC | 7,433 ops/s | 113.88 µs | 386.67 µs | ok |
| `ML-DSA-65` | op=verify | PQC | 13,339 ops/s | 64.55 µs | 184.13 µs | ok |
| `ML-DSA-87` | op=keygen | PQC | 8,857 ops/s | 98.74 µs | 266.74 µs | ok |
| `ML-DSA-87` | op=sign | PQC | 6,098 ops/s | 145.11 µs | 391.72 µs | ok |
| `ML-DSA-87` | op=verify | PQC | 10,124 ops/s | 96.54 µs | 114.29 µs | ok |

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

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `AES-256-GCM` | op=encrypt, input_bytes=64 | QR | 69 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=64 | QR | 70 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=encrypt, input_bytes=1024 | QR | 798 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=1024 | QR | 816 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=encrypt, input_bytes=65536 | QR | 3,575 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-256-GCM` | op=decrypt, input_bytes=65536 | QR | 3,599 MB/s | ok · Grover → ~128-bit quantum security |
| `AES-128-GCM` | op=encrypt, input_bytes=64 | classical | 69 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=64 | classical | 68 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=encrypt, input_bytes=1024 | classical | 583 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=1024 | classical | 813 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=encrypt, input_bytes=65536 | classical | 3,835 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `AES-128-GCM` | op=decrypt, input_bytes=65536 | classical | 3,849 MB/s | ok · Grover → ~64-bit — below the post-quantum bar |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=64 | QR | 58 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=64 | QR | 60 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=1024 | QR | 655 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=1024 | QR | 650 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=65536 | QR | 2,034 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=65536 | QR | 2,080 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

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

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `sha256` | input_bytes=64 | classical | 65 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha256` | input_bytes=1024 | classical | 640 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha256` | input_bytes=65536 | classical | 1,550 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=64 | QR | 54 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=1024 | QR | 396 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha384` | input_bytes=65536 | QR | 748 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=64 | QR | 53 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=1024 | QR | 395 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha512` | input_bytes=65536 | QR | 747 MB/s | ok · Merkle-Damgard — length-extendable (key via HMAC) |
| `sha3_256` | input_bytes=64 | classical | 48 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_256` | input_bytes=1024 | classical | 295 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_256` | input_bytes=65536 | classical | 426 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=64 | QR | 49 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=1024 | QR | 186 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `sha3_512` | input_bytes=65536 | QR | 240 MB/s | ok · Keccak sponge — length-extension-immune, design-diverse from SHA-2 |
| `blake2b` | input_bytes=64 | QR | 80 MB/s | ok |
| `blake2b` | input_bytes=1024 | QR | 514 MB/s | ok |
| `blake2b` | input_bytes=65536 | QR | 739 MB/s | ok |
| `blake2s` | input_bytes=64 | classical | 86 MB/s | ok |
| `blake2s` | input_bytes=1024 | classical | 369 MB/s | ok |
| `blake2s` | input_bytes=65536 | classical | 467 MB/s | ok |

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

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `HMAC-SHA256` | input_bytes=64 | classical | 30 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA256` | input_bytes=1024 | classical | 373 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA256` | input_bytes=65536 | classical | 1,501 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=64 | QR | 23 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=1024 | QR | 243 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA384` | input_bytes=65536 | QR | 732 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=64 | QR | 22 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=1024 | QR | 243 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `HMAC-SHA512` | input_bytes=65536 | QR | 732 MB/s | ok · nested MAC — keys a Merkle-Damgard hash safely |
| `Poly1305` | input_bytes=64 | QR | 19 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=1024 | QR | 275 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=65536 | QR | 4,873 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

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
| `PBKDF2-HMAC-SHA256` | iterations=10000 | classical | 1,445 ops/s | 689.94 µs | 730.01 µs | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `PBKDF2-HMAC-SHA256` | iterations=100000 | classical | 140.8 ops/s | 6.94 ms | 10.04 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `PBKDF2-HMAC-SHA256` | iterations=600000 | classical | 22.7 ops/s | 44.19 ms | 45.06 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `HKDF-SHA256` | ikm_bytes=64, out_bytes=32 | classical | 580,396 ops/s | 1.67 µs | 1.83 µs | ok · extract-then-expand KDF — HIGH-entropy inputs (RFC 5869) |
| `HKDF-SHA384` | ikm_bytes=64, out_bytes=32 | QR | 477,434 ops/s | 1.96 µs | 2.50 µs | ok · extract-then-expand KDF — HIGH-entropy inputs (RFC 5869) |
| `Argon2id` | profile=interactive, time_cost=2, memory_cost=65536, parallelism=1 | QR | 15.6 ops/s | 63.20 ms | 77.21 ms | ok · memory-hard passphrase KDF — LOW-entropy inputs, GPU/ASIC-resistant |
| `Argon2id` | profile=moderate, time_cost=3, memory_cost=262144, parallelism=4 | QR | 9.47 ops/s | 105.24 ms | 108.44 ms | ok · memory-hard passphrase KDF — LOW-entropy inputs, GPU/ASIC-resistant |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `PBKDF2-HMAC-SHA256` | iterations=10000 | classical | 341.3 ops/s | 2.93 ms | 3.00 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `PBKDF2-HMAC-SHA256` | iterations=100000 | classical | 34.2 ops/s | 29.22 ms | 29.34 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `PBKDF2-HMAC-SHA256` | iterations=600000 | classical | 5.71 ops/s | 175.11 ms | 175.26 ms | ok · nested MAC — keys a Merkle-Damgard hash safely · iteration-only passphrase KDF — NO memory-hardness (weakest) |
| `HKDF-SHA256` | ikm_bytes=64, out_bytes=32 | classical | 219,175 ops/s | 4.25 µs | 4.49 µs | ok · extract-then-expand KDF — HIGH-entropy inputs (RFC 5869) |
| `HKDF-SHA384` | ikm_bytes=64, out_bytes=32 | QR | 167,654 ops/s | 5.60 µs | 5.96 µs | ok · extract-then-expand KDF — HIGH-entropy inputs (RFC 5869) |
| `Argon2id` | profile=interactive, time_cost=2, memory_cost=65536, parallelism=1 | QR | 13.4 ops/s | 74.60 ms | 75.97 ms | ok · memory-hard passphrase KDF — LOW-entropy inputs, GPU/ASIC-resistant |
| `Argon2id` | profile=moderate, time_cost=3, memory_cost=262144, parallelism=4 | QR | 6.04 ops/s | 164.98 ms | 167.88 ms | ok · memory-hard passphrase KDF — LOW-entropy inputs, GPU/ASIC-resistant |

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
| `CycloneDDS` | — | — | — | ⚠️ skipped: CycloneDDS PQC test binary not built on this platform |
| `FastDDS` | — | — | — | ⚠️ skipped: Fast DDS PKI-DH test binary not built on this platform |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `CycloneDDS classical (RSA id · ECDH P-256)` | — | — | 1.97 ms | 1.97 ms | 5.99 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS classical (RSA id · ECDH P-256) — full process` | — | — | 105.30 ms | 105.30 ms | 281.52 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-768` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-768 | — | 2.04 ms | 2.04 ms | 3.52 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-768 — full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-768 | — | 101.79 ms | 101.79 ms | 134.79 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-1024` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | — | 1.99 ms | 1.99 ms | 2.18 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-1024 — full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | — | 98.95 ms | 98.95 ms | 112.49 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS ML-DSA-87 identity (PQ auth)` | — | — | 2.30 ms | 2.30 ms | 4.40 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS ML-DSA-87 identity (PQ auth) — full process` | — | — | 59.72 ms | 59.72 ms | 64.67 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS full CNSA 2.0 (ML-DSA-87 · ML-KEM-1024)` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | — | 2.55 ms | 2.55 ms | 7.62 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS full CNSA 2.0 (ML-DSA-87 · ML-KEM-1024) — full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | — | 59.30 ms | 59.30 ms | 67.62 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `FastDDS PKI-DH local-identity validate — full process` | — | — | 37.70 ms | 37.70 ms | 86.47 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `CycloneDDS` | — | — | — | ⚠️ skipped: CycloneDDS PQC test binary not built on this platform |
| `FastDDS` | — | — | — | ⚠️ skipped: Fast DDS PKI-DH test binary not built on this platform |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `CycloneDDS` | — | — | — | ⚠️ skipped: CycloneDDS PQC test binary not built on this platform |
| `FastDDS` | — | — | — | ⚠️ skipped: Fast DDS PKI-DH test binary not built on this platform |

## GPU offload — swapover cost & throughput crossover (scalability, not latency)

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `dispatch+sync swapover (unified memory)` | backend=mlx.core, gpu=Apple M5 (Apple GPU / Metal) | — | 198.08 µs | 198.08 µs | 655.16 µs | ok · irreducible per-offload cost; unified memory (no PCIe). vs 83 ns bus hop / 12 µs ML-KEM — GPU disqualified for the latency path |
| `throughput vs CPU` | batch_elems=4096, backend=mlx.core | — | — | — | — | ok · CPU wins (swapover not amortized); batch=4,096 f32 = 16 KiB |
| `throughput vs CPU` | batch_elems=65536, backend=mlx.core | — | — | — | — | ok · CPU wins (swapover not amortized); batch=65,536 f32 = 256 KiB |
| `throughput vs CPU` | batch_elems=262144, backend=mlx.core | — | — | — | — | ok · CPU wins (swapover not amortized); batch=262,144 f32 = 1024 KiB |
| `throughput vs CPU` | batch_elems=1048576, backend=mlx.core | — | — | — | — | ok · GPU wins; batch=1,048,576 f32 = 4096 KiB |
| `throughput vs CPU` | batch_elems=4194304, backend=mlx.core | — | — | — | — | ok · GPU wins; batch=4,194,304 f32 = 16384 KiB |
| `throughput vs CPU` | batch_elems=16777216, backend=mlx.core | — | — | — | — | ok · GPU wins; batch=16,777,216 f32 = 65536 KiB |
| `crossover batch (GPU starts winning)` | backend=mlx.core | — | — | — | — | ok · GPU offload pays off above ~1,048,576 f32 elems (~4096 KiB). At 1 KiB/stream that is ~4,096 concurrent streams — i.e. GPU is a SWARM/MESH/high-density-electrode scalability tool, not a per-node one |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `swapover` | — | — | — | ⚠️ skipped: no GPU compute backend and no GPU hardware detected |
| `throughput_crossover` | — | — | — | ⚠️ skipped: no GPU compute backend and no GPU hardware detected |

## RTL / FPGA (cycle-exact simulation + formal proof — no hardware)

**HDL-sim · RTL @ 200 MHz (icarus)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `SPSC FIFO enqueue->dequeue latency` | clock_mhz=200.0, width_bits=64, depth=16 | — | 10.0 ns | 10.0 ns | 0.0 ns | ok · 2 clock cycles, cycle-exact; = 10.00 ns @ 200 MHz. The bus ring as RTL. |
| `SPSC FIFO steady-state throughput` | clock_mhz=200.0 | — | 199,902,391 items/s | — | — | ok · 1.000 items/cycle x 200 MHz (1.0 = full rate) |
| `SPSC FIFO formal proof (SymbiYosys + z3)` | method=k-induction | — | — | — | — | ok · PROVEN unbounded (k-induction): never overflow, never full&empty, count consistent |

## robobus bus / determinism / real-time

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `determinism_probe` | — | — | — | ⚠️ skipped: package import failed: No module named 'robobus' |
| `bus_latency` | — | — | — | ⚠️ skipped: package import failed: No module named 'robobus' |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `determinism_probe` | — | — | — | ⚠️ skipped: no probe()/measure() entrypoint |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `determinism_probe` | — | — | — | ⚠️ skipped: package import failed: No module named 'robobus' |
| `bus_latency` | — | — | — | ⚠️ skipped: package import failed: No module named 'robobus' |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `determinism_probe` | — | — | — | ⚠️ skipped: package import failed: No module named 'robobus' |
| `bus_latency` | — | — | — | ⚠️ skipped: package import failed: No module named 'robobus' |


---

**Classes.** `PQC` = post-quantum *asymmetric* (FIPS 203 ML-KEM / FIPS 204 ML-DSA), replacing quantum-broken RSA/ECC. `HYBRID` = classical ⊕ PQC (CNSA 2.0 transition, e.g. ECDH ‖ ML-KEM → HKDF-SHA384). `QR` = quantum-**resistant** symmetric/hash (AES-256, ChaCha20-Poly1305, SHA-384/512, SHA3, KMAC, Argon2id) — Grover only square-roots symmetric search, so these keep their margins and are part of CNSA 2.0; *not* PQC (an asymmetric term), but *not* classical either. `classical` = quantum-broken asymmetric (RSA/ECDH/ECDSA/Ed25519) or sub-strength symmetric (AES-128, SHA-256 collision). Latency percentiles are per-operation; throughput is aggregate._
