# Security model

Encryption is **optional and opt-in** (`--security <suite>`); the core bus runs with
zero crypto installed. When enabled, every link gets the same protections regardless of
runtime or transport (the crypto sits on opaque bytes below the codec).

## What's protected

| Property | Mechanism |
|---|---|
| Confidentiality | AES-256-GCM / ChaCha20-Poly1305 / **AES-GCM-SIV** (nonce-misuse-resistant) |
| Integrity + authenticity | AEAD tag (tamper → frame rejected) |
| **Anti-replay** | per-message authenticated counter + IPsec/DTLS sliding window; replays & too-old frames dropped |
| **Channel binding** | per-channel HKDF subkey bound to the shared transport id, a frame for channel A can't be accepted on B |
| **In-session rekey** | epoch keys (HKDF ratchet every N messages) bound nonce usage + single-key blast radius |
| Quantum-safe key agreement | ML-KEM (+ hybrid X25519/X448); MITM-resistant via ML-DSA-signed offer |
| Forward secrecy | per-session at handshake; run a fresh KEM handshake periodically for in-session FS |
| Key zeroization | `SecretBuffer`: mlock'd, wiped on `wipe()` and on `__del__`; sidecar wipes on stop/SIGTERM; `mlockall` available |

## Threat model & limits (honest)

* **Single sealing producer per channel.** Anti-replay assumes one sender per channel
  (matches the SPMC bus). Multiple independent secure producers on one channel would
  interleave counters.
* **CPython `bytes` can't be wiped.** Transient key copies (from `os.urandom`/key files)
  persist until GC; the long-lived copy lives in a `SecretBuffer`. For true zeroization
  use the native AEAD + the **sidecar** (separate, mlock'd process, the strong boundary).
* **Metadata is not hidden** on network transports (who talks to whom, timing). For the
  Tor/privacy-distro case, add Noise/TLS + constant-rate padding under the transport
  (roadmap).
* **Not FIPS-validated.** Approved algorithms + FIPS-mode policy + KAT self-tests + a
  crypto-boundary sidecar are provided; CMVP validation requires an accredited lab
  (see [CMVP-READINESS.md](CMVP-READINESS.md)).
* **Fail-closed:** a wrong-key/tampered frame raises; replays/too-old are dropped silently.

## Quick use

```bash
robobus crypto keygen --out ~/.robobus/key          # 32-byte AEAD key (0600)
robobus udp --to telem:239.0.0.1:5000 --from cmd:5001 --security cnsa20 --keyfile ~/.robobus/key
robobus crypto sidecar --keyfile ~/.robobus/fips.key # then export ROBOBUS_FIPS_SIDECAR=/tmp/robobus-fips.sock
```
