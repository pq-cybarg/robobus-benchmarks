# PQC DDS-Security

Non-invasive patches add **CNSA 2.0 post-quantum** protection to the built-in DDS-Security
authentication plugin of **both** DDS stacks — same design, adapted to each codebase. Live-verified
via each project's own handshake unit test.

| | Fast DDS v3.1.0 | Cyclone DDS 0.10.5 |
|---|---|---|
| Pinned commit | `e2afc15…` | `2cdd114…` |
| Hybrid key agreement | ✅ ECDH+ML-KEM-768/1024 | ✅ ECDH+ML-KEM-768/1024 |
| ML-DSA-87 identity signatures | ✅ | ✅ |
| Verified by | `BuiltinPKIDH` gtest | `ddssec_handshake` CUnit (2-peer) |

## Two layers, both post-quantum

**1 · Key agreement (confidentiality).** Classical **ECDH P-256** combined with **ML-KEM** (FIPS
203) through **HKDF-SHA384** (SP 800-56C): `SharedSecret = HKDF-SHA384(ECDH ‖ ML-KEM)`. Hybrid is
the right call here because key agreement has the *harvest-now-decrypt-later* threat — breaking
ECDH alone doesn't recover the key.

- Fast DDS signs the raw token bytes, so ML-KEM material rides inside the already-signed `dh1`/`dh2`
  properties.
- Cyclone DDS **re-serializes** the DH keys for the signed content, so embedded bytes would be
  *unsigned* — instead the ML-KEM public key/ciphertext travel in **separate signed `pqc1`/`pqc2`**
  properties added to every sign+verify array.
- **Anti-downgrade:** once hybrid is negotiated (via the signature-covered `c.kagree_algo`) or
  locally required, a missing ML-KEM secret **fails the handshake** — no silent fallback to
  ECDH-only. (Negative-tested.)

**2 · Identity signatures (authentication).** The plugins accept **ML-DSA-87** (FIPS 204) X.509
identity certificates ([RFC 9881](https://datatracker.ietf.org/doc/rfc9881/)) and sign/verify the
handshake with them. ML-DSA is a *pure* signature — no external digest — so the sign path uses
`md=NULL` + the one-shot `EVP_DigestSign/Verify` (the streaming API fails for ML-DSA on OpenSSL
3.6.3). Pure ML-DSA (not composite) is the CNSA-2.0 requirement; the composite path
([draft-ietf-lamps-pq-composite-sigs](https://datatracker.ietf.org/doc/draft-ietf-lamps-pq-composite-sigs/))
is documented for PQ/T-hybrid regimes.

## Why hybridize key agreement but not signatures

Key agreement must resist a *future* quantum computer decrypting *today's* recorded traffic →
hybrid. A signature only needs to hold until it's verified (no retroactive break) → pure ML-DSA is
sufficient and CNSA 2.0 does not require hybrid signatures.

## Performance

The post-quantum cost is small and one-time. From [Benchmarks](Benchmarks) (Apple M5):

- Hybrid key agreement (ECDH+ML-KEM-1024): **142 µs**.
- Full authenticated handshake: **598 µs** (NIST-1) → **1.15 ms** (CNSA 2.0, ML-DSA-sign-bound).
- DDS handshake incl. transport: classical **1.92 ms** → full CNSA 2.0 **2.44 ms** — PQ adds
  only ~0.5 ms, and it's a one-time per-peer cost.

## Reproduce

```bash
python scripts/patch_apply.py --component cyclonedds   # pristine + pinned + patch (git-apply clean)
python scripts/patch_apply.py --component fastdds
```

See `patches/*/INTEGRATION.md` and `patches/manifest.json` (exact pins + verified liboqs/OpenSSL/
asio versions). Standards: FIPS 203, FIPS 204, CNSA 2.0, RFC 9881, SP 800-56C.
