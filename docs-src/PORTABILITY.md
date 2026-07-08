# Portability matrix

Two layers, very different reach:

* **robobus core** (bus + codec + crypto) — pure-Python stdlib + `cryptography`
  (+ optional `quantcrypt`/`liboqs`) + a tiny portable C poller. Runs **everywhere**
  Python runs.
* **ROS 1 / ROS 2 / LSL native stacks** — via RoboStack/conda (desktop OSes + Pi) or
  via a `rosbridge`/`micro-ROS` client (mobile).

| Platform | ROS 2 | ROS 1 | LSL | robobus bus + PQC | How |
|---|---|---|---|---|---|
| **macOS** (arm64/x64) | ✅ full | ✅ full | ✅ | ✅ | `scripts/install_macos.sh` (tested on M5/26.1) |
| **Linux x86_64** (Debian/Ubuntu/Fedora/Arch) | ✅ full | ✅ full | ✅ | ✅ (`/dev/shm`) | `scripts/install_linux.sh` |
| **Linux aarch64** | ✅ full | ✅ full | ✅ | ✅ | `scripts/install_linux.sh` |
| **Privacy distros** (Kali, Parrot, PureOS) | ✅ | ✅ | ✅ | ✅ | `scripts/install_linux.sh` |
| **Whonix / Kicksecure** | ✅¹ | ✅¹ | ✅ | ✅ | install over Tor; bus is host-local |
| **Tails** | ✅² | ✅² | ✅ | ✅ | install to Persistent Storage (amnesic otherwise) |
| **Qubes OS** | ✅³ | ✅³ | ✅ | ✅ | per-AppVM/TemplateVM; bus stays in-qube |
| **Windows 10/11** (x64) | ✅ | ✅ | ✅ | ✅ (`%TEMP%` mmap) | `scripts\install_windows.ps1` |
| **Raspberry Pi** (64-bit OS) | ✅⁴ | ✅⁴ | ✅ | ✅ (`/dev/shm`) | `scripts/install_rpi.sh` |
| **Android / GrapheneOS** | ⚠️ via bridge | ⚠️ via bridge | ✅⁵ | ✅ (Termux) | see below |
| **iOS / iPadOS** | ⚠️ via bridge | ⚠️ via bridge | ✅⁶ | ✅ (a-Shell/embed) | see below |

¹ on Tor-routed distros conda solves are slow (network-bound) — but the bus itself needs no network.
² Tails is amnesic; point `ROBOTICS_STACK` at a `/live/persistence` path.
³ Each qube is its own Linux; install in the AppVM (or a TemplateVM to persist).
⁴ 64-bit only (no 32-bit ROS on RoboStack); Gazebo is heavy on a Pi.
⁵ liblsl builds for Android (NDK); pylsl via Termux.
⁶ liblsl builds for iOS; use a-Shell/Pythonista or embed liblsl in an app.

## Why desktop ROS can't run on Android/iOS

RoboStack is conda, and there is no conda for Android/iOS. micro-ROS targets MCUs, not
phones. So on mobile you run the **robobus bus + PQC crypto + LSL in Python**, and reach
a ROS graph elsewhere over the network:

```
 Phone (Termux / a-Shell)                     Robot or workstation (Linux/macOS/Win)
 ┌───────────────────────────┐                ┌─────────────────────────────────────┐
 │ robobus bus + crypto      │   rosbridge    │  rosbridge_server  ──►  ROS 2 graph  │
 │ pylsl  ───────────────────┼──  WebSocket ──┼─►  (Nav2 / MoveIt / sensors)         │
 │ your app (PQC-secured)    │   (wss + AEAD) │  robobus ros2 bridge ──► bus         │
 └───────────────────────────┘                └─────────────────────────────────────┘
```

### Android / GrapheneOS

1. Install **Termux** (F-Droid; GrapheneOS: install in a sandboxed profile).
2. `pkg install python clang openssl`; `pip install cryptography quantcrypt pylsl`.
3. `pip install -e .` from this repo — the bus + crypto + LSL adapter work natively
   (ring dir auto-selects `$PREFIX/tmp`).
4. To reach ROS, run `rosbridge_server` on the robot and talk to it over `wss://`
   (wrap the channel with a robobus suite for end-to-end PQC on top of TLS).

GrapheneOS note: Termux runs in the normal app sandbox; the bus is process-local to
Termux. Cross-app IPC needs a content provider or a localhost socket.

### iOS / iPadOS

1. Use **a-Shell** (Python + clang, sandboxed) or embed CPython + liblsl in an app.
2. `pip install cryptography pylsl` (quantcrypt/liboqs may need a prebuilt wheel or the
   pure-Python KEM fallback). `pip install -e .`.
3. Reach ROS via `rosbridge` over `wss://`, same as Android.
4. App Store distribution requires embedding (no `pip` at runtime); the bus + crypto are
   plain Python/C and embed cleanly.

## The C poller across OSes

`native/shm_bench.c` is C11 + POSIX mmap. It builds with `clang`/`gcc` on macOS, Linux,
and Raspberry Pi as-is. On Windows, compile with clang-cl or MSVC and swap `mmap` for
`CreateFileMapping`/`MapViewOfFile` (the ring layout is identical; the wire format is
byte-compatible across all platforms).

## Cross-platform test evidence (not just claims)

Every target OS reduces to a **(libc × CPU arch)** substrate plus a package manager;
distro branding doesn't affect a pure-Python + OpenSSL/liboqs stack. So we *prove*
portability by running the suite on those substrates via **Docker + QEMU**
(`scripts/qemu_test.sh`, wired into CI as the `cross-arch` matrix):

| Substrate | libc / arch | Covers | Result |
|---|---|---|---|
| Debian aarch64 | glibc / aarch64 | Raspberry Pi OS 64-bit, Kali, Parrot, Whonix, Tails, PureOS, Ubuntu, Mint | ✅ core + classical crypto |
| Alpine aarch64 | musl / aarch64 | containers, embedded, minimal images | ✅ core + classical crypto |
| Debian x86_64 (QEMU) | glibc / x86_64 | desktops/servers, most distros | ✅ core |
| Debian armv7 (QEMU) | glibc / armv7l | **Raspberry Pi 32-bit** | ✅ core |
| macOS arm64 (native) | — / arm64 | dev machine | ✅ full 135-test suite |

The pure-stdlib **core** (ring, codec, bus, schema) and the **classical crypto**
(AES-256-GCM, SHA-2/3, HKDF, KMAC-via-OpenSSL, Argon2id) pass on all of the above; the
**PQC** layer (ML-KEM/ML-DSA via liboqs) runs wherever liboqs is installed and **skips
gracefully** (never errors) where it isn't — so the matrix stays green on minimal images.
Reproduce locally: `bash scripts/qemu_test.sh` (needs Docker; QEMU auto-registered).

| Platform | Verified how |
|---|---|
| macOS, Windows 10/11 | native GitHub-Actions runners (`test` job) + local macOS |
| PQC DDS-Security handshake | built + measured green on CI: Linux, macOS, **Windows native MSVC (VS2022) AND WSL2** (`dds-benchmarks` workflow) |
| Linux x86_64 / aarch64 / armv7, Alpine (musl) | QEMU/container `cross-arch` CI matrix (above) |
| Raspberry Pi OS (64 & 32-bit) | covered by Debian aarch64 + armv7 cells |
| Android / GrapheneOS (Termux) | aarch64 substrate cell + documented Termux install |
| iOS / iPadOS | documented manual path (a-Shell); not CI-automatable |

## Age-verification laws & the privacy/security distros

The stack is **distro-agnostic** — it runs on any Linux regardless of policy — but since
target users care about age-verification/anti-surveillance posture, here is the grounded
2025–2026 landscape (sources in git history / the research note):

* **The framing caveat:** age-verification laws (UK Online Safety Act, EU proposals) target
  *websites/platforms/app-stores*, not operating systems, so a Linux distro has nothing to
  "implement" under them. The one wave that touched OSes — **California AB 1043** (age-signal
  duty on OS/app-store providers) — was **amended by AB 1856 (May 2026) to exempt
  open-source operating systems** (EFF confirms this "substantially reduces the threat").
  So mainstream Linux is effectively **out of scope** of the law that started the debate.
* **Distros with a documented, on-the-record refusal:**
  * **GrapheneOS** (Android-based) — strongest, best-corroborated: public stance (Mar 2026)
    that it "will remain usable by anyone… without requiring personal information,
    identification or an account." Runs the robobus bus + crypto via Termux (see above).
  * **Zorin OS** (Ubuntu-based) — official forum statement: "no plans to introduce mandatory
    age or ID verification." Debian/glibc substrate → covered by the aarch64/x86_64 cells.
  * **Garuda Linux** (Arch-based) — public statement it "will not implement any age
    verification measures." Arch/glibc → same substrate.
* **Privacy/cybersecurity distros — ethos-aligned** (anti-surveillance by design; no
  AV-specific statement found): **Tails, Whonix, Qubes OS, Kali, Parrot, PureOS, BlackArch,
  Pentoo**. All reduce to Debian/Arch/Gentoo on glibc (or Alpine/musl) — all covered by the
  test matrix above. (Systemd-free distros — **Artix, Alpine, antiX** — additionally avoid a
  reported systemd `birthDate` userdb field; robobus depends on none of that either way.)
* **Broader opposition** (well-sourced, not distro statements): EFF, the Tor Project,
  Mullvad, Proton, and Mozilla co-signed a 19-organization letter (May 2026) opposing
  age-verification overreach.

Bottom line: **robobus imposes no identity/age requirement of its own and runs on all of
the above** — the privacy posture is the OS's to make; we don't get in its way.
