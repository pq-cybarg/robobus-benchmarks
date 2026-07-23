# Compliance

> **Honest scope.** This project implements **approved algorithms** and a **FIPS-mode
> architecture** (algorithm policy + power-on self-tests + a crypto-boundary sidecar).
> It is **not** a CMVP-validated cryptographic module, only an accredited CST lab can
> issue that certificate. Where a standard requires a *validated module* (not just an
> approved algorithm), this is marked **Module-required** and satisfied by pointing the
> sidecar at a validated backend (OpenSSL 3 FIPS provider, AWS-LC-FIPS, or a PKCS#11 HSM).
> See [CMVP-READINESS.md](CMVP-READINESS.md).

## Algorithm conformance (what robobus implements)

| Standard | Algorithms used | Where | Status |
|---|---|---|---|
| **FIPS 203** (ML-KEM) | ML-KEM-512/768/1024 | KEM handshake | Approved-alg ✅ |
| **FIPS 204** (ML-DSA) | ML-DSA-44/65/87 | handshake auth | Approved-alg ✅ |
| **FIPS 205** (SLH-DSA) | SPHINCS+-SHA2 | handshake auth | Approved-alg ✅ |
| **FIPS 197 / SP 800-38D** | AES-256-GCM | per-message AEAD | Approved-alg ✅ |
| **FIPS 180-4** | SHA-256/384/512 | KDF/transcript | Approved-alg ✅ |
| **FIPS 202** | SHA3-256/384/512, SHAKE | KDF/transcript | Approved-alg ✅ |
| **FIPS 198-1** | HMAC (via HKDF) | key derivation | Approved-alg ✅ |
| **SP 800-56C** | HKDF key derivation / KEM combiner | session keys | Approved-alg ✅ |
| **SP 800-90A** | OS CSPRNG/DRBG (`os.urandom`/`secrets`) | nonces/keys | OS-provided ✅ |
| **FIPS 186-5** | EdDSA (Ed25519) | classical auth | Approved-alg ✅ |
| ChaCha20-Poly1305, X25519/X448 | n/a | optional non-FIPS | **Not FIPS** (flagged) |

`robobus crypto compliance` runs **power-on self-tests** (KATs for AES-256-GCM, SHA-2,
SHA-3; pairwise-consistency for every ML-KEM/ML-DSA parameter set + SLH-DSA) and a
policy check that rejects non-conformant suites.

## Standards posture by subsystem

| Subsystem | Relevant standards | Status & notes |
|---|---|---|
| **robobus crypto** | FIPS 140-3, 203/204/205, CNSA 2.0, CSfC, ISO/IEC 18033, 19790 | Approved algorithms; **Module-required** for 140-3 validation → FIPS sidecar |
| **robobus bus** |, (transport, no crypto) | Host-local shared memory; carries ciphertext when a suite is set |
| **ROS 2 DDS** | DDS-Security (OMG), AES-GCM | `scripts/setup_sros2.sh` (classical transport security); not PQC |
| **ROS 1** | n/a | No native transport security; use robobus app-layer crypto |
| **LSL** | n/a | No native security; robobus carries AEAD ciphertext over LSL |
| **Process / org** | ISO/IEC 27001, SOC 2 | Out of software scope (ISMS/process controls) |
| **RF / radios** | **FCC Part 15**, ETSI EN 300/301 | Applies to the robot's wireless **hardware**, not this middleware. Use FCC/CE-certified radio modules; software adds no emissions |

## Suite → standard mapping

| Suite | NIST level | Conforms to | Note |
|---|---|---|---|
| `nist1` | 1 | FIPS | ML-KEM-512 + ML-DSA-44 |
| `nist3` | 3 | FIPS | ML-KEM-768 + ML-DSA-65 |
| `nist5` | 5 | FIPS | ML-KEM-1024 + ML-DSA-87 + SHA-512/SHA3-512 (Cat-5 hash) |
| `cnsa20` | 5 | **CNSA 2.0** + FIPS | ML-KEM-1024 + ML-DSA-87 + AES-256 + SHA-384 (NSA's exact suite) |
| `csfc` | 5 | **CSfC** | two independent AEAD layers (defence in depth) |
| `sphincs5` | 5 | FIPS (FIPS 205) | hash-based signatures |
| `hybrid3/5` | 3/5 | NIST hybrid (**non-FIPS**: X25519/X448) | strongest belt-and-suspenders, not FIPS |
| `classical` | 0 | none (not quantum-safe) | interop only |

### NIST-5 vs CNSA 2.0, a real distinction

These two are routinely conflated; they are **not** the same hash policy, and the
configurator treats them as separate buttons for exactly this reason.

**NIST security categories are set by *collision* resistance (≈ output ÷ 2), not by
output width:**

| Hash | Output | Collision strength | NIST category | Length-extension |
|---|---|---|---|---|
| SHA-512, SHA3-512, SHAKE-256 | 512 / ≥512 | 256-bit | **Category 5** | SHA3/SHAKE immune; SHA-512 vulnerable |
| SHA-384 | 384 | 192-bit | Category 4 | immune (truncated SHA-512) |
| SHA-256, SHA3-256, BLAKE3 | 256 | 128-bit | Category 2 | SHA-256 vulnerable; SHA3/BLAKE3 immune |

* **Pure NIST Category 5 *requires* SHA-512 / SHA3-512 / SHAKE-256**, a 256-bit
  collision bound. SHA-384 (192-bit collision) is Category 4 and **does not** satisfy a
  strict NIST-5 hash requirement. Note **BLAKE3**: a 256-bit output but only a **128-bit
  collision** bound, so it lands at Category 2, far below NIST-5, regardless of its speed.
* **CNSA 2.0 is a *separate* NSA profile** that deliberately specifies **SHA-384** (with
  ML-KEM-1024 + ML-DSA-87 + AES-256-GCM). It is the NSA's exact national-security suite,
  not "NIST-5 with a weaker hash", so it earns its own button rather than being folded
  into the NIST-level selector.
* **Length extension:** SHA-2 in its full-width forms (SHA-256, SHA-512) is
  length-extension-vulnerable; **SHA-3/SHAKE, BLAKE3, and truncated SHA-384 are immune.**
  The configurator surfaces this as a live caveat whenever a full-width SHA-2 hash is
  selected.
* **Equivalent NIST classes are equally secure.** At a given category, a hash-based
  signature (SLH-DSA) is **not** "more secure" than a lattice one (ML-DSA, Falcon), the
  category *is* the security claim. The "Most secure + fast" preset therefore picks the
  **fastest** primitive within the target category, never a slower one for a false sense
  of margin.

### Build & price any suite interactively

The **[interactive configurator](../speed.html#configure)** turns every row of this table
into a live performance spec: choose a language, KEM, signature, AEAD, hash, keystore-KDF,
and transport, and it reports the NIST category it satisfies (strict weakest-link, with a
"capped by …" note), whether it meets CNSA 2.0, the length-extension caveat, the standards
it conforms to, and the measured cost, handshake, per-message envelope (p50/p90/p99
latency + rate + byte/data rate), transport rate, and keystore-unlock. That's how a suite
maps directly to numbers you can compare against a competing product.

## Running the checks

```bash
robobus crypto compliance --standard fips     --suite nist5
robobus crypto compliance --standard cnsa20   --suite cnsa20
robobus crypto compliance --standard csfc     --suite csfc
```

Exit code is non-zero if any self-test fails or the suite is non-conformant, wire it
into CI as a gate.

## FIPS sidecar (the crypto boundary)

```bash
# terminal 1, the boundary process (link a validated module in production)
robobus crypto sidecar --keyfile ~/.robobus/fips.key --alg aes256-gcm
# terminal 2, apps delegate AEAD to it automatically
export ROBOBUS_FIPS_SIDECAR=/tmp/robobus-fips.sock
robobus ros2 --from-bus /cmd:cmd --security cnsa20 --keyfile ~/.robobus/fips.key
```

In FIPS mode all AEAD goes through the sidecar, isolating key material and the
cryptographic boundary from the application, the structure CMVP expects.
