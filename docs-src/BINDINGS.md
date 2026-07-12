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
* **Cython** — `bench/cython/cyaead.pyx` (typed-Python → C AES-256-GCM on OpenSSL EVP),
  wire-compatible `RBX1`, **bidirectional Python↔Cython conformance tested** (`tests/test_cython.py`).
  ~3.4× faster than pure Python (1.4 vs 4.7 µs seal+open), closing most of the gap to native C —
  the point of Cython: keep Python ergonomics, get near-C throughput.

**Embed it anywhere — `librobobus` (C ABI):** `librobobus/` builds a dependency-light shared
library (`robobus.dll` / `librobobus.dylib` / `librobobus.so` + a static lib, via CMake on every
OS) exposing AES-256-GCM `RBX1` seal/open and the codec behind a stable C ABI. Any language links
it over its FFI (`ctypes`, P/Invoke, JNA/Panama, `ffi-napi`, `bindgen`). It is proven byte-identical
to the Python reference on Linux, macOS, Windows **and five emulated ISAs including big-endian
s390x** — its C self-test embeds the exact bytes Python emits, and a `ctypes` test cross-conforms
both directions (`tests/test_cabi.py`, `.github/workflows/shared-lib.yml`).

**Packaged & publishable:** Rust → **crates.io** (`Cargo.toml`), JS → **npm**
(`package.json` + TypeScript types), Java → **Maven Central** (`pom.xml`, sources+javadoc+GPG).
`cargo package` / `npm pack` / `javac` all build locally; a tag runs
`.github/workflows/publish-bindings.yml` (each registry gated on a repo variable).
* **Struct codegen for the layout** — `Schema.render(lang)` emits all 14: C, C++, Rust, Go,
  Java, C#, TypeScript, Python, Julia, MATLAB/Octave, Swift, Kotlin, Ruby, Lua — and **every one
  is compile/run-verified**: its generated reader parses Python's packed little-endian bytes
  byte-for-byte in `tests/test_codegen.py`.

**Every toolchain, actually run — no silent skips.** `tools/all-languages.Dockerfile` installs
*all* of these toolchains in one image (gcc/clang, Go, Rust, JDK, .NET, Node+TypeScript, Julia,
Octave, Swift, Kotlin, Ruby, Lua, Python+Cython) and runs the full polyglot conformance with a
hard "versions print or abort" gate — 12-language codegen + the six native seal/open bindings,
green together. It reproduces on any machine with Docker (`docker build -f
tools/all-languages.Dockerfile …`), so "all languages pass" is a command anyone can re-run, not a
claim.

### 2. Via a transport client (reach the bus over a wire it already speaks)

A language with no native binding but *any* MQTT/AMQP/Zenoh/TCP client can talk to robobus:
run a `robobus <transport>` bridge, and have the app implement just the `RBX1` AEAD (one
AES-256-GCM call — available in every platform crypto lib) to send/receive hardened frames.
Example: a Swift/iOS app uses an MQTT client + CryptoKit AES-256-GCM.

## Language matrix (hardened endpoints)

| Language | native binding | struct codegen | AES-256-GCM lib | PQC (ML-KEM/ML-DSA) |
|---|---|---|---|---|
| C / C++ | ✅ (`native/` + `librobobus` C ABI) | ✅ | OpenSSL | liboqs |
| Rust | ✅ (`bindings/rust`) | ✅ | `aes-gcm` (RustCrypto) | `oqs` crate |
| Python | ✅ (core) | ✅ | `cryptography` | liboqs / quantcrypt |
| Cython | ✅ (`bench/cython`) | ✅ (via Python) | OpenSSL EVP | liboqs / quantcrypt |
| Go | codegen ✅ | ✅ | `crypto/aes`+`cipher` | liboqs-go |
| Java / Kotlin | codegen ✅ | ✅ | JCE / BouncyCastle | liboqs-java, BC |
| C# / .NET | codegen ✅ | ✅ | `System.Security.Cryptography` | liboqs / BC |
| JavaScript / TS | ✅ (`bindings/js`) | ✅ | WebCrypto / node:crypto | liboqs-wasm |
| Julia, MATLAB, Swift, Ruby, Lua, … | via transport client | (add to `render`) | platform crypto | liboqs bindings |

Every listed language has an AES-256-GCM implementation and a liboqs binding, so **national-
security-grade hardening (CNSA 2.0 / FIPS) is reachable in all of them**.

## Build from source & release automation

One portable command builds **every** artifact from source into `dist/` — no conda/ROS, runs
on Linux, macOS, and Windows (Git Bash); each component is skipped-and-reported if its
toolchain is absent:

    scripts/build_release.sh            # or: make release

It produces the native `librobobus` C-ABI library (shared + static + header, KAT-self-tested),
the Rust `.crate`, the npm `.tgz`, the Java `.jar`, the Python wheel + sdist, and a `SHA256SUMS`.
For the native library on every CPU ISA via Docker/QEMU (aarch64, armv7, ppc64le, riscv64,
big-endian s390x): `tools/package-librobobus-arches.sh` (`make release-arches`).

On a `v*` tag, `release.yml` runs the same build across Linux/macOS/Windows + the five ISAs and
attaches the packaged `librobobus` artifacts to the GitHub Release alongside Sigstore-signed +
SLSA-attested Python wheels and a CycloneDX SBOM; `publish-bindings.yml` publishes the
Rust/npm/Maven packages — one tag, every language, every platform.

## Adding a language to `render()`

Add a type map + a `_render_<lang>` method in `robobus/schema.py` (see the eight existing
ones). The layout is fixed little-endian packed, so a generator is ~20 lines; add a compile
check to `tests/test_codegen.py` if a toolchain is available.
