#!/usr/bin/env python3
"""
Render benchmark JSON (from run_benchmarks.py) into:
  * a comprehensive Markdown report  -> bench/reports/BENCHMARKS.md   (wiki + private repo)
  * a self-contained static HTML site -> bench/site/index.html         (GitHub Pages)

Reads every bench/results/latest-*.json (one per platform) so that as the SAME script is
run on macOS / Windows / Linux / Android / iOS, each platform's column simply appears.

Pure stdlib. Charts are inline SVG (no external JS/CDN) so the page works offline and on
GitHub Pages with zero build step.
"""
from __future__ import annotations

import glob
import html
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS_DIR = os.path.join(HERE, "results")
REPORTS_DIR = os.path.join(HERE, "reports")
SITE_DIR = os.path.join(HERE, "site")

GROUP_TITLES = {
    "bus": "Shared-memory bus — nanosecond latency (native SPSC ring)",
    "hash": "Hashing (SHA-2 / SHA-3 / BLAKE2)",
    "aead": "Authenticated encryption (AES-GCM / ChaCha20-Poly1305)",
    "mac": "Message authentication (HMAC / Poly1305)",
    "kdf": "Key derivation (HKDF / PBKDF2 / Argon2id)",
    "kem": "Key encapsulation & key exchange (ML-KEM vs classical)",
    "hybrid_kem": "Hybrid PQC key agreement (ECDH ‖ ML-KEM → HKDF-SHA384)",
    "handshake": "Full authenticated handshake crypto (isolated from DDS transport)",
    "sig": "Digital signatures (ML-DSA vs classical)",
    "dds_handshake": "DDS-Security live handshakes (Fast DDS + CycloneDDS)",
    "correctness": "Portability / correctness — emulated ISAs (QEMU; timing NOT measured, by design)",
    "formal": "Formal verification — machine-checked proofs of the C bus ring (cbmc) & RTL (SymbiYosys)",
    "hdl_sim": "RTL / FPGA (cycle-exact simulation + formal proof — no hardware)",
    "gpu": "GPU offload — swapover cost & throughput crossover (scalability, not latency)",
    "robobus": "robobus bus / determinism / real-time",
}

GROUP_ORDER = ["correctness", "formal", "bus", "kem", "hybrid_kem", "handshake", "sig", "aead", "hash", "mac", "kdf",
               "dds_handshake", "gpu", "hdl_sim", "robobus"]

PQC = {"ML-KEM-512", "ML-KEM-768", "ML-KEM-1024", "ML-DSA-44", "ML-DSA-65", "ML-DSA-87"}
HYBRID = {"ECDH-P256+ML-KEM-768", "ECDH-P256+ML-KEM-1024"}


def load_all() -> list[dict]:
    docs = []
    for f in sorted(glob.glob(os.path.join(RESULTS_DIR, "latest-*.json"))):
        try:
            docs.append(json.load(open(f)))
        except Exception:
            pass
    return docs


def fmt(v, unit) -> str:
    if v is None:
        return "—"
    if unit in ("MB/s",):
        return f"{v:,.0f}"
    if v >= 1000:
        return f"{v:,.0f}"
    if v >= 10:
        return f"{v:,.1f}"
    return f"{v:,.2f}"


def props(name: str) -> str:
    """Structural / functional property — the axis ORTHOGONAL to the quantum-security class.

    e.g. SHA3 vs SHA2 is not a quantum difference (both QR at >=384-bit) but a construction
    difference (sponge vs Merkle-Damgard -> length-extension immunity -> native KMAC). Argon2id
    vs HKDF is not a quantum difference but a role difference (memory-hard passphrase KDF for
    LOW-entropy inputs vs fast KDF for HIGH-entropy inputs).
    """
    n = name.lower().replace("_", "-")   # sha3_512 -> sha3-512 (so "sha3-" won't match "sha384")
    out = []
    if any(k in n for k in ("sha3-", "shake", "kmac")):
        out.append("Keccak sponge — length-extension-immune, design-diverse from SHA-2")
    if "kmac" in n:
        out.append("keyed hash directly (SP 800-185) — no HMAC nesting needed")
    if any(k in n for k in ("sha-256", "sha256", "sha-384", "sha384", "sha-512", "sha512")) \
            and "hmac" not in n and "hkdf" not in n:
        out.append("Merkle-Damgard — length-extendable (key via HMAC)")
    if "hmac" in n:
        out.append("nested MAC — keys a Merkle-Damgard hash safely")
    if "argon2" in n:
        out.append("memory-hard passphrase KDF — LOW-entropy inputs, GPU/ASIC-resistant")
    if "pbkdf2" in n:
        out.append("iteration-only passphrase KDF — NO memory-hardness (weakest)")
    if "hkdf" in n:
        out.append("extract-then-expand KDF — HIGH-entropy inputs (RFC 5869)")
    if "poly1305" in n:
        out.append("one-time Wegman-Carter MAC (with ChaCha20)")
    if "aes-256" in n:
        out.append("Grover → ~128-bit quantum security")
    if "aes-128" in n:
        out.append("Grover → ~64-bit — below the post-quantum bar")
    return " · ".join(out)


def fmt_lat(ns) -> str:
    """Auto-scale a nanosecond latency to ns / µs / ms so sub-µs values read as nanoseconds."""
    if ns is None:
        return "—"
    if ns < 1000:
        return f"{ns:,.1f} ns"
    if ns < 1_000_000:
        return f"{ns/1000:,.2f} µs"
    return f"{ns/1_000_000:,.2f} ms"


def primary_metric(r: dict):
    m = r["metrics"]
    u = r["unit"]
    if u == "MB/s":
        return m.get("mb_per_s")
    if u == "ns":                 # latency distribution -> headline is p50
        return m.get("p50_ns")
    if u == "ns/op":              # amortized op -> headline is the op rate
        return m.get("ops_per_s")
    return m.get("ops_per_s")


def primary_str(r: dict) -> str:
    v = primary_metric(r)
    u = r["unit"]
    if v is None:
        return "—"
    if u == "pass":
        pv = r["metrics"].get("passed")
        return "✓ pass" if pv else ("—" if pv is None else "✗ FAIL")
    if u == "ns":                 # p50 latency, ns-scaled
        return fmt_lat(v)
    if u == "ns/op":              # rate + amortized ns/op
        mean = r["metrics"].get("mean_ns")
        return f"{fmt(v, u)} ops/s ({fmt_lat(mean)}/op)" if mean else f"{fmt(v, u)} ops/s"
    return f"{fmt(v, u)} {u}"


def lat_pair(r: dict):
    """Return (p50_str, p99_str) auto-scaled, or (None, None)."""
    m = r["metrics"]
    if "p50_ns" in m:
        return fmt_lat(m["p50_ns"]), fmt_lat(m.get("p99_ns", 0))
    return None, None


def tag(name: str) -> str:
    """Classify a row into four quantum-security classes by pattern.

    PQC       = post-quantum *asymmetric* (ML-KEM, ML-DSA, SLH-DSA, Falcon, HQC) — the new NIST
                hard-problem algorithms that replace quantum-broken RSA/ECC.
    HYBRID    = a classical asymmetric primitive combined with a PQC one (CNSA 2.0 transition
                pattern), e.g. ECDH ‖ ML-KEM. NOTE: a PQC KEM together with a PQC signature
                (ML-KEM + ML-DSA) is all-PQC, NOT hybrid — hybrid requires a *classical* term.
    QR        = quantum-RESISTANT symmetric/hash/KDF: secure against a quantum adversary at its
                size (Grover only square-roots symmetric search). AES-256, ChaCha20-Poly1305,
                SHA-384/512, SHA3-*, KMAC, HMAC-SHA-384/512, HKDF-SHA-384, BLAKE2b, Argon2id —
                these ARE part of CNSA 2.0 (not "PQC", but not "classical" either).
    classical = quantum-BROKEN asymmetric (RSA, ECDH/ECDSA, X25519/Ed25519) OR symmetric/hash
                below the post-quantum bar (AES-128 ~64-bit under Grover; SHA-256 collision).
    """
    n = name.lower().replace("_", "-")   # hashlib uses sha3_512 / blake2b; normalize to dashes
    has_kem = ("ml-kem" in n) or ("kyber" in n)
    has_pq_sig = any(k in n for k in ("ml-dsa", "dilithium", "falcon", "sphincs", "slh-dsa"))
    has_pqc = has_kem or has_pq_sig or ("hqc" in n) or ("frodo" in n) or ("mceliece" in n)
    has_classical_asym = any(k in n for k in (
        "ecdh", "x25519", "x448", "p-256", "p256", "prime256v1", "rsa", "ecdsa",
        "ed25519", "ed448", "dh+modp"))
    if "hybrid" in n:
        return "HYBRID"
    if has_pqc and has_classical_asym:   # classical ⊕ PQC only; PQC-KEM + PQC-sig is all-PQC
        return "HYBRID"
    if has_pqc:
        return "PQC"
    # symmetric / hash / MAC / KDF: quantum-resistant only at sufficient strength
    # >=256-bit symmetric keys + >=384-bit-strength hashes/XOFs (the CNSA 2.0 symmetric floor);
    # 256-bit hashes (SHA-256 / SHA3-256) stay classical (collision below the post-quantum bar).
    qr = any(k in n for k in (
        "aes-256", "chacha20", "poly1305", "sha384", "sha-384", "sha512", "sha-512",
        "sha3-384", "sha3-512", "shake256", "blake2b", "kmac", "argon2"))
    if qr:
        return "QR"
    if has_classical_asym:
        return "classical"
    # remaining symmetric/hash below the PQ bar (AES-128, SHA-256, HMAC-SHA256, PBKDF2, ...)
    return "classical"


# Only these groups compare crypto PRIMITIVES, so only they carry a quantum-security class. For
# the portability/correctness matrix, the formal proofs, the bus, the HDL sim, handshakes, etc.
# a QR/classical/PQC badge is meaningless (the row is a check or a latency, not an algorithm).
_CLASS_GROUPS = {"kem", "hybrid_kem", "sig", "aead", "hash", "mac", "kdf"}

def class_cell(group: str, name: str) -> str:
    """Quantum-security class, shown only for crypto-primitive groups; '—' everywhere else."""
    return tag(name) if group in _CLASS_GROUPS else "—"


# --------------------------------------------------------------------------------------
# Markdown
# --------------------------------------------------------------------------------------
def md_platform_block(doc: dict) -> str:
    p = doc["platform"]
    deps = p["dependencies"]
    lines = [
        f"- **OS:** {p['system']} {p['release']} ({p['platform']})",
        f"- **CPU:** {p.get('cpu_brand', p.get('processor') or p['machine'])}"
        f" — {p.get('cpu_count_physical', p['cpu_count_logical'])} cores"
        + (f", {p['mem_total_bytes'] // (1024**3)} GB RAM" if p.get("mem_total_bytes") else ""),
        f"- **Python:** {p['python_version']} ({p['python_impl']})",
        f"- **Crypto backends:** " + (", ".join(f"{k} {v}" for k, v in deps["available"].items()) or "stdlib only"),
    ]
    if deps["missing"]:
        lines.append(f"- **Absent on this host (SKIPPED):** {', '.join(deps['missing'])}")
    envp = p.get("environment", {})
    if envp.get("emulated"):
        lines.insert(0, f"- **EMULATED ISA ({envp['emulated']}, QEMU):** correctness/portability only "
                        f"— timing is NOT cycle-accurate under emulation and is not measured.")
    m = p.get("measurement", {})
    if m.get("fidelity_tier"):
        lines.append(f"- **Fidelity tier:** {m['fidelity_tier']}")
    conds = []
    if m.get("cpu_governor"):
        conds.append(f"governor={'/'.join(m['cpu_governor'])}")
    if m.get("turbo"):
        conds.append(f"turbo={m['turbo']}")
    if m.get("smt_active") is not None:
        conds.append(f"SMT={'on' if m['smt_active'] else 'off'}")
    if m.get("isolated_cpus") is not None:
        conds.append(f"isolcpus={m['isolated_cpus'] or 'none'}")
    if m.get("pinned") is not None:
        conds.append(f"pinned={m['pinned']}")
    if conds:
        lines.append(f"- **Measurement conditions:** {', '.join(conds)}")
    if m.get("uncontrolled_noise"):
        lines.append(f"- **Uncontrolled noise:** {'; '.join(m['uncontrolled_noise'])}")
    return "\n".join(lines)


def md_table(doc: dict, group: str) -> str:
    rows = [r for r in doc["results"] if r["group"] == group]
    if not rows:
        return "_No results for this group on this platform._\n"
    has_lat = any("p50_ns" in r["metrics"] for r in rows if r["status"] == "ok")
    hdr = ["Algorithm", "Config", "Class", "Throughput / rate"]
    if has_lat:
        hdr += ["p50", "p99"]
    hdr += ["Status"]
    out = ["| " + " | ".join(hdr) + " |", "|" + "|".join(["---"] * len(hdr)) + "|"]
    for r in rows:
        cfg = ", ".join(f"{k}={v}" for k, v in r["config"].items()) or "—"
        if r["status"] != "ok":
            cells = [f"`{r['name']}`", cfg, class_cell(group, r["name"]), "—"]
            if has_lat:
                cells += ["—", "—"]
            cells += [f"⚠️ {r['status']}: {r['note']}"]
            out.append("| " + " | ".join(cells) + " |")
            continue
        cells = [f"`{r['name']}`", cfg, class_cell(group, r["name"]), primary_str(r)]
        if has_lat:
            p50, p99 = lat_pair(r)
            cells += [p50 or "—", p99 or "—"]
        extra = " · ".join(x for x in [props(r["name"]), r.get("note", "")] if x)
        cells += ["ok" + (f" · {extra}" if extra else "")]
        out.append("| " + " | ".join(cells) + " |")
    return "\n".join(out) + "\n"


def render_markdown(docs: list[dict]) -> str:
    now = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    S = []
    S.append("# robobus / PQC-DDS — full-system benchmarks\n")
    S.append("> **Scope.** Every capability of the stack — post-quantum and classical key "
             "encapsulation, hybrid key agreement, digital signatures, authenticated "
             "encryption, hashing, MACs, key-derivation, live DDS-Security handshakes, and "
             "the robobus bus — measured across all available modes, sizes and techniques by "
             "**one script** (`bench/run_benchmarks.py`).\n")
    S.append("> ⚠️ **Platform caveat.** These figures were measured **on macOS only** so far. "
             "They are inherently CPU-, OS- and build-specific and are **not** portable claims. "
             "The value here is the *method*: the identical script is designed to run on "
             "macOS, Windows, every supported Linux, Android and iOS, skipping only what a "
             "given platform lacks. Re-run it on each target to populate that platform's column.\n")
    S.append(f"_Generated {now} from `bench/results/latest-*.json`._\n")

    S.append("## Platforms measured\n")
    for doc in docs:
        p = doc["platform"]
        S.append(f"### {p['system']} · {p.get('cpu_brand', p['machine'])}\n")
        S.append(md_platform_block(doc) + "\n")

    S.append("## How to reproduce\n")
    S.append("```bash\n"
             "# one script, every platform — measures what it can, skips the rest with a reason\n"
             "python bench/run_benchmarks.py            # full run\n"
             "python bench/run_benchmarks.py --quick    # fast pass\n"
             "python bench/render_report.py             # regenerate this report + the HTML site\n"
             "```\n")
    S.append("Optional backends unlock more rows: `cryptography` (AEAD, ECDH, classical "
             "signatures), `oqs`/liboqs (ML-KEM, ML-DSA), `argon2-cffi` (Argon2id). Absent "
             "backends produce **SKIPPED** rows — never a crash — which is exactly how the same "
             "script stays valid on constrained platforms (e.g. stock Android/iOS Python).\n")

    for group in GROUP_ORDER:
        title = GROUP_TITLES.get(group, group)
        any_rows = any(any(r["group"] == group for r in d["results"]) for d in docs)
        if not any_rows:
            continue
        S.append(f"## {title}\n")
        for doc in docs:
            p = doc["platform"]
            if not any(r["group"] == group for r in doc["results"]):
                continue
            S.append(f"**{p['system']} · {p.get('cpu_brand', p['machine'])}**\n")
            S.append(md_table(doc, group))
    S.append("\n---\n")
    S.append("**Classes.** `PQC` = post-quantum *asymmetric* (FIPS 203 ML-KEM / FIPS 204 ML-DSA), "
             "replacing quantum-broken RSA/ECC. `HYBRID` = classical ⊕ PQC (CNSA 2.0 transition, "
             "e.g. ECDH ‖ ML-KEM → HKDF-SHA384). `QR` = quantum-**resistant** symmetric/hash "
             "(AES-256, ChaCha20-Poly1305, SHA-384/512, SHA3, KMAC, Argon2id) — Grover only "
             "square-roots symmetric search, so these keep their margins and are part of CNSA 2.0; "
             "*not* PQC (an asymmetric term), but *not* classical either. `classical` = "
             "quantum-broken asymmetric (RSA/ECDH/ECDSA/Ed25519) or sub-strength symmetric "
             "(AES-128, SHA-256 collision). Latency percentiles are per-operation; throughput is "
             "aggregate._\n")
    return "\n".join(S)


# --------------------------------------------------------------------------------------
# HTML (self-contained, inline SVG charts)
# --------------------------------------------------------------------------------------
def svg_bar_chart(title, rows, unit, *, width=720, log=False):
    """rows: list of (label, value, klass). Renders a horizontal bar chart as inline SVG."""
    rows = [(l, v, k) for (l, v, k) in rows if v]
    if not rows:
        return ""
    import math
    vmax = max(v for _, v, _ in rows)
    barh, gap, left, top = 26, 10, 210, 34
    h = top + len(rows) * (barh + gap) + 16
    colors = {"PQC": "#7c5cff", "HYBRID": "#00b4d8", "QR": "#3fb950", "classical": "#8a8f98"}
    plot_w = width - left - 90

    def scale(v):
        if log:
            return max(2, plot_w * (math.log10(v) / math.log10(vmax))) if v > 0 else 2
        return max(2, plot_w * (v / vmax))

    parts = [f'<svg viewBox="0 0 {width} {h}" class="chart" role="img" aria-label="{html.escape(title)}">']
    parts.append(f'<text x="0" y="20" class="ct">{html.escape(title)}</text>')
    y = top
    for label, v, klass in rows:
        w = scale(v)
        c = colors.get(klass, "#8a8f98")
        parts.append(f'<text x="{left-8}" y="{y+barh*0.68}" class="cl" text-anchor="end">{html.escape(label)}</text>')
        parts.append(f'<rect x="{left}" y="{y}" width="{w:.1f}" height="{barh}" rx="4" fill="{c}"/>')
        val = f"{v:,.0f}" if v >= 100 else f"{v:,.1f}"
        parts.append(f'<text x="{left+w+6:.1f}" y="{y+barh*0.68}" class="cv">{val}</text>')
        y += barh + gap
    parts.append(f'<text x="{left}" y="{h-2}" class="cu">{html.escape(unit)}'
                 + ("  ·  log scale" if log else "") + "</text>")
    parts.append("</svg>")
    return "".join(parts)


def collect_chart(doc, group, name_filter, op, metric="ops_per_s"):
    rows = []
    for r in doc["results"]:
        if r["group"] != group or r["status"] != "ok":
            continue
        if r["config"].get("op") != op:
            continue
        if name_filter and not name_filter(r["name"]):
            continue
        v = r["metrics"].get(metric)
        if v:
            rows.append((r["name"], v, tag(r["name"])))
    return rows


def html_table(doc, group):
    rows = [r for r in doc["results"] if r["group"] == group]
    if not rows:
        return "<p class='muted'>No results for this group.</p>"
    has_lat = any("p50_ns" in r["metrics"] for r in rows if r["status"] == "ok")
    cols = ["Algorithm", "Config", "Class", "Rate / latency"]
    if has_lat:
        cols += ["p50", "p99"]
    cols += ["Status"]
    out = ["<table><thead><tr>" + "".join(f"<th>{c}</th>" for c in cols) + "</tr></thead><tbody>"]
    for r in rows:
        cfg = ", ".join(f"{k}={v}" for k, v in r["config"].items()) or "—"
        klass = class_cell(group, r["name"])
        badge = "—" if klass == "—" else f"<span class='badge {klass.lower()}'>{klass}</span>"
        if r["status"] != "ok":
            cells = [f"<code>{html.escape(r['name'])}</code>", html.escape(cfg), badge, "—"]
            if has_lat:
                cells += ["—", "—"]
            cells += [f"<span class='skip'>{html.escape(r['status'])}: {html.escape(r['note'])[:90]}</span>"]
        else:
            cells = [f"<code>{html.escape(r['name'])}</code>", html.escape(cfg), badge,
                     html.escape(primary_str(r))]
            if has_lat:
                p50, p99 = lat_pair(r)
                cells += [p50 or "—", p99 or "—"]
            pr = props(r["name"])
            bits = []
            if pr:
                bits.append(f"<span style='color:#7ee787'>{html.escape(pr)}</span>")
            if r.get("note"):
                bits.append(html.escape(r["note"]))
            note = (f"<div class='muted' style='font-size:11px'>{' · '.join(bits)}</div>"
                    if bits else "")
            cells += [f"<span class='ok'>ok</span>{note}"]
        out.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


CSS = """
:root{--bg:#0d1117;--panel:#161b22;--line:#21262d;--fg:#e6edf3;--muted:#8a8f98;
 --pqc:#7c5cff;--hybrid:#00b4d8;--qr:#3fb950;--classical:#8a8f98;--accent:#2f81f7}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);
 font:15px/1.55 -apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,Helvetica,Arial,sans-serif}
.wrap{max-width:1040px;margin:0 auto;padding:32px 22px 80px}
h1{font-size:30px;margin:0 0 6px}h2{font-size:22px;margin:44px 0 10px;padding-top:10px;border-top:1px solid var(--line)}
h3{font-size:16px;color:var(--muted);margin:22px 0 8px;font-weight:600}
a{color:var(--accent)}code{background:#010409;padding:1px 6px;border-radius:5px;font-size:13px}
.sub{color:var(--muted);margin:0 0 18px}
.callout{background:#1c1400;border:1px solid #b8860b55;border-radius:10px;padding:12px 16px;margin:16px 0;color:#f0d98c}
.card{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:16px 18px;margin:14px 0}
.meta{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:8px 22px;margin:8px 0}
.meta div{color:var(--muted);font-size:14px}.meta b{color:var(--fg)}
table{border-collapse:collapse;width:100%;font-size:13.5px;margin:6px 0 4px}
th,td{border-bottom:1px solid var(--line);padding:7px 10px;text-align:left;vertical-align:top}
th{color:var(--muted);font-weight:600;font-size:12px;text-transform:uppercase;letter-spacing:.04em}
tbody tr:hover{background:#1b2129}
.muted{color:var(--muted)}.ok{color:#3fb950}.skip{color:#d29922;font-size:12px}
.badge{display:inline-block;padding:1px 8px;border-radius:20px;font-size:11px;font-weight:700;letter-spacing:.03em}
.badge.pqc{background:#7c5cff22;color:#b3a1ff;border:1px solid #7c5cff55}
.badge.hybrid{background:#00b4d822;color:#7fdcef;border:1px solid #00b4d855}
.badge.qr{background:#3fb95022;color:#7ee787;border:1px solid #3fb95055}
.badge.classical{background:#8a8f9822;color:#b6bcc6;border:1px solid #8a8f9855}
.chart{width:100%;height:auto;margin:6px 0 2px}
.chart .ct{fill:var(--fg);font-size:14px;font-weight:700}
.chart .cl{fill:var(--muted);font-size:12px}.chart .cv{fill:var(--fg);font-size:12px;font-weight:600}
.chart .cu{fill:var(--muted);font-size:11px}
.legend{display:flex;gap:16px;margin:6px 0 14px;font-size:12px;color:var(--muted)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.dot{width:11px;height:11px;border-radius:3px;display:inline-block}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:18px}@media(max-width:820px){.grid2{grid-template-columns:1fr}}
footer{color:var(--muted);font-size:13px;margin-top:40px;border-top:1px solid var(--line);padding-top:16px}
"""


def render_html(docs: list[dict]) -> str:
    now = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime())
    P = ['<!doctype html><html lang="en"><head><meta charset="utf-8">',
         '<meta name="viewport" content="width=device-width,initial-scale=1">',
         '<title>robobus / PQC-DDS benchmarks</title>',
         f"<style>{CSS}</style></head><body><div class='wrap'>"]
    P.append("<h1>robobus / PQC-DDS — full-system benchmarks</h1>")
    P.append("<p class='sub'>Post-quantum &amp; classical key encapsulation, hybrid key "
             "agreement, signatures, AEAD, hashing, MACs, KDFs, live DDS-Security handshakes "
             "and the robobus bus — measured end to end by one portable script.</p>")
    P.append("<div class='callout'>⚠️ <b>Measured on macOS only (so far).</b> These numbers are "
             "CPU/OS/build-specific and are not portable claims. The deliverable is the "
             "<i>method</i>: the identical <code>run_benchmarks.py</code> is built to run on "
             "macOS, Windows, all supported Linux, Android and iOS — each platform measures what "
             "it has and records the rest as <b>SKIPPED</b>. Re-run to add a platform's column.</div>")
    P.append(f"<p class='muted'>Generated {now}. "
             "<a href='https://github.com/pq-cybarg'>pq-cybarg</a>.</p>")
    P.append("<div class='legend'>"
             "<span><i class='dot' style='background:var(--pqc)'></i>PQC — post-quantum asymmetric (ML-KEM/ML-DSA)</span>"
             "<span><i class='dot' style='background:var(--hybrid)'></i>Hybrid — classical ⊕ PQC</span>"
             "<span><i class='dot' style='background:var(--qr)'></i>QR — quantum-resistant symmetric (AES-256, SHA-384/512…)</span>"
             "<span><i class='dot' style='background:var(--classical)'></i>classical — quantum-broken (RSA/ECC) or sub-strength</span></div>")
    P.append("<div class='card' style='font-size:13px'><b>On the four classes.</b> "
             "<span class='badge pqc'>PQC</span> is reserved for the new NIST <i>asymmetric</i> "
             "standards (FIPS 203 ML-KEM, FIPS 204 ML-DSA) that replace RSA/ECC — which Shor's "
             "algorithm breaks outright (<span class='badge classical'>classical</span>). "
             "<span class='badge qr'>QR</span> covers symmetric &amp; hash primitives that stay "
             "secure against a quantum adversary at their size: Grover only <i>square-roots</i> "
             "symmetric search, so <code>AES-256</code> keeps ~128-bit security and "
             "<code>SHA-384/512</code>/<code>SHA3</code>/<code>KMAC</code> keep their margins — "
             "CNSA 2.0 keeps exactly these. So AES-256 is <i>not</i> PQC (that's an asymmetric "
             "term) but it <i>is</i> quantum-resistant — it is not \"classical\". Sub-strength "
             "symmetric (AES-128 → ~64-bit under Grover; SHA-256 collision) stays classical.</div>")
    P.append("<div class='card' style='font-size:13px'><b>A second, orthogonal axis — construction "
             "&amp; role (the green notes in each row).</b> Two primitives can share a quantum class "
             "yet differ structurally: <code>SHA3</code>/<code>SHAKE</code>/<code>KMAC</code> use the "
             "<i>Keccak sponge</i>, which is <i>length-extension-immune</i> — so KMAC (SP 800-185) "
             "keys a hash <i>directly</i> with no HMAC nesting, and it's design-diverse from SHA-2's "
             "Merkle–Damgård (which <i>is</i> length-extendable, hence HMAC). That is not a "
             "quantum-status difference — SHA-384/512 and SHA3-384/512 are equally QR. Likewise "
             "<code>Argon2id</code> is not \"just a KDF\": it is a <i>memory-hard passphrase</i> KDF "
             "for <i>low-entropy</i> inputs (GPU/ASIC-resistant), a different role from "
             "<code>HKDF</code>/<code>KMAC</code>-KDF, which are fast extractors for "
             "<i>high-entropy</i> inputs, and stronger than <code>PBKDF2</code> (iterations only, no "
             "memory-hardness). The <b>Class</b> badge is the quantum axis; the green note is the "
             "construction/role axis.</div>")

    # platform cards
    for doc in docs:
        p = doc["platform"]
        deps = p["dependencies"]
        emu = p.get("environment", {}).get("emulated")
        title = f"Emulated ISA — {emu} (QEMU)" if emu else "Host measured"
        P.append(f"<div class='card'><h3 style='margin-top:0'>{html.escape(title)}</h3>")
        if emu:
            P.append("<div class='callout' style='margin:0 0 10px'>EMULATED — correctness/portability "
                     "only. QEMU is not cycle-accurate; timing is <b>not measured</b> here.</div>")
        P.append("<div class='meta'>")
        P.append(f"<div><b>OS</b> {html.escape(p['system'])} {html.escape(p['release'])}</div>")
        P.append(f"<div><b>CPU</b> {html.escape(str(p.get('cpu_brand', p['machine'])))} "
                 f"({p.get('cpu_count_physical', p['cpu_count_logical'])} cores)</div>")
        P.append(f"<div><b>Python</b> {html.escape(p['python_version'])} {html.escape(p['python_impl'])}</div>")
        P.append(f"<div><b>Backends</b> {html.escape(', '.join(deps['available']) or 'stdlib only')}</div>")
        if deps["missing"]:
            P.append(f"<div><b>Skipped</b> {html.escape(', '.join(deps['missing']))}</div>")
        m = p.get("measurement", {})
        if m.get("fidelity_tier"):
            P.append(f"<div><b>Fidelity</b> {html.escape(m['fidelity_tier'])}</div>")
        if m.get("uncontrolled_noise"):
            P.append(f"<div style='grid-column:1/-1;color:#d29922'><b>Uncontrolled noise</b> "
                     f"{html.escape('; '.join(m['uncontrolled_noise']))}</div>")
        P.append("</div></div>")

    # headline charts (first doc)
    if docs:
        d0 = docs[0]
        P.append("<h2>Headline: the cost of going post-quantum</h2>")
        P.append("<div class='grid2'>")
        kem = collect_chart(d0, "kem", None, "encapsulate") + \
            collect_chart(d0, "kem", None, "derive")
        P.append("<div class='card'>" + svg_bar_chart(
            "Key exchange / encapsulation — ops/s (higher is better)", kem, "operations / second", log=True) + "</div>")
        sig = collect_chart(d0, "sig", None, "sign")
        P.append("<div class='card'>" + svg_bar_chart(
            "Signing — ops/s (higher is better)", sig, "operations / second", log=True) + "</div>")
        P.append("</div><div class='grid2'>")
        sigv = collect_chart(d0, "sig", None, "verify")
        P.append("<div class='card'>" + svg_bar_chart(
            "Verification — ops/s (higher is better)", sigv, "operations / second", log=True) + "</div>")
        hyb = collect_chart(d0, "hybrid_kem", None, "full_two_party_handshake")
        aead = [(r["name"] + " enc", r["metrics"].get("mb_per_s"), tag(r["name"]))
                for r in d0["results"] if r["group"] == "aead" and r["status"] == "ok"
                and r["config"].get("op") == "encrypt"
                and r["config"].get("input_bytes") == max(
                    (rr["config"].get("input_bytes", 0) for rr in d0["results"]
                     if rr["group"] == "aead"), default=0)]
        P.append("<div class='card'>" + svg_bar_chart(
            "Hybrid handshake (ECDH‖ML-KEM→HKDF) — handshakes/s", hyb, "handshakes / second") +
            svg_bar_chart("AEAD throughput @ largest block — MB/s", aead, "MB / second") + "</div>")
        P.append("</div>")

    # full tables per group
    for group in GROUP_ORDER:
        if not any(any(r["group"] == group for r in d["results"]) for d in docs):
            continue
        P.append(f"<h2>{html.escape(GROUP_TITLES.get(group, group))}</h2>")
        for doc in docs:
            if not any(r["group"] == group for r in doc["results"]):
                continue
            p = doc["platform"]
            P.append(f"<h3>{html.escape(p['system'])} · {html.escape(str(p.get('cpu_brand', p['machine'])))}</h3>")
            P.append(html_table(doc, group))

    P.append("<footer>PQC = FIPS 203 (ML-KEM) / FIPS 204 (ML-DSA). Hybrid = classical ‖ PQC "
             "combined via HKDF-SHA384 (CNSA 2.0). Latency percentiles are per-operation; "
             "throughput is aggregate. One script, every platform — "
             "<code>bench/run_benchmarks.py</code>.</footer>")
    P.append("</div></body></html>")
    return "".join(P)


def main() -> int:
    docs = load_all()
    if not docs:
        print("no bench/results/latest-*.json found — run run_benchmarks.py first")
        return 1
    os.makedirs(REPORTS_DIR, exist_ok=True)
    os.makedirs(SITE_DIR, exist_ok=True)
    md = render_markdown(docs)
    open(os.path.join(REPORTS_DIR, "BENCHMARKS.md"), "w").write(md)
    open(os.path.join(SITE_DIR, "index.html"), "w").write(render_html(docs))
    # copy the raw json into the site for download/provenance
    for doc in docs:
        slug = f"{doc['platform']['system']}-{doc['platform']['machine']}".lower().replace(" ", "_")
        open(os.path.join(SITE_DIR, f"data-{slug}.json"), "w").write(json.dumps(doc, indent=2))
    print(f"wrote {os.path.join(REPORTS_DIR, 'BENCHMARKS.md')}")
    print(f"wrote {os.path.join(SITE_DIR, 'index.html')}")
    print(f"platforms: {', '.join(d['platform']['system'] for d in docs)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
