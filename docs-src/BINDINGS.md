# Multi-language bindings

robobus bridges **many** protocols, and each carries the same PQC-hardened frames:

| Protocol | robobus module | native language ecosystems (a sampling) |
|---|---|---|
| shared-memory bus | `robobus` core | any language with `mmap` + a crypto lib |
| ROS 1 | `ros1_adapter` | C++, Python, Lisp, Java, JS, C#, Go, Rust |
| ROS 2 | `ros2_adapter` | C++, Python, Rust, Java, JS, C#, Go, Ada, C |
| LSL | `lsl_adapter` | C, C++, Python, C#, Java, MATLAB, Rust, Julia, Octave |
| ZeroCM | `transports.zcm` | C, C++, Java, Python, MATLAB, NodeJS, Go, Julia |
| MQTT | `transports.mqtt` | **~every language** (Paho + others) |
| AMQP / RabbitMQ | `transports.amqp` | ~every language |
| Zenoh | `transports.zenoh` | C, C++, Rust, Python, REST, Kotlin |
| CAN / CAN-FD | `transports.can` | C, C++, Python, Rust, Go |
| TCP / UDP / serial | `transports.*` | universal (stdlib sockets/serial everywhere) |

So "multi-language" is the **union** of all these ecosystems — effectively every mainstream
language. Two ways to reach robobus from any language:

### 1. Native endpoint (implement the wire format)

The format ([PROTOCOL.md](PROTOCOL.md)) is small: an mmap seqlock ring, a codec frame, an
AES-256-GCM (`RBX1`) frame, and fixed-layout schema structs. Implement those and you have a
full, hardened robobus peer. Proven today:

* **C** — `native/shm_bench.c` (ring), `native/conformance.c` (codec + AEAD), tested vs Python.
* **Rust** — `bindings/rust/` (codec + AES-256-GCM), **bidirectional Python↔Rust conformance tested**.
* **JavaScript / Node** — `bindings/js/` (codec + AES-256-GCM via `node:crypto`; WebCrypto in
  browsers), **bidirectional Python↔Node conformance tested** — powers web/Electron dashboards.
* **Java** — `bindings/java/` (codec + AES-256-GCM via JCE), **bidirectional Python↔Java
  conformance tested** (`tests/test_java.py`) — for JVM/Android robotics apps.

**Packaged & publishable:** Rust → **crates.io** (`Cargo.toml`), JS → **npm**
(`package.json` + TypeScript types), Java → **Maven Central** (`pom.xml`, sources+javadoc+GPG).
`cargo package` / `npm pack` / `javac` all build locally; a tag runs
`.github/workflows/publish-bindings.yml` (each registry gated on a repo variable).
* **Struct codegen for the layout** — `Schema.render(lang)` emits all 14: C, C++, Rust, Go,
  Java, C#, TypeScript, Python, Julia, MATLAB/Octave, Swift, Kotlin, Ruby, Lua — and **every one
  is compile/run-verified**: its generated reader parses Python's packed bytes byte-for-byte in
  `tests/test_codegen.py`.

### 2. Via a transport client (reach the bus over a wire it already speaks)

A language with no native binding but *any* MQTT/AMQP/Zenoh/TCP client can talk to robobus:
run a `robobus <transport>` bridge, and have the app implement just the `RBX1` AEAD (one
AES-256-GCM call — available in every platform crypto lib) to send/receive hardened frames.
Example: a Swift/iOS app uses an MQTT client + CryptoKit AES-256-GCM.

## Language matrix (hardened endpoints)

| Language | native binding | struct codegen | AES-256-GCM lib | PQC (ML-KEM/ML-DSA) |
|---|---|---|---|---|
| C / C++ | ✅ (`native/`) | ✅ | OpenSSL | liboqs |
| Rust | ✅ (`bindings/rust`) | ✅ | `aes-gcm` (RustCrypto) | `oqs` crate |
| Python | ✅ (core) | ✅ | `cryptography` | liboqs / quantcrypt |
| Go | codegen ✅ | ✅ | `crypto/aes`+`cipher` | liboqs-go |
| Java / Kotlin | codegen ✅ | ✅ | JCE / BouncyCastle | liboqs-java, BC |
| C# / .NET | codegen ✅ | ✅ | `System.Security.Cryptography` | liboqs / BC |
| JavaScript / TS | ✅ (`bindings/js`) | ✅ | WebCrypto / node:crypto | liboqs-wasm |
| Julia, MATLAB, Swift, Ruby, Lua, … | via transport client | (add to `render`) | platform crypto | liboqs bindings |

Every listed language has an AES-256-GCM implementation and a liboqs binding, so **national-
security-grade hardening (CNSA 2.0 / FIPS) is reachable in all of them**.

## Adding a language to `render()`

Add a type map + a `_render_<lang>` method in `robobus/schema.py` (see the eight existing
ones). The layout is fixed little-endian packed, so a generator is ~20 lines; add a compile
check to `tests/test_codegen.py` if a toolchain is available.
