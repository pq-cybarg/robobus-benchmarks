# robobus wire protocol (language-agnostic)

Everything on the bus is bytes in a fixed, documented layout, so the bus is **not
Python-specific**. The Python core and the C poller (`native/shm_bench.c`) already
interoperate over the *same* ring file, any language with mmap + integer/byte ops can
join. All integers are **little-endian** unless noted.

## 1. Ring file (shared-memory channel)

One mmap'd file per channel: `<dir>/<channel>.ring` where `<dir>` is `/dev/shm/robobus`
(Linux), `$TMPDIR/robobus` (macOS), `%TEMP%\robobus` (Windows), or `$ROBOBUS_DIR`.

```
Header (64 bytes):
  off 0   8s   magic        "ROBOBUS\x01"
  off 8   u32  version      1
  off 12  u32  slot_size    bytes per slot (incl. 12-byte slot header)
  off 16  u32  n_slots
  off 20  u32  flags        (reserved, 0)
  off 24  u64  cursor       highest published sequence (0 = empty)
  off 32  u64  created_ns
  off 40  u64  writer_pid
  off 48  16   reserved

Slot i  (at off = 64 + i*slot_size):
  off 0   u64  seq          sequence number this slot holds
  off 8   u32  length       payload length
  off 12  ..   payload      (length bytes; capacity = slot_size - 12)
```

**Writer (single producer):** `seq = cursor + 1`; `slot = (seq-1) % n_slots`; write
`length` + `payload`; publish by storing `seq` into the slot, then storing `cursor = seq`
(in that order; use a release barrier in compiled languages).

**Reader (any number):** track your own `next` (start at `cursor+1` for live, or
`max(1, cursor-n_slots+1)` for oldest). If `cursor >= next`: if `cursor-next >= n_slots`
you were lapped (skip ahead, count drops); read slot for `next`, copy payload, re-read
`seq`, if it changed, the writer lapped you mid-copy: retry/skip (seqlock). See
`robobus/shm_ring.py` and `native/shm_bench.c` for two reference implementations.

## 2. Codec frame (the slot payload, plaintext)

```
  off 0   u8   type         1=float64[] 2=int32[] 3=utf8 str 4=utf8 JSON 5=bytes 6=schema
  off 1   u64  stamp_ns     sender time.monotonic_ns (host-wide clock)
  off 9   ..   body         type 1: float64*, 2: int32*, 3/4: utf-8, 5: bytes,
                            6: schema_id(u32) + packed fixed-layout struct
```

**Typed/schema frames (type 6)** carry a fixed, packed, little-endian struct plus a
4-byte schema id for validation (`robobus.schema.Schema`). Because the layout is fixed,
a field can be read at its offset without unpacking the whole message, and
`Schema.c_struct()` emits the matching `#pragma pack(1)` C struct, a C/Rust program can
`fread` the body directly. This is verified in `tests/test_schema.py` (a compiled C
program reads Python's packed bytes).

`stamp_ns` lets any reader compute one-way latency against its own monotonic clock.

## 3. Crypto frame (when a security suite is set; wraps the codec frame)

The codec frame is AEAD-sealed, then the sealed bytes become the slot payload:

```
  off 0   4s   magic        "RBX1"
  off 4   u8   alg          1=AES-256-GCM  2=ChaCha20-Poly1305
  off 5   u8   flags        (reserved, 0)
  off 6   12   nonce        random 96-bit
  off 18  ..   ciphertext + 16-byte GCM/Poly1305 tag
```

The 18-byte header is the AEAD **associated data** (authenticated, so alg/nonce can't be
altered). For CSfC (`layers=2`) the frame is sealed twice under two HKDF-derived keys
(inner first). Session keys come from the KEM handshake (§4) or a pre-shared 32-byte key.

## 4. Handshake (out-of-band, for key agreement)

A responder publishes `{suite, kem_pub, token, identity_pub}` where `token = Sign_idpriv
(kem_pub)`. The initiator verifies `token` against a trusted `identity_pub`, runs
`KEM.encapsulate(kem_pub) -> (ct, ss)`, and both sides derive
`session_key = HKDF(hash, ss, salt=H(kem_pub||ct), info="robobus-session")`. Algorithms
per suite (see `robobus/crypto/suites.py`); ML-KEM/ML-DSA byte sizes are the FIPS 203/204
standard sizes. This layer is transport-agnostic, exchange the bytes over any channel.

## 5. Implementing a binding

Minimum to join the bus from another language:
1. mmap the ring file; implement the §1 reader/writer (the hard part is the seqlock, copy
   the reference logic exactly).
2. Implement §2 encode/decode (trivial: a type byte, a u64, and an array/string/bytes).
3. (Optional) §3 with the platform AEAD (every crypto lib has AES-256-GCM) for encryption,
   and §4 with a PQC lib (liboqs has C/C++/Rust/Go/Java/Python bindings) for key agreement.

Reference C code: `native/shm_bench.c` (ring reader/writer) and `native/conformance.c`
(codec parser + AES-256-GCM open). **Cross-language interop is tested**:
`tests/test_conformance.py` has the compiled C program parse Python's plaintext codec
frames and decrypt Python's AES-256-GCM frames, byte-for-byte. Rust/C++/JS bindings are
on the roadmap ([ROADMAP.md](ROADMAP.md)).
