"""
DDS-Security live handshake benchmarks (Fast DDS + CycloneDDS).

IMPORTANT — measure the handshake, not the process. A naive wall-clock of the test binary is
~100 ms, but that is dominated by process startup (dynamic-linking libdds+liboqs+openssl), DDS
participant creation, and SPDP *discovery* timers (the periodic re-announce) plus teardown — none
of which is the handshake. CycloneDDS logs each security FSM transition with microsecond
timestamps, so we parse them and report the ISOLATED handshake window:

    first "begin handshake"  ->  last "final result ... OK / OK_FINAL_MESSAGE"

which excludes startup/discovery/teardown. We report that distribution across runs, and keep the
full-process wall-clock separately, clearly labelled. The *pure cryptographic* handshake cost
(ECDH+ML-KEM+HKDF, no DDS serialization/transport) is the `hybrid_kem` group.

Binaries are platform-local build artifacts; absent -> every row SKIPPED with a reason.
"""
from __future__ import annotations

import os
import re
import subprocess
import time

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ENV_LIB = os.environ.get("ROBOBUS_ENV_LIB",
                         os.path.expanduser("~/robotics-stack/mf/envs/ros2_kilted/lib"))
OQS_LIB = os.path.expanduser("~/_oqs/lib")

_TS = re.compile(r"^(\d{10}\.\d+)\s")
_BEGIN = re.compile(r"handle begin handshake|begin_handshake", re.I)
_FINAL = re.compile(r"final result.*(OK|OK_FINAL_MESSAGE)", re.I)


def _dyld(extra):
    parts = [p for p in extra if p and os.path.isdir(p)]
    parts += [ENV_LIB, OQS_LIB]
    key = "DYLD_LIBRARY_PATH" if os.uname().sysname == "Darwin" else "LD_LIBRARY_PATH"
    env = dict(os.environ)
    env[key] = ":".join(parts + ([env[key]] if env.get(key) else []))
    return env


def _percentiles(ns):
    s = sorted(ns)
    n = len(s)
    if n == 0:
        return {}

    def pct(p):
        if n == 1:
            return float(s[0])
        k = (n - 1) * p
        lo = int(k)
        hi = min(lo + 1, n - 1)
        return s[lo] + (s[hi] - s[lo]) * (k - lo)
    import statistics
    return {"n": n, "min_ns": s[0], "p50_ns": pct(.5), "p90_ns": pct(.9), "p99_ns": pct(.99),
            "max_ns": s[-1], "mean_ns": statistics.fmean(s)}


def _handshake_window_ns(stdout: str):
    """Isolated handshake latency = last OK-final timestamp - first begin-handshake timestamp."""
    begin = None
    last_final = None
    for line in stdout.splitlines():
        m = _TS.match(line)
        if not m:
            continue
        t = float(m.group(1))
        if _BEGIN.search(line) and begin is None:
            begin = t
        if _FINAL.search(line):
            last_final = t
    if begin is None or last_final is None or last_final < begin:
        return None
    return (last_final - begin) * 1e9


def _run_configs(record, skip, exe, cwd, env_base, configs, group_dep):
    for name, cmd_extra, env_extra in configs:
        hs_samples = []
        wall_samples = []
        ok = 0
        for _ in range(20):
            env = dict(env_base)
            env.update(env_extra)
            t0 = time.perf_counter_ns()
            try:
                p = subprocess.run(exe + cmd_extra, env=env, cwd=cwd,
                                   capture_output=True, text=True, timeout=120)
            except Exception:
                continue
            wall = time.perf_counter_ns() - t0
            if p.returncode != 0:
                continue
            ok += 1
            wall_samples.append(wall)
            hs = _handshake_window_ns(p.stdout + p.stderr)
            if hs is not None:
                hs_samples.append(hs)
        if not ok:
            skip("dds_handshake", name, group_dep, "test did not pass on this host")
            continue
        cfg = {k: v for k, v in env_extra.items()}
        if hs_samples:
            metrics = _percentiles(hs_samples)
            metrics["runs"] = ok
            record("dds_handshake", name, cfg, "ns", metrics, dependency=group_dep,
                   note="ISOLATED handshake window (FSM begin->OK), excludes startup/discovery/teardown")
        # always also record the full-process wall-clock, clearly labelled
        wm = _percentiles(wall_samples)
        wm["runs"] = ok
        record("dds_handshake", name + " — full process", cfg, "ns", wm, dependency=group_dep,
               note="whole test process: startup + participant create + SPDP discovery + handshake + teardown")


def run(record, skip, measure_wall=None):
    _cyclonedds(record, skip)
    _fastdds(record, skip)


def _cyclonedds(record, skip):
    bt = os.path.join(REPO, "build/overlay/cyclonedds/_bt")
    exe = os.path.join(bt, "bin", "cunit_security_core")
    if not os.path.exists(exe):
        skip("dds_handshake", "CycloneDDS", "cunit_security_core",
             "CycloneDDS PQC test binary not built on this platform")
        return
    env_base = _dyld([os.path.join(bt, "lib"), os.path.join(bt, "src/security/core/tests")])
    base = [exe, "-s", "ddssec_handshake", "-t"]
    configs = [
        ("CycloneDDS classical (RSA id · ECDH P-256)", ["happy_day"], {}),
        ("CycloneDDS hybrid ECDH+ML-KEM-768", ["happy_day"], {"CYCLONEDDS_PQC_KAGREE": "ECDH+ML-KEM-768"}),
        ("CycloneDDS hybrid ECDH+ML-KEM-1024", ["happy_day"], {"CYCLONEDDS_PQC_KAGREE": "ECDH+ML-KEM-1024"}),
        ("CycloneDDS ML-DSA-87 identity (PQ auth)", ["happy_day_mldsa"], {}),
        ("CycloneDDS full CNSA 2.0 (ML-DSA-87 · ML-KEM-1024)", ["happy_day_mldsa"],
         {"CYCLONEDDS_PQC_KAGREE": "ECDH+ML-KEM-1024"}),
    ]
    _run_configs(record, skip, base, bt, env_base, configs, "cunit_security_core")


def _fastdds(record, skip):
    d = os.path.join(REPO, "build/overlay/fastdds/_bt/test/unittest/security/authentication")
    exe = os.path.join(d, "BuiltinPKIDH")
    if not os.path.exists(exe):
        skip("dds_handshake", "FastDDS", "BuiltinPKIDH",
             "Fast DDS PKI-DH test binary not built on this platform")
        return
    env = _dyld([os.path.join(REPO, "build/overlay/fastdds/src/cpp")])
    env["CERTS_PATH"] = os.path.join(REPO, "build/overlay/fastdds/test/certs")
    base = [exe, "--gtest_filter=AuthenticationPluginTest.validate_local_identity_validation_ok_with_pwd"]
    # gtest prints per-test "(N ms)"; we still record the full-process wall-clock here since the
    # Fast DDS unit test has no FSM timestamp log to isolate against.
    _run_configs(record, skip, base, d, env, [
        ("FastDDS PKI-DH local-identity validate", [], {})], "BuiltinPKIDH")
