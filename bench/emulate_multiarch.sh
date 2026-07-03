#!/usr/bin/env bash
# QEMU multi-arch PORTABILITY / CORRECTNESS verification (NOT timing).
#
# Runs `bench/run_benchmarks.py --verify` inside emulated-ISA containers (Docker + QEMU binfmt).
# Purpose: prove the crypto + wire code COMPUTES CORRECTLY across architectures (endianness, word
# size, alignment) — especially big-endian s390x. Timing under QEMU is NOT cycle-accurate and would
# not reflect real hardware, so it is deliberately not measured here.
#
# Usage: bench/emulate_multiarch.sh [linux/arm64 linux/riscv64 linux/s390x ...]
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PLATFORMS="${*:-linux/arm64 linux/riscv64 linux/ppc64le linux/s390x linux/arm/v7 linux/386}"
for plat in $PLATFORMS; do
  echo "==================== $plat ===================="
  docker run --rm --platform "$plat" -e ROBOBUS_EMULATED="$plat" \
    -v "$ROOT/bench:/w/bench" -w /w python:3.12-slim sh -c '
      pip install --quiet --only-binary :all: cryptography 2>/dev/null || true
      python bench/run_benchmarks.py --verify --out /w/bench/results --label "emulated $ROBOBUS_EMULATED"
    ' 2>&1 | grep -vE "pip|WARNING|notice" | tail -4
done
