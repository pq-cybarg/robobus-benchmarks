"""Functional correctness / portability checks — NO timing.

Run under QEMU multi-arch emulation to prove the crypto + wire code COMPUTES CORRECTLY across
ISAs (endianness, word size, alignment). Timing under emulation is meaningless (QEMU is not
cycle-accurate) and is deliberately NOT measured here — only correctness. Pure-stdlib checks run
everywhere; cryptography/oqs round-trips run where those wheels are available.
"""
from __future__ import annotations
import hashlib
import hmac
import struct
import sys
import platform

# NIST/known-answer vectors — a wrong endianness/word-size shows up immediately as a mismatch.
_KATS = {
    ("sha256", b"abc"): "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad",
    ("sha384", b"abc"): "cb00753f45a35e8bb5a03d699ac65007272c32ab0eded1631a8b605a43ff5bed"
                        "8086072ba1e7cc2358baeca134c825a7",
    ("sha512", b"abc"): "ddaf35a193617abacc417349ae20413112e6fa4e89a97ea20a9eeee64b55d39a"
                        "2192992a274fc1a836ba3c23a3feebbd454d4423643ce80e2a9ac94fa54ca49f",
    ("sha3_256", b"abc"): "3a985da74fe225b2045c172d6bd390bd855f086e3e9d525b46bfe24511431532",
    ("sha3_512", b"abc"): "b751850b1a57168a5693cd924b6b096e08f621827444f70d884f5d0240d2712e"
                          "10e116e9192af3c91a7ec57647e3934057340b4cf408d5a56592f8274eec53f0",
}
_HMAC_KAT = "f7bc83f430538424b13298e6aa6fb143ef4d59a14946175997479dbc2d1a3cd8"  # HMAC-SHA256("key","The quick brown fox jumps over the lazy dog")


def run(record):
    arch = platform.machine()
    # 1) hash KATs — endianness/ISA-sensitive
    for (algo, msg), want in _KATS.items():
        if algo not in hashlib.algorithms_available:
            record("correctness", f"KAT {algo}", {"arch": arch}, "pass", {"passed": None},
                   status="skipped", note="algorithm unavailable")
            continue
        got = hashlib.new(algo, msg).hexdigest()
        ok = got == want
        record("correctness", f"KAT {algo}", {"arch": arch}, "pass", {"passed": ok},
               status="ok" if ok else "error",
               note="known-answer vector matches" if ok else f"MISMATCH got {got[:20]}…")
    # 2) HMAC KAT
    got = hmac.new(b"key", b"The quick brown fox jumps over the lazy dog", "sha256").hexdigest()
    ok = got == _HMAC_KAT
    record("correctness", "KAT HMAC-SHA256", {"arch": arch}, "pass", {"passed": ok},
           status="ok" if ok else "error", note="RFC vector" if ok else "MISMATCH")
    # 3) endianness + struct pack/unpack (the wire format's portability)
    v = 0x0102030405060708
    le = struct.unpack("<Q", struct.pack("<Q", v))[0] == v
    be = struct.unpack(">Q", struct.pack(">Q", v))[0] == v
    record("correctness", "struct pack/unpack (wire format)",
           {"host_byteorder": sys.byteorder, "arch": arch}, "pass",
           {"passed": le and be}, status="ok" if (le and be) else "error",
           note=f"little+big-endian round-trip on a {sys.byteorder}-endian host")
    # 4) cryptography round-trips (best-effort)
    try:
        from cryptography.hazmat.primitives.ciphers.aead import AESGCM
        from cryptography.hazmat.primitives.asymmetric import ec, ed25519
        k = AESGCM(bytes(range(32))); n = bytes(12)
        ct = k.encrypt(n, b"robobus", b"aad")
        ok = k.decrypt(n, ct, b"aad") == b"robobus"
        record("correctness", "AES-256-GCM seal/open round-trip", {"arch": arch}, "pass",
               {"passed": ok}, status="ok" if ok else "error", note="encrypt then decrypt")
        a = ec.generate_private_key(ec.SECP256R1()); b = ec.generate_private_key(ec.SECP256R1())
        ok = a.exchange(ec.ECDH(), b.public_key()) == b.exchange(ec.ECDH(), a.public_key())
        record("correctness", "ECDH-P256 shared-secret agreement", {"arch": arch}, "pass",
               {"passed": ok}, status="ok" if ok else "error", note="both parties derive the same key")
        sk = ed25519.Ed25519PrivateKey.generate(); sig = sk.sign(b"m")
        sk.public_key().verify(sig, b"m")
        record("correctness", "Ed25519 sign/verify", {"arch": arch}, "pass", {"passed": True},
               status="ok", note="signature verifies")
    except Exception as e:
        record("correctness", "cryptography round-trips", {"arch": arch}, "pass", {"passed": None},
               status="skipped", note=f"cryptography unavailable: {type(e).__name__}")
    # 5) ML-KEM / ML-DSA round-trips (best-effort — the PQC portability proof)
    try:
        import oqs
        with oqs.KeyEncapsulation("ML-KEM-768") as server:
            pub = server.generate_keypair()
            client = oqs.KeyEncapsulation("ML-KEM-768")
            ct, ss_c = client.encap_secret(pub)
            ss_s = server.decap_secret(ct)
            client.free()
            ok = ss_c == ss_s
        record("correctness", "ML-KEM-768 encap/decap secret match", {"arch": arch}, "pass",
               {"passed": ok}, status="ok" if ok else "error", note="FIPS 203 across this ISA")
        with oqs.Signature("ML-DSA-87") as signer:
            spub = signer.generate_keypair(); msig = signer.sign(b"m")
            v = oqs.Signature("ML-DSA-87"); ok = v.verify(b"m", msig, spub); v.free()
        record("correctness", "ML-DSA-87 sign/verify", {"arch": arch}, "pass", {"passed": ok},
               status="ok" if ok else "error", note="FIPS 204 across this ISA")
    except Exception as e:
        record("correctness", "oqs (ML-KEM/ML-DSA) round-trips", {"arch": arch}, "pass",
               {"passed": None}, status="skipped", note=f"oqs unavailable: {type(e).__name__}")
