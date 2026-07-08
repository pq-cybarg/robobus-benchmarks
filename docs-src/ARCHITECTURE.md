# Architecture

## 1. Isolation model (no disruption)

Everything lives in an isolated Miniforge (conda) prefix.

* **No `conda init`.** We never edit `~/.zshrc`/`~/.zprofile`. The base environment does
  not auto-activate, so a normal shell keeps the system `python3` untouched.
* **Shell-local activation.** `env/activate-*.sh` run `conda shell.<sh> hook` for the
  *current shell only* and `conda activate` the target env. Close the shell, it's gone.
* **Three environments**, all Python 3.12.13 (same ABI, so the pure-stdlib bus imports
  identically): `ros2_kilted`, `ros1_noetic`, `lsl`.
* **RoboStack** provides ROS as conda packages — the only open-source path to ROS on
  Apple Silicon. ROS 2 from `robostack-kilted`, ROS 1 from `robostack-staging`.

## 2. The bus (`robobus.shm_ring`)

A single-producer / multi-consumer ring buffer over an mmap'd file.

* **Why mmap-of-a-file:** macOS has no `/dev/shm`; an mmap'd file stays in the unified
  page cache (RAM). On Linux we use `/dev/shm` (tmpfs) directly. One file per channel.
* **Why pure stdlib:** the core has to import in three different conda Pythons plus the
  system Python. A compiled wheel would need rebuilding per interpreter; `mmap` +
  `struct` do not.
* **Seqlock overwrite semantics (LMAX-Disruptor style):** a monotonically increasing
  `cursor`; each slot stamped with its sequence. A reader copies a slot then re-checks
  the stamp — if the writer lapped it mid-copy, it retries or skips ahead (counting
  drops). Wait-free for the producer; "latest-wins" — the right default for sensors and
  control loops. Correctness is covered by `tests/test_shm_ring.py` (wraparound,
  drop-detection, multi-reader, torn-read).

Frame format and slot layout are documented in `robobus/shm_ring.py`.

## 3. Why the bus *is* the cross-runtime bridge

There is **no prebuilt `ros1_bridge` for Noetic↔Kilted** (it's rarely built for newer
ROS 2 distros, and never for this pairing on RoboStack). Rather than fight that, each
runtime gets a thin adapter that maps its topics/streams onto bus channels:

* `robobus.ros2_adapter` (rclpy) — `--to-bus` subscriptions + `--from-bus` busy-poll
  publisher threads.
* `robobus.ros1_adapter` (rospy) — the same, in ROS 1. ROS1→bus→ROS2 *is* the
  `ros1_bridge` replacement, and it's faster (shared memory, not DDS+TCPROS).
* `robobus.lsl_adapter` (pylsl) — LSL inlets/outlets ↔ bus, including an opaque
  encrypted-string transport mode.

Proven end-to-end by `scripts/e2e_demo.sh`: ROS1→bus→ROS2 topic and ROS2→bus→live LSL
stream, all delivering at ~27 µs (dominated by ROS serialization + thread poll, not the
bus).

## 4. Latency engineering

Three transports, each tuned for localhost:

* **Bus:** the floor. Raw in-thread hop ~0.52 µs; Python cross-process round-trip
  p50 3.2 µs. The compiled `native/shm_bench.c` (C11 atomics, busy-spin) puts 97% of
  cross-process messages under the 1 µs clock tick — **sub-microsecond is real with a
  compiled poller**; the residual tail is the macOS scheduler descheduling busy-spin
  threads (fixable with RT thread QoS / core isolation).
* **ROS 2 DDS:** `config/fastdds_shm.xml` forces the Fast DDS shared-memory transport +
  UDP-localhost and disables builtin transports; `config/cyclonedds.xml` pins CycloneDDS
  to loopback with multicast off (deterministic discovery on macOS). `ROS_AUTOMATIC_
  DISCOVERY_RANGE=LOCALHOST` keeps discovery on-host.
* **LSL:** `config/lsl_api.cfg` restricts resolution to localhost with small buffers.

For the lowest possible latency, use the bus with `put_raw`/`recv_raw` (skip the codec)
and busy-spin readers (`spin_us=0`).

## 5. Codec

`robobus.codec` — a compact self-describing frame `[type][stamp_ns][payload]` carrying
float64/int32 arrays, strings, JSON, or raw bytes, with a `monotonic_ns` send timestamp
(one host-wide clock, so any reader computes true one-way latency). JSON is the generic
path for arbitrary ROS messages; bytes is the opaque path for already-serialized data.

## 6. Security (optional, layered *below* the codec)

`robobus.crypto` adds authenticated encryption **without touching the hot path's
design**: PQC math runs once per session; every message is just AEAD.

* **Per message:** AES-256-GCM (default) or ChaCha20-Poly1305 — a self-describing
  `magic|alg|nonce|ciphertext+tag` frame. Hardware-accelerated; GB/s.
* **Per session:** a KEM handshake (ML-KEM, optionally hybrid with X25519/X448),
  authenticated by a PQ signature (ML-DSA / Falcon / SLH-DSA) over the transcript to
  stop MITM, deriving a 256-bit session key via HKDF (SHA-2/SHA-3).
* **Suites** (`robobus.crypto.suites`) name the intent: `nist1/3/5`, `hybrid3/5`,
  `cnsa20`, `csfc` (two independent AEAD layers), `sphincs5`, `falcon5`, `classical`.
* **Backends** auto-select **liboqs** (full OQS catalog: 32 KEMs, 221 sigs) →
  **quantcrypt** (PQClean) → **pyca cryptography** (AEAD, SHA-3, classical).
* **FIPS sidecar** (`robobus.crypto.sidecar`): a separate process is the cryptographic
  boundary; in a compliant deployment it links a CMVP-validated module. See
  [COMPLIANCE.md](COMPLIANCE.md) and [CMVP-READINESS.md](CMVP-READINESS.md).

The same encrypted bytes ride the bus, ROS topics, and LSL string streams unchanged, so
encryption is uniform across all three runtimes — and entirely opt-in.
