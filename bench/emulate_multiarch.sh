#!/usr/bin/env bash
# QEMU multi-arch PORTABILITY / CORRECTNESS verification (NOT timing).
#
# Runs `bench/run_benchmarks.py --verify` inside emulated-ISA containers (Docker + QEMU binfmt) to
# prove the crypto + wire code COMPUTES CORRECTLY across architectures (endianness, word size,
# alignment) — especially big-endian s390x. Timing under QEMU is NOT cycle-accurate and would not
# reflect real hardware, so it is deliberately not measured here.
#
# Backends: we use Debian's PREBUILT python3-cryptography (built by Debian for every release arch —
# s390x, ppc64el, arm64, armhf, riscv64, i386), so AES-GCM / ECDH / Ed25519 actually RUN on each
# ISA instead of skipping. (pip's cryptography has wheels only for arm64/x86, so on exotic arches it
# tried a Rust source build and failed — that was the earlier skip.) The PQC backend liboqs is not
# Debian-packaged; set BUILD_OQS=1 to build it (fast on native arm64, slow under emulation). It is
# bounded by OQS_BUILD_TIMEOUT so a slow build can never block the verify run itself.
#
# Usage: bench/emulate_multiarch.sh [linux/arm64 linux/riscv64 linux/s390x linux/ppc64le ...]
#   BUILD_OQS=1 bench/emulate_multiarch.sh linux/arm64      # also run ML-KEM/ML-DSA round-trips
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLATFORMS="${*:-linux/arm64 linux/riscv64 linux/ppc64le linux/s390x linux/arm/v7 linux/386}"
BUILD_OQS="${BUILD_OQS:-0}"
OQS_BUILD_TIMEOUT="${OQS_BUILD_TIMEOUT:-1200}"
for plat in $PLATFORMS; do
  echo "==================== $plat  (BUILD_OQS=$BUILD_OQS) ===================="
  docker run --rm --platform "$plat" \
    -e ROBOBUS_EMULATED="$plat" -e BUILD_OQS="$BUILD_OQS" -e OQS_BUILD_TIMEOUT="$OQS_BUILD_TIMEOUT" \
    -v "$ROOT/bench:/w/bench" -w /w debian:trixie-slim bash -c '
      export DEBIAN_FRONTEND=noninteractive
      apt-get update -qq >/dev/null 2>&1
      # prebuilt AEAD/ECDH/Ed25519 for THIS arch — no compiler needed
      apt-get install -y -qq python3 python3-cryptography >/dev/null 2>&1
      # optional PQC backend (liboqs / oqs) — best-effort, bounded so it never blocks verify
      if [ "$BUILD_OQS" = "1" ]; then
        apt-get install -y -qq python3-pip cmake ninja-build gcc git python3-dev libssl-dev >/dev/null 2>&1
        timeout "$OQS_BUILD_TIMEOUT" pip install --quiet --break-system-packages liboqs-python >/dev/null 2>&1 || true
      fi
      python3 bench/run_benchmarks.py --verify --out /w/bench/results --label "emulated $ROBOBUS_EMULATED"
    ' 2>&1 | grep -vE "^(Requirement|Collecting|Downloading|Installing|Using|Preparing|Unpacking|Setting|Selecting|Get:|Fetched|Reading|Building|  )" | tail -8
done
