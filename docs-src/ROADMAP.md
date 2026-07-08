# Roadmap

Forward-looking items with concrete design paths. The core stack (ROS 1 + ROS 2 + LSL +
bus + PQC crypto + compliance) is complete and tested today; these extend reach.

## 1. PQC in SROS2 / DDS-Security

* **Key agreement — LIVE on CI.** `patches/fastdds/0001-cnsa2-pqc-dds-security.patch`
  adds hybrid **ECDH+ML-KEM-768/1024** to Fast DDS's built-in PKI-DH auth plugin
  (`SharedSecret = HKDF-SHA384(ECDH‖ML-KEM)`, CNSA 2.0). The ML-KEM material rides
  inside the already-signed `dh1`/`dh2` properties, so no signature-code changes.
  The whole patched Fast DDS tree builds green on CI and links liboqs 0.15.0; crypto core
  + full handshake math are conformance-verified vs OpenSSL 3, and `git apply --check` is
  clean vs pristine v3.1.0.
* **Identity/auth — dependency-gated.** DDS identity certs signed with **ML-DSA-87**
  (FIPS 204) need Fast DDS built against an OpenSSL that exposes ML-DSA (OpenSSL 3.5+ /
  `oqs-provider`); no plugin code change once the cert path accepts PQC signatures.
  Until then, run RSA-3072/ECDSA-P384 identities with the hybrid ML-KEM key agreement
  above (confidentiality is already quantum-safe).
* **CycloneDDS — LIVE-VERIFIED, incl. ML-DSA-87 identity.** `patches/cyclonedds/0001-cnsa2-pqc-dds-security.patch`
  ports the same hybrid ECDH+ML-KEM design to CycloneDDS's C auth plugin, plus **ML-DSA-87**
  (FIPS 204) post-quantum identity signatures. From-scratch on CI it passes CycloneDDS's own
  two-peer `ddssec_handshake` suite — classical, hybrid ML-KEM-768 **and** 1024, and a full
  CNSA 2.0 handshake (ML-DSA-87 identity + ML-KEM-1024) — measured live on **Linux, macOS and
  Windows (native MSVC + WSL2)**. A separate `0002` patch makes the handshake `INITIAL_DELAY`
  env-tunable (the 10 ms settle, not crypto, dominates the end-to-end time; ~9 ms recoverable).
* **Available now (defence in depth):** even without the DDS build, layer **robobus
  app-layer PQC** (`--security cnsa20`) on the payloads — quantum-safe end-to-end across
  DDS **and** ROS 1 / LSL (which DDS-Security can't touch).

## 2. Transports — IMPLEMENTED (UDP / MQTT / serial / ZeroCM)

Shipped in `robobus/transports/` (a `FrameBridge` base + thin subclasses):

* **UDP** (`robobus udp`) — stdlib, unicast/multicast; tested with PQC encryption.
* **TCP** (`robobus tcp`) — stdlib, length-framed, auto-reconnect; tested with PQC.
* **MQTT** (`robobus mqtt`) — needs `paho-mqtt`.
* **serial/radio** (`robobus serial`) — needs `pyserial`; length-framed stream.
* **CAN bus** (`robobus can`) — needs `python-can`; segments frames over CAN/CAN-FD MTU.
* **Zenoh** (`robobus zenoh`) — needs `eclipse-zenoh`; LAN/WAN/edge pub-sub.
* **ZeroCM** (`robobus zcm`) — needs `zerocm`; UDP-multicast/IPC/serial for embedded+radio.
* **AMQP / RabbitMQ** (`robobus amqp`) — needs `pika`.

Each carries opaque, optionally AEAD-sealed frames, so **all transports inherit the full
PQC suite** via `--security`. UDP & TCP are tested on loopback (plaintext + CNSA-2.0).

Implemented transports today: UDP, TCP, MQTT, serial, CAN, Zenoh, ZeroCM, AMQP, **Kafka**
(confluent-kafka / kafka-python), and **DDS-as-a-transport** (`robobus dds`, opaque sealed
frames on a native DDS topic) — plus the ROS 1, ROS 2, LSL runtime adapters. Kafka is tested
with an in-memory broker (plaintext + CNSA-2.0), DDS with a real rclpy round-trip
(`tests/test_kafka_dds.py`). **Still to add:** raw multicast discovery — each is just another
`FrameBridge` subclass.

**Multi-language — DONE:** Rust reference binding (`bindings/rust/`, Python↔Rust AES-256-GCM
conformance tested); C reference (`native/`); and `Schema.render()` codegen for 14 languages
(C, C++, Rust, Go, Java, C#, TypeScript/JS, Python, Julia, MATLAB/Octave, Swift, Kotlin, Ruby,
Lua) with C++/Go/Rust compile-verified. See [BINDINGS.md](BINDINGS.md). Any language with
AES-256-GCM (all of them) can be a hardened endpoint. Remaining: package the bindings for
crates.io / npm / Maven and add native ring readers beyond C/Rust.

## 3. Multi-language bindings

The wire format ([PROTOCOL.md](PROTOCOL.md)) is language-agnostic and already proven
cross-language: `native/shm_bench.c` (C) reads/writes the *same* ring as the Python core.

* **Planned bindings:** C/C++ (header-only ring + codec), **Rust** (memmap2 + a seqlock
  reader; liboqs has a Rust crate), and **JavaScript/TypeScript** (Node `Buffer` + a
  native addon or WASM) for browser/Electron dashboards.
* PQC in other languages: **liboqs** provides C/C++/Rust/Go/Java/Python/JS bindings, so the
  handshake (§4 of PROTOCOL.md) ports directly; AES-256-GCM/SHA-3 exist in every platform
  crypto library.
* Deliverable shape: a small `bindings/<lang>/` reference implementation per language plus
  a shared conformance test (encode a frame in lang A, decode in lang B).

## 4. Hardening — DONE this round

* **Security:** anti-replay (sliding window), per-channel key binding, rekey ratchet,
  AES-GCM-SIV, `SecretBuffer` zeroization (mlock + wipe-on-drop), sidecar wipe-on-exit —
  wired into SecurePub/Sub and all transports. See [SECURITY.md](SECURITY.md).
* **Latency tail:** `robobus.realtime` (macOS QoS / Linux SCHED_FIFO + `mlockall` + core
  pinning) cut p90 ~12× on macOS; zero-copy `recv_view`. `robobus bench --realtime`.
* **Robustness:** fuzz harness for codec + AEAD + the native C parser; ThreadSanitizer
  proves the seqlock's C11 acquire/release ordering race-free (`native/shm_tsan.c`).
* **Ops:** `robobus top` live monitor; GitHub Actions CI (`.github/workflows/ci.yml`);
  module-integrity SHA3 self-test.

**DONE:** typed/schema channels (`robobus.schema`: fixed-layout structs, zero-copy field
access, `c_struct()` codegen, T_SCHEMA frame, TypedPub/Sub) — layout proven to match C
byte-for-byte.

**DONE since:** Linux hard-RT p99 harness (`scripts/rt_latency.py` + `robobus.realtime` +
a `hard-rt` self-hosted CI job — see [REALTIME.md](REALTIME.md)); CycloneDX SBOM +
**Sigstore-signed / SLSA-attested** release pipeline (`.github/workflows/release.yml`);
**Rust, JS, and Java** reference bindings (all Python-cross-conformance-tested) packaged
for crates.io / npm / Maven Central.

**Still to add:** a compiled Python ring reader (note: per the AEAD measurements, ctypes
per-call overhead means the *native data-plane* — `native/shm_bench.c`, ~100 ns for 97.5 %
of messages — not a ctypes reader, is the real ns-scale path).
