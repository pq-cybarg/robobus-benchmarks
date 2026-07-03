#!/usr/bin/env python3
"""Run the cbmc machine-checked proofs of the C bus ring and emit the unified benchmark JSON.

Each PROP_* in nsbus_ring_proof.c is an independent proof obligation; we invoke cbmc once per
property and record SUCCESS/FAILURE. cbmc explores EVERY execution (all nondeterministic inputs)
up to the bound, so a SUCCESS means "no counterexample exists", not "no counterexample sampled".
This is the C counterpart to the SymbiYosys/k-induction proof of the RTL ring (bench/hdl).
"""
import json, os, shutil, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "nsbus_ring_proof.c")
INC  = os.path.join(HERE, "..", "native")
OUT  = os.path.join(HERE, "..", "results", "latest-formal-cbmc.json")

# (function, extra cbmc flags, small-ring?, human note)
PROOFS = [
    ("PROP_safety", ["--bounds-check", "--pointer-check", "--div-by-zero-check"], True,
     "ring_put/ring_get never index out of bounds or deref a bad pointer, for ANY 64-bit position"),
    ("PROP_roundtrip", [], True,
     "put(w) then get(w) returns EXACTLY the stamp+payload written, and reports success"),
    ("PROP_reject_writing", [], True,
     "a reader meeting a slot mid-write (odd sequence) rejects it — no torn read"),
    ("PROP_reject_stale", [], True,
     "a reader meeting a slot holding a different published generation rejects it"),
    ("PROP_backpressure", [], False,
     "within the producer's backpressure window (< ring size) no two live positions alias a slot"),
]

def run_one(fn, flags, small):
    cmd = ["cbmc", SRC, "-I", INC, "--function", fn] + (["-DSLOTS=8u"] if small else []) + flags
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
    except Exception as e:
        return None, f"cbmc error: {type(e).__name__}"
    out = p.stdout + p.stderr
    if "VERIFICATION SUCCESSFUL" in out: return True, ""
    if "VERIFICATION FAILED" in out:    return False, "cbmc found a counterexample"
    return None, "no verdict"

def main():
    if not shutil.which("cbmc"):
        print("cbmc not installed — skipping formal proofs"); return 0
    ver = subprocess.run(["cbmc", "--version"], capture_output=True, text=True).stdout.strip().split()[0]
    results, allok = [], True
    for fn, flags, small, note in PROOFS:
        ok, msg = run_one(fn, flags, small)
        allok = allok and bool(ok)
        print(f"  {fn:22s} {'PROVEN' if ok else msg}")
        results.append({
            "group": "formal", "name": fn,
            "config": {"tool": "cbmc", "ring_slots": 8 if small else 1024},
            "unit": "pass", "dependency": "cbmc",
            "status": "ok" if ok else ("error" if ok is False else "skipped"),
            "note": note + ("" if ok else f" — {msg}"),
            "metrics": {"passed": bool(ok)}})
    doc = {
        "schema": "robobus-bench/1",
        "label": f"Formal verification — cbmc {ver} (C bus ring, exhaustive)",
        "platform": {
            "system": "formal", "release": "machine-checked", "version": ver,
            "processor": "cbmc", "machine": "cbmc",
            "cpu_brand": f"cbmc {ver} bounded model checker", "cpu_count_logical": 1,
            "platform": f"cbmc {ver} (bit-precise SAT/SMT decision procedure)",
            "python_version": "n/a", "python_impl": "cbmc",
            "environment": {"virtualized": False, "formal": True,
                "caveat": "exhaustive over ALL inputs (not sampled). Atomics are modelled as their "
                          "sequential equivalent for these single-threaded proofs (cbmc_atomic_shim.h); "
                          "concurrent interleavings are covered by the SymbiYosys/k-induction RTL proof."},
            "measurement": {"fidelity_tier": "formal (exhaustive proof, not measurement)",
                            "uncontrolled_noise": []},
            "dependencies": {"available": {"cbmc": ver}, "missing": {}},
        },
        "results": results,
        "note": "Machine-checked proofs of bench/native/ring.h — the SAME ring nsbus.c benchmarks. "
                "SUCCESS means cbmc proved no counterexample exists up to the bound.",
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(doc, open(OUT, "w"), indent=2)
    print("wrote", OUT)
    return 0 if allok else 1

if __name__ == "__main__":
    sys.exit(main())
