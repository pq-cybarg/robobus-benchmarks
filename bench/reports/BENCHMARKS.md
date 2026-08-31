# robobus / PQC-DDS, full-system benchmarks

> **Scope.** Every capability of the stack, post-quantum and classical key encapsulation, hybrid key agreement, digital signatures, authenticated encryption, hashing, MACs, key-derivation, live DDS-Security handshakes, and the robobus bus, measured across all available modes, sizes and techniques by **one script** (`bench/run_benchmarks.py`).

> **Platform caveat.** These figures were measured **on macOS only** so far. They are inherently CPU-, OS- and build-specific and are **not** portable claims. The value here is the *method*: the identical script is designed to run on macOS, Windows, every supported Linux, Android and iOS, skipping only what a given platform lacks. Re-run it on each target to populate that platform's column.

_Generated 2026-08-31 01:29 UTC from `bench/results/latest-*.json`._

## Platforms measured

### Darwin · Apple M1 (Virtual)

- **OS:** Darwin 25.5.0 (macOS-26.5.2-arm64-arm-64bit)
- **CPU:** Apple M1 (Virtual), 3 cores, 7 GB RAM
- **Python:** 3.12.10 (CPython)
- **Crypto backends:** cryptography 50.0.1, oqs 0.16.0, argon2 25.1.0, psutil 7.2.2
- **Fidelity tier:** 1-virtualized (GitHub-hosted VM — coverage only)
- **Uncontrolled noise:** macOS: no core isolation / governor control (soft-RT only)

### Darwin · Apple M5

- **OS:** Darwin 25.1.0 (macOS-26.1-arm64-arm-64bit)
- **CPU:** Apple M5, 10 cores, 32 GB RAM
- **Python:** 3.12.13 (CPython)
- **Crypto backends:** cryptography 49.0.0, oqs 0.15.0, argon2 25.1.0, psutil 7.2.2, blake3 1.0.9
- **Fidelity tier:** 3-baremetal-partial (real hardware, some noise controls)
- **Uncontrolled noise:** macOS: no core isolation / governor control (soft-RT only)

### Darwin · PQC-DDS build, macOS Apple Silicon CI

- **OS:** Darwin 25.1.0 (macOS-26.1-arm64-arm-64bit)
- **CPU:** PQC-DDS build, macOS Apple Silicon CI, 10 cores, 32 GB RAM
- **Python:** 3.12.13 (CPython)
- **Crypto backends:** cryptography 49.0.0, oqs 0.15.0, argon2 25.1.0, psutil 7.2.2, blake3 1.0.9
- **Fidelity tier:** 3-baremetal-partial (real hardware, some noise controls)
- **Uncontrolled noise:** macOS: no core isolation / governor control (soft-RT only)

### formal · cbmc 6.9.0 bounded model checker

- **OS:** formal machine-checked (cbmc 6.9.0 (bit-precise SAT/SMT decision procedure))
- **CPU:** cbmc 6.9.0 bounded model checker, 1 cores
- **Python:** n/a (cbmc)
- **Crypto backends:** cbmc 6.9.0
- **Fidelity tier:** formal (exhaustive proof, not measurement)

### HDL-sim · RTL @ 200 MHz (icarus)

- **OS:** HDL-sim cycle-exact (cocotb/icarus cycle-accurate simulation)
- **CPU:** RTL @ 200 MHz (icarus), 1 cores
- **Python:** n/a (cocotb)
- **Crypto backends:** cocotb 2.0.1, icarus present
- **Fidelity tier:** 6/7-hdl-sim (cycle-exact RTL, no hardware)

### Linux · armv7l

- **EMULATED ISA (linux/arm/v7, QEMU):** correctness/portability only , timing is NOT cycle-accurate under emulation and is not measured.
- **OS:** Linux 6.12.76-linuxkit (Linux-6.12.76-linuxkit-armv7l-with-glibc2.41)
- **CPU:** armv7l, 10 cores
- **Python:** 3.13.5 (CPython)
- **Crypto backends:** cryptography 43.0.0, oqs 0.15.0
- **Absent on this host (SKIPPED):** argon2, psutil
- **Fidelity tier:** 2-baremetal-untuned (real hardware, default OS noise)
- **Measurement conditions:** isolcpus=none, pinned=False
- **Uncontrolled noise:** no isolated cores (isolcpus=) -> scheduler + IRQ noise

### Linux · PQC-DDS build, debian trixie (x86_64 CI)

- **OS:** Linux 6.17.0-1018-azure (Linux-6.17.0-1018-azure-x86_64-with-glibc2.41)
- **CPU:** PQC-DDS build, debian trixie (x86_64 CI), 2 cores
- **Python:** 3.13.5 (CPython)
- **Crypto backends:** cryptography 43.0.0
- **Absent on this host (SKIPPED):** oqs, argon2, psutil
- **Fidelity tier:** 1-virtualized (GitHub-hosted VM, coverage only)
- **Measurement conditions:** governor=performance, turbo=on, SMT=on, isolcpus=none, pinned=False
- **Uncontrolled noise:** turbo/boost on (opportunistic clocks -> variance); SMT/hyperthreading active (sibling-core contention); no isolated cores (isolcpus=) -> scheduler + IRQ noise

### Linux · i686

- **EMULATED ISA (linux/386, QEMU):** correctness/portability only , timing is NOT cycle-accurate under emulation and is not measured.
- **OS:** Linux 6.12.76-linuxkit (Linux-6.12.76-linuxkit-i686-with-glibc2.41)
- **CPU:** i686, 10 cores
- **Python:** 3.13.5 (CPython)
- **Crypto backends:** cryptography 43.0.0, oqs 0.15.0
- **Absent on this host (SKIPPED):** argon2, psutil
- **Fidelity tier:** 2-baremetal-untuned (real hardware, default OS noise)
- **Measurement conditions:** isolcpus=none, pinned=False
- **Uncontrolled noise:** no isolated cores (isolcpus=) -> scheduler + IRQ noise

### Linux · ppc64le

- **EMULATED ISA (linux/ppc64le, QEMU):** correctness/portability only , timing is NOT cycle-accurate under emulation and is not measured.
- **OS:** Linux 6.12.76-linuxkit (Linux-6.12.76-linuxkit-ppc64le-with-glibc2.41)
- **CPU:** ppc64le, 10 cores
- **Python:** 3.13.5 (CPython)
- **Crypto backends:** cryptography 43.0.0, oqs 0.15.0
- **Absent on this host (SKIPPED):** argon2, psutil
- **Fidelity tier:** 2-baremetal-untuned (real hardware, default OS noise)
- **Measurement conditions:** isolcpus=none, pinned=False
- **Uncontrolled noise:** no isolated cores (isolcpus=) -> scheduler + IRQ noise

### Linux · riscv64

- **EMULATED ISA (linux/riscv64, QEMU):** correctness/portability only , timing is NOT cycle-accurate under emulation and is not measured.
- **OS:** Linux 6.12.76-linuxkit (Linux-6.12.76-linuxkit-riscv64-with-glibc2.41)
- **CPU:** riscv64, 10 cores
- **Python:** 3.13.5 (CPython)
- **Crypto backends:** cryptography 43.0.0, oqs 0.15.0
- **Absent on this host (SKIPPED):** argon2, psutil
- **Fidelity tier:** 2-baremetal-untuned (real hardware, default OS noise)
- **Measurement conditions:** isolcpus=none, pinned=False
- **Uncontrolled noise:** no isolated cores (isolcpus=) -> scheduler + IRQ noise

### Linux · s390x

- **EMULATED ISA (linux/s390x, QEMU):** correctness/portability only , timing is NOT cycle-accurate under emulation and is not measured.
- **OS:** Linux 6.12.76-linuxkit (Linux-6.12.76-linuxkit-s390x-with-glibc2.41)
- **CPU:** s390x, 10 cores
- **Python:** 3.13.5 (CPython)
- **Crypto backends:** cryptography 43.0.0, oqs 0.15.0
- **Absent on this host (SKIPPED):** argon2, psutil
- **Fidelity tier:** 2-baremetal-untuned (real hardware, default OS noise)
- **Measurement conditions:** isolcpus=none, pinned=False
- **Uncontrolled noise:** no isolated cores (isolcpus=) -> scheduler + IRQ noise

### Linux · x86_64

- **OS:** Linux 6.17.0-1020-azure (Linux-6.17.0-1020-azure-x86_64-with-glibc2.39)
- **CPU:** x86_64, 2 cores, 15 GB RAM
- **Python:** 3.12.13 (CPython)
- **Crypto backends:** cryptography 50.0.0, oqs 0.16.0, argon2 25.1.0, psutil 7.2.2
- **Fidelity tier:** 1-virtualized (GitHub-hosted VM — coverage only)
- **Measurement conditions:** SMT=on, isolcpus=none, pinned=False
- **Uncontrolled noise:** SMT/hyperthreading active (sibling-core contention); no isolated cores (isolcpus=) -> scheduler + IRQ noise

### Windows · AMD64

- **OS:** Windows 2025Server (Windows-2025Server-10.0.26100-SP0)
- **CPU:** AMD64 Family 25 Model 1 Stepping 1, AuthenticAMD, 2 cores, 15 GB RAM
- **Python:** 3.12.10 (CPython)
- **Crypto backends:** cryptography 49.0.0, oqs 0.15.0, argon2 25.1.0, psutil 7.2.2
- **Fidelity tier:** 1-virtualized (GitHub-hosted VM, coverage only)

## How to reproduce

```bash
# one script, every platform, measures what it can, skips the rest with a reason
python bench/run_benchmarks.py            # full run
python bench/run_benchmarks.py --quick    # fast pass
python bench/render_report.py             # regenerate this report + the HTML site
```

Optional backends unlock more rows: `cryptography` (AEAD, ECDH, classical signatures), `oqs`/liboqs (ML-KEM, ML-DSA), `argon2-cffi` (Argon2id). Absent backends produce **SKIPPED** rows, never a crash, which is exactly how the same script stays valid on constrained platforms (e.g. stock Android/iOS Python).

## Portability / correctness, emulated ISAs (QEMU; timing NOT measured, by design)

**Linux · armv7l**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `KAT sha256` | arch=armv7l | ,  | ,  | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 · known-answer vector matches |
| `KAT sha384` | arch=armv7l | ,  | ,  | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 · known-answer vector matches |
| `KAT sha512` | arch=armv7l | ,  | ,  | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade · known-answer vector matches |
| `KAT sha3_256` | arch=armv7l | ,  | ,  | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 · known-answer vector matches |
| `KAT sha3_512` | arch=armv7l | ,  | ,  | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade · known-answer vector matches |
| `KAT HMAC-SHA256` | arch=armv7l | ,  | ,  | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) · RFC vector |
| `struct pack/unpack (wire format)` | host_byteorder=little, arch=armv7l | ,  | ,  | ok · little+big-endian round-trip on a little-endian host |
| `AES-256-GCM seal/open round-trip` | arch=armv7l | ,  | ,  | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) · encrypt then decrypt |
| `ECDH-P256 shared-secret agreement` | arch=armv7l | ,  | ,  | ok · both parties derive the same key |
| `Ed25519 sign/verify` | arch=armv7l | ,  | ,  | ok · signature verifies |
| `ML-KEM-768 encap/decap secret match` | arch=armv7l | ,  | ,  | ok · FIPS 203 across this ISA |
| `ML-DSA-87 sign/verify` | arch=armv7l | ,  | ,  | ok · FIPS 204 across this ISA |

**Linux · i686**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `KAT sha256` | arch=i686 | ,  | ,  | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 · known-answer vector matches |
| `KAT sha384` | arch=i686 | ,  | ,  | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 · known-answer vector matches |
| `KAT sha512` | arch=i686 | ,  | ,  | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade · known-answer vector matches |
| `KAT sha3_256` | arch=i686 | ,  | ,  | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 · known-answer vector matches |
| `KAT sha3_512` | arch=i686 | ,  | ,  | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade · known-answer vector matches |
| `KAT HMAC-SHA256` | arch=i686 | ,  | ,  | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) · RFC vector |
| `struct pack/unpack (wire format)` | host_byteorder=little, arch=i686 | ,  | ,  | ok · little+big-endian round-trip on a little-endian host |
| `AES-256-GCM seal/open round-trip` | arch=i686 | ,  | ,  | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) · encrypt then decrypt |
| `ECDH-P256 shared-secret agreement` | arch=i686 | ,  | ,  | ok · both parties derive the same key |
| `Ed25519 sign/verify` | arch=i686 | ,  | ,  | ok · signature verifies |
| `ML-KEM-768 encap/decap secret match` | arch=i686 | ,  | ,  | ok · FIPS 203 across this ISA |
| `ML-DSA-87 sign/verify` | arch=i686 | ,  | ,  | ok · FIPS 204 across this ISA |

**Linux · ppc64le**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `KAT sha256` | arch=ppc64le | ,  | ,  | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 · known-answer vector matches |
| `KAT sha384` | arch=ppc64le | ,  | ,  | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 · known-answer vector matches |
| `KAT sha512` | arch=ppc64le | ,  | ,  | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade · known-answer vector matches |
| `KAT sha3_256` | arch=ppc64le | ,  | ,  | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 · known-answer vector matches |
| `KAT sha3_512` | arch=ppc64le | ,  | ,  | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade · known-answer vector matches |
| `KAT HMAC-SHA256` | arch=ppc64le | ,  | ,  | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) · RFC vector |
| `struct pack/unpack (wire format)` | host_byteorder=little, arch=ppc64le | ,  | ,  | ok · little+big-endian round-trip on a little-endian host |
| `AES-256-GCM seal/open round-trip` | arch=ppc64le | ,  | ,  | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) · encrypt then decrypt |
| `ECDH-P256 shared-secret agreement` | arch=ppc64le | ,  | ,  | ok · both parties derive the same key |
| `Ed25519 sign/verify` | arch=ppc64le | ,  | ,  | ok · signature verifies |
| `ML-KEM-768 encap/decap secret match` | arch=ppc64le | ,  | ,  | ok · FIPS 203 across this ISA |
| `ML-DSA-87 sign/verify` | arch=ppc64le | ,  | ,  | ok · FIPS 204 across this ISA |

**Linux · riscv64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `KAT sha256` | arch=riscv64 | ,  | ,  | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 · known-answer vector matches |
| `KAT sha384` | arch=riscv64 | ,  | ,  | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 · known-answer vector matches |
| `KAT sha512` | arch=riscv64 | ,  | ,  | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade · known-answer vector matches |
| `KAT sha3_256` | arch=riscv64 | ,  | ,  | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 · known-answer vector matches |
| `KAT sha3_512` | arch=riscv64 | ,  | ,  | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade · known-answer vector matches |
| `KAT HMAC-SHA256` | arch=riscv64 | ,  | ,  | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) · RFC vector |
| `struct pack/unpack (wire format)` | host_byteorder=little, arch=riscv64 | ,  | ,  | ok · little+big-endian round-trip on a little-endian host |
| `AES-256-GCM seal/open round-trip` | arch=riscv64 | ,  | ,  | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) · encrypt then decrypt |
| `ECDH-P256 shared-secret agreement` | arch=riscv64 | ,  | ,  | ok · both parties derive the same key |
| `Ed25519 sign/verify` | arch=riscv64 | ,  | ,  | ok · signature verifies |
| `ML-KEM-768 encap/decap secret match` | arch=riscv64 | ,  | ,  | ok · FIPS 203 across this ISA |
| `ML-DSA-87 sign/verify` | arch=riscv64 | ,  | ,  | ok · FIPS 204 across this ISA |

**Linux · s390x**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `KAT sha256` | arch=s390x | ,  | ,  | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 · known-answer vector matches |
| `KAT sha384` | arch=s390x | ,  | ,  | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 · known-answer vector matches |
| `KAT sha512` | arch=s390x | ,  | ,  | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade · known-answer vector matches |
| `KAT sha3_256` | arch=s390x | ,  | ,  | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 · known-answer vector matches |
| `KAT sha3_512` | arch=s390x | ,  | ,  | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade · known-answer vector matches |
| `KAT HMAC-SHA256` | arch=s390x | ,  | ,  | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) · RFC vector |
| `struct pack/unpack (wire format)` | host_byteorder=big, arch=s390x | ,  | ,  | ok · little+big-endian round-trip on a big-endian host |
| `AES-256-GCM seal/open round-trip` | arch=s390x | ,  | ,  | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) · encrypt then decrypt |
| `ECDH-P256 shared-secret agreement` | arch=s390x | ,  | ,  | ok · both parties derive the same key |
| `Ed25519 sign/verify` | arch=s390x | ,  | ,  | ok · signature verifies |
| `ML-KEM-768 encap/decap secret match` | arch=s390x | ,  | ,  | ok · FIPS 203 across this ISA |
| `ML-DSA-87 sign/verify` | arch=s390x | ,  | ,  | ok · FIPS 204 across this ISA |

## Formal verification, machine-checked proofs of the C bus ring (cbmc) & RTL (SymbiYosys)

**formal · cbmc 6.9.0 bounded model checker**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `PROP_safety` | tool=cbmc, ring_slots=8 | ,  | ,  | ok · ring_put/ring_get never index out of bounds or deref a bad pointer, for ANY 64-bit position |
| `PROP_roundtrip` | tool=cbmc, ring_slots=8 | ,  | ,  | ok · put(w) then get(w) returns EXACTLY the stamp+payload written, and reports success |
| `PROP_reject_writing` | tool=cbmc, ring_slots=8 | ,  | ,  | ok · a reader meeting a slot mid-write (odd sequence) rejects it, no torn read |
| `PROP_reject_stale` | tool=cbmc, ring_slots=8 | ,  | ,  | ok · a reader meeting a slot holding a different published generation rejects it |
| `PROP_backpressure` | tool=cbmc, ring_slots=1024 | ,  | ,  | ok · within the producer's backpressure window (< ring size) no two live positions alias a slot |

## Shared-memory bus, nanosecond latency (native SPSC ring)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ring put+get, amortized 1-core` | realtime=off, clock_ns_per_tick=41.66667 | ,  | 146,598,200 ops/s (6.8 ns/op) | ,  | ,  | ok · pure ring op cost; clock mach_absolute_time res 41.7 ns |
| `cross-thread one-way latency` | realtime=off, ipc=fork+mmap(MAP_SHARED), warmup_msgs=20000 | ,  | 83.3 ns | 83.3 ns | 4.29 µs | ok · 98.0% <100 ns; max at 56% of run (mid-run scheduler jitter); no RT |
| `cross-process one-way latency` | realtime=off, ipc=fork+mmap(MAP_SHARED), warmup_msgs=20000 | ,  | 83.3 ns | 83.3 ns | 125.0 ns | ok · 98.7% <100 ns; max at 16% of run (mid-run scheduler jitter); no RT |
| `ring put+get, amortized 1-core (RT)` | realtime=on, clock_ns_per_tick=41.66667 | ,  | 128,959,300 ops/s (7.8 ns/op) | ,  | ,  | ok · pure ring op cost; clock mach_absolute_time res 41.7 ns |
| `cross-thread one-way latency (RT)` | realtime=on, ipc=fork+mmap(MAP_SHARED), warmup_msgs=20000 | ,  | 83.3 ns | 83.3 ns | 2.04 µs | ok · 97.2% <100 ns; max at 11% of run (mid-run scheduler jitter); RT hardened |
| `cross-process one-way latency (RT)` | realtime=on, ipc=fork+mmap(MAP_SHARED), warmup_msgs=20000 | ,  | 83.3 ns | 83.3 ns | 1.67 µs | ok · 97.5% <100 ns; max at 38% of run (mid-run scheduler jitter); RT hardened |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ring put+get, amortized 1-core` | realtime=off, clock_ns_per_tick=41.66667 | ,  | 295,033,800 ops/s (3.4 ns/op) | ,  | ,  | ok · pure ring op cost; clock res 41.7 ns |
| `cross-process one-way latency` | realtime=off, warmup_msgs=20000 | ,  | 83.3 ns | 83.3 ns | 48.00 µs | ok · 94.2% <100 ns; 20000 msgs warmup discarded; max at 18% of run (mid-run scheduler jitter); no RT |
| `ring put+get, amortized 1-core (RT)` | realtime=on, clock_ns_per_tick=41.66667 | ,  | 272,456,300 ops/s (3.7 ns/op) | ,  | ,  | ok · pure ring op cost; clock res 41.7 ns |
| `cross-process one-way latency (RT)` | realtime=on, warmup_msgs=20000 | ,  | 83.3 ns | 83.3 ns | 166.7 ns | ok · 98.4% <100 ns; 20000 msgs warmup discarded; max at 20% of run (mid-run scheduler jitter); RT time-constraint policy |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ring put+get, amortized 1-core` | realtime=off, clock_ns_per_tick=1.0 | ,  | 547,484,300 ops/s (1.8 ns/op) | ,  | ,  | ok · pure ring op cost; clock CLOCK_MONOTONIC_RAW res 1.0 ns |
| `cross-thread one-way latency` | realtime=off, ipc=fork+mmap(MAP_SHARED), warmup_msgs=20000 | ,  | 120.0 ns | 120.0 ns | 130.0 ns | ok · 0.0% <100 ns; max at 32% of run (mid-run scheduler jitter); no RT |
| `cross-process one-way latency` | realtime=off, ipc=fork+mmap(MAP_SHARED), warmup_msgs=20000 | ,  | 130.0 ns | 130.0 ns | 140.0 ns | ok · 0.0% <100 ns; max at 88% of run (mid-run scheduler jitter); no RT |
| `ring put+get, amortized 1-core (RT)` | realtime=on, clock_ns_per_tick=1.0 | ,  | 547,951,200 ops/s (1.8 ns/op) | ,  | ,  | ok · pure ring op cost; clock CLOCK_MONOTONIC_RAW res 1.0 ns |
| `cross-thread one-way latency (RT)` | realtime=on, ipc=fork+mmap(MAP_SHARED), warmup_msgs=20000 | ,  | 120.0 ns | 120.0 ns | 130.0 ns | ok · 0.0% <100 ns; max at 11% of run (mid-run scheduler jitter); RT hardened |
| `cross-process one-way latency (RT)` | realtime=on, ipc=fork+mmap(MAP_SHARED), warmup_msgs=20000 | ,  | 130.0 ns | 130.0 ns | 140.0 ns | ok · 0.0% <100 ns; max at 60% of run (mid-run scheduler jitter); RT hardened |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ring put+get, amortized 1-core` | realtime=off, clock_ns_per_tick=100.0 | ,  | 535,234,500 ops/s (1.9 ns/op) | ,  | ,  | ok · pure ring op cost; clock QueryPerformanceCounter res 100.0 ns |
| `cross-thread one-way latency` | realtime=off, ipc=CreateProcess+CreateFileMapping, warmup_msgs=20000 | ,  | 100.0 ns | 100.0 ns | 300.0 ns | ok · 1.9% <100 ns; max at 89% of run (mid-run scheduler jitter); no RT |
| `cross-process one-way latency` | realtime=off, ipc=CreateProcess+CreateFileMapping, warmup_msgs=20000 | ,  | 100.0 ns | 100.0 ns | 600.0 ns | ok · 0.4% <100 ns; max at 27% of run (mid-run scheduler jitter); no RT |
| `ring put+get, amortized 1-core (RT)` | realtime=on, clock_ns_per_tick=100.0 | ,  | 528,167,200 ops/s (1.9 ns/op) | ,  | ,  | ok · pure ring op cost; clock QueryPerformanceCounter res 100.0 ns |
| `cross-thread one-way latency (RT)` | realtime=on, ipc=CreateProcess+CreateFileMapping, warmup_msgs=20000 | ,  | 100.0 ns | 100.0 ns | 400.0 ns | ok · 1.3% <100 ns; max at 69% of run (mid-run scheduler jitter); RT hardened |
| `cross-process one-way latency (RT)` | realtime=on, ipc=CreateProcess+CreateFileMapping, warmup_msgs=20000 | ,  | 100.0 ns | 100.0 ns | 1.80 µs | ok · 0.3% <100 ns; max at 93% of run (mid-run scheduler jitter); RT hardened |

## Key encapsulation & key exchange (ML-KEM vs classical)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `X25519` | op=keygen | classical | 10,131 ops/s | 96.25 µs | 122.31 µs | ok |
| `X25519` | op=derive | classical | 6,263 ops/s | 157.58 µs | 179.99 µs | ok |
| `ECDH-P256` | op=keygen | classical | 59,723 ops/s | 16.33 µs | 20.71 µs | ok |
| `ECDH-P256` | op=derive | classical | 21,684 ops/s | 44.46 µs | 60.64 µs | ok |
| `ML-KEM-512` | op=keygen | PQC | 72,610 ops/s | 12.92 µs | 17.17 µs | ok |
| `ML-KEM-512` | op=encapsulate | PQC | 70,075 ops/s | 13.71 µs | 19.84 µs | ok |
| `ML-KEM-512` | op=decapsulate | PQC | 84,224 ops/s | 11.17 µs | 13.21 µs | ok |
| `ML-KEM-768` | op=keygen | PQC | 48,845 ops/s | 19.50 µs | 28.21 µs | ok |
| `ML-KEM-768` | op=encapsulate | PQC | 47,541 ops/s | 20.04 µs | 27.42 µs | ok |
| `ML-KEM-768` | op=decapsulate | PQC | 52,976 ops/s | 17.50 µs | 25.00 µs | ok |
| `ML-KEM-1024` | op=keygen | PQC | 39,374 ops/s | 24.62 µs | 32.04 µs | ok |
| `ML-KEM-1024` | op=encapsulate | PQC | 37,967 ops/s | 25.67 µs | 31.54 µs | ok |
| `ML-KEM-1024` | op=decapsulate | PQC | 39,253 ops/s | 24.88 µs | 31.13 µs | ok |

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
| `X25519` | op=keygen | classical | 24,238 ops/s | 40.36 µs | 50.80 µs | ok |
| `X25519` | op=derive | classical | 25,201 ops/s | 38.90 µs | 48.37 µs | ok |
| `ECDH-P256` | op=keygen | classical | 62,726 ops/s | 15.44 µs | 23.55 µs | ok |
| `ECDH-P256` | op=derive | classical | 16,405 ops/s | 59.93 µs | 69.71 µs | ok |
| `ML-KEM-512` | op=keygen | PQC | 50,605 ops/s | 19.20 µs | 27.77 µs | ok |
| `ML-KEM-512` | op=encapsulate | PQC | 48,477 ops/s | 20.10 µs | 28.72 µs | ok |
| `ML-KEM-512` | op=decapsulate | PQC | 69,502 ops/s | 13.94 µs | 22.04 µs | ok |
| `ML-KEM-768` | op=keygen | PQC | 39,032 ops/s | 24.98 µs | 34.20 µs | ok |
| `ML-KEM-768` | op=encapsulate | PQC | 38,057 ops/s | 25.63 µs | 35.16 µs | ok |
| `ML-KEM-768` | op=decapsulate | PQC | 47,928 ops/s | 20.31 µs | 28.97 µs | ok |
| `ML-KEM-1024` | op=keygen | PQC | 31,868 ops/s | 30.63 µs | 39.90 µs | ok |
| `ML-KEM-1024` | op=encapsulate | PQC | 31,174 ops/s | 31.37 µs | 40.92 µs | ok |
| `ML-KEM-1024` | op=decapsulate | PQC | 35,543 ops/s | 27.51 µs | 36.09 µs | ok |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `X25519` | op=keygen | classical | 24,041 ops/s | 40.40 µs | 71.50 µs | ok |
| `X25519` | op=derive | classical | 24,779 ops/s | 39.30 µs | 64.88 µs | ok |
| `ECDH-P256` | op=keygen | classical | 51,443 ops/s | 18.50 µs | 37.30 µs | ok |
| `ECDH-P256` | op=derive | classical | 17,595 ops/s | 55.30 µs | 75.40 µs | ok |
| `ML-KEM-512` | op=keygen | PQC | 5,163 ops/s | 187.00 µs | 235.04 µs | ok |
| `ML-KEM-512` | op=encapsulate | PQC | 4,039 ops/s | 235.80 µs | 388.28 µs | ok |
| `ML-KEM-512` | op=decapsulate | PQC | 3,366 ops/s | 289.60 µs | 351.16 µs | ok |
| `ML-KEM-768` | op=keygen | PQC | 3,263 ops/s | 297.70 µs | 352.57 µs | ok |
| `ML-KEM-768` | op=encapsulate | PQC | 2,795 ops/s | 348.25 µs | 404.08 µs | ok |
| `ML-KEM-768` | op=decapsulate | PQC | 2,339 ops/s | 418.20 µs | 472.70 µs | ok |
| `ML-KEM-1024` | op=keygen | PQC | 2,289 ops/s | 427.60 µs | 487.74 µs | ok |
| `ML-KEM-1024` | op=encapsulate | PQC | 2,014 ops/s | 487.50 µs | 542.40 µs | ok |
| `ML-KEM-1024` | op=decapsulate | PQC | 1,714 ops/s | 572.10 µs | 660.10 µs | ok |

## Hybrid PQC key agreement (ECDH ‖ ML-KEM → HKDF-SHA384)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ECDH-P256+ML-KEM-768` | op=full_two_party_handshake | HYBRID | 4,382 handshakes/s | 222.94 µs | 262.15 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |
| `ECDH-P256+ML-KEM-1024` | op=full_two_party_handshake | HYBRID | 4,019 handshakes/s | 244.62 µs | 294.68 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ECDH-P256+ML-KEM-768` | op=full_two_party_handshake | HYBRID | 7,811 handshakes/s | 125.96 µs | 150.96 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |
| `ECDH-P256+ML-KEM-1024` | op=full_two_party_handshake | HYBRID | 7,040 handshakes/s | 140.88 µs | 161.17 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ECDH-P256+ML-KEM-768` | op=full_two_party_handshake | HYBRID | 3,498 handshakes/s | 281.57 µs | 308.71 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |
| `ECDH-P256+ML-KEM-1024` | op=full_two_party_handshake | HYBRID | 3,269 handshakes/s | 301.08 µs | 362.21 µs | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `ECDH-P256+ML-KEM-768` | op=full_two_party_handshake | HYBRID | 735.8 handshakes/s | 1.36 ms | 1.54 ms | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |
| `ECDH-P256+ML-KEM-1024` | op=full_two_party_handshake | HYBRID | 559.4 handshakes/s | 1.78 ms | 1.88 ms | ok · ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties |

## Full authenticated handshake crypto (isolated from DDS transport)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `NIST-1 (ML-KEM-512 + ML-DSA-44)` | op=full_authenticated_handshake | PQC | 1,846 handshakes/s | 525.54 µs | 771.08 µs | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `NIST-3 (ML-KEM-768 + ML-DSA-65)` | op=full_authenticated_handshake | PQC | 1,340 handshakes/s | 725.65 µs | 1.07 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `CNSA 2.0 / NIST-5 (ML-KEM-1024 + ML-DSA-87)` | op=full_authenticated_handshake | PQC | 989.5 handshakes/s | 995.96 µs | 1.29 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `key agreement only — hybrid ECDH+ML-KEM rekey (no identity sig)` | note=see hybrid_kem | HYBRID | ,  | ,  | ,  | ok · the recurring/rekey cost is the hybrid_kem group: ~128 µs (ECDH+ML-KEM+HKDF, no signatures) |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `NIST-1 (ML-KEM-512 + ML-DSA-44)` | op=full_authenticated_handshake | PQC | 1,609 handshakes/s | 599.04 µs | 1.15 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `NIST-3 (ML-KEM-768 + ML-DSA-65)` | op=full_authenticated_handshake | PQC | 1,076 handshakes/s | 889.21 µs | 1.69 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `CNSA 2.0 / NIST-5 (ML-KEM-1024 + ML-DSA-87)` | op=full_authenticated_handshake | PQC | 836.8 handshakes/s | 1.15 ms | 1.96 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `key agreement only, hybrid ECDH+ML-KEM rekey (no identity sig)` | note=see hybrid_kem | HYBRID | ,  | ,  | ,  | ok · the recurring/rekey cost is the hybrid_kem group: ~128 µs (ECDH+ML-KEM+HKDF, no signatures) |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `NIST-1 (ML-KEM-512 + ML-DSA-44)` | op=full_authenticated_handshake | PQC | 1,444 handshakes/s | 674.66 µs | 957.33 µs | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `NIST-3 (ML-KEM-768 + ML-DSA-65)` | op=full_authenticated_handshake | PQC | 1,084 handshakes/s | 902.71 µs | 1.31 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `CNSA 2.0 / NIST-5 (ML-KEM-1024 + ML-DSA-87)` | op=full_authenticated_handshake | PQC | 890.0 handshakes/s | 1.11 ms | 1.49 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `key agreement only — hybrid ECDH+ML-KEM rekey (no identity sig)` | note=see hybrid_kem | HYBRID | ,  | ,  | ,  | ok · the recurring/rekey cost is the hybrid_kem group: ~128 µs (ECDH+ML-KEM+HKDF, no signatures) |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `NIST-1 (ML-KEM-512 + ML-DSA-44)` | op=full_authenticated_handshake | PQC | 137.2 handshakes/s | 7.01 ms | 10.03 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `NIST-3 (ML-KEM-768 + ML-DSA-65)` | op=full_authenticated_handshake | PQC | 88.3 handshakes/s | 9.98 ms | 18.48 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `CNSA 2.0 / NIST-5 (ML-KEM-1024 + ML-DSA-87)` | op=full_authenticated_handshake | PQC | 62.4 handshakes/s | 15.23 ms | 21.60 ms | ok · 3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities provisioned out-of-band (not timed); isolated from DDS transport |
| `key agreement only, hybrid ECDH+ML-KEM rekey (no identity sig)` | note=see hybrid_kem | HYBRID | ,  | ,  | ,  | ok · the recurring/rekey cost is the hybrid_kem group: ~128 µs (ECDH+ML-KEM+HKDF, no signatures) |

## Digital signatures (ML-DSA vs classical)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `Ed25519` | op=keygen | classical | 10,881 ops/s | 90.29 µs | 101.81 µs | ok |
| `Ed25519` | op=sign | classical | 10,785 ops/s | 91.96 µs | 103.59 µs | ok |
| `Ed25519` | op=verify | classical | 4,940 ops/s | 198.29 µs | 227.24 µs | ok |
| `ECDSA-P256` | op=sign | classical | 37,869 ops/s | 25.67 µs | 32.21 µs | ok |
| `ECDSA-P256` | op=verify | classical | 15,842 ops/s | 61.46 µs | 77.37 µs | ok |
| `RSA-3072-PSS` | op=sign | classical | 284.0 ops/s | 3.42 ms | 5.51 ms | ok |
| `RSA-3072-PSS` | op=verify | classical | 17,532 ops/s | 55.71 µs | 66.31 µs | ok |
| `ML-DSA-44` | op=keygen | PQC | 28,439 ops/s | 34.46 µs | 41.54 µs | ok |
| `ML-DSA-44` | op=sign | PQC | 13,478 ops/s | 60.19 µs | 212.11 µs | ok |
| `ML-DSA-44` | op=verify | PQC | 28,649 ops/s | 33.88 µs | 43.96 µs | ok |
| `ML-DSA-65` | op=keygen | PQC | 17,328 ops/s | 56.33 µs | 67.13 µs | ok |
| `ML-DSA-65` | op=sign | PQC | 8,804 ops/s | 95.46 µs | 318.42 µs | ok |
| `ML-DSA-65` | op=verify | PQC | 18,527 ops/s | 53.42 µs | 62.34 µs | ok |
| `ML-DSA-87` | op=keygen | PQC | 9,805 ops/s | 100.00 µs | 135.11 µs | ok |
| `ML-DSA-87` | op=sign | PQC | 5,975 ops/s | 146.58 µs | 391.28 µs | ok |
| `ML-DSA-87` | op=verify | PQC | 10,387 ops/s | 94.12 µs | 130.61 µs | ok |

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
| `Ed25519` | op=keygen | classical | 24,182 ops/s | 40.48 µs | 50.77 µs | ok |
| `Ed25519` | op=sign | classical | 22,929 ops/s | 42.77 µs | 52.27 µs | ok |
| `Ed25519` | op=verify | classical | 7,421 ops/s | 132.95 µs | 144.87 µs | ok |
| `ECDSA-P256` | op=sign | classical | 33,767 ops/s | 28.92 µs | 38.14 µs | ok |
| `ECDSA-P256` | op=verify | classical | 12,310 ops/s | 79.89 µs | 91.49 µs | ok |
| `RSA-3072-PSS` | op=sign | classical | 438.1 ops/s | 2.26 ms | 2.92 ms | ok |
| `RSA-3072-PSS` | op=verify | classical | 18,104 ops/s | 54.26 µs | 63.89 µs | ok |
| `ML-DSA-44` | op=keygen | PQC | 24,536 ops/s | 39.94 µs | 50.32 µs | ok |
| `ML-DSA-44` | op=sign | PQC | 10,786 ops/s | 75.15 µs | 289.46 µs | ok |
| `ML-DSA-44` | op=verify | PQC | 24,032 ops/s | 40.78 µs | 50.32 µs | ok |
| `ML-DSA-65` | op=keygen | PQC | 16,226 ops/s | 60.59 µs | 71.47 µs | ok |
| `ML-DSA-65` | op=sign | PQC | 7,219 ops/s | 115.16 µs | 392.85 µs | ok |
| `ML-DSA-65` | op=verify | PQC | 16,406 ops/s | 59.87 µs | 71.34 µs | ok |
| `ML-DSA-87` | op=keygen | PQC | 10,997 ops/s | 89.61 µs | 101.78 µs | ok |
| `ML-DSA-87` | op=sign | PQC | 5,970 ops/s | 145.59 µs | 422.36 µs | ok |
| `ML-DSA-87` | op=verify | PQC | 11,238 ops/s | 87.51 µs | 100.13 µs | ok |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `Ed25519` | op=keygen | classical | 23,752 ops/s | 40.90 µs | 57.80 µs | ok |
| `Ed25519` | op=sign | classical | 22,502 ops/s | 43.10 µs | 62.33 µs | ok |
| `Ed25519` | op=verify | classical | 8,251 ops/s | 118.40 µs | 149.09 µs | ok |
| `ECDSA-P256` | op=sign | classical | 30,791 ops/s | 30.90 µs | 53.10 µs | ok |
| `ECDSA-P256` | op=verify | classical | 12,919 ops/s | 75.20 µs | 109.13 µs | ok |
| `RSA-3072-PSS` | op=sign | classical | 482.5 ops/s | 2.04 ms | 2.87 ms | ok |
| `RSA-3072-PSS` | op=verify | classical | 18,071 ops/s | 53.50 µs | 87.19 µs | ok |
| `ML-DSA-44` | op=keygen | PQC | 2,240 ops/s | 436.85 µs | 513.94 µs | ok |
| `ML-DSA-44` | op=sign | PQC | 686.4 ops/s | 1.17 ms | 4.11 ms | ok |
| `ML-DSA-44` | op=verify | PQC | 1,952 ops/s | 501.40 µs | 579.73 µs | ok |
| `ML-DSA-65` | op=keygen | PQC | 1,270 ops/s | 773.80 µs | 848.47 µs | ok |
| `ML-DSA-65` | op=sign | PQC | 384.5 ops/s | 2.11 ms | 7.41 ms | ok |
| `ML-DSA-65` | op=verify | PQC | 1,211 ops/s | 809.75 µs | 988.07 µs | ok |
| `ML-DSA-87` | op=keygen | PQC | 780.8 ops/s | 1.28 ms | 1.34 ms | ok |
| `ML-DSA-87` | op=sign | PQC | 331.2 ops/s | 2.52 ms | 7.26 ms | ok |
| `ML-DSA-87` | op=verify | PQC | 738.2 ops/s | 1.36 ms | 1.41 ms | ok |

## Authenticated encryption (AES-GCM / ChaCha20-Poly1305)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `AES-256-GCM` | op=encrypt, input_bytes=64 | QR | 83 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=decrypt, input_bytes=64 | QR | 84 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=encrypt, input_bytes=1024 | QR | 1,065 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=decrypt, input_bytes=1024 | QR | 1,069 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=encrypt, input_bytes=65536 | QR | 6,219 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=decrypt, input_bytes=65536 | QR | 6,195 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-128-GCM` | op=encrypt, input_bytes=64 | QR | 86 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=decrypt, input_bytes=64 | QR | 85 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=encrypt, input_bytes=1024 | QR | 1,112 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=decrypt, input_bytes=1024 | QR | 1,095 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=encrypt, input_bytes=65536 | QR | 7,177 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=decrypt, input_bytes=65536 | QR | 7,256 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=64 | QR | 66 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=64 | QR | 64 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=1024 | QR | 675 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=1024 | QR | 668 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=65536 | QR | 1,732 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=65536 | QR | 1,706 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `AES-256-GCM` | op=encrypt, input_bytes=64 | QR | 197 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=decrypt, input_bytes=64 | QR | 195 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=encrypt, input_bytes=1024 | QR | 2,261 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=decrypt, input_bytes=1024 | QR | 2,247 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=encrypt, input_bytes=16384 | QR | 6,949 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=decrypt, input_bytes=16384 | QR | 6,899 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=encrypt, input_bytes=262144 | QR | 8,158 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=decrypt, input_bytes=262144 | QR | 8,096 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=encrypt, input_bytes=1048576 | QR | 8,168 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=decrypt, input_bytes=1048576 | QR | 8,009 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-128-GCM` | op=encrypt, input_bytes=64 | QR | 195 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=decrypt, input_bytes=64 | QR | 185 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=encrypt, input_bytes=1024 | QR | 2,238 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=decrypt, input_bytes=1024 | QR | 2,217 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=encrypt, input_bytes=16384 | QR | 6,688 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=decrypt, input_bytes=16384 | QR | 5,649 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=encrypt, input_bytes=262144 | QR | 8,254 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=decrypt, input_bytes=262144 | QR | 8,218 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=encrypt, input_bytes=1048576 | QR | 8,189 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=decrypt, input_bytes=1048576 | QR | 8,176 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
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
| `AES-256-GCM` | op=encrypt, input_bytes=64 | QR | 72 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=decrypt, input_bytes=64 | QR | 70 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=encrypt, input_bytes=1024 | QR | 793 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=decrypt, input_bytes=1024 | QR | 800 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=encrypt, input_bytes=65536 | QR | 3,230 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=decrypt, input_bytes=65536 | QR | 3,238 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-128-GCM` | op=encrypt, input_bytes=64 | QR | 72 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=decrypt, input_bytes=64 | QR | 71 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=encrypt, input_bytes=1024 | QR | 815 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=decrypt, input_bytes=1024 | QR | 821 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=encrypt, input_bytes=65536 | QR | 3,441 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=decrypt, input_bytes=65536 | QR | 3,438 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=64 | QR | 58 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=64 | QR | 58 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=1024 | QR | 606 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=1024 | QR | 603 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=65536 | QR | 1,731 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=65536 | QR | 1,715 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `AES-256-GCM` | op=encrypt, input_bytes=64 | QR | 53 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=decrypt, input_bytes=64 | QR | 52 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=encrypt, input_bytes=1024 | QR | 664 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=decrypt, input_bytes=1024 | QR | 660 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=encrypt, input_bytes=65536 | QR | 3,465 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-256-GCM` | op=decrypt, input_bytes=65536 | QR | 3,476 MB/s | ok · AES-256 → NIST Level 5, CNSA 2.0 (Grover leaves 128-bit) |
| `AES-128-GCM` | op=encrypt, input_bytes=64 | QR | 53 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=decrypt, input_bytes=64 | QR | 51 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=encrypt, input_bytes=1024 | QR | 674 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=decrypt, input_bytes=1024 | QR | 668 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=encrypt, input_bytes=65536 | QR | 3,694 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `AES-128-GCM` | op=decrypt, input_bytes=65536 | QR | 3,710 MB/s | ok · AES-128 → NIST Level 1, the QR floor (128-bit; Grover→64-bit); below CNSA 2.0 |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=64 | QR | 46 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=64 | QR | 46 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=1024 | QR | 551 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=1024 | QR | 550 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=encrypt, input_bytes=65536 | QR | 2,015 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `ChaCha20-Poly1305` | op=decrypt, input_bytes=65536 | QR | 1,983 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

## Hashing (SHA-2 / SHA-3 / BLAKE2)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `sha256` | input_bytes=64 | QR | 131 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha256` | input_bytes=1024 | QR | 1,179 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha256` | input_bytes=65536 | QR | 2,404 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha384` | input_bytes=64 | QR | 124 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `sha384` | input_bytes=1024 | QR | 813 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `sha384` | input_bytes=65536 | QR | 1,403 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `sha512` | input_bytes=64 | QR | 126 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade |
| `sha512` | input_bytes=1024 | QR | 835 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade |
| `sha512` | input_bytes=65536 | QR | 1,402 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade |
| `sha3_256` | input_bytes=64 | QR | 85 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha3_256` | input_bytes=1024 | QR | 466 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha3_256` | input_bytes=65536 | QR | 647 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha3_512` | input_bytes=64 | QR | 82 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade |
| `sha3_512` | input_bytes=1024 | QR | 254 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade |
| `sha3_512` | input_bytes=65536 | QR | 321 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade |
| `blake2b` | input_bytes=64 | QR | 139 MB/s | ok |
| `blake2b` | input_bytes=1024 | QR | 763 MB/s | ok |
| `blake2b` | input_bytes=65536 | QR | 994 MB/s | ok |
| `blake2s` | input_bytes=64 | QR | 164 MB/s | ok |
| `blake2s` | input_bytes=1024 | QR | 517 MB/s | ok |
| `blake2s` | input_bytes=65536 | QR | 609 MB/s | ok |
| `blake3` | input_bytes=64 | QR | 126 MB/s | ok · BLAKE3, Merkle-tree hash, parallel + SIMD, XOF; 256-bit (NIST Level-1 QR floor) |
| `blake3` | input_bytes=1024 | QR | 590 MB/s | ok · BLAKE3, Merkle-tree hash, parallel + SIMD, XOF; 256-bit (NIST Level-1 QR floor) |
| `blake3` | input_bytes=65536 | QR | 1,651 MB/s | ok · BLAKE3, Merkle-tree hash, parallel + SIMD, XOF; 256-bit (NIST Level-1 QR floor) |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `sha256` | input_bytes=64 | QR | 156 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha256` | input_bytes=1024 | QR | 464 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha256` | input_bytes=16384 | QR | 1,642 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha256` | input_bytes=262144 | QR | 2,882 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha256` | input_bytes=1048576 | QR | 2,834 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha384` | input_bytes=64 | QR | 130 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `sha384` | input_bytes=1024 | QR | 823 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `sha384` | input_bytes=16384 | QR | 1,640 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `sha384` | input_bytes=262144 | QR | 1,533 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `sha384` | input_bytes=1048576 | QR | 1,550 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `sha512` | input_bytes=64 | QR | 113 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade |
| `sha512` | input_bytes=1024 | QR | 978 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade |
| `sha512` | input_bytes=16384 | QR | 1,628 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade |
| `sha512` | input_bytes=262144 | QR | 1,658 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade |
| `sha512` | input_bytes=1048576 | QR | 1,677 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade |
| `sha3_256` | input_bytes=64 | QR | 111 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha3_256` | input_bytes=1024 | QR | 632 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha3_256` | input_bytes=16384 | QR | 853 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha3_256` | input_bytes=262144 | QR | 922 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha3_256` | input_bytes=1048576 | QR | 823 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha3_512` | input_bytes=64 | QR | 112 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade |
| `sha3_512` | input_bytes=1024 | QR | 396 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade |
| `sha3_512` | input_bytes=16384 | QR | 443 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade |
| `sha3_512` | input_bytes=262144 | QR | 504 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade |
| `sha3_512` | input_bytes=1048576 | QR | 514 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade |
| `blake2b` | input_bytes=64 | QR | 162 MB/s | ok |
| `blake2b` | input_bytes=1024 | QR | 905 MB/s | ok |
| `blake2b` | input_bytes=16384 | QR | 1,184 MB/s | ok |
| `blake2b` | input_bytes=262144 | QR | 1,159 MB/s | ok |
| `blake2b` | input_bytes=1048576 | QR | 1,272 MB/s | ok |
| `blake2s` | input_bytes=64 | QR | 164 MB/s | ok |
| `blake2s` | input_bytes=1024 | QR | 604 MB/s | ok |
| `blake2s` | input_bytes=16384 | QR | 774 MB/s | ok |
| `blake2s` | input_bytes=262144 | QR | 733 MB/s | ok |
| `blake2s` | input_bytes=1048576 | QR | 739 MB/s | ok |
| `blake3` | input_bytes=64 | QR | 157 MB/s | ok · BLAKE3, Merkle-tree hash, parallel + SIMD, XOF; 256-bit (NIST Level-1 QR floor) |
| `blake3` | input_bytes=1024 | QR | 878 MB/s | ok · BLAKE3, Merkle-tree hash, parallel + SIMD, XOF; 256-bit (NIST Level-1 QR floor) |
| `blake3` | input_bytes=16384 | QR | 2,165 MB/s | ok · BLAKE3, Merkle-tree hash, parallel + SIMD, XOF; 256-bit (NIST Level-1 QR floor) |
| `blake3` | input_bytes=262144 | QR | 2,308 MB/s | ok · BLAKE3, Merkle-tree hash, parallel + SIMD, XOF; 256-bit (NIST Level-1 QR floor) |
| `blake3` | input_bytes=1048576 | QR | 2,363 MB/s | ok · BLAKE3, Merkle-tree hash, parallel + SIMD, XOF; 256-bit (NIST Level-1 QR floor) |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `sha256` | input_bytes=64 | QR | 72 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha256` | input_bytes=1024 | QR | 650 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha256` | input_bytes=65536 | QR | 1,376 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha384` | input_bytes=64 | QR | 57 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `sha384` | input_bytes=1024 | QR | 385 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `sha384` | input_bytes=65536 | QR | 665 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `sha512` | input_bytes=64 | QR | 57 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade |
| `sha512` | input_bytes=1024 | QR | 387 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade |
| `sha512` | input_bytes=65536 | QR | 666 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade |
| `sha3_256` | input_bytes=64 | QR | 49 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha3_256` | input_bytes=1024 | QR | 278 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha3_256` | input_bytes=65536 | QR | 390 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha3_512` | input_bytes=64 | QR | 50 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade |
| `sha3_512` | input_bytes=1024 | QR | 170 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade |
| `sha3_512` | input_bytes=65536 | QR | 212 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade |
| `blake2b` | input_bytes=64 | QR | 85 MB/s | ok |
| `blake2b` | input_bytes=1024 | QR | 500 MB/s | ok |
| `blake2b` | input_bytes=65536 | QR | 676 MB/s | ok |
| `blake2s` | input_bytes=64 | QR | 95 MB/s | ok |
| `blake2s` | input_bytes=1024 | QR | 332 MB/s | ok |
| `blake2s` | input_bytes=65536 | QR | 403 MB/s | ok |
| `blake3` | input_bytes=64 | QR | 91 MB/s | ok · BLAKE3, Merkle-tree hash, parallel + SIMD, XOF; 256-bit (NIST Level-1 QR floor) |
| `blake3` | input_bytes=1024 | QR | 511 MB/s | ok · BLAKE3, Merkle-tree hash, parallel + SIMD, XOF; 256-bit (NIST Level-1 QR floor) |
| `blake3` | input_bytes=65536 | QR | 3,318 MB/s | ok · BLAKE3, Merkle-tree hash, parallel + SIMD, XOF; 256-bit (NIST Level-1 QR floor) |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `sha256` | input_bytes=64 | QR | 56 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha256` | input_bytes=1024 | QR | 592 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha256` | input_bytes=65536 | QR | 1,540 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha384` | input_bytes=64 | QR | 49 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `sha384` | input_bytes=1024 | QR | 379 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `sha384` | input_bytes=65536 | QR | 741 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `sha512` | input_bytes=64 | QR | 49 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade |
| `sha512` | input_bytes=1024 | QR | 382 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade |
| `sha512` | input_bytes=65536 | QR | 740 MB/s | ok · Merkle-Damgard, length-extendable (key via HMAC) · 512-bit, CNSA 2.0-grade |
| `sha3_256` | input_bytes=64 | QR | 44 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha3_256` | input_bytes=1024 | QR | 284 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha3_256` | input_bytes=65536 | QR | 421 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · SHA-256 → NIST Level 2 collision; below CNSA 2.0's SHA-384 |
| `sha3_512` | input_bytes=64 | QR | 44 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade |
| `sha3_512` | input_bytes=1024 | QR | 179 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade |
| `sha3_512` | input_bytes=65536 | QR | 235 MB/s | ok · Keccak sponge, length-extension-immune, design-diverse from SHA-2 · 512-bit, CNSA 2.0-grade |
| `blake2b` | input_bytes=64 | QR | 70 MB/s | ok |
| `blake2b` | input_bytes=1024 | QR | 418 MB/s | ok |
| `blake2b` | input_bytes=65536 | QR | 586 MB/s | ok |
| `blake2s` | input_bytes=64 | QR | 78 MB/s | ok |
| `blake2s` | input_bytes=1024 | QR | 288 MB/s | ok |
| `blake2s` | input_bytes=65536 | QR | 355 MB/s | ok |
| `blake3` | input_bytes=64 | QR | 82 MB/s | ok · BLAKE3, Merkle-tree hash, parallel + SIMD, XOF; 256-bit (NIST Level-1 QR floor) |
| `blake3` | input_bytes=1024 | QR | 548 MB/s | ok · BLAKE3, Merkle-tree hash, parallel + SIMD, XOF; 256-bit (NIST Level-1 QR floor) |
| `blake3` | input_bytes=65536 | QR | 3,844 MB/s | ok · BLAKE3, Merkle-tree hash, parallel + SIMD, XOF; 256-bit (NIST Level-1 QR floor) |

## Message authentication (HMAC / Poly1305)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `HMAC-SHA256` | input_bytes=64 | QR | 46 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HMAC-SHA256` | input_bytes=1024 | QR | 587 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HMAC-SHA256` | input_bytes=65536 | QR | 2,328 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HMAC-SHA384` | input_bytes=64 | QR | 43 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `HMAC-SHA384` | input_bytes=1024 | QR | 468 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `HMAC-SHA384` | input_bytes=65536 | QR | 1,369 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `HMAC-SHA512` | input_bytes=64 | QR | 44 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 512-bit, CNSA 2.0-grade |
| `HMAC-SHA512` | input_bytes=1024 | QR | 474 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 512-bit, CNSA 2.0-grade |
| `HMAC-SHA512` | input_bytes=65536 | QR | 1,376 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 512-bit, CNSA 2.0-grade |
| `Poly1305` | input_bytes=64 | QR | 14 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=1024 | QR | 220 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=65536 | QR | 4,482 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `HMAC-SHA256` | input_bytes=64 | QR | 77 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HMAC-SHA256` | input_bytes=1024 | QR | 888 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HMAC-SHA256` | input_bytes=16384 | QR | 2,723 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HMAC-SHA256` | input_bytes=262144 | QR | 2,902 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HMAC-SHA256` | input_bytes=1048576 | QR | 3,134 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HMAC-SHA384` | input_bytes=64 | QR | 64 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `HMAC-SHA384` | input_bytes=1024 | QR | 644 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `HMAC-SHA384` | input_bytes=16384 | QR | 1,598 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `HMAC-SHA384` | input_bytes=262144 | QR | 1,849 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `HMAC-SHA384` | input_bytes=1048576 | QR | 1,839 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `HMAC-SHA512` | input_bytes=64 | QR | 65 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 512-bit, CNSA 2.0-grade |
| `HMAC-SHA512` | input_bytes=1024 | QR | 696 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 512-bit, CNSA 2.0-grade |
| `HMAC-SHA512` | input_bytes=16384 | QR | 1,632 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 512-bit, CNSA 2.0-grade |
| `HMAC-SHA512` | input_bytes=262144 | QR | 1,842 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 512-bit, CNSA 2.0-grade |
| `HMAC-SHA512` | input_bytes=1048576 | QR | 1,866 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 512-bit, CNSA 2.0-grade |
| `Poly1305` | input_bytes=64 | QR | 42 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=1024 | QR | 599 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=16384 | QR | 4,966 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=262144 | QR | 8,236 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=1048576 | QR | 8,534 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `HMAC-SHA256` | input_bytes=64 | QR | 32 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HMAC-SHA256` | input_bytes=1024 | QR | 380 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HMAC-SHA256` | input_bytes=65536 | QR | 1,340 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HMAC-SHA384` | input_bytes=64 | QR | 22 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `HMAC-SHA384` | input_bytes=1024 | QR | 235 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `HMAC-SHA384` | input_bytes=65536 | QR | 654 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `HMAC-SHA512` | input_bytes=64 | QR | 22 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 512-bit, CNSA 2.0-grade |
| `HMAC-SHA512` | input_bytes=1024 | QR | 233 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 512-bit, CNSA 2.0-grade |
| `HMAC-SHA512` | input_bytes=65536 | QR | 654 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 512-bit, CNSA 2.0-grade |
| `Poly1305` | input_bytes=64 | QR | 20 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=1024 | QR | 292 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=65536 | QR | 4,462 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `HMAC-SHA256` | input_bytes=64 | QR | 23 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HMAC-SHA256` | input_bytes=1024 | QR | 299 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HMAC-SHA256` | input_bytes=65536 | QR | 1,433 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HMAC-SHA384` | input_bytes=64 | QR | 18 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `HMAC-SHA384` | input_bytes=1024 | QR | 206 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `HMAC-SHA384` | input_bytes=65536 | QR | 707 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `HMAC-SHA512` | input_bytes=64 | QR | 18 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 512-bit, CNSA 2.0-grade |
| `HMAC-SHA512` | input_bytes=1024 | QR | 207 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 512-bit, CNSA 2.0-grade |
| `HMAC-SHA512` | input_bytes=65536 | QR | 708 MB/s | ok · nested MAC, keys a Merkle-Damgard hash safely · 512-bit, CNSA 2.0-grade |
| `Poly1305` | input_bytes=64 | QR | 12 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=1024 | QR | 180 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |
| `Poly1305` | input_bytes=65536 | QR | 4,198 MB/s | ok · one-time Wegman-Carter MAC (with ChaCha20) |

## Key derivation (HKDF / PBKDF2 / Argon2id)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `PBKDF2-HMAC-SHA256` | iterations=10000 | QR | 505.3 ops/s | 1.96 ms | 2.11 ms | ok · nested MAC, keys a Merkle-Damgard hash safely · iteration-only passphrase KDF, NO memory-hardness (weakest) · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `PBKDF2-HMAC-SHA256` | iterations=100000 | QR | 50.2 ops/s | 19.83 ms | 20.79 ms | ok · nested MAC, keys a Merkle-Damgard hash safely · iteration-only passphrase KDF, NO memory-hardness (weakest) · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `PBKDF2-HMAC-SHA256` | iterations=600000 | QR | 8.40 ops/s | 119.02 ms | 120.19 ms | ok · nested MAC, keys a Merkle-Damgard hash safely · iteration-only passphrase KDF, NO memory-hardness (weakest) · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HKDF-SHA256` | ikm_bytes=64, out_bytes=32 | QR | 211,897 ops/s | 4.71 µs | 5.25 µs | ok · extract-then-expand KDF, HIGH-entropy inputs (RFC 5869) · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HKDF-SHA384` | ikm_bytes=64, out_bytes=32 | QR | 194,209 ops/s | 4.88 µs | 5.92 µs | ok · extract-then-expand KDF, HIGH-entropy inputs (RFC 5869) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `Argon2id` | profile=interactive, time_cost=2, memory_cost=65536, parallelism=1 | QR | 12.4 ops/s | 78.61 ms | 84.23 ms | ok · memory-hard passphrase KDF, LOW-entropy inputs, GPU/ASIC-resistant |
| `Argon2id` | profile=moderate, time_cost=3, memory_cost=262144, parallelism=4 | QR | 4.53 ops/s | 209.11 ms | 244.58 ms | ok · memory-hard passphrase KDF, LOW-entropy inputs, GPU/ASIC-resistant |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `PBKDF2-HMAC-SHA256` | iterations=10000 | QR | 1,445 ops/s | 689.94 µs | 730.01 µs | ok · nested MAC, keys a Merkle-Damgard hash safely · iteration-only passphrase KDF, NO memory-hardness (weakest) · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `PBKDF2-HMAC-SHA256` | iterations=100000 | QR | 140.8 ops/s | 6.94 ms | 10.04 ms | ok · nested MAC, keys a Merkle-Damgard hash safely · iteration-only passphrase KDF, NO memory-hardness (weakest) · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `PBKDF2-HMAC-SHA256` | iterations=600000 | QR | 22.7 ops/s | 44.19 ms | 45.06 ms | ok · nested MAC, keys a Merkle-Damgard hash safely · iteration-only passphrase KDF, NO memory-hardness (weakest) · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HKDF-SHA256` | ikm_bytes=64, out_bytes=32 | QR | 580,396 ops/s | 1.67 µs | 1.83 µs | ok · extract-then-expand KDF, HIGH-entropy inputs (RFC 5869) · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HKDF-SHA384` | ikm_bytes=64, out_bytes=32 | QR | 477,434 ops/s | 1.96 µs | 2.50 µs | ok · extract-then-expand KDF, HIGH-entropy inputs (RFC 5869) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `Argon2id` | profile=interactive, time_cost=2, memory_cost=65536, parallelism=1 | QR | 15.6 ops/s | 63.20 ms | 77.21 ms | ok · memory-hard passphrase KDF, LOW-entropy inputs, GPU/ASIC-resistant |
| `Argon2id` | profile=moderate, time_cost=3, memory_cost=262144, parallelism=4 | QR | 9.47 ops/s | 105.24 ms | 108.44 ms | ok · memory-hard passphrase KDF, LOW-entropy inputs, GPU/ASIC-resistant |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `PBKDF2-HMAC-SHA256` | iterations=10000 | QR | 338.3 ops/s | 2.95 ms | 3.05 ms | ok · nested MAC, keys a Merkle-Damgard hash safely · iteration-only passphrase KDF, NO memory-hardness (weakest) · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `PBKDF2-HMAC-SHA256` | iterations=100000 | QR | 33.9 ops/s | 29.52 ms | 29.63 ms | ok · nested MAC, keys a Merkle-Damgard hash safely · iteration-only passphrase KDF, NO memory-hardness (weakest) · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `PBKDF2-HMAC-SHA256` | iterations=600000 | QR | 5.64 ops/s | 177.15 ms | 177.35 ms | ok · nested MAC, keys a Merkle-Damgard hash safely · iteration-only passphrase KDF, NO memory-hardness (weakest) · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HKDF-SHA256` | ikm_bytes=64, out_bytes=32 | QR | 228,134 ops/s | 4.06 µs | 4.45 µs | ok · extract-then-expand KDF, HIGH-entropy inputs (RFC 5869) · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HKDF-SHA384` | ikm_bytes=64, out_bytes=32 | QR | 172,468 ops/s | 5.46 µs | 5.95 µs | ok · extract-then-expand KDF, HIGH-entropy inputs (RFC 5869) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `Argon2id` | profile=interactive, time_cost=2, memory_cost=65536, parallelism=1 | QR | 13.1 ops/s | 76.16 ms | 77.10 ms | ok · memory-hard passphrase KDF, LOW-entropy inputs, GPU/ASIC-resistant |
| `Argon2id` | profile=moderate, time_cost=3, memory_cost=262144, parallelism=4 | QR | 5.48 ops/s | 181.82 ms | 184.52 ms | ok · memory-hard passphrase KDF, LOW-entropy inputs, GPU/ASIC-resistant |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `PBKDF2-HMAC-SHA256` | iterations=10000 | QR | 184.3 ops/s | 5.03 ms | 10.38 ms | ok · nested MAC, keys a Merkle-Damgard hash safely · iteration-only passphrase KDF, NO memory-hardness (weakest) · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `PBKDF2-HMAC-SHA256` | iterations=100000 | QR | 20.0 ops/s | 50.02 ms | 50.75 ms | ok · nested MAC, keys a Merkle-Damgard hash safely · iteration-only passphrase KDF, NO memory-hardness (weakest) · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `PBKDF2-HMAC-SHA256` | iterations=600000 | QR | 3.33 ops/s | 297.81 ms | 306.60 ms | ok · nested MAC, keys a Merkle-Damgard hash safely · iteration-only passphrase KDF, NO memory-hardness (weakest) · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HKDF-SHA256` | ikm_bytes=64, out_bytes=32 | QR | 167,605 ops/s | 5.50 µs | 11.60 µs | ok · extract-then-expand KDF, HIGH-entropy inputs (RFC 5869) · 128-bit quantum PRF security, quantum-safe (Grover-halved, not collision-bound) |
| `HKDF-SHA384` | ikm_bytes=64, out_bytes=32 | QR | 135,921 ops/s | 6.90 µs | 14.90 µs | ok · extract-then-expand KDF, HIGH-entropy inputs (RFC 5869) · SHA-384 → NIST Level 4 collision, CNSA 2.0 |
| `Argon2id` | profile=interactive, time_cost=2, memory_cost=65536, parallelism=1 | QR | 10.4 ops/s | 95.76 ms | 97.94 ms | ok · memory-hard passphrase KDF, LOW-entropy inputs, GPU/ASIC-resistant |
| `Argon2id` | profile=moderate, time_cost=3, memory_cost=262144, parallelism=4 | QR | 4.48 ops/s | 220.22 ms | 228.51 ms | ok · memory-hard passphrase KDF, LOW-entropy inputs, GPU/ASIC-resistant |

## DDS-Security live handshakes (Fast DDS + CycloneDDS)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `CycloneDDS` | ,  | ,  | ,  | _skipped_, CycloneDDS PQC test binary not built on this platform |
| `FastDDS` | ,  | ,  | ,  | _skipped_, Fast DDS PKI-DH test binary not built on this platform |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `CycloneDDS classical (RSA id · ECDH P-256)` | ,  | classical | 1.97 ms | 1.97 ms | 5.99 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS classical (RSA id · ECDH P-256), full process` | ,  | classical | 105.30 ms | 105.30 ms | 281.52 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-768` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-768 | HYBRID | 2.04 ms | 2.04 ms | 3.52 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-768, full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-768 | HYBRID | 101.79 ms | 101.79 ms | 134.79 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-1024` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | HYBRID | 1.99 ms | 1.99 ms | 2.18 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-1024, full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | HYBRID | 98.95 ms | 98.95 ms | 112.49 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS ML-DSA-87 identity (PQ auth)` | ,  | PQC | 2.30 ms | 2.30 ms | 4.40 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS ML-DSA-87 identity (PQ auth), full process` | ,  | PQC | 59.72 ms | 59.72 ms | 64.67 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS full CNSA 2.0 (ML-DSA-87 · ML-KEM-1024)` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | PQC | 2.55 ms | 2.55 ms | 7.62 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS full CNSA 2.0 (ML-DSA-87 · ML-KEM-1024), full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | PQC | 59.30 ms | 59.30 ms | 67.62 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `FastDDS PKI-DH local-identity validate, full process` | ,  | classical | 37.70 ms | 37.70 ms | 86.47 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |

**Darwin · PQC-DDS build, macOS Apple Silicon CI**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `CycloneDDS classical (RSA id · ECDH P-256)` | ,  | classical | 1.97 ms | 1.97 ms | 5.99 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS classical (RSA id · ECDH P-256), full process` | ,  | classical | 105.30 ms | 105.30 ms | 281.52 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-768` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-768 | HYBRID | 2.04 ms | 2.04 ms | 3.52 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-768, full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-768 | HYBRID | 101.79 ms | 101.79 ms | 134.79 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-1024` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | HYBRID | 1.99 ms | 1.99 ms | 2.18 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-1024, full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | HYBRID | 98.95 ms | 98.95 ms | 112.49 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS ML-DSA-87 identity (PQ auth)` | ,  | PQC | 2.30 ms | 2.30 ms | 4.40 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS ML-DSA-87 identity (PQ auth), full process` | ,  | PQC | 59.72 ms | 59.72 ms | 64.67 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS full CNSA 2.0 (ML-DSA-87 · ML-KEM-1024)` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | PQC | 2.55 ms | 2.55 ms | 7.62 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS full CNSA 2.0 (ML-DSA-87 · ML-KEM-1024), full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | PQC | 59.30 ms | 59.30 ms | 67.62 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `FastDDS PKI-DH local-identity validate, full process` | ,  | classical | 37.70 ms | 37.70 ms | 86.47 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |

**Linux · PQC-DDS build, debian trixie (x86_64 CI)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `CycloneDDS classical (RSA id · ECDH P-256)` | ,  | classical | 3.48 ms | 3.48 ms | 7.66 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS classical (RSA id · ECDH P-256), full process` | ,  | classical | 103.16 ms | 103.16 ms | 175.15 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-768` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-768 | HYBRID | 3.72 ms | 3.72 ms | 3.94 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-768, full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-768 | HYBRID | 102.89 ms | 102.89 ms | 104.20 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-1024` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | HYBRID | 3.67 ms | 3.67 ms | 4.32 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS hybrid ECDH+ML-KEM-1024, full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | HYBRID | 102.60 ms | 102.60 ms | 104.33 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS ML-DSA-87 identity (PQ auth)` | ,  | PQC | 6.57 ms | 6.57 ms | 8.10 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS ML-DSA-87 identity (PQ auth), full process` | ,  | PQC | 32.26 ms | 32.26 ms | 34.05 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `CycloneDDS full CNSA 2.0 (ML-DSA-87 · ML-KEM-1024)` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | PQC | 6.76 ms | 6.76 ms | 9.38 ms | ok · ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown |
| `CycloneDDS full CNSA 2.0 (ML-DSA-87 · ML-KEM-1024), full process` | CYCLONEDDS_PQC_KAGREE=ECDH+ML-KEM-1024 | PQC | 32.31 ms | 32.31 ms | 35.91 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |
| `FastDDS PKI-DH local-identity validate, full process` | ,  | classical | 6.77 ms | 6.77 ms | 7.32 ms | ok · whole test process: startup + participant create + SPDP discovery + handshake + teardown |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `CycloneDDS` | ,  | ,  | ,  | _skipped_, CycloneDDS PQC test binary not built on this platform |
| `FastDDS` | ,  | ,  | ,  | _skipped_, Fast DDS PKI-DH test binary not built on this platform |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `CycloneDDS` | ,  | ,  | ,  | _skipped_, CycloneDDS PQC test binary not built on this platform |
| `FastDDS` | ,  | ,  | ,  | _skipped_, Fast DDS PKI-DH test binary not built on this platform |

## GPU offload, swapover cost & throughput crossover (scalability, not latency)

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `swapover — Apple M5 (unified memory) (modeled)` | device=Apple M5 (unified memory), modeled=True, dispatch_us=204.0 | ,  | 204.00 µs | 204.00 µs | 0.0 ns | ok · projected dispatch+sync = 204 us. CALIBRATED: GPU saturates ~120 GB/s unified LPDDR5; numpy CPU ~17.5 GB/s effective -> reproduces the measured ~4 MiB crossover |
| `crossover batch — Apple M5 (unified memory) (modeled)` | device=Apple M5 (unified memory), modeled=True | ,  | ,  | ,  | ,  | ok · GPU overtakes CPU above ~4.0 MiB resident / 4.0 MiB cold (host<->device copy each batch); ~4,081 concurrent 1-KiB streams. Roofline projection — see GPGPU-Sim/Accel-Sim for cycle-accurate. CALIBRATED: GPU saturates ~120 GB/s unified LPDDR5; numpy CPU ~17.5 GB/s effective -> reproduces the measured ~4 MiB crossover |
| `swapover — NVIDIA A100 80GB (PCIe4 x16) (modeled)` | device=NVIDIA A100 80GB (PCIe4 x16), modeled=True, dispatch_us=8.0 | ,  | 8.00 µs | 8.00 µs | 0.0 ns | ok · projected dispatch+sync = 8 us. PROJECTED: HBM2e 1.94 TB/s, PCIe4 x16 ~25 GB/s effective, ~8 us launch |
| `crossover batch — NVIDIA A100 80GB (PCIe4 x16) (modeled)` | device=NVIDIA A100 80GB (PCIe4 x16), modeled=True | ,  | ,  | ,  | ,  | ok · GPU overtakes CPU above ~319 KiB resident / never (per-byte slower) cold (host<->device copy each batch); ~319 concurrent 1-KiB streams. Roofline projection — see GPGPU-Sim/Accel-Sim for cycle-accurate. PROJECTED: HBM2e 1.94 TB/s, PCIe4 x16 ~25 GB/s effective, ~8 us launch |
| `swapover — NVIDIA H100 (PCIe5 x16) (modeled)` | device=NVIDIA H100 (PCIe5 x16), modeled=True, dispatch_us=6.0 | ,  | 6.00 µs | 6.00 µs | 0.0 ns | ok · projected dispatch+sync = 6 us. PROJECTED: HBM3 3.35 TB/s, PCIe5 x16 ~55 GB/s effective, ~6 us launch |
| `crossover batch — NVIDIA H100 (PCIe5 x16) (modeled)` | device=NVIDIA H100 (PCIe5 x16), modeled=True | ,  | ,  | ,  | ,  | ok · GPU overtakes CPU above ~237 KiB resident / never (per-byte slower) cold (host<->device copy each batch); ~237 concurrent 1-KiB streams. Roofline projection — see GPGPU-Sim/Accel-Sim for cycle-accurate. PROJECTED: HBM3 3.35 TB/s, PCIe5 x16 ~55 GB/s effective, ~6 us launch |
| `swapover — NVIDIA H100 (NVLink) (modeled)` | device=NVIDIA H100 (NVLink), modeled=True, dispatch_us=6.0 | ,  | 6.00 µs | 6.00 µs | 0.0 ns | ok · projected dispatch+sync = 6 us. PROJECTED: HBM3 3.35 TB/s, NVLink ~450 GB/s effective, ~6 us launch |
| `crossover batch — NVIDIA H100 (NVLink) (modeled)` | device=NVIDIA H100 (NVLink), modeled=True | ,  | ,  | ,  | ,  | ok · GPU overtakes CPU above ~237 KiB resident / 289 KiB cold (host<->device copy each batch); ~237 concurrent 1-KiB streams. Roofline projection — see GPGPU-Sim/Accel-Sim for cycle-accurate. PROJECTED: HBM3 3.35 TB/s, NVLink ~450 GB/s effective, ~6 us launch |
| `swapover — AMD MI250 (PCIe4 x16) (modeled)` | device=AMD MI250 (PCIe4 x16), modeled=True, dispatch_us=8.0 | ,  | 8.00 µs | 8.00 µs | 0.0 ns | ok · projected dispatch+sync = 8 us. PROJECTED: HBM2e ~3.2 TB/s (per-GCD aggregate), PCIe4 x16 ~25 GB/s, ~8 us launch |
| `crossover batch — AMD MI250 (PCIe4 x16) (modeled)` | device=AMD MI250 (PCIe4 x16), modeled=True | ,  | ,  | ,  | ,  | ok · GPU overtakes CPU above ~316 KiB resident / never (per-byte slower) cold (host<->device copy each batch); ~316 concurrent 1-KiB streams. Roofline projection — see GPGPU-Sim/Accel-Sim for cycle-accurate. PROJECTED: HBM2e ~3.2 TB/s (per-GCD aggregate), PCIe4 x16 ~25 GB/s, ~8 us launch |
| `_group_error` | ,  | ,  | ,  | ,  | ,  | _error_, ModuleNotFoundError: No module named 'numpy' |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `dispatch+sync swapover (unified memory)` | backend=mlx.core, gpu=Apple M5 (Apple GPU / Metal) | ,  | 198.08 µs | 198.08 µs | 655.16 µs | ok · irreducible per-offload cost; unified memory (no PCIe). vs 83 ns bus hop / 12 µs ML-KEM, GPU disqualified for the latency path |
| `throughput vs CPU` | batch_elems=4096, backend=mlx.core | ,  | ,  | ,  | ,  | ok · CPU wins (swapover not amortized); batch=4,096 f32 = 16 KiB |
| `throughput vs CPU` | batch_elems=65536, backend=mlx.core | ,  | ,  | ,  | ,  | ok · CPU wins (swapover not amortized); batch=65,536 f32 = 256 KiB |
| `throughput vs CPU` | batch_elems=262144, backend=mlx.core | ,  | ,  | ,  | ,  | ok · CPU wins (swapover not amortized); batch=262,144 f32 = 1024 KiB |
| `throughput vs CPU` | batch_elems=1048576, backend=mlx.core | ,  | ,  | ,  | ,  | ok · GPU wins; batch=1,048,576 f32 = 4096 KiB |
| `throughput vs CPU` | batch_elems=4194304, backend=mlx.core | ,  | ,  | ,  | ,  | ok · GPU wins; batch=4,194,304 f32 = 16384 KiB |
| `throughput vs CPU` | batch_elems=16777216, backend=mlx.core | ,  | ,  | ,  | ,  | ok · GPU wins; batch=16,777,216 f32 = 65536 KiB |
| `crossover batch (GPU starts winning)` | backend=mlx.core | ,  | ,  | ,  | ,  | ok · GPU offload pays off above ~1,048,576 f32 elems (~4096 KiB). At 1 KiB/stream that is ~4,096 concurrent streams, i.e. GPU is a SWARM/MESH/high-density-electrode scalability tool, not a per-node one |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `swapover — Apple M5 (unified memory) (modeled)` | device=Apple M5 (unified memory), modeled=True, dispatch_us=204.0 | ,  | 204.00 µs | 204.00 µs | 0.0 ns | ok · projected dispatch+sync = 204 us. CALIBRATED: GPU saturates ~120 GB/s unified LPDDR5; numpy CPU ~17.5 GB/s effective -> reproduces the measured ~4 MiB crossover |
| `crossover batch — Apple M5 (unified memory) (modeled)` | device=Apple M5 (unified memory), modeled=True | ,  | ,  | ,  | ,  | ok · GPU overtakes CPU above ~4.0 MiB resident / 4.0 MiB cold (host<->device copy each batch); ~4,081 concurrent 1-KiB streams. Roofline projection — see GPGPU-Sim/Accel-Sim for cycle-accurate. CALIBRATED: GPU saturates ~120 GB/s unified LPDDR5; numpy CPU ~17.5 GB/s effective -> reproduces the measured ~4 MiB crossover |
| `swapover — NVIDIA A100 80GB (PCIe4 x16) (modeled)` | device=NVIDIA A100 80GB (PCIe4 x16), modeled=True, dispatch_us=8.0 | ,  | 8.00 µs | 8.00 µs | 0.0 ns | ok · projected dispatch+sync = 8 us. PROJECTED: HBM2e 1.94 TB/s, PCIe4 x16 ~25 GB/s effective, ~8 us launch |
| `crossover batch — NVIDIA A100 80GB (PCIe4 x16) (modeled)` | device=NVIDIA A100 80GB (PCIe4 x16), modeled=True | ,  | ,  | ,  | ,  | ok · GPU overtakes CPU above ~319 KiB resident / never (per-byte slower) cold (host<->device copy each batch); ~319 concurrent 1-KiB streams. Roofline projection — see GPGPU-Sim/Accel-Sim for cycle-accurate. PROJECTED: HBM2e 1.94 TB/s, PCIe4 x16 ~25 GB/s effective, ~8 us launch |
| `swapover — NVIDIA H100 (PCIe5 x16) (modeled)` | device=NVIDIA H100 (PCIe5 x16), modeled=True, dispatch_us=6.0 | ,  | 6.00 µs | 6.00 µs | 0.0 ns | ok · projected dispatch+sync = 6 us. PROJECTED: HBM3 3.35 TB/s, PCIe5 x16 ~55 GB/s effective, ~6 us launch |
| `crossover batch — NVIDIA H100 (PCIe5 x16) (modeled)` | device=NVIDIA H100 (PCIe5 x16), modeled=True | ,  | ,  | ,  | ,  | ok · GPU overtakes CPU above ~237 KiB resident / never (per-byte slower) cold (host<->device copy each batch); ~237 concurrent 1-KiB streams. Roofline projection — see GPGPU-Sim/Accel-Sim for cycle-accurate. PROJECTED: HBM3 3.35 TB/s, PCIe5 x16 ~55 GB/s effective, ~6 us launch |
| `swapover — NVIDIA H100 (NVLink) (modeled)` | device=NVIDIA H100 (NVLink), modeled=True, dispatch_us=6.0 | ,  | 6.00 µs | 6.00 µs | 0.0 ns | ok · projected dispatch+sync = 6 us. PROJECTED: HBM3 3.35 TB/s, NVLink ~450 GB/s effective, ~6 us launch |
| `crossover batch — NVIDIA H100 (NVLink) (modeled)` | device=NVIDIA H100 (NVLink), modeled=True | ,  | ,  | ,  | ,  | ok · GPU overtakes CPU above ~237 KiB resident / 289 KiB cold (host<->device copy each batch); ~237 concurrent 1-KiB streams. Roofline projection — see GPGPU-Sim/Accel-Sim for cycle-accurate. PROJECTED: HBM3 3.35 TB/s, NVLink ~450 GB/s effective, ~6 us launch |
| `swapover — AMD MI250 (PCIe4 x16) (modeled)` | device=AMD MI250 (PCIe4 x16), modeled=True, dispatch_us=8.0 | ,  | 8.00 µs | 8.00 µs | 0.0 ns | ok · projected dispatch+sync = 8 us. PROJECTED: HBM2e ~3.2 TB/s (per-GCD aggregate), PCIe4 x16 ~25 GB/s, ~8 us launch |
| `crossover batch — AMD MI250 (PCIe4 x16) (modeled)` | device=AMD MI250 (PCIe4 x16), modeled=True | ,  | ,  | ,  | ,  | ok · GPU overtakes CPU above ~316 KiB resident / never (per-byte slower) cold (host<->device copy each batch); ~316 concurrent 1-KiB streams. Roofline projection — see GPGPU-Sim/Accel-Sim for cycle-accurate. PROJECTED: HBM2e ~3.2 TB/s (per-GCD aggregate), PCIe4 x16 ~25 GB/s, ~8 us launch |
| `swapover` | ,  | ,  | ,  | ,  | ,  | _skipped_, no GPU on this runner — the GPU swapover/crossover is measured on the Apple-Silicon host |
| `throughput_crossover` | ,  | ,  | ,  | ,  | ,  | _skipped_, no GPU on this runner — the GPU swapover/crossover is measured on the Apple-Silicon host |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `swapover, Apple M5 (unified memory) (modeled)` | device=Apple M5 (unified memory), modeled=True, dispatch_us=204.0 | ,  | 204.00 µs | 204.00 µs | 0.0 ns | ok · projected dispatch+sync = 204 us. CALIBRATED: GPU saturates ~120 GB/s unified LPDDR5; numpy CPU ~17.5 GB/s effective -> reproduces the measured ~4 MiB crossover |
| `crossover batch, Apple M5 (unified memory) (modeled)` | device=Apple M5 (unified memory), modeled=True | ,  | ,  | ,  | ,  | ok · GPU overtakes CPU above ~4.0 MiB resident / 4.0 MiB cold (host<->device copy each batch); ~4,081 concurrent 1-KiB streams. Roofline projection, see GPGPU-Sim/Accel-Sim for cycle-accurate. CALIBRATED: GPU saturates ~120 GB/s unified LPDDR5; numpy CPU ~17.5 GB/s effective -> reproduces the measured ~4 MiB crossover |
| `swapover, NVIDIA A100 80GB (PCIe4 x16) (modeled)` | device=NVIDIA A100 80GB (PCIe4 x16), modeled=True, dispatch_us=8.0 | ,  | 8.00 µs | 8.00 µs | 0.0 ns | ok · projected dispatch+sync = 8 us. PROJECTED: HBM2e 1.94 TB/s, PCIe4 x16 ~25 GB/s effective, ~8 us launch |
| `crossover batch, NVIDIA A100 80GB (PCIe4 x16) (modeled)` | device=NVIDIA A100 80GB (PCIe4 x16), modeled=True | ,  | ,  | ,  | ,  | ok · GPU overtakes CPU above ~319 KiB resident / never (per-byte slower) cold (host<->device copy each batch); ~319 concurrent 1-KiB streams. Roofline projection, see GPGPU-Sim/Accel-Sim for cycle-accurate. PROJECTED: HBM2e 1.94 TB/s, PCIe4 x16 ~25 GB/s effective, ~8 us launch |
| `swapover, NVIDIA H100 (PCIe5 x16) (modeled)` | device=NVIDIA H100 (PCIe5 x16), modeled=True, dispatch_us=6.0 | ,  | 6.00 µs | 6.00 µs | 0.0 ns | ok · projected dispatch+sync = 6 us. PROJECTED: HBM3 3.35 TB/s, PCIe5 x16 ~55 GB/s effective, ~6 us launch |
| `crossover batch, NVIDIA H100 (PCIe5 x16) (modeled)` | device=NVIDIA H100 (PCIe5 x16), modeled=True | ,  | ,  | ,  | ,  | ok · GPU overtakes CPU above ~237 KiB resident / never (per-byte slower) cold (host<->device copy each batch); ~237 concurrent 1-KiB streams. Roofline projection, see GPGPU-Sim/Accel-Sim for cycle-accurate. PROJECTED: HBM3 3.35 TB/s, PCIe5 x16 ~55 GB/s effective, ~6 us launch |
| `swapover, NVIDIA H100 (NVLink) (modeled)` | device=NVIDIA H100 (NVLink), modeled=True, dispatch_us=6.0 | ,  | 6.00 µs | 6.00 µs | 0.0 ns | ok · projected dispatch+sync = 6 us. PROJECTED: HBM3 3.35 TB/s, NVLink ~450 GB/s effective, ~6 us launch |
| `crossover batch, NVIDIA H100 (NVLink) (modeled)` | device=NVIDIA H100 (NVLink), modeled=True | ,  | ,  | ,  | ,  | ok · GPU overtakes CPU above ~237 KiB resident / 289 KiB cold (host<->device copy each batch); ~237 concurrent 1-KiB streams. Roofline projection, see GPGPU-Sim/Accel-Sim for cycle-accurate. PROJECTED: HBM3 3.35 TB/s, NVLink ~450 GB/s effective, ~6 us launch |
| `swapover, AMD MI250 (PCIe4 x16) (modeled)` | device=AMD MI250 (PCIe4 x16), modeled=True, dispatch_us=8.0 | ,  | 8.00 µs | 8.00 µs | 0.0 ns | ok · projected dispatch+sync = 8 us. PROJECTED: HBM2e ~3.2 TB/s (per-GCD aggregate), PCIe4 x16 ~25 GB/s, ~8 us launch |
| `crossover batch, AMD MI250 (PCIe4 x16) (modeled)` | device=AMD MI250 (PCIe4 x16), modeled=True | ,  | ,  | ,  | ,  | ok · GPU overtakes CPU above ~316 KiB resident / never (per-byte slower) cold (host<->device copy each batch); ~316 concurrent 1-KiB streams. Roofline projection, see GPGPU-Sim/Accel-Sim for cycle-accurate. PROJECTED: HBM2e ~3.2 TB/s (per-GCD aggregate), PCIe4 x16 ~25 GB/s, ~8 us launch |
| `swapover` | ,  | ,  | ,  | ,  | ,  | _skipped_, no GPU on this runner, the GPU swapover/crossover is measured on the Apple-Silicon host |
| `throughput_crossover` | ,  | ,  | ,  | ,  | ,  | _skipped_, no GPU on this runner, the GPU swapover/crossover is measured on the Apple-Silicon host |

## RTL / FPGA (cycle-exact simulation + formal proof, no hardware)

**HDL-sim · RTL @ 200 MHz (icarus)**

| Algorithm | Config | Class | Throughput / rate | p50 | p99 | Status |
|---|---|---|---|---|---|---|
| `SPSC FIFO enqueue->dequeue latency` | clock_mhz=200.0, width_bits=64, depth=16 | ,  | 10.0 ns | 10.0 ns | 0.0 ns | ok · 2 clock cycles, cycle-exact; = 10.00 ns @ 200 MHz. The bus ring as RTL. |
| `SPSC FIFO steady-state throughput` | clock_mhz=200.0 | ,  | 199,902,391 items/s | ,  | ,  | ok · 1.000 items/cycle x 200 MHz (1.0 = full rate) |
| `SPSC FIFO formal proof (SymbiYosys + z3)` | method=k-induction | ,  | ,  | ,  | ,  | ok · PROVEN unbounded (k-induction): never overflow, never full&empty, count consistent |

## robobus bus / determinism / real-time

**Darwin · Apple M1 (Virtual)**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `determinism_probe` | ,  | ,  | ,  | _skipped_, n/a here — needs the robobus package (private repo); the portable `bus` group measures the same ring on this platform |
| `bus_latency` | ,  | ,  | ,  | _skipped_, n/a here — needs the robobus package (private repo); the portable `bus` group measures the same ring on this platform |

**Darwin · Apple M5**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `determinism_probe` | ,  | ,  | ,  | ok · adaptive determinism probe output |

**Linux · x86_64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `determinism_probe` | ,  | ,  | ,  | _skipped_, n/a here — needs the robobus package (private repo); the portable `bus` group measures the same ring on this platform |
| `bus_latency` | ,  | ,  | ,  | _skipped_, n/a here — needs the robobus package (private repo); the portable `bus` group measures the same ring on this platform |

**Windows · AMD64**

| Algorithm | Config | Class | Throughput / rate | Status |
|---|---|---|---|---|
| `determinism_probe` | ,  | ,  | ,  | _skipped_, n/a here, needs the robobus package (private repo); the portable `bus` group measures the same ring on this platform |
| `bus_latency` | ,  | ,  | ,  | _skipped_, n/a here, needs the robobus package (private repo); the portable `bus` group measures the same ring on this platform |


---

**Classes (grounded in NIST).** `classical` = quantum-**broken** asymmetric, RSA, DH, ECDH, ECDSA, Ed25519, which Shor breaks and NIST IR 8547 lists as quantum-vulnerable (deprecate 2030 / disallow 2035). `PQC` = the NIST post-quantum *asymmetric* standards (FIPS 203 ML-KEM, FIPS 204 ML-DSA) that replace them. `HYBRID` = classical ⊕ PQC (the CNSA 2.0 transition, e.g. ECDH ‖ ML-KEM → HKDF-SHA384). `QR` = symmetric / hash / MAC / KDF: quantum does **not** break these (only Grover's square-root applies), and NIST *defines* its strength Categories 1–5 BY them (Cat 1 = AES-128, 2 = SHA-256, 3 = AES-192, 4 = SHA-384, 5 = AES-256). So AES-128 and SHA-256 are quantum-security *levels*, not "classical", the NIST Category and CNSA-2.0 fitness are in each row's role note. **AES-128 (Level 1) is the QR floor**; anything weaker, 3DES (112-bit), DES, RC4, MD5, SHA-1, is sub-threshold and stays `classical`. Latency percentiles are per-operation; throughput is aggregate._
