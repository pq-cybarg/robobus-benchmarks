# Architecture

ROS 1 (Noetic), ROS 2 (Kilted) and LabStreamingLayer each have their own transport. robobus unifies
them with one idea: **a host-local shared-memory ring buffer that every runtime attaches to** — the
universal, nanosecond-latency fabric. The native transports still work; the bus is what makes "all
three talk" trivial and fast.

```
 ROS 1 (Noetic)            ROS 2 (Kilted)              LabStreamingLayer
   rospy node  ─┐          rclpy node ─┐               pylsl in/outlet ─┐
                │                       │                                │
            ┌───┴───────────────────────┴────────────────────────────────┴───┐
            │     robobus shared-memory bus  (mmap ring, seqlock SPMC)         │
            │     ~ns raw hop · optional AES-256-GCM / ML-KEM / ML-DSA / SHA-3 │
            └──────────────────────────────────────────────────────────────────┘
```

## The bus

- **SPSC/SPMC ring** in shared memory (`mmap`), **seqlock per slot** — lock-free, wait-free reads.
- Native C11-atomics poller (`native/`) with an identical layout for the sub-µs path; the Python
  layer (`robobus/`) drives ROS/LSL adapters, codecs and crypto.
- **Measured (Apple M5):** amortized ring op **3.9 ns**, cross-process one-way **p50 83 ns**,
  98%+ under 100 ns with RT hardening (see [Benchmarks](Benchmarks)).
- Zero-copy `recv_view`; back-pressure via reader/writer indices.

## Layers

| Layer | Where | Role |
|---|---|---|
| Ring | `robobus/shm_ring.py`, `native/*.c` | the mmap fabric |
| Bus | `robobus/bus.py` | Publisher/Subscriber over the ring |
| Codecs | `robobus/codec*` | raw / float / int / string / json / bytes |
| Crypto | `robobus/crypto/` | AEAD, KEM, signatures, KDF, suites, channel, compliance |
| Transports | `robobus/transports/` | udp/tcp/mqtt/serial/can/zenoh/zcm/amqp/kafka/dds bridges |
| Real-time | `robobus/realtime.py`, `determinism.py` | tail-bounding + adaptive probe |

## Crypto stack (CNSA 2.0)

Audited COTS only on the default path — liboqs (ML-KEM/ML-DSA), OpenSSL 3 (AEAD, HKDF, KMAC via
EVP), argon2-cffi (passphrase KDF). KDF placement matters: **Argon2id** for passphrase→key,
**HKDF/KMAC** for high-entropy inputs. Suites span `classical … nist1/3/5 … cnsa20`. See
[PQC DDS-Security](PQC-DDS-Security) for the DDS integration.

## Portability

The bus + crypto + benchmark harness are written to run on macOS, Windows, every supported Linux,
Android and iOS. The [Benchmarks](Benchmarks) harness is capability-detecting: each platform
measures what it supports and records the rest as SKIPPED, so the *same script* stays valid
everywhere.
