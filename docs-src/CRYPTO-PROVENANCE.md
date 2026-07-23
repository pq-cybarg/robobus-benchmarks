# Cryptographic provenance, what's audited COTS vs. our code

**Design rule: never reimplement an audited primitive.** Every cryptographic
*primitive* (cipher, hash, MAC, KDF, KEM, signature, RNG) comes from an established,
audited/validated library. Our code is the *composition* around them, framing,
key schedule, handshake wiring, anti-replay, which is protocol code, not new math.

This is the answer to "what should we be using audited COTS for, and where is our
implementation actually better?": **use COTS for all primitives; our value is
integration, and integration is what should be reviewed, not primitives.**

**Measured across every language.** The [Speed matrix](../speed.html) exercises all **26 of these
primitives** (4 AEADs, 6 hashes, 5 KDF/MACs, 3 ML-KEM + X25519, 3 ML-DSA + SLH-DSA + 2 Falcon +
Ed25519) in **33 language configs**, and every cell resolves to one of these audited providers, 
each language uses its native stack where it has one (OpenSSL/CryptoKit/JCE/RustCrypto…), otherwise
it reaches the *same* audited C through one labeled shim, `librbcrypto`, over **OpenSSL 3.6.3 +
liboqs + libblake3**. Argon2id is known-answer-verified (byte-for-byte vs the PHC reference) in
every language; the AEAD round-trip is asserted; the PQC groups also carry the distinct backends
(OpenSSL EVP vs liboqs vs Go's native `crypto/mlkem`) side-by-side so the implementation, not just
the primitive, is visible. No language reimplements a primitive, the shim is a *binding*, not new math.

## Primitive → provider (all audited COTS)

| Primitive | Provider (default) | Validation pedigree | Our code |
|---|---|---|---|
| AES-256-GCM, AES-GCM-SIV, ChaCha20-Poly1305 | **OpenSSL 3** via pyca `cryptography` | FIPS 140-3 (OpenSSL FIPS provider); CAVP | none, direct call |
| SHA-2 / SHA-3 / SHAKE | **OpenSSL 3** via pyca `cryptography` | FIPS 180-4 / 202; CAVP | none, direct call |
| HKDF (HMAC extract/expand) | **OpenSSL 3** via pyca `cryptography` | RFC 5869; SP 800-56C; CAVP HMAC | none, direct call |
| **KMAC256** | **OpenSSL 3 `EVP_MAC`** (`_kmac_openssl.py`, ctypes) | FIPS SP 800-185; CAVP | ctypes *binding* only; primitive is OpenSSL's |
| PBKDF2-HMAC-SHA-512 | **OpenSSL 3** via pyca | SP 800-132; CAVP | none, direct call |
| scrypt | **OpenSSL** via `hashlib.scrypt` | RFC 7914 | none, stdlib call |
| Argon2id | **argon2-cffi** (PHC reference C impl) | PHC winner; RFC 9106 | none, direct call |
| ML-KEM 512/768/1024 | **liboqs** (Open Quantum Safe) | FIPS 203; NIST KAT-tested in liboqs | none, direct call |
| ML-DSA 44/65/87, Falcon, SLH-DSA | **liboqs** | FIPS 204/205; NIST KAT | none, direct call |
| X25519 / X448 / Ed25519 / P-256 ECDH | **OpenSSL 3** via pyca / DDS plugin | FIPS 186-5 / RFC 7748 | none, direct call |
| CSPRNG (key/nonce generation) | **OS RNG** (`os.urandom`) + liboqs/OpenSSL RNG | SP 800-90A/B (OS entropy) | none, direct call |

### The one reimplementation, and why it's a *fallback* only

`robobus/crypto/kmac.py` contains a pure-Python Keccak-f[1600] → cSHAKE256 → KMAC256.
It exists because Python's `hashlib` exposes SHAKE256 but **not** cSHAKE/KMAC (different
domain-separation suffix). It is **not** the default: `primitives.kmac256` routes to
**OpenSSL's audited `EVP_MAC` KMAC-256** whenever OpenSSL 3 is present (i.e. essentially
always, pyca and liboqs both link it). The pure-Python path is used only on a
stdlib-only platform with no OpenSSL 3, and even then it is gated by:

* byte-for-byte agreement with OpenSSL's KMAC-256 (cross-implementation), **and**
* the NIST SP 800-185 KMAC256 sample vectors,

both enforced in `tests/test_kmac.py`. `primitives.KMAC_BACKEND` reports which is live
(`"openssl"` or `"python-keccak"`), and `robobus crypto backends` prints it.

> Should we have written it at all? For the default path, no, OpenSSL is the right
> answer, and that is now the default. The fallback earns its place only as a
> KAT-gated portability shim, never as a primitive we ask you to trust on its own.

## Where our code legitimately lives (and what to review)

None of these introduce new primitives; they *compose* the COTS ones. This is the
surface that warrants review (not the algorithms):

| Our component | What it is | Built on |
|---|---|---|
| `RBX1` AEAD frame | self-describing nonce+tag framing | OpenSSL AEAD |
| Hybrid KEM combiner | `KDF(ECDH ‖ ML-KEM, transcript)` construction (SP 800-56C rev3) | OpenSSL HKDF/KMAC + liboqs |
| Anti-replay window | RFC 6479 sliding window + per-channel HKDF binding + epoch rekey | OpenSSL HKDF |
| Passphrase keyfile | Argon2id/scrypt/PBKDF2 → AES-GCM-wrap of a random key | argon2-cffi / OpenSSL |
| PKI-DH PQC patch | carries ML-KEM in the signed `dh1`/`dh2`; `HKDF-SHA384(ECDH‖ML-KEM)` | OpenSSL + liboqs |
| Native AES fast path (`_native.py`) | cffi *plumbing* to OpenSSL `EVP_*` | OpenSSL AES-GCM |

So the honest scope of any "reaudit" is: (1) the combiner/handshake **construction**,
(2) the anti-replay and key-schedule logic, (3) the framing/serialization, and (4) the
one KMAC ctypes binding + its KAT-gated fallback. The primitives themselves are already
FIPS/CAVP-validated COTS and are not re-audited.

## Implementation security ≠ functional correctness

Interop + KATs prove an implementation computes the *right answer*. They do **not** prove
it computes it *safely*: two implementations can interoperate perfectly while one leaks
the private key. The distinct threat classes, and how this stack handles each:

| Threat | Example | Our posture |
|---|---|---|
| **Timing side-channel** | KyberSlash (secret-dependent division in ML-KEM); non-constant-time ML-DSA rejection sampling / NTT | Use only constant-time implementations (liboqs, OpenSSL); **verify with valgrind TIMECOP** (`scripts/ct_verify_liboqs.sh`) on the pinned liboqs |
| **Weak/reused signing randomness** | deterministic-nonce fault attacks on Dilithium/ML-DSA | FIPS 204 **hedged** signing (fresh randomness per sig), asserted for OpenSSL *and* liboqs in `tests/test_mldsa_openssl.py` |
| **Missing zeroization** | secret key lingers in freed memory | liboqs & OpenSSL zeroize key material on free; robobus `SecretBuffer` (mlock + wipe-on-drop) for app-layer keys |
| **Fault / power / EM** | glitching, DPA on an embedded target | Out of software scope, use a certified HSM/secure element; documented as an honest limit |

### The implementations we allow (and the ones we don't)

ML-KEM / ML-DSA come from **exactly two** places, both mainstream and constant-time-reviewed:

* **liboqs 0.15.0** (Open Quantum Safe), PQClean-derived reference code; its CI runs
  **valgrind TIMECOP constant-time tests**, and 0.15.0 post-dates the KyberSlash fixes.
  This is robobus's ML-KEM/ML-DSA backend.
* **OpenSSL ≥ 3.5.1 native default provider**, the DDS identity-cert path. We require
  **≥ 3.5.1** (not the first-cut 3.5.0) and verify at test time; the env ships **3.6.3**.

We do **not** roll our own PQC, and we do **not** accept unaudited third-party providers.
`tests/test_mldsa_openssl.py` enforces the version floor and **cross-verifies OpenSSL
against liboqs both directions**, two independent FIPS 204 implementations agreeing is
strong evidence neither has a functional defect; TIMECOP covers the timing dimension.

### What we verify vs. what needs a lab

* **Automated (CI):** correctness (interop + FIPS 204 sizes), tamper rejection, hedged
  randomization, OpenSSL version floor, and **constant-timeness via TIMECOP on Linux**
  (`make ct-verify`; skipped on macOS where valgrind has no arm64 target).
* **Not automated (needs hardware):** power/EM side-channel and active fault-injection
  resistance. For those threat models, run the PQC in a certified HSM / secure element, 
  no pure-software stack can attest to them.

## Is KMAC the default KDF? No, and that's deliberate

KMAC is *offered* (suite `nist5-kmac`), but the **default KDF is HKDF-HMAC-SHA-384**,
because:

* CNSA 2.0 lists **SHA-384 / HMAC**, not KMAC, so HKDF-SHA384 is the compliance-first choice;
* HMAC-SHA-384 is hardware-accelerated (SHA-NI / ARMv8 crypto), faster than software Keccak.

KMAC is the right pick when a deployment wants a single Keccak primitive end-to-end
(hash + MAC + KDF) with no HMAC nesting and built-in domain separation. Both are
SP 800-56C rev3-approved; it's a per-suite choice, and either way the *implementation*
is OpenSSL's audited one.
