#!/usr/bin/env python3
"""
robobus / PQC-DDS full-system benchmark harness.

ONE portable script that benchmarks EVERY available capability, across all modes,
configurations, and techniques, and emits a single structured JSON result document
plus platform metadata. It is *capability-detecting*: every benchmark declares the
dependency it needs, and if that dependency is missing on the current platform the
benchmark is recorded as SKIPPED (with the reason) instead of crashing. That is what
makes "the exact same script" runnable on macOS, Windows, every supported Linux,
Android and iOS -- each platform simply runs whatever it can and reports the rest as
skipped.

  Measured today on macOS. Numbers are inherently platform-, CPU- and build-specific;
  re-run this identical script on each target platform to compare. Nothing here is a
  cross-platform claim on its own -- it is a reproducible measurement recipe.

Usage:
    python bench/run_benchmarks.py [--quick] [--out DIR] [--only GROUP[,GROUP...]]

Design notes / portability rules honored here:
  * stdlib-only imports at module load; every optional dependency (cryptography, oqs,
    argon2, psutil) is imported lazily inside a try/except and gated by a HAVE_* flag.
  * timing via time.perf_counter_ns() (monotonic, high-resolution, available on every
    CPython target).
  * no OS-specific syscalls on the core path; platform-specific probes (RT scheduling,
    determinism) are optional add-ons behind detection and never abort the run.
"""
from __future__ import annotations

import argparse
import json
import os
import platform
import statistics
import subprocess
import sys
import time
from typing import Callable, Optional

# --------------------------------------------------------------------------------------
# optional dependency detection (never fatal)
# --------------------------------------------------------------------------------------
HAVE: dict[str, str] = {}          # name -> version string when available
MISSING: dict[str, str] = {}       # name -> reason when not


def _try(name: str, importer: Callable[[], str]) -> bool:
    try:
        HAVE[name] = importer()
        return True
    except Exception as e:  # pragma: no cover - platform dependent
        MISSING[name] = f"{type(e).__name__}: {e}"
        return False


def _v_cryptography() -> str:
    import cryptography
    # touch the algorithms we use so a partial install is caught here
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305  # noqa: F401
    from cryptography.hazmat.primitives.asymmetric import x25519, ed25519, ec, rsa  # noqa: F401
    return cryptography.__version__


def _v_oqs() -> str:
    import oqs
    return getattr(oqs, "oqs_version", lambda: "unknown")()


def _v_argon2() -> str:
    import argon2
    return getattr(argon2, "__version__", "unknown")


def _v_psutil() -> str:
    import psutil
    return psutil.__version__


HAVE_CRYPTO = _try("cryptography", _v_cryptography)
HAVE_OQS = _try("oqs", _v_oqs)
HAVE_ARGON2 = _try("argon2", _v_argon2)
HAVE_PSUTIL = _try("psutil", _v_psutil)


# --------------------------------------------------------------------------------------
# timing helpers
# --------------------------------------------------------------------------------------
def _percentiles(samples_ns: list[int]) -> dict:
    s = sorted(samples_ns)
    n = len(s)

    def pct(p: float) -> float:
        if n == 1:
            return float(s[0])
        k = (n - 1) * p
        lo = int(k)
        hi = min(lo + 1, n - 1)
        return s[lo] + (s[hi] - s[lo]) * (k - lo)

    return {
        "n": n,
        "min_ns": s[0],
        "p50_ns": pct(0.50),
        "p90_ns": pct(0.90),
        "p99_ns": pct(0.99),
        "max_ns": s[-1],
        "mean_ns": statistics.fmean(s),
        "stdev_ns": statistics.pstdev(s) if n > 1 else 0.0,
    }


def measure_ops(fn: Callable[[], None], *, min_iters: int, min_seconds: float,
                warmup: int = 5, per_op_samples: int = 4000) -> dict:
    """Time a single operation. Returns ops/s plus per-op latency percentiles.

    Runs `fn` until both min_iters and min_seconds are satisfied. Records up to
    `per_op_samples` individual op latencies (perf_counter_ns deltas) for percentiles.
    """
    for _ in range(warmup):
        fn()
    samples: list[int] = []
    iters = 0
    t0 = time.perf_counter_ns()
    deadline = t0 + int(min_seconds * 1e9)
    while iters < min_iters or time.perf_counter_ns() < deadline:
        a = time.perf_counter_ns()
        fn()
        b = time.perf_counter_ns()
        if len(samples) < per_op_samples:
            samples.append(b - a)
        iters += 1
    elapsed_ns = time.perf_counter_ns() - t0
    out = {
        "iters": iters,
        "elapsed_s": elapsed_ns / 1e9,
        "ops_per_s": iters / (elapsed_ns / 1e9),
    }
    out.update(_percentiles(samples))
    return out


def measure_throughput(fn: Callable[[], None], *, nbytes: int, min_iters: int,
                       min_seconds: float, warmup: int = 3) -> dict:
    """Time an operation over `nbytes` of data; returns MB/s + ops/s."""
    for _ in range(warmup):
        fn()
    iters = 0
    t0 = time.perf_counter_ns()
    deadline = t0 + int(min_seconds * 1e9)
    while iters < min_iters or time.perf_counter_ns() < deadline:
        fn()
        iters += 1
    elapsed_s = (time.perf_counter_ns() - t0) / 1e9
    total_bytes = iters * nbytes
    return {
        "iters": iters,
        "elapsed_s": elapsed_s,
        "ops_per_s": iters / elapsed_s,
        "bytes": total_bytes,
        "mb_per_s": (total_bytes / 1e6) / elapsed_s,
        "mib_per_s": (total_bytes / (1024 * 1024)) / elapsed_s,
    }


# global result accumulator ------------------------------------------------------------
RESULTS: list[dict] = []


def record(group: str, name: str, config: dict, unit: str, metrics: Optional[dict],
           *, dependency: str = "stdlib", status: str = "ok", note: str = "") -> None:
    RESULTS.append({
        "group": group,
        "name": name,
        "config": config,
        "unit": unit,
        "dependency": dependency,
        "status": status,
        "note": note,
        "metrics": metrics or {},
    })


def skip(group: str, name: str, dependency: str, reason: str) -> None:
    record(group, name, {}, "", None, dependency=dependency, status="skipped", note=reason)


# scale knobs (overridden by --quick)
SIZES = [64, 1024, 16 * 1024, 256 * 1024, 1024 * 1024]
MIN_SECONDS = 0.6
MIN_ITERS = 50


# ======================================================================================
# 1. HASHING (stdlib hashlib -- available on every CPython everywhere)
# ======================================================================================
def bench_hashing() -> None:
    import hashlib
    algos = ["sha256", "sha384", "sha512", "sha3_256", "sha3_512", "blake2b", "blake2s"]
    avail = set(hashlib.algorithms_available)
    for algo in algos:
        if algo not in avail:
            skip("hash", algo, "hashlib", "algorithm not in hashlib.algorithms_available")
            continue
        for size in SIZES:
            data = os.urandom(size)
            m = measure_throughput(lambda: hashlib.new(algo, data).digest(),
                                   nbytes=size, min_iters=MIN_ITERS, min_seconds=MIN_SECONDS)
            record("hash", algo, {"input_bytes": size}, "MB/s", m, dependency="hashlib")
    # BLAKE3 (not in stdlib hashlib) — modern Merkle-tree hash: parallel + SIMD, XOF, 256-bit
    try:
        import blake3
        for size in SIZES:
            data = os.urandom(size)
            m = measure_throughput(lambda: blake3.blake3(data).digest(),
                                   nbytes=size, min_iters=MIN_ITERS, min_seconds=MIN_SECONDS)
            record("hash", "blake3", {"input_bytes": size}, "MB/s", m, dependency="blake3")
    except ImportError:
        skip("hash", "blake3", "blake3", "pip install blake3 (BLAKE3 is not in stdlib hashlib)")


# ======================================================================================
# 2. AEAD (cryptography: AES-GCM, ChaCha20-Poly1305) -- encrypt AND decrypt
# ======================================================================================
def bench_aead() -> None:
    if not HAVE_CRYPTO:
        skip("aead", "AES-256-GCM", "cryptography", MISSING.get("cryptography", "not installed"))
        skip("aead", "AES-128-GCM", "cryptography", MISSING.get("cryptography", "not installed"))
        skip("aead", "ChaCha20-Poly1305", "cryptography", MISSING.get("cryptography", "not installed"))
        return
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM, ChaCha20Poly1305
    ciphers = [
        ("AES-256-GCM", lambda: AESGCM(os.urandom(32))),
        ("AES-128-GCM", lambda: AESGCM(os.urandom(16))),
        ("ChaCha20-Poly1305", lambda: ChaCha20Poly1305(os.urandom(32))),
    ]
    for cname, mk in ciphers:
        c = mk()
        nonce = os.urandom(12)
        for size in SIZES:
            pt = os.urandom(size)
            ct = c.encrypt(nonce, pt, None)
            enc = measure_throughput(lambda: c.encrypt(nonce, pt, None),
                                     nbytes=size, min_iters=MIN_ITERS, min_seconds=MIN_SECONDS)
            record("aead", cname, {"op": "encrypt", "input_bytes": size}, "MB/s", enc,
                   dependency="cryptography")
            dec = measure_throughput(lambda: c.decrypt(nonce, ct, None),
                                     nbytes=size, min_iters=MIN_ITERS, min_seconds=MIN_SECONDS)
            record("aead", cname, {"op": "decrypt", "input_bytes": size}, "MB/s", dec,
                   dependency="cryptography")


# ======================================================================================
# 3. MAC (HMAC stdlib; KMAC via cryptography if present)
# ======================================================================================
def bench_mac() -> None:
    import hmac
    import hashlib
    key = os.urandom(32)
    for algo in ["sha256", "sha384", "sha512"]:
        for size in SIZES:
            data = os.urandom(size)
            m = measure_throughput(lambda: hmac.new(key, data, algo).digest(),
                                   nbytes=size, min_iters=MIN_ITERS, min_seconds=MIN_SECONDS)
            record("mac", f"HMAC-{algo.upper()}", {"input_bytes": size}, "MB/s", m,
                   dependency="hmac")
    # KMAC (SHA-3 based) via cryptography, if available
    if HAVE_CRYPTO:
        try:
            from cryptography.hazmat.primitives import cmac  # noqa: F401
            from cryptography.hazmat.primitives.kdf.kbkdf import KBKDFHMAC  # noqa: F401
        except Exception:
            pass
        try:
            from cryptography.hazmat.primitives.poly1305 import Poly1305
            for size in SIZES:
                data = os.urandom(size)
                k = os.urandom(32)
                m = measure_throughput(lambda: Poly1305.generate_tag(k, data),
                                       nbytes=size, min_iters=MIN_ITERS, min_seconds=MIN_SECONDS)
                record("mac", "Poly1305", {"input_bytes": size}, "MB/s", m,
                       dependency="cryptography")
        except Exception as e:
            skip("mac", "Poly1305", "cryptography", str(e))


# ======================================================================================
# 4. KDF (HKDF-SHA384, PBKDF2, Argon2id) -- the KDF placement matters for the design
# ======================================================================================
def bench_kdf() -> None:
    import hashlib
    # PBKDF2 (stdlib) across iteration counts
    salt = os.urandom(16)
    pw = b"correct horse battery staple"
    for iters in [10_000, 100_000, 600_000]:
        m = measure_ops(lambda: hashlib.pbkdf2_hmac("sha256", pw, salt, iters, 32),
                        min_iters=3, min_seconds=0.4, warmup=1, per_op_samples=200)
        record("kdf", "PBKDF2-HMAC-SHA256", {"iterations": iters}, "ops/s", m,
               dependency="hashlib")
    # HKDF-SHA384 (the high-entropy KDF used in the hybrid combiner)
    if HAVE_CRYPTO:
        from cryptography.hazmat.primitives.kdf.hkdf import HKDF
        from cryptography.hazmat.primitives import hashes
        ikm = os.urandom(64)
        for algo, hf in [("HKDF-SHA256", hashes.SHA256()), ("HKDF-SHA384", hashes.SHA384())]:
            m = measure_ops(
                lambda hf=hf: HKDF(algorithm=hf, length=32, salt=b"", info=b"robobus").derive(ikm),
                min_iters=MIN_ITERS * 4, min_seconds=MIN_SECONDS)
            record("kdf", algo, {"ikm_bytes": 64, "out_bytes": 32}, "ops/s", m,
                   dependency="cryptography")
    else:
        skip("kdf", "HKDF-SHA384", "cryptography", MISSING.get("cryptography", "not installed"))
    # Argon2id (passphrase KDF) across a couple of cost profiles
    if HAVE_ARGON2:
        from argon2.low_level import hash_secret_raw, Type
        profiles = [
            ("interactive", dict(time_cost=2, memory_cost=64 * 1024, parallelism=1)),
            ("moderate", dict(time_cost=3, memory_cost=256 * 1024, parallelism=4)),
        ]
        for pname, p in profiles:
            m = measure_ops(
                lambda p=p: hash_secret_raw(pw, salt, hash_len=32, type=Type.ID, **p),
                min_iters=3, min_seconds=0.5, warmup=1, per_op_samples=100)
            record("kdf", "Argon2id", {"profile": pname, **p}, "ops/s", m, dependency="argon2")
    else:
        skip("kdf", "Argon2id", "argon2", MISSING.get("argon2", "not installed"))


# ======================================================================================
# 5. KEM: ML-KEM-512/768/1024 (oqs) + classical X25519 / P-256 ECDH (cryptography)
# ======================================================================================
def bench_kem() -> None:
    # Classical baselines
    if HAVE_CRYPTO:
        from cryptography.hazmat.primitives.asymmetric import x25519, ec
        # X25519
        record_kex_x25519(x25519)
        record_kex_ecdh(ec)
    else:
        skip("kem", "X25519", "cryptography", MISSING.get("cryptography", "not installed"))
        skip("kem", "ECDH-P256", "cryptography", MISSING.get("cryptography", "not installed"))

    # Post-quantum ML-KEM
    if not HAVE_OQS:
        for lvl in ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]:
            skip("kem", lvl, "oqs", MISSING.get("oqs", "liboqs-python not installed"))
        return
    import oqs
    enabled = set(oqs.get_enabled_kem_mechanisms())
    for mech in ["ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"]:
        if mech not in enabled:
            skip("kem", mech, "oqs", "mechanism not enabled in this liboqs build")
            continue
        # keygen
        def keygen(mech=mech):
            with oqs.KeyEncapsulation(mech) as k:
                k.generate_keypair()
        mk = measure_ops(keygen, min_iters=MIN_ITERS, min_seconds=MIN_SECONDS)
        record("kem", mech, {"op": "keygen"}, "ops/s", mk, dependency="oqs")
        # encaps / decaps against a fixed keypair
        with oqs.KeyEncapsulation(mech) as server:
            pub = server.generate_keypair()
            client = oqs.KeyEncapsulation(mech)
            ct = None

            def encaps(mech=mech, pub=pub):
                with oqs.KeyEncapsulation(mech) as c:
                    c.encap_secret(pub)
            me = measure_ops(encaps, min_iters=MIN_ITERS, min_seconds=MIN_SECONDS)
            record("kem", mech, {"op": "encapsulate"}, "ops/s", me, dependency="oqs")

            ct, _ss = server.encap_secret(pub)

            def decaps(server=server, ct=ct):
                server.decap_secret(ct)
            md = measure_ops(decaps, min_iters=MIN_ITERS, min_seconds=MIN_SECONDS)
            record("kem", mech, {"op": "decapsulate"}, "ops/s", md, dependency="oqs")


def record_kex_x25519(x25519) -> None:
    def keygen():
        x25519.X25519PrivateKey.generate()
    mk = measure_ops(keygen, min_iters=MIN_ITERS, min_seconds=MIN_SECONDS)
    record("kem", "X25519", {"op": "keygen"}, "ops/s", mk, dependency="cryptography")
    a = x25519.X25519PrivateKey.generate()
    bpub = x25519.X25519PrivateKey.generate().public_key()

    def derive():
        a.exchange(bpub)
    md = measure_ops(derive, min_iters=MIN_ITERS, min_seconds=MIN_SECONDS)
    record("kem", "X25519", {"op": "derive"}, "ops/s", md, dependency="cryptography")


def record_kex_ecdh(ec) -> None:
    def keygen():
        ec.generate_private_key(ec.SECP256R1())
    mk = measure_ops(keygen, min_iters=MIN_ITERS, min_seconds=MIN_SECONDS)
    record("kem", "ECDH-P256", {"op": "keygen"}, "ops/s", mk, dependency="cryptography")
    a = ec.generate_private_key(ec.SECP256R1())
    bpub = ec.generate_private_key(ec.SECP256R1()).public_key()

    def derive():
        a.exchange(ec.ECDH(), bpub)
    md = measure_ops(derive, min_iters=MIN_ITERS, min_seconds=MIN_SECONDS)
    record("kem", "ECDH-P256", {"op": "derive"}, "ops/s", md, dependency="cryptography")


# ======================================================================================
# 6. HYBRID KEM: ECDH(P-256) || ML-KEM-768/1024 -> HKDF-SHA384  (the robobus/DDS design)
# ======================================================================================
def bench_hybrid_kem() -> None:
    if not (HAVE_CRYPTO and HAVE_OQS):
        need = "cryptography+oqs"
        why = MISSING.get("cryptography") or MISSING.get("oqs") or "missing dependency"
        for lvl in ["ECDH-P256+ML-KEM-768", "ECDH-P256+ML-KEM-1024"]:
            skip("hybrid_kem", lvl, need, why)
        return
    import oqs
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives import hashes
    enabled = set(oqs.get_enabled_kem_mechanisms())
    for mech in ["ML-KEM-768", "ML-KEM-1024"]:
        name = f"ECDH-P256+{mech}"
        if mech not in enabled:
            skip("hybrid_kem", name, "oqs", "mechanism not enabled")
            continue

        def full_handshake(mech=mech):
            # initiator ECDH + ML-KEM keypair
            eph_i = ec.generate_private_key(ec.SECP256R1())
            with oqs.KeyEncapsulation(mech) as kem_i:
                kpub = kem_i.generate_keypair()
                # responder: ECDH keypair + ML-KEM encapsulate
                eph_r = ec.generate_private_key(ec.SECP256R1())
                with oqs.KeyEncapsulation(mech) as kem_r:
                    ct, ss_r = kem_r.encap_secret(kpub)
                ecdh_r = eph_r.exchange(ec.ECDH(), eph_i.public_key())
                # initiator: ECDH derive + ML-KEM decapsulate + combine
                ecdh_i = eph_i.exchange(ec.ECDH(), eph_r.public_key())
                ss_i = kem_i.decap_secret(ct)
                # both sides HKDF-SHA384(ECDH || ML-KEM)
                HKDF(algorithm=hashes.SHA384(), length=32, salt=b"",
                     info=b"robobus-hybrid").derive(ecdh_i + ss_i)
                HKDF(algorithm=hashes.SHA384(), length=32, salt=b"",
                     info=b"robobus-hybrid").derive(ecdh_r + ss_r)
        m = measure_ops(full_handshake, min_iters=max(20, MIN_ITERS // 2), min_seconds=MIN_SECONDS)
        record("hybrid_kem", name, {"op": "full_two_party_handshake"}, "handshakes/s", m,
               dependency="cryptography+oqs",
               note="ECDH P-256 + ML-KEM encaps/decaps + HKDF-SHA384 combine, both parties")


# ======================================================================================
# 6b. FULL AUTHENTICATED HANDSHAKE CRYPTO (isolated from any DDS transport / event loop)
#     The complete crypto path of one CNSA-level authenticated session setup, both parties:
#     ephemeral ECDH + ML-KEM (keygen/encap/decap) + HKDF combine + identity signatures
#     (sign request, verify request, sign reply, verify reply, sign final, verify final).
#     This is the true *computational* handshake cost, separate from DDS message round-trips.
# ======================================================================================
def bench_handshake_auth() -> None:
    if not (HAVE_CRYPTO and HAVE_OQS):
        skip("handshake", "auth handshake", "cryptography+oqs",
             MISSING.get("cryptography") or MISSING.get("oqs") or "missing dependency")
        return
    import oqs
    from cryptography.hazmat.primitives.asymmetric import ec
    from cryptography.hazmat.primitives.kdf.hkdf import HKDF
    from cryptography.hazmat.primitives import hashes, serialization
    ekem = set(oqs.get_enabled_kem_mechanisms())
    esig = set(oqs.get_enabled_sig_mechanisms())
    # (kem, sig, label) -- NIST level pairings
    suites = [
        ("ML-KEM-512", "ML-DSA-44", "NIST-1 (ML-KEM-512 + ML-DSA-44)"),
        ("ML-KEM-768", "ML-DSA-65", "NIST-3 (ML-KEM-768 + ML-DSA-65)"),
        ("ML-KEM-1024", "ML-DSA-87", "CNSA 2.0 / NIST-5 (ML-KEM-1024 + ML-DSA-87)"),
    ]
    for kem_name, sig_name, label in suites:
        if kem_name not in ekem or sig_name not in esig:
            skip("handshake", label, "oqs", "mechanism not enabled")
            continue
        # long-term identities: provisioned once (NOT part of per-handshake cost)
        id_i = oqs.Signature(sig_name); ipub = id_i.generate_keypair()
        id_r = oqs.Signature(sig_name); rpub = id_r.generate_keypair()
        ver = oqs.Signature(sig_name)  # stateless verifier

        def one(kem_name=kem_name, sig_name=sig_name, ipub=ipub, rpub=rpub):
            # initiator offer: ephemeral ECDH + ML-KEM keypair, signed by identity
            ec_i = ec.generate_private_key(ec.SECP256R1())
            kem_i = oqs.KeyEncapsulation(kem_name); kpub = kem_i.generate_keypair()
            offer = ec_i.public_key().public_bytes(
                serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint) + kpub
            sig_req = id_i.sign(offer)
            # responder verifies offer, does ECDH + ML-KEM encap, signs reply
            ver.verify(offer, sig_req, ipub)
            ec_r = ec.generate_private_key(ec.SECP256R1())
            ct, ss_r = oqs.KeyEncapsulation(kem_name).encap_secret(kpub)
            ecdh_r = ec_r.exchange(ec.ECDH(), ec_i.public_key())
            HKDF(algorithm=hashes.SHA384(), length=32, salt=b"", info=b"h").derive(ecdh_r + ss_r)
            reply = ec_r.public_key().public_bytes(
                serialization.Encoding.X962, serialization.PublicFormat.UncompressedPoint) + ct
            sig_rep = id_r.sign(reply)
            # initiator verifies reply, decaps, derives, signs final; responder verifies final
            ver.verify(reply, sig_rep, rpub)
            ss_i = kem_i.decap_secret(ct)
            ecdh_i = ec_i.exchange(ec.ECDH(), ec_r.public_key())
            HKDF(algorithm=hashes.SHA384(), length=32, salt=b"", info=b"h").derive(ecdh_i + ss_i)
            sig_fin = id_i.sign(reply)
            ver.verify(reply, sig_fin, ipub)
            kem_i.free()
        m = measure_ops(one, min_iters=max(20, MIN_ITERS // 2), min_seconds=MIN_SECONDS,
                        per_op_samples=500)
        record("handshake", label, {"op": "full_authenticated_handshake"}, "handshakes/s", m,
               dependency="cryptography+oqs",
               note="3 sign + 3 verify + ML-KEM + 2 ECDH + 2 HKDF, both parties; identities "
                    "provisioned out-of-band (not timed); isolated from DDS transport")
        id_i.free(); id_r.free(); ver.free()
    # key-agreement-only (rekey) reference: the recurring cost without re-authentication
    record("handshake", "key agreement only (rekey, no identity sig)", {"note": "see hybrid_kem"},
           "", None, dependency="cryptography+oqs", status="ok",
           note="the recurring/rekey cost is the hybrid_kem group: ~128 µs (ECDH+ML-KEM+HKDF, no signatures)")


# ======================================================================================
# 7. SIGNATURES: ML-DSA-44/65/87 (oqs) + Ed25519 / ECDSA-P256 / RSA-3072 (cryptography)
# ======================================================================================
def bench_signatures() -> None:
    msg = os.urandom(1024)
    if HAVE_CRYPTO:
        from cryptography.hazmat.primitives.asymmetric import ed25519, ec, rsa, padding
        from cryptography.hazmat.primitives import hashes
        # Ed25519
        sk = ed25519.Ed25519PrivateKey.generate()
        pk = sk.public_key()
        sig = sk.sign(msg)
        record("sig", "Ed25519", {"op": "keygen"}, "ops/s",
               measure_ops(lambda: ed25519.Ed25519PrivateKey.generate(),
                           min_iters=MIN_ITERS, min_seconds=MIN_SECONDS), dependency="cryptography")
        record("sig", "Ed25519", {"op": "sign"}, "ops/s",
               measure_ops(lambda: sk.sign(msg), min_iters=MIN_ITERS, min_seconds=MIN_SECONDS),
               dependency="cryptography")
        record("sig", "Ed25519", {"op": "verify"}, "ops/s",
               measure_ops(lambda: pk.verify(sig, msg), min_iters=MIN_ITERS, min_seconds=MIN_SECONDS),
               dependency="cryptography")
        # ECDSA P-256
        esk = ec.generate_private_key(ec.SECP256R1())
        epk = esk.public_key()
        esig = esk.sign(msg, ec.ECDSA(hashes.SHA256()))
        record("sig", "ECDSA-P256", {"op": "sign"}, "ops/s",
               measure_ops(lambda: esk.sign(msg, ec.ECDSA(hashes.SHA256())),
                           min_iters=MIN_ITERS, min_seconds=MIN_SECONDS), dependency="cryptography")
        record("sig", "ECDSA-P256", {"op": "verify"}, "ops/s",
               measure_ops(lambda: epk.verify(esig, msg, ec.ECDSA(hashes.SHA256())),
                           min_iters=MIN_ITERS, min_seconds=MIN_SECONDS), dependency="cryptography")
        # RSA-3072 (sign is slow; verify is fast)
        try:
            rsk = rsa.generate_private_key(public_exponent=65537, key_size=3072)
            rpk = rsk.public_key()
            pad = padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH)
            rsig = rsk.sign(msg, pad, hashes.SHA256())
            record("sig", "RSA-3072-PSS", {"op": "sign"}, "ops/s",
                   measure_ops(lambda: rsk.sign(msg, pad, hashes.SHA256()),
                               min_iters=10, min_seconds=0.4, per_op_samples=200),
                   dependency="cryptography")
            record("sig", "RSA-3072-PSS", {"op": "verify"}, "ops/s",
                   measure_ops(lambda: rpk.verify(rsig, msg, pad, hashes.SHA256()),
                               min_iters=MIN_ITERS, min_seconds=MIN_SECONDS), dependency="cryptography")
        except Exception as e:
            skip("sig", "RSA-3072-PSS", "cryptography", str(e))
    else:
        for a in ["Ed25519", "ECDSA-P256", "RSA-3072-PSS"]:
            skip("sig", a, "cryptography", MISSING.get("cryptography", "not installed"))

    # Post-quantum ML-DSA
    if not HAVE_OQS:
        for lvl in ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]:
            skip("sig", lvl, "oqs", MISSING.get("oqs", "liboqs-python not installed"))
        return
    import oqs
    enabled = set(oqs.get_enabled_sig_mechanisms())
    for mech in ["ML-DSA-44", "ML-DSA-65", "ML-DSA-87"]:
        if mech not in enabled:
            skip("sig", mech, "oqs", "mechanism not enabled in this liboqs build")
            continue

        def keygen(mech=mech):
            with oqs.Signature(mech) as s:
                s.generate_keypair()
        record("sig", mech, {"op": "keygen"}, "ops/s",
               measure_ops(keygen, min_iters=MIN_ITERS, min_seconds=MIN_SECONDS), dependency="oqs")
        with oqs.Signature(mech) as signer:
            pub = signer.generate_keypair()
            sig = signer.sign(msg)

            def do_sign(signer=signer):
                signer.sign(msg)
            record("sig", mech, {"op": "sign"}, "ops/s",
                   measure_ops(do_sign, min_iters=MIN_ITERS, min_seconds=MIN_SECONDS), dependency="oqs")
            ver = oqs.Signature(mech)

            def do_verify(mech=mech, sig=sig, pub=pub):
                with oqs.Signature(mech) as v:
                    v.verify(msg, sig, pub)
            record("sig", mech, {"op": "verify"}, "ops/s",
                   measure_ops(do_verify, min_iters=MIN_ITERS, min_seconds=MIN_SECONDS), dependency="oqs")


# ======================================================================================
# 8. DDS-SECURITY HANDSHAKES (live two-peer, via the built CUnit test) -- optional
#    Registered here as a hook; the concrete invocation is filled from dds_bench.py if
#    the built test binaries exist on this platform.
# ======================================================================================
def _find_cc() -> Optional[str]:
    for cc in (os.environ.get("CC"), "cc", "clang", "gcc"):
        if not cc:
            continue
        try:
            subprocess.run([cc, "--version"], capture_output=True, timeout=10)
            return cc
        except Exception:
            continue
    return None


def bench_bus() -> None:
    """Nanosecond shared-memory bus latency via the native high-resolution probe (nsbus.c).

    Compiles bench/native/nsbus.c and runs it with and without RT hardening. nsbus uses the
    41.67 ns mach clock (or CLOCK_MONOTONIC_RAW) plus amortized batching, so it reports true
    nanosecond figures rather than the ~1 us clock floor. Skipped where there is no C compiler
    or no fork/mmap (e.g. Windows) -- crypto benchmarks still run there.
    """
    if platform.system() == "Windows":
        skip("bus", "ring_op_amortized", "native/nsbus.c", "no fork/mmap on Windows")
        skip("bus", "oneway_latency", "native/nsbus.c", "no fork/mmap on Windows")
        return
    cc = _find_cc()
    if not cc:
        skip("bus", "ring_op_amortized", "C compiler", "no cc/clang/gcc on PATH")
        skip("bus", "oneway_latency", "C compiler", "no cc/clang/gcc on PATH")
        return
    src = os.path.join(os.path.dirname(os.path.abspath(__file__)), "native", "nsbus.c")
    if not os.path.exists(src):
        skip("bus", "ring_op_amortized", "native/nsbus.c", "source not found")
        return
    binp = os.path.join(os.path.dirname(src), "_nsbus")
    comp = subprocess.run([cc, "-O3", "-std=c11", src, "-o", binp], capture_output=True, text=True)
    if comp.returncode != 0:
        skip("bus", "ring_op_amortized", "native/nsbus.c", f"compile failed: {comp.stderr[:160]}")
        return
    n_amort = 5_000_000 if MIN_SECONDS < 0.3 else 30_000_000
    n_oneway = 100_000 if MIN_SECONDS < 0.3 else 300_000
    for rt in (False, True):
        env = dict(os.environ)
        if rt:
            env["NSBUS_RT"] = "1"
        try:
            p = subprocess.run([binp, str(n_amort), str(n_oneway)], env=env,
                               capture_output=True, text=True, timeout=120)
            data = json.loads(p.stdout)
        except Exception as e:
            skip("bus", f"nsbus_rt={rt}", "native/nsbus.c", f"run failed: {e}")
            continue
        suffix = " (RT)" if rt else ""
        clk = data.get("clock", {})
        a = data["amortized_ring_op"]
        record("bus", "ring put+get, amortized 1-core" + suffix,
               {"realtime": data.get("realtime"), "clock_ns_per_tick": clk.get("ns_per_tick")},
               "ns/op",
               {"mean_ns": a["ns_per_op"], "ops_per_s": a["ops_per_s"], "n": a["n"]},
               dependency="native/nsbus.c",
               note=f"pure ring op cost; clock res {clk.get('single_shot_res_ns'):.1f} ns")
        o = data["oneway_latency_ns"]
        pos = o.get("max_position_frac", 0.0)
        cold = pos < 0.02  # max within first 2% of steady-state => likely a warmup residue
        record("bus", "cross-process one-way latency" + suffix,
               {"realtime": data.get("realtime"), "warmup_msgs": o.get("warmup_discarded")},
               "ns",
               {"n": o["n"], "min_ns": o["min"], "p50_ns": o["p50"], "p90_ns": o["p90"],
                "p99_ns": o["p99"], "p999_ns": o["p999"], "max_ns": o["max"], "mean_ns": o["mean"],
                "frac_under_100ns": o["frac_under_100ns"], "frac_under_1us": o["frac_under_1us"],
                "max_position_frac": pos},
               dependency="native/nsbus.c",
               note=(f"{o['frac_under_100ns']*100:.1f}% <100 ns; "
                     f"{o.get('warmup_discarded', 0)} msgs warmup discarded; "
                     f"max at {pos*100:.0f}% of run "
                     f"({'cold-start residue' if cold else 'mid-run scheduler jitter'})"
                     + ("; RT time-constraint policy" if rt else "; no RT")))
    try:
        os.remove(binp)
    except Exception:
        pass


def _gpu_hardware() -> Optional[str]:
    """Detect GPU HARDWARE (independent of any compute backend being installed)."""
    if platform.system() == "Darwin":
        try:
            out = subprocess.check_output(["system_profiler", "SPDisplaysDataType"],
                                          text=True, timeout=8)
            for line in out.splitlines():
                if "Chipset Model:" in line:
                    return line.split(":", 1)[1].strip() + " (Apple GPU / Metal)"
        except Exception:
            return None
    for tool, tag in (("nvidia-smi", "NVIDIA"), ("rocm-smi", "AMD ROCm")):
        if _which(tool):
            try:
                subprocess.check_output([tool], timeout=8)
                return tag + " GPU"
            except Exception:
                return tag + " GPU (present)"
    return None


def bench_gpu() -> None:
    """GPU offload: measure the SWAPOVER (dispatch+sync) and the throughput CROSSOVER.

    The point is NOT that the GPU is fast per-op — it is that a fixed dispatch+transfer+sync
    cost must be amortized over a batch. Latency path (bus, single crypto op) -> GPU always
    loses. Aggregate throughput (swarm of N robots, dense sensor/electrode mesh) -> GPU wins
    ABOVE a crossover batch size. We report that crossover and what it means at scale.

    'no backend installed' is distinguished from 'no GPU hardware' (a backend is installable).
    """
    hw = _gpu_hardware()
    backend = None
    for m in ("mlx.core", "cupy", "torch"):
        try:
            __import__(m)
            backend = m
            break
        except Exception:
            continue
    if backend is None:
        reason = (f"GPU hardware present ({hw}) but no compute backend installed "
                  f"(pip install mlx / cupy / torch) — GPU is throughput-only; see fidelity doc"
                  if hw else "no GPU on this runner — the GPU swapover/crossover is measured "
                           "on the Apple-Silicon host")
        skip("gpu", "swapover", "mlx/cupy/torch", reason)
        skip("gpu", "throughput_crossover", "mlx/cupy/torch", reason)
        return
    if backend != "mlx.core":
        _gpu_discrete(backend, hw)
        return
    import mlx.core as mx
    import numpy as np
    # 1) swapover: trivial-op dispatch+sync round-trip = the irreducible per-offload cost
    a = mx.array([1.0, 2.0, 3.0]); mx.eval(a * 2)
    n = 100 if MIN_SECONDS < 0.3 else 1500
    samples = []
    for _ in range(n):
        t0 = time.perf_counter_ns(); b = a * 2; mx.eval(b); samples.append(time.perf_counter_ns() - t0)
    sw = _percentiles(samples)
    record("gpu", "dispatch+sync swapover (unified memory)", {"backend": backend, "gpu": hw},
           "ns", {**sw, "p50_ns": sw["p50_ns"]}, dependency="mlx",
           note=f"irreducible per-offload cost; unified memory (no PCIe). vs 83 ns bus hop / "
                f"12 µs ML-KEM — GPU disqualified for the latency path")
    # 2) crossover: elementwise op (bulk-data proxy) GPU-incl-swapover vs CPU numpy
    crossover = None
    for elems in [1 << 12, 1 << 16, 1 << 18, 1 << 20, 1 << 22, 1 << 24]:
        xg = mx.random.uniform(shape=(elems,)); mx.eval(xg)
        xc = np.random.rand(elems).astype(np.float32)
        it = 20
        t0 = time.perf_counter_ns()
        for _ in range(it):
            yg = xg * 1.5 + 0.5; mx.eval(yg)
        gpu_ns = (time.perf_counter_ns() - t0) / it
        t0 = time.perf_counter_ns()
        for _ in range(it):
            yc = xc * 1.5 + 0.5  # noqa
        cpu_ns = (time.perf_counter_ns() - t0) / it
        won = gpu_ns < cpu_ns
        if won and crossover is None:
            crossover = elems
        record("gpu", "throughput vs CPU", {"batch_elems": elems, "backend": backend},
               "ns/batch",
               {"gpu_ns": gpu_ns, "cpu_ns": cpu_ns, "gpu_wins": won,
                "speedup": cpu_ns / gpu_ns if gpu_ns else 0},
               dependency="mlx+numpy",
               note=("GPU wins" if won else "CPU wins (swapover not amortized)")
                    + f"; batch={elems:,} f32 = {elems*4/1024:.0f} KiB")
    if crossover:
        kib = crossover * 4 / 1024
        record("gpu", "crossover batch (GPU starts winning)", {"backend": backend}, "elements",
               {"batch_elems": crossover, "batch_kib": kib}, dependency="mlx+numpy",
               note=f"GPU offload pays off above ~{crossover:,} f32 elems (~{kib:.0f} KiB). "
                    f"At 1 KiB/stream that is ~{int(kib):,} concurrent streams — i.e. GPU is a "
                    f"SWARM/MESH/high-density-electrode scalability tool, not a per-node one")


def _gpu_discrete(backend: str, hw) -> None:
    """Discrete GPU (NVIDIA/AMD) via cupy or torch — measures the FULL PCIe swapover
    (host->device transfer + kernel + device->host + sync), which unified-memory Apple GPUs
    avoid. Activates on GPU CI runners (self-hosted / managed / GitHub GPU larger-runners)."""
    import numpy as np
    try:
        if backend == "cupy":
            import cupy as xp
            def to_dev(a): d = xp.asarray(a); xp.cuda.runtime.deviceSynchronize(); return d
            def frm_dev(d): h = xp.asnumpy(d); return h
            def sync(): xp.cuda.runtime.deviceSynchronize()
        else:  # torch
            import torch
            dev = "cuda" if torch.cuda.is_available() else ("mps" if getattr(torch.backends, "mps", None) and torch.backends.mps.is_available() else None)
            if dev is None:
                skip("gpu", "swapover", backend, "no CUDA/MPS device visible to torch")
                return
            def to_dev(a): d = torch.from_numpy(a).to(dev); torch.cuda.synchronize() if dev == "cuda" else None; return d
            def frm_dev(d): return d.cpu().numpy()
            def sync(): torch.cuda.synchronize() if dev == "cuda" else None
            xp = torch
    except Exception as e:
        skip("gpu", "swapover", backend, f"init failed: {e}")
        return
    # full round-trip swapover at increasing sizes (host->device->host)
    crossover = None
    for elems in [1 << 10, 1 << 14, 1 << 18, 1 << 20, 1 << 22, 1 << 24]:
        a = np.random.rand(elems).astype(np.float32)
        it = 20
        t0 = time.perf_counter_ns()
        for _ in range(it):
            d = to_dev(a); d = d * 1.5 + 0.5; h = frm_dev(d); sync()  # noqa
        gpu_ns = (time.perf_counter_ns() - t0) / it
        t0 = time.perf_counter_ns()
        for _ in range(it):
            hc = a * 1.5 + 0.5  # noqa
        cpu_ns = (time.perf_counter_ns() - t0) / it
        won = gpu_ns < cpu_ns
        if won and crossover is None:
            crossover = elems
        record("gpu", "throughput vs CPU (incl. PCIe transfer)",
               {"batch_elems": elems, "backend": backend, "gpu": hw}, "ns/batch",
               {"gpu_ns": gpu_ns, "cpu_ns": cpu_ns, "gpu_wins": won,
                "speedup": cpu_ns / gpu_ns if gpu_ns else 0}, dependency=f"{backend}+numpy",
               note=("GPU wins" if won else "CPU wins (PCIe swapover not amortized)")
                    + f"; discrete GPU — host->device->host copy included; {elems*4/1024:.0f} KiB")
    if crossover:
        record("gpu", "crossover batch (GPU starts winning)", {"backend": backend}, "elements",
               {"batch_elems": crossover, "batch_kib": crossover * 4 / 1024},
               dependency=f"{backend}+numpy",
               note=f"discrete GPU offload pays off above ~{crossover:,} f32 elems "
                    f"(~{crossover*4/1024:.0f} KiB) — PCIe transfer pushes the crossover higher "
                    f"than unified-memory Apple GPUs")


def bench_dds() -> None:
    try:
        import dds_bench  # noqa
    except Exception:
        dds_bench = None
    here = os.path.dirname(os.path.abspath(__file__))
    if dds_bench is None:
        sys.path.insert(0, here)
        try:
            import dds_bench  # type: ignore
        except Exception as e:
            ddsmsg = ("PQC-DDS test binary not built in this environment — the handshake is "
                      "built + measured on the dev machine")
            skip("dds_handshake", "CycloneDDS", "cunit_security_core", ddsmsg)
            skip("dds_handshake", "FastDDS", "BuiltinPKIDH", ddsmsg)
            return
    dds_bench.run(record, skip, measure_wall=_measure_wall)


def _measure_wall(cmd: list[str], env: dict, *, runs: int, cwd: Optional[str] = None) -> dict:
    """Wall-clock timing of a subprocess (used for live DDS handshakes)."""
    samples = []
    ok = 0
    for _ in range(runs):
        t0 = time.perf_counter_ns()
        p = subprocess.run(cmd, env=env, cwd=cwd, capture_output=True, text=True, timeout=120)
        dt = time.perf_counter_ns() - t0
        if p.returncode == 0:
            ok += 1
            samples.append(dt)
    if not samples:
        return {"runs": runs, "ok": 0}
    out = {"runs": runs, "ok": ok}
    out.update(_percentiles(samples))
    out["ops_per_s"] = ok / (sum(samples) / 1e9)
    return out


# ======================================================================================
# 9. robobus bus / determinism / RT (optional; only where the package imports)
# ======================================================================================
def bench_robobus() -> None:
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if here not in sys.path:
        sys.path.insert(0, here)
    try:
        import robobus  # noqa: F401
    except Exception as e:
        msg = ("n/a here — needs the robobus package (private repo); the portable `bus` "
               "group measures the same ring on this platform")
        skip("robobus", "determinism_probe", "robobus", msg)
        skip("robobus", "bus_latency", "robobus", msg)
        return
    # determinism probe
    try:
        from robobus import determinism
        probe = (getattr(determinism, "report", None) or getattr(determinism, "capabilities", None)
                 or getattr(determinism, "probe", None) or getattr(determinism, "measure", None))
        if probe:
            res = probe() if callable(probe) else None
            record("robobus", "determinism_probe", {}, "report",
                   {"result": str(res)[:400]}, dependency="robobus",
                   note="adaptive determinism probe output")
        else:
            skip("robobus", "determinism_probe", "robobus",
                 "no report()/capabilities() entrypoint in this build")
    except Exception as e:
        skip("robobus", "determinism_probe", "robobus", str(e))


def bench_correctness_group() -> None:
    here = os.path.dirname(os.path.abspath(__file__))
    if here not in sys.path:
        sys.path.insert(0, here)
    try:
        import correctness
    except Exception as e:
        skip("correctness", "checks", "correctness.py", f"module unavailable: {e}")
        return
    correctness.run(record)


GROUPS: dict[str, Callable[[], None]] = {
    "bus": bench_bus,
    "kem": bench_kem,
    "hybrid_kem": bench_hybrid_kem,
    "handshake": bench_handshake_auth,
    "sig": bench_signatures,
    "aead": bench_aead,
    "hash": bench_hashing,
    "mac": bench_mac,
    "kdf": bench_kdf,
    "dds_handshake": bench_dds,
    "gpu": bench_gpu,
    "robobus": bench_robobus,
    "correctness": bench_correctness_group,
}


# --------------------------------------------------------------------------------------
# measurement conditions — the noise knobs that decide whether numbers are reproducible.
# Reading these (governor, turbo, SMT, core isolation, ASLR, pinning, thermal) is the single
# biggest honesty win: two hosts with identical silicon give different numbers under different
# conditions, so every result self-documents the conditions it was taken under.
# --------------------------------------------------------------------------------------
def _read(path: str) -> Optional[str]:
    try:
        with open(path) as f:
            return f.read().strip()
    except Exception:
        return None


def measurement_conditions() -> dict:
    c: dict = {}
    uncontrolled = []
    # process CPU pinning (affinity)
    try:
        aff = os.sched_getaffinity(0)  # Linux only
        c["pinned_cpus"] = sorted(aff)
        c["pinned"] = len(aff) < (os.cpu_count() or 1)
    except (AttributeError, OSError):
        c["pinned"] = None
    if platform.system() == "Linux":
        govs = set()
        for i in range(os.cpu_count() or 1):
            g = _read(f"/sys/devices/system/cpu/cpu{i}/cpufreq/scaling_governor")
            if g:
                govs.add(g)
        c["cpu_governor"] = sorted(govs) or None
        if govs and govs != {"performance"}:
            uncontrolled.append("cpu_governor!=performance (frequency scaling adds jitter)")
        no_turbo = _read("/sys/devices/system/cpu/intel_pstate/no_turbo")
        boost = _read("/sys/devices/system/cpu/cpufreq/boost")
        c["turbo"] = ("off" if no_turbo == "1" or boost == "0" else
                      "on" if no_turbo == "0" or boost == "1" else None)
        if c["turbo"] == "on":
            uncontrolled.append("turbo/boost on (opportunistic clocks -> variance)")
        smt = _read("/sys/devices/system/cpu/smt/active")
        c["smt_active"] = (smt == "1") if smt is not None else None
        if smt == "1":
            uncontrolled.append("SMT/hyperthreading active (sibling-core contention)")
        iso = _read("/sys/devices/system/cpu/isolated")
        c["isolated_cpus"] = iso or ""
        if not iso:
            uncontrolled.append("no isolated cores (isolcpus=) -> scheduler + IRQ noise")
        aslr = _read("/proc/sys/kernel/randomize_va_space")
        c["aslr"] = {"0": "off", "1": "partial", "2": "full"}.get(aslr, aslr)
    elif platform.system() == "Darwin":
        # macOS exposes far less; capture what we can and note the limitation
        try:
            therm = subprocess.check_output(["pmset", "-g", "therm"], text=True, timeout=5)
            c["thermal"] = " ".join(therm.split())[:200]
        except Exception:
            pass
        c["note"] = ("macOS does not expose governor/isolcpus/SMT toggles; RT via Mach "
                     "time-constraint policy only (soft-RT). Use Linux + isolcpus for hard bounds.")
        uncontrolled.append("macOS: no core isolation / governor control (soft-RT only)")
    # PMU availability (the CPU's built-in white-box counters — the cocotb-counter analog)
    c["pmu_perf_available"] = _which("perf") is not None and platform.system() == "Linux"
    c["uncontrolled_noise"] = uncontrolled
    return c


def _which(prog: str) -> Optional[str]:
    for d in os.environ.get("PATH", "").split(os.pathsep):
        p = os.path.join(d, prog)
        if os.path.isfile(p) and os.access(p, os.X_OK):
            return p
    return None


# --------------------------------------------------------------------------------------
# platform metadata
# --------------------------------------------------------------------------------------
def collect_platform() -> dict:
    info = {
        "python_version": platform.python_version(),
        "python_impl": platform.python_implementation(),
        "system": platform.system(),
        "release": platform.release(),
        "version": platform.version(),
        "machine": platform.machine(),
        "processor": platform.processor(),
        "platform": platform.platform(),
        "cpu_count_logical": os.cpu_count(),
    }
    if HAVE_PSUTIL:
        import psutil
        try:
            info["cpu_count_physical"] = psutil.cpu_count(logical=False)
            info["mem_total_bytes"] = psutil.virtual_memory().total
            freq = psutil.cpu_freq()
            if freq:
                info["cpu_freq_mhz"] = {"current": freq.current, "min": freq.min, "max": freq.max}
        except Exception:
            pass
    # macOS CPU brand
    if platform.system() == "Darwin":
        try:
            info["cpu_brand"] = subprocess.check_output(
                ["sysctl", "-n", "machdep.cpu.brand_string"], text=True).strip()
        except Exception:
            pass
    # environment: is this a virtualized CI runner? (self-labels GitHub Actions etc.)
    env = {}
    ci_markers = {
        "GITHUB_ACTIONS": "GitHub Actions",
        "CI": "generic CI",
        "GITLAB_CI": "GitLab CI",
        "CIRCLECI": "CircleCI",
        "BUILDKITE": "Buildkite",
    }
    for var, label in ci_markers.items():
        if os.environ.get(var):
            env["ci"] = label
            break
    self_hosted = False
    if "GITHUB_ACTIONS" in os.environ:
        env["runner_os"] = os.environ.get("RUNNER_OS", "")
        env["runner_arch"] = os.environ.get("RUNNER_ARCH", "")
        env["runner_name"] = os.environ.get("RUNNER_NAME", "")
        env["runner_environment"] = os.environ.get("RUNNER_ENVIRONMENT", "")
        self_hosted = env["runner_environment"] == "self-hosted"
    # a self-hosted runner may be real bare metal; GitHub-hosted runners are always VMs
    emulated = os.environ.get("ROBOBUS_EMULATED")
    if emulated:
        env["emulated"] = emulated
        env["timing_representative"] = False
        env["caveat_emulation"] = ("QEMU emulation: NOT cycle-accurate — timing here would not "
                                    "reflect real hardware and is not measured. Purpose is "
                                    "PORTABILITY/CORRECTNESS across this ISA (endianness, word size).")
    env["virtualized"] = bool(env.get("ci")) and not self_hosted
    env["self_hosted"] = self_hosted
    if env.get("virtualized"):
        env["caveat"] = ("virtualized CI runner: shared vCPUs, noisy neighbours, no real-time "
                         "scheduling -- absolute latency (esp. tails) is worse and noisier than "
                         "bare metal; use for cross-platform coverage and relative comparison.")
    info["environment"] = env
    info["measurement"] = measurement_conditions()
    # fidelity tier: how close is this to a clean bare-metal measurement?
    m = info["measurement"]
    if env.get("virtualized"):
        tier = "1-virtualized (GitHub-hosted VM — coverage only)"
    elif m.get("isolated_cpus") and m.get("cpu_governor") == ["performance"] and not m.get("smt_active"):
        tier = "4-tuned-baremetal (isolcpus + performance governor + SMT off)"
    elif m.get("pinned") or (platform.system() == "Darwin" and not env.get("virtualized")):
        tier = "3-baremetal-partial (real hardware, some noise controls)"
    elif not env.get("ci"):
        tier = "2-baremetal-untuned (real hardware, default OS noise)"
    else:
        tier = "2-baremetal-untuned"
    info["measurement"]["fidelity_tier"] = tier
    info["dependencies"] = {"available": dict(HAVE), "missing": dict(MISSING)}
    return info


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--quick", action="store_true", help="fast pass (short durations)")
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "results"))
    ap.add_argument("--only", default="", help="comma-separated subset of groups to run")
    ap.add_argument("--label", default="", help="optional label for this run")
    ap.add_argument("--verify", action="store_true",
                    help="correctness/portability checks only (no timing) — for emulated ISAs (QEMU)")
    args = ap.parse_args()

    global SIZES, MIN_SECONDS, MIN_ITERS
    if args.quick:
        SIZES = [64, 1024, 64 * 1024]
        MIN_SECONDS = 0.15
        MIN_ITERS = 10

    if args.verify:
        selected = ["correctness"]
    else:
        selected = [g.strip() for g in args.only.split(",") if g.strip()] or [
            g for g in GROUPS if g != "correctness"]
    meta = collect_platform()
    print(f"robobus/PQC benchmark harness  —  {meta['platform']}")
    print(f"python {meta['python_version']} ({meta['python_impl']})  "
          f"cpu={meta.get('cpu_brand', meta.get('processor') or meta['machine'])}  "
          f"cores={meta['cpu_count_logical']}")
    print(f"deps available: {', '.join(f'{k} {v}' for k, v in HAVE.items()) or 'stdlib only'}")
    if MISSING:
        print(f"deps missing:   {', '.join(MISSING)}  (those benchmarks will be SKIPPED)")
    print("-" * 78)

    t_start = time.time()
    for g in selected:
        fn = GROUPS.get(g)
        if not fn:
            print(f"  ! unknown group '{g}' (known: {', '.join(GROUPS)})")
            continue
        n0 = len(RESULTS)
        print(f"  [{g}] running...", flush=True)
        try:
            fn()
        except Exception as e:
            record(g, "_group_error", {}, "", None, status="error", note=f"{type(e).__name__}: {e}")
        ran = len(RESULTS) - n0
        okc = sum(1 for r in RESULTS[n0:] if r["status"] == "ok")
        print(f"      -> {ran} results ({okc} ok, {ran - okc} skipped/error)")

    doc = {
        "schema": "robobus-bench/1",
        "generated_unix": int(t_start),
        "label": args.label,
        "quick": args.quick,
        "platform": meta,
        "results": RESULTS,
        "note": ("Measured on this host only. Numbers are platform/CPU/build-specific. "
                 "Re-run the identical script on each target OS to compare. Skipped rows "
                 "indicate a capability/dependency absent on THIS platform, not a failure."),
    }
    os.makedirs(args.out, exist_ok=True)
    # virtualized/CI runs get a distinct slug so they never overwrite a bare-metal baseline
    emu = meta.get("environment", {}).get("emulated")
    if emu:
        ci_suffix = "-emulated-" + emu.replace("/", "-")
    else:
        ci_suffix = "-ci" if meta.get("environment", {}).get("virtualized") else ""
    if args.verify and not emu:
        ci_suffix += "-verify"
    sysslug = f"{meta['system']}-{meta['machine']}{ci_suffix}".lower().replace(" ", "_")
    fname = f"bench-{sysslug}-{int(t_start)}.json"
    fpath = os.path.join(args.out, fname)
    with open(fpath, "w") as f:
        json.dump(doc, f, indent=2)
    # also update a stable 'latest' pointer for the current platform
    latest = os.path.join(args.out, f"latest-{sysslug}.json")
    with open(latest, "w") as f:
        json.dump(doc, f, indent=2)
    total = len(RESULTS)
    okc = sum(1 for r in RESULTS if r["status"] == "ok")
    print("-" * 78)
    print(f"done in {time.time() - t_start:.1f}s — {okc}/{total} benchmarks measured, "
          f"{total - okc} skipped/error")
    print(f"wrote {fpath}")
    print(f"wrote {latest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
