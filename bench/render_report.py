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
    "robobus": "robobus bus / determinism / real-time",
}

GROUP_ORDER = ["bus", "kem", "hybrid_kem", "handshake", "sig", "aead", "hash", "mac", "kdf",
               "dds_handshake", "robobus"]

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
    if name in PQC:
        return "PQC"
    if name in HYBRID:
        return "HYBRID"
    return "classical"


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
            cells = [f"`{r['name']}`", cfg, tag(r["name"]), "—"]
            if has_lat:
                cells += ["—", "—"]
            cells += [f"⚠️ {r['status']}: {r['note']}"]
            out.append("| " + " | ".join(cells) + " |")
            continue
        cells = [f"`{r['name']}`", cfg, tag(r["name"]), primary_str(r)]
        if has_lat:
            p50, p99 = lat_pair(r)
            cells += [p50 or "—", p99 or "—"]
        note = f" · {r['note']}" if r.get("note") else ""
        cells += ["ok" + note]
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
    S.append("_`PQC` = FIPS 203/204 post-quantum (ML-KEM / ML-DSA). `HYBRID` = classical ‖ PQC "
             "combined through HKDF-SHA384 (CNSA 2.0). `classical` = pre-quantum baseline for "
             "comparison. Latency percentiles are per-operation; throughput is aggregate._\n")
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
    colors = {"PQC": "#7c5cff", "HYBRID": "#00b4d8", "classical": "#8a8f98"}
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
        klass = tag(r["name"])
        badge = f"<span class='badge {klass.lower()}'>{klass}</span>"
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
            note = f"<div class='muted' style='font-size:11px'>{html.escape(r['note'])}</div>" if r.get("note") else ""
            cells += [f"<span class='ok'>ok</span>{note}"]
        out.append("<tr>" + "".join(f"<td>{c}</td>" for c in cells) + "</tr>")
    out.append("</tbody></table>")
    return "".join(out)


CSS = """
:root{--bg:#0d1117;--panel:#161b22;--line:#21262d;--fg:#e6edf3;--muted:#8a8f98;
 --pqc:#7c5cff;--hybrid:#00b4d8;--classical:#8a8f98;--accent:#2f81f7}
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
             "<span><i class='dot' style='background:var(--pqc)'></i>PQC (FIPS 203/204)</span>"
             "<span><i class='dot' style='background:var(--hybrid)'></i>Hybrid (CNSA 2.0)</span>"
             "<span><i class='dot' style='background:var(--classical)'></i>classical baseline</span></div>")

    # platform cards
    for doc in docs:
        p = doc["platform"]
        deps = p["dependencies"]
        P.append("<div class='card'><h3 style='margin-top:0'>Host measured</h3><div class='meta'>")
        P.append(f"<div><b>OS</b> {html.escape(p['system'])} {html.escape(p['release'])}</div>")
        P.append(f"<div><b>CPU</b> {html.escape(str(p.get('cpu_brand', p['machine'])))} "
                 f"({p.get('cpu_count_physical', p['cpu_count_logical'])} cores)</div>")
        P.append(f"<div><b>Python</b> {html.escape(p['python_version'])} {html.escape(p['python_impl'])}</div>")
        P.append(f"<div><b>Backends</b> {html.escape(', '.join(deps['available']) or 'stdlib only')}</div>")
        if deps["missing"]:
            P.append(f"<div><b>Skipped</b> {html.escape(', '.join(deps['missing']))}</div>")
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
