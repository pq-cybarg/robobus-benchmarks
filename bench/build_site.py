#!/usr/bin/env python3
"""build_site.py — assemble the robobus PROJECT WEBSITE (not just the benchmark report).

Produces a small multi-page static site into bench/site/ (then the CI copies it to docs/ for
GitHub Pages), with a shared nav:  Home · Benchmarks · Docs · GitHub.

  index.html        the landing page — the "latency spectrum" thesis + measured headline numbers
  benchmarks.html   the full live report (bench/render_report.py's output, wrapped in the shell)
  docs/<slug>.html  the design docs (docs-src/*.md rendered), with a docs sidebar

Design: a measurement-instrument identity — the numbers are the hero (JetBrains Mono), Space
Grotesk for display, a deep instrument-black base with a teal "signal" accent. The signature is
the ns→ms latency spectrum (the project's own thesis: "latency is not one number").

Deps: `markdown` (docs rendering). render_report is imported for the benchmark body + its CSS.
Run: python bench/build_site.py   (after run_benchmarks.py + the data-*.json exist)
"""
from __future__ import annotations

import glob
import html
import json
import os
import re
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SITE = os.path.join(HERE, "site")
DOCS_SRC = os.path.join(ROOT, "docs-src")
GH = "https://github.com/pq-cybarg/robobus-benchmarks"

# ---------------------------------------------------------------------------------------------
# design tokens — measurement instrument. Numbers are the hero.
# ---------------------------------------------------------------------------------------------
CSS = """
:root{
  --bg:#0a0e13; --bg2:#0d131b; --panel:#111a24; --panel2:#0f1620; --line:#1e2a37;
  --fg:#e9eef4; --muted:#8a9bab; --dim:#5f7183;
  --signal:#4fd1c5; --signal-ink:#0a0e13; --amber:#f4b46a; --violet:#8b7cff;
  --pqc:#8b7cff; --hybrid:#22c3e6; --qr:#4ec97a; --classical:#8a9bab;
  --maxw:1080px;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth;overflow-x:hidden}
body{margin:0;max-width:100%;overflow-x:hidden;background:
  radial-gradient(1200px 600px at 78% -8%, #10202a 0%, transparent 60%),
  radial-gradient(900px 500px at 0% 0%, #131024 0%, transparent 55%),
  var(--bg);
  color:var(--fg);font-family:'Inter',ui-sans-serif,system-ui,-apple-system,Segoe UI,Roboto,sans-serif;
  font-size:16px;line-height:1.6;-webkit-font-smoothing:antialiased}
.mono{font-family:'JetBrains Mono',ui-monospace,SFMono-Regular,Menlo,monospace}
a{color:var(--signal);text-decoration:none}a:hover{text-decoration:underline}
h1,h2,h3{font-family:'Space Grotesk',ui-sans-serif,system-ui,sans-serif;line-height:1.12;letter-spacing:-.01em;font-weight:600}
.wrap{max-width:var(--maxw);margin:0 auto;padding:0 22px}

/* ---- nav ---- */
.nav{position:sticky;top:0;z-index:50;backdrop-filter:blur(10px);
  background:color-mix(in srgb,var(--bg) 82%,transparent);border-bottom:1px solid var(--line)}
.nav .row{max-width:var(--maxw);margin:0 auto;padding:12px 22px;display:flex;align-items:center;gap:8px 10px;flex-wrap:wrap}
.brand{display:flex;align-items:center;gap:11px;font-family:'Space Grotesk';font-weight:600;font-size:18px;color:var(--fg);letter-spacing:-.02em}
.brand:hover{text-decoration:none}
.brand .glyph{width:26px;height:26px;flex:0 0 auto}
.nav .links{margin-left:auto;display:flex;gap:4px;align-items:center;flex-wrap:wrap}
.nav a.tab{color:var(--muted);padding:7px 13px;border-radius:8px;font-size:14.5px;font-weight:500}
.nav a.tab:hover{color:var(--fg);background:var(--panel);text-decoration:none}
.nav a.tab.active{color:var(--signal);background:color-mix(in srgb,var(--signal) 12%,transparent)}
.nav a.gh{color:var(--muted);display:inline-flex;padding:7px 10px;border-radius:8px}
.nav a.gh:hover{color:var(--fg);background:var(--panel)}

/* ---- hero ---- */
.hero{padding:74px 0 30px;position:relative}
.eyebrow{font-family:'JetBrains Mono';font-size:12.5px;letter-spacing:.16em;text-transform:uppercase;color:var(--signal);margin:0 0 18px}
.hero h1{font-size:clamp(34px,6vw,62px);margin:0 0 20px;max-width:15ch}
.hero h1 em{font-style:normal;color:var(--signal)}
.lede{font-size:clamp(17px,2.4vw,21px);color:var(--muted);max-width:60ch;margin:0 0 30px}
.cta{display:flex;gap:12px;flex-wrap:wrap}
.btn{display:inline-flex;align-items:center;gap:8px;padding:11px 18px;border-radius:10px;font-weight:600;font-size:15px;border:1px solid transparent}
.btn.primary{background:var(--signal);color:var(--signal-ink)}
.btn.primary:hover{background:#6fe0d6;text-decoration:none}
.btn.ghost{border-color:var(--line);color:var(--fg)}
.btn.ghost:hover{border-color:var(--signal);background:var(--panel);text-decoration:none}

/* ---- latency spectrum (signature) ---- */
.spectrum{margin:52px 0 8px}
.spectrum .cap{display:flex;justify-content:space-between;align-items:baseline;margin:0 0 14px}
.spectrum .cap b{font-family:'Space Grotesk';font-weight:600;font-size:15px}
.spectrum .cap span{font-family:'JetBrains Mono';font-size:12px;color:var(--dim)}
.spec-scroll{overflow-x:auto;overflow-y:hidden;margin:0 -2px;padding:0 2px}
.spec-svg{width:100%;min-width:580px;height:auto;display:block}

/* ---- generic sections ---- */
section{padding:56px 0;border-top:1px solid var(--line)}
.sec-eyebrow{font-family:'JetBrains Mono';font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--dim);margin:0 0 10px}
h2.title{font-size:clamp(24px,3.5vw,34px);margin:0 0 8px}
.sec-lede{color:var(--muted);max-width:64ch;margin:0 0 26px}

/* stat strip */
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:1px;background:var(--line);border:1px solid var(--line);border-radius:14px;overflow:hidden}
.stat{background:var(--panel);padding:18px 18px}
.stat .n{font-family:'JetBrains Mono';font-size:clamp(22px,3vw,30px);font-weight:700;color:var(--fg);letter-spacing:-.02em}
.stat .n small{font-size:.5em;color:var(--muted);font-weight:500;margin-left:3px}
.stat .l{font-size:12.5px;color:var(--muted);margin-top:5px;line-height:1.4}

/* feature cards */
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(250px,1fr));gap:16px}
.fcard{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:14px;padding:22px}
.fcard .k{font-family:'JetBrains Mono';font-size:12px;color:var(--signal);letter-spacing:.04em;margin:0 0 12px}
.fcard h3{font-size:18px;margin:0 0 8px}
.fcard p{color:var(--muted);font-size:14.5px;margin:0}
.fcard .pqc{color:var(--pqc)}.fcard .hybrid{color:var(--hybrid)}.fcard .qr{color:var(--qr)}

/* transports */
.xgrid{display:grid;gap:14px}
@media(min-width:720px){.xgrid{grid-template-columns:1fr 1fr}}
.xgrp{border:1px solid var(--line);border-radius:14px;background:linear-gradient(180deg,var(--panel),var(--panel2));padding:16px 18px}
.xgrp .xh{font-family:'JetBrains Mono';font-size:11.5px;letter-spacing:.11em;text-transform:uppercase;color:var(--signal);margin:0 0 13px}
.xrow{display:flex;flex-wrap:wrap;gap:8px}
.chip{display:inline-flex;align-items:baseline;gap:7px;padding:8px 12px;border:1px solid var(--line);border-radius:9px;background:var(--bg2);font-size:14px;color:var(--fg);font-weight:500}
.chip small{color:var(--muted);font-size:11px;font-family:'JetBrains Mono';font-weight:400}
.lock{display:inline-flex;align-items:center;gap:8px;margin-top:20px;padding:9px 14px;border:1px solid color-mix(in srgb,var(--qr) 34%,var(--line));border-radius:999px;background:color-mix(in srgb,var(--qr) 7%,transparent);font-size:13.5px;color:#bfe8cf}
.lock b{color:var(--qr)}

/* layer table */
.ltab{width:100%;border-collapse:collapse;font-size:14.5px}
.ltab th,.ltab td{text-align:left;padding:11px 14px;border-bottom:1px solid var(--line)}
.ltab th{font-size:11.5px;text-transform:uppercase;letter-spacing:.06em;color:var(--dim);font-weight:600}
.ltab td.reg{font-family:'JetBrains Mono';color:var(--signal);font-size:13px}
.ltab td.n{font-family:'JetBrains Mono';color:var(--fg)}
.ltab tr:hover td{background:var(--panel2)}

/* callout */
.note{background:color-mix(in srgb,var(--amber) 8%,var(--panel));border:1px solid color-mix(in srgb,var(--amber) 34%,var(--line));border-radius:12px;padding:14px 18px;color:#f1d9b3;font-size:14.5px}
.note b{color:var(--amber)}
code{font-family:'JetBrains Mono';background:#060a10;border:1px solid var(--line);padding:1px 6px;border-radius:5px;font-size:.86em}

footer.site{border-top:1px solid var(--line);margin-top:20px;padding:34px 0 60px;color:var(--dim);font-size:13.5px}
footer.site .row{display:flex;flex-wrap:wrap;gap:18px 40px;justify-content:space-between}
footer.site a{color:var(--muted)}
.pill{display:inline-flex;gap:7px;align-items:center;font-family:'JetBrains Mono';font-size:12px;color:var(--qr);border:1px solid color-mix(in srgb,var(--qr) 40%,var(--line));border-radius:999px;padding:4px 11px}
.pill .d{width:7px;height:7px;border-radius:50%;background:var(--qr);box-shadow:0 0 8px var(--qr)}

@media (max-width:640px){.hero{padding:48px 0 20px}.nav a.tab{padding:6px 9px}}
@media (prefers-reduced-motion:no-preference){
  .reveal{animation:rise .7s cubic-bezier(.2,.7,.2,1) both}
  @keyframes rise{from{opacity:0;transform:translateY(14px)}to{opacity:1;transform:none}}
  .spec-mark{animation:pop .5s ease both}@keyframes pop{from{opacity:0}to{opacity:1}}
}
"""

FONTS = ("<link rel='preconnect' href='https://fonts.googleapis.com'>"
         "<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>"
         "<link href='https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@500;600;700"
         "&family=JetBrains+Mono:wght@400;500;700&family=Inter:wght@400;500;600&display=swap' rel='stylesheet'>")

GLYPH = ("<svg class='glyph' viewBox='0 0 32 32' fill='none' aria-hidden='true'>"
         "<rect x='1.5' y='1.5' width='29' height='29' rx='8' stroke='#1e2a37' stroke-width='1.5'/>"
         "<path d='M7 20 L11 20 L13 10 L16 24 L19 13 L21 20 L25 20' stroke='#4fd1c5' "
         "stroke-width='2' stroke-linecap='round' stroke-linejoin='round'/></svg>")

TABS = [("Home", "index.html", "home"), ("Benchmarks", "benchmarks.html", "benchmarks"),
        ("Docs", "docs/index.html", "docs")]


def nav(active, prefix=""):
    links = "".join(
        f"<a class='tab{' active' if key==active else ''}' href='{prefix}{href}'>{name}</a>"
        for name, href, key in TABS)
    gh = (f"<a class='gh' href='{GH}' aria-label='GitHub'>"
          "<svg width='19' height='19' viewBox='0 0 16 16' fill='currentColor'><path d='M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z'/></svg></a>")
    return (f"<div class='nav'><div class='row'><a class='brand' href='{prefix}index.html'>{GLYPH}robobus</a>"
            f"<nav class='links'>{links}{gh}</nav></div></div>")


def page(title, active, body, prefix="", extra_head="", desc=""):
    d = html.escape(desc or "Post-quantum, real-time robotics middleware — measured, not claimed.")
    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{html.escape(title)}</title><meta name='description' content='{d}'>"
            f"{FONTS}<style>{CSS}</style>{extra_head}</head><body>"
            f"{nav(active,prefix)}{body}"
            f"<footer class='site'><div class='wrap'><div class='row'>"
            f"<div>robobus — post-quantum, real-time robotics middleware. "
            f"CNSA 2.0 (FIPS 203 ML-KEM · FIPS 204 ML-DSA).</div>"
            f"<div><a href='{prefix}index.html'>Home</a> · <a href='{prefix}benchmarks.html'>Benchmarks</a> "
            f"· <a href='{prefix}docs/index.html'>Docs</a> · <a href='{GH}'>GitHub</a></div>"
            f"</div></div></footer></body></html>")


# ---------------------------------------------------------------------------------------------
# the latency spectrum — the signature. log axis 1ns .. 10ms with the measured layers plotted.
# ---------------------------------------------------------------------------------------------
def latency_spectrum():
    import math
    lo, hi = 1e-9, 1e-2            # 1 ns .. 10 ms  (7 decades)
    W, H = 1040, 250
    padL, padR, base = 12, 12, 176
    span = W - padL - padR
    llo, lhi = math.log10(lo), math.log10(hi)

    def x(sec):
        return padL + span * (math.log10(sec) - llo) / (lhi - llo)

    # regime bands — the "orders of magnitude" made visible
    bands = [(1e-9, 1e-6, "nanoseconds", "#0f2a2b"),   # ns
             (1e-6, 1e-3, "microseconds", "#181633"),  # µs
             (1e-3, 1e-2, "milliseconds", "#2a1e17")]  # ms
    marks = [  # seconds, label, value, cssvar, label-y, anchor  (explicit so nothing collides)
        (3.9e-9,  "Bus op",           "3.9 ns",     "--signal", 130, "middle"),
        (83e-9,   "Bus one-way IPC",  "83 ns",      "--signal", 88,  "middle"),
        (135e-6,  "PQC key agreement","≈135 µs",    "--hybrid", 130, "middle"),
        (1.15e-3, "Auth handshake",   "0.6–1.2 ms", "--pqc",    70,  "end"),
        (2.0e-3,  "DDS-Sec window",   "≈2 ms",      "--amber",  112, "start"),
    ]
    S = [f"<svg class='spec-svg' viewBox='0 0 {W} {H}' role='img' "
         f"aria-label='Latency spectrum from nanoseconds to milliseconds, log scale'>",
         "<defs><linearGradient id='sg' x1='0' x2='1'>"
         "<stop offset='0' stop-color='#4fd1c5'/><stop offset='.5' stop-color='#8b7cff'/>"
         "<stop offset='1' stop-color='#f4b46a'/></linearGradient>"
         "<filter id='glow' x='-60%' y='-60%' width='220%' height='220%'>"
         "<feGaussianBlur stdDeviation='3.2' result='b'/><feMerge>"
         "<feMergeNode in='b'/><feMergeNode in='SourceGraphic'/></feMerge></filter></defs>"]
    # bands + zone labels (labels near the top edge, dim — clearly background)
    for a, b, lab, fill in bands:
        xa, xb = x(a), x(b)
        S.append(f"<rect x='{xa:.1f}' y='16' width='{xb-xa:.1f}' height='{base-16}' fill='{fill}' opacity='.5'/>")
        S.append(f"<text x='{(xa+xb)/2:.1f}' y='30' fill='#46586a' font-size='10.5' letter-spacing='2.5' "
                 f"font-family='JetBrains Mono' text-anchor='middle'>{lab.upper()}</text>")
        S.append(f"<line x1='{xb:.1f}' y1='16' x2='{xb:.1f}' y2='{base}' stroke='#223040' stroke-width='1' stroke-dasharray='2 4'/>")
    # baseline
    S.append(f"<line x1='{padL}' y1='{base}' x2='{W-padR}' y2='{base}' stroke='url(#sg)' stroke-width='2.5'/>")
    # decade ticks
    for e in range(-9, -1):
        sec = 10.0**e; xx = x(sec)
        lab = {-9:"1 ns",-6:"1 µs",-3:"1 ms",-2:"10 ms"}.get(e, "")
        S.append(f"<line x1='{xx:.1f}' y1='{base-4}' x2='{xx:.1f}' y2='{base+5}' stroke='#33475a' stroke-width='1'/>")
        if lab:
            S.append(f"<text x='{xx:.1f}' y='{base+22}' fill='#6d8296' font-size='11.5' "
                     f"font-family='JetBrains Mono' text-anchor='middle'>{lab}</text>")
    # markers: value chip + label above, leader line to a glowing dot on the baseline
    for i, (sec, label, val, var, ly, anchor) in enumerate(marks):
        xx = x(sec)
        tx = xx + (-4 if anchor == 'end' else 4 if anchor == 'start' else 0)
        S.append(f"<g class='spec-mark' style='animation-delay:{i*.07+.15:.2f}s'>")
        S.append(f"<line x1='{xx:.1f}' y1='{ly+8}' x2='{xx:.1f}' y2='{base-3}' stroke='var({var})' stroke-width='1.2' opacity='.45'/>")
        S.append(f"<circle cx='{xx:.1f}' cy='{base}' r='5' fill='var({var})' filter='url(#glow)'/>")
        S.append(f"<circle cx='{xx:.1f}' cy='{base}' r='5' fill='var({var})'/>")
        S.append(f"<text x='{tx:.1f}' y='{ly}' fill='var({var})' font-size='15' font-weight='700' "
                 f"font-family='JetBrains Mono' text-anchor='{anchor}'>{val}</text>")
        S.append(f"<text x='{tx:.1f}' y='{ly-18}' fill='#9fb0bf' font-size='12' "
                 f"font-family='Inter' text-anchor='{anchor}'>{html.escape(label)}</text>")
        S.append("</g>")
    S.append("</svg>")
    return "".join(S)


def home():
    spec = latency_spectrum()
    stats = [
        ("3.9<small>ns</small>", "Shared-memory bus op (amortized), Apple M5"),
        ("83<small>ns</small>", "Bus one-way IPC · p50 · 98%+ &lt; 100 ns (RT)"),
        ("≈135<small>µs</small>", "PQC key agreement — ECDH ‖ ML-KEM → HKDF-384"),
        ("5<small>ISAs</small>", "PQC byte-portable: x86-64, aarch64, armv7, s390x (BE), riscv64, ppc64le"),
        ("4<small>OS</small>", "Handshake measured on Linux, macOS, Windows (MSVC + WSL2)"),
        ("9<small>orders</small>", "Latency regimes spanned — ns to ms — each measured on its own terms"),
    ]
    stat_html = "".join(f"<div class='stat'><div class='n mono'>{n}</div><div class='l'>{l}</div></div>"
                        for n, l in stats)
    layers = [
        ("Shared-memory bus op (amortized)", "nanoseconds", "3.9 ns/op"),
        ("Bus one-way IPC latency", "nanoseconds", "p50 83 ns"),
        ("Per-message AEAD (AES-256-GCM)", "ns / byte", "multi-GB/s"),
        ("Key agreement / rekey (ECDH+ML-KEM)", "microseconds", "129–142 µs"),
        ("Full authenticated handshake", "µs → ~1 ms", "0.6 → 1.15 ms"),
        ("DDS-Security handshake window", "milliseconds", "≈2 ms (isolated)"),
    ]
    layer_rows = "".join(
        f"<tr><td>{html.escape(a)}</td><td class='reg'>{html.escape(b)}</td><td class='n'>{html.escape(c)}</td></tr>"
        for a, b, c in layers)
    feats = [
        ("crypto", "pqc", "CNSA 2.0 post-quantum",
         "FIPS 203 ML-KEM and FIPS 204 ML-DSA, hybridised with classical ECDH/ECDSA through "
         "HKDF-SHA384 — the NSA CNSA 2.0 transition profile, not a toy."),
        ("transport", "", "Sub-microsecond bus",
         "A lock-free shared-memory SPSC ring in C: single-digit-nanosecond ops, p50 one-way IPC "
         "under 100 ns, formally proven (CBMC) and RT-hardened."),
        ("dds", "hybrid", "PQC-hardened DDS-Security",
         "Patched CycloneDDS & Fast DDS authentication: hybrid ECDH+ML-KEM key agreement and "
         "ML-DSA-87 identity signatures, measured live on Linux, macOS and Windows."),
        ("proof", "qr", "Measured, not claimed",
         "One capability-detecting script across every platform; QEMU byte-portability on five "
         "ISAs incl. big-endian s390x; CBMC + SymbiYosys formal proofs of the ring."),
    ]
    feat_html = "".join(
        f"<div class='fcard'><div class='k'>{html.escape(k)}</div>"
        f"<h3 class='{cls}'>{html.escape(t)}</h3><p>{p}</p></div>"
        for k, cls, t, p in feats)
    # transports — the universal-bridge story (any link takes --security cnsa20)
    xports = [
        ("Robotics &amp; real-time",
         [("ROS 2", "rclpy"), ("ROS 1", "rospy"), ("DDS", "topic"),
          ("Zenoh", "eclipse"), ("ZeroCM", "zcm"), ("CAN bus", "python-can")]),
        ("Messaging &amp; streaming",
         [("MQTT", "IoT"), ("Apache Kafka", "pipelines"), ("AMQP", "RabbitMQ")]),
        ("Wire &amp; edge",
         [("UDP", "uni/multicast"), ("TCP", "stdlib"), ("Serial", "radio")]),
        ("Biosignals",
         [("LSL", "Lab Streaming Layer")]),
    ]
    xhtml = "".join(
        f"<div class='xgrp'><div class='xh'>{title}</div><div class='xrow'>" +
        "".join(f"<div class='chip'>{name}<small>{tag}</small></div>" for name, tag in chips) +
        "</div></div>" for title, chips in xports)

    body = f"""
<header class='hero'><div class='wrap reveal'>
  <p class='eyebrow'>post-quantum · real-time · robotics middleware</p>
  <h1>Latency is not one number. So we measured <em>all nine orders of magnitude.</em></h1>
  <p class='lede'>A sub-microsecond shared-memory bus that bridges ROS&nbsp;1/2, LSL, MQTT, Kafka,
  Zenoh, CAN, serial and more — and wraps <em>any</em> link in CNSA&nbsp;2.0 post-quantum crypto,
  even protocols with no security of their own. Benchmarked end to end by one portable script.</p>
  <div class='cta'>
    <a class='btn primary' href='benchmarks.html'>See the benchmarks →</a>
    <a class='btn ghost' href='docs/index.html'>Read the docs</a>
  </div>
  <div class='spectrum'>
    <div class='cap'><b>The measured stack</b><span>log scale · 1 ns → 10 ms</span></div>
    <div class='spec-scroll'>{spec}</div>
  </div>
</div></header>

<section><div class='wrap'>
  <p class='sec-eyebrow'>headline · Apple M5 baseline</p>
  <h2 class='title'>What it does, in numbers</h2>
  <p class='sec-lede'>Every figure below is produced by <code>run_benchmarks.py</code> and refreshed
  on CI. Numbers are CPU/OS/build-specific — the deliverable is the method.</p>
  <div class='stats'>{stat_html}</div>
</div></section>

<section><div class='wrap'>
  <p class='sec-eyebrow'>the whole point</p>
  <h2 class='title'>Read the layers</h2>
  <p class='sec-lede'>The stack spans nine orders of magnitude and each layer has its own regime —
  conflating them is how benchmarks lie. The runtime hot path is ns/GB·s; handshakes are a
  one-time per-peer cost amortised to zero over a session.</p>
  <div style='overflow-x:auto'><table class='ltab'><thead><tr><th>Layer</th><th>Regime</th><th>Apple M5</th></tr></thead>
  <tbody>{layer_rows}</tbody></table></div>
</div></section>

<section><div class='wrap'>
  <p class='sec-eyebrow'>one bus · every transport</p>
  <h2 class='title'>Bridges everything — and secures the links that can't secure themselves</h2>
  <p class='sec-lede'>robobus sits at the centre as a post-quantum-secured hub; a thin bridge maps
  each protocol's topics or streams onto bus channels. And <b>any</b> bridge takes
  <code>--security cnsa20 --keyfile</code> — so CNSA&nbsp;2.0 crypto wraps MQTT, Kafka, serial or
  CAN exactly as it wraps DDS, even where the wire protocol has no security of its own.</p>
  <div class='xgrid'>{xhtml}</div>
  <div class='lock'>🔒&nbsp;<span><b>Post-quantum on any link.</b> One <code>--security</code> flag seals the
  payload the same way regardless of transport — ML-KEM key agreement, AES-256-GCM, ML-DSA identity.</span></div>
</div></section>

<section><div class='wrap'>
  <p class='sec-eyebrow'>reach it from any language</p>
  <h2 class='title'>Five native implementations, fourteen generated</h2>
  <p class='sec-lede'>The wire format is small — an mmap seqlock ring, a codec frame, an
  AES-256-GCM frame, fixed-layout schema structs. Five languages implement it natively and are
  <b>bidirectionally conformance-tested against Python</b> (Python seals → the other opens, and
  back); the schema layout is code-generated for fourteen more, each compile/run-verified
  against Python's packed bytes.</p>
  <div class='xrow' style='margin:0 0 16px'>
    <div class='chip'>Python<small>reference</small></div>
    <div class='chip'>C<small>native ring</small></div>
    <div class='chip'>Rust<small>crates.io</small></div>
    <div class='chip'>JavaScript · Node<small>npm</small></div>
    <div class='chip'>Java<small>Maven Central</small></div>
  </div>
  <p style='color:var(--muted);font-size:13.5px;margin:0'><span style='font-family:"JetBrains Mono";
  font-size:11.5px;letter-spacing:.06em;color:var(--dim)'>SCHEMA CODEGEN · 14 &nbsp;</span>
  C · C++ · Rust · Go · Java · C# · TypeScript · Python · Julia · MATLAB/Octave · Swift · Kotlin · Ruby · Lua</p>
</div></section>

<section><div class='wrap'>
  <p class='sec-eyebrow'>architecture</p>
  <h2 class='title'>Four things, done to standard</h2>
  <div class='cards'>{feat_html}</div>
</div></section>

<section><div class='wrap'>
  <p class='sec-eyebrow'>honest measurement</p>
  <h2 class='title'>How the numbers are made</h2>
  <p class='sec-lede'>Nanosecond timing uses amortised batching (a single <code>clock_gettime</code>
  on macOS is only ~1&nbsp;µs granular); a 20k-message warmup is discarded so cold-start jitter
  doesn't pollute the steady-state tail; DDS handshakes are reported as the isolated FSM window
  (begin → OK), not the ~100&nbsp;ms process wall-clock (startup + SPDP discovery + teardown).</p>
  <div class='note'><b>Coverage, honestly.</b> The public site's CI runners are
  <b>virtualized</b> (shared vCPUs, no real-time scheduling), so their columns are for
  cross-platform coverage and relative comparison — not bare-metal nanosecond claims. Each run
  self-labels its measurement fidelity.</div>
  <p style='margin-top:22px'><a class='btn ghost' href='benchmarks.html'>Open the full report →</a></p>
</div></section>
"""
    return page("robobus — post-quantum, real-time robotics middleware", "home", body,
                desc="A sub-microsecond bus, CNSA 2.0 post-quantum crypto, and PQC-hardened "
                     "DDS-Security — measured across nine orders of magnitude.")


# ---------------------------------------------------------------------------------------------
# benchmarks page — wrap render_report's body in the shell, re-themed to the site palette
# ---------------------------------------------------------------------------------------------
def benchmarks():
    import render_report as R
    docs = R.load_all()
    inner = R.render_html(docs) if docs else "<div class='wrap'><p>No benchmark data found.</p></div>"
    # extract render_report's <style> and its <body> inner content
    m_style = re.search(r"<style>(.*?)</style>", inner, re.S)
    rep_css = m_style.group(1) if m_style else ""
    m_body = re.search(r"<body>(.*?)</body>", inner, re.S)
    rep_body = m_body.group(1) if m_body else inner
    # drop the report's own H1 + sub — our intro section is the page header (avoids duplication)
    rep_body = re.sub(r"<h1>robobus / PQC-DDS[^<]*</h1>", "", rep_body)
    rep_body = re.sub(r"<p class='sub'>.*?</p>", "", rep_body, count=1, flags=re.S)
    # re-theme: our tokens override render_report's :root; keep the site fonts (its body{font:...}
    # shorthand would otherwise reset the family) and align its wrap width to ours.
    override = ("<style>" + rep_css +
                ":root{--bg:#0a0e13;--panel:#111a24;--line:#1e2a37;--fg:#e9eef4;--muted:#8a9bab;--accent:#4fd1c5}"
                "body{font-family:'Inter',ui-sans-serif,system-ui,sans-serif}"
                ".wrap{max-width:var(--maxw,1080px)}"
                "table{display:block;overflow-x:auto;max-width:100%}"  # wide data tables scroll on mobile
                "</style>")
    # inject a clean page header at the top of the report's own wrap (one flow → no dead gap)
    header = ("<p style=\"font-family:'JetBrains Mono';font-size:12px;letter-spacing:.14em;"
              "text-transform:uppercase;color:#8a9bab;margin:0 0 10px\">Live · refreshed on CI</p>"
              "<div style=\"font-family:'Space Grotesk';font-weight:600;font-size:clamp(26px,4vw,36px);"
              "letter-spacing:-.02em;margin:0 0 22px;color:#e9eef4\">Full-system benchmarks</div>")
    rep_body = rep_body.replace("<div class='wrap'>", "<div class='wrap'>" + header, 1)
    return page("Benchmarks · robobus", "benchmarks", rep_body, extra_head=override,
                desc="Full-system post-quantum & real-time benchmarks for robobus, refreshed on CI.")


# ---------------------------------------------------------------------------------------------
# docs — render docs-src/*.md with a sidebar
# ---------------------------------------------------------------------------------------------
DOC_ORDER = ["ARCHITECTURE", "PROTOCOL", "SECURITY", "COMPLIANCE", "CMVP-READINESS",
             "CRYPTO-PROVENANCE", "PORTABILITY", "DETERMINISM", "REALTIME", "SUPPLY-CHAIN",
             "BINDINGS", "ROADMAP"]
DOC_TITLES = {
    "ARCHITECTURE": "Architecture", "PROTOCOL": "Wire protocol", "SECURITY": "Security model",
    "COMPLIANCE": "Compliance", "CMVP-READINESS": "CMVP readiness",
    "CRYPTO-PROVENANCE": "Crypto provenance", "PORTABILITY": "Portability",
    "DETERMINISM": "Determinism", "REALTIME": "Real-time", "SUPPLY-CHAIN": "Supply chain",
    "BINDINGS": "Language bindings", "ROADMAP": "Roadmap"}


def _md(text):
    try:
        import markdown
    except ImportError:
        return "<pre>" + html.escape(text) + "</pre>"
    return markdown.markdown(text, extensions=["tables", "fenced_code", "toc", "sane_lists", "attr_list"])


def _slug(name):
    return name.lower()


def doc_sidebar(active, present):
    items = "".join(
        f"<a href='{_slug(n)}.html' class='ditem{' active' if n==active else ''}'>{html.escape(DOC_TITLES.get(n,n))}</a>"
        for n in DOC_ORDER if n in present)
    return f"<aside class='dside'><div class='dside-t'>Documentation</div>{items}</aside>"


DOCS_CSS = """
<style>
.dwrap{max-width:var(--maxw);margin:0 auto;padding:34px 22px 40px;display:grid;grid-template-columns:220px 1fr;gap:34px;align-items:start}
.dside{position:sticky;top:70px;font-size:14px}
.dside-t{font-family:'JetBrains Mono';font-size:11.5px;letter-spacing:.12em;text-transform:uppercase;color:var(--dim);margin:0 0 10px;padding-left:12px}
.dside a.ditem{display:block;color:var(--muted);padding:7px 12px;border-radius:8px;border-left:2px solid transparent}
.dside a.ditem:hover{color:var(--fg);background:var(--panel);text-decoration:none}
.dside a.ditem.active{color:var(--signal);border-left-color:var(--signal);background:color-mix(in srgb,var(--signal) 9%,transparent)}
.dbody{min-width:0}
.dbody h1{font-size:clamp(26px,4vw,38px);margin:0 0 8px;letter-spacing:-.02em}
.dbody h2{font-size:23px;margin:36px 0 10px;padding-top:14px;border-top:1px solid var(--line)}
.dbody h3{font-size:18px;margin:26px 0 8px;color:var(--fg)}
.dbody p,.dbody li{color:#cdd6e0}
.dbody a{color:var(--signal)}
.dbody code{font-family:'JetBrains Mono';background:#060a10;border:1px solid var(--line);padding:1px 6px;border-radius:5px;font-size:.85em}
.dbody pre{background:#060a10;border:1px solid var(--line);border-radius:10px;padding:15px 17px;overflow:auto;font-size:13px}
.dbody pre code{background:none;border:none;padding:0}
.dbody table{border-collapse:collapse;width:100%;margin:16px 0;font-size:14px;display:block;overflow-x:auto}
.dbody th,.dbody td{border:1px solid var(--line);padding:9px 12px;text-align:left}
.dbody th{background:var(--panel);color:var(--fg);font-family:'Space Grotesk'}
.dbody tr:hover td{background:var(--panel2)}
.dbody blockquote{border-left:3px solid var(--signal);margin:14px 0;padding:2px 16px;color:var(--muted);background:var(--panel2);border-radius:0 8px 8px 0}
.dbody hr{border:none;border-top:1px solid var(--line);margin:26px 0}
.dbody ul,.dbody ol{padding-left:22px}
.dbody li{margin:5px 0}
.dlede{color:var(--muted);margin:0 0 22px;font-size:15px}
@media (max-width:760px){.dwrap{grid-template-columns:1fr}.dside{position:static;display:flex;flex-wrap:wrap;gap:4px}.dside-t{width:100%}}
</style>"""


def docs_pages():
    present = {}
    if os.path.isdir(DOCS_SRC):
        for f in glob.glob(os.path.join(DOCS_SRC, "*.md")):
            present[os.path.splitext(os.path.basename(f))[0]] = f
    out = {}
    ordered = [n for n in DOC_ORDER if n in present] + [n for n in present if n not in DOC_ORDER]
    # index
    cards = "".join(
        f"<a class='fcard' href='{_slug(n)}.html' style='text-decoration:none;display:block'>"
        f"<h3 style='color:var(--fg)'>{html.escape(DOC_TITLES.get(n,n))}</h3>"
        f"<p>{html.escape(_first_line(present[n]))}</p></a>" for n in ordered)
    idx_body = (f"<div class='dwrap'>{doc_sidebar(None, present)}<div class='dbody'>"
                f"<h1>Documentation</h1><p class='dlede'>Design, protocol, security and compliance "
                f"references for the robobus stack.</p><div class='cards'>{cards}</div></div></div>")
    out["index"] = page("Docs · robobus", "docs", idx_body, prefix="../", extra_head=DOCS_CSS,
                        desc="Design, protocol, security and compliance documentation for robobus.")
    for n in ordered:
        with open(present[n]) as fh:
            md = fh.read()
        html_body = _md(md)
        body = (f"<div class='dwrap'>{doc_sidebar(n, present)}"
                f"<article class='dbody'>{html_body}</article></div>")
        out[_slug(n)] = page(f"{DOC_TITLES.get(n,n)} · robobus docs", "docs", body,
                             prefix="../", extra_head=DOCS_CSS,
                             desc=_first_line(present[n]))
    return out, present


def _first_line(path):
    try:
        with open(path) as f:
            for line in f:
                s = line.strip().lstrip("#").strip()
                if s and not s.startswith("!") and not s.startswith("|"):
                    return s[:150]
    except OSError:
        pass
    return ""


def main():
    os.makedirs(SITE, exist_ok=True)
    os.makedirs(os.path.join(SITE, "docs"), exist_ok=True)
    open(os.path.join(SITE, "index.html"), "w").write(home())
    open(os.path.join(SITE, "benchmarks.html"), "w").write(benchmarks())
    docs, present = docs_pages()
    for slug, content in docs.items():
        open(os.path.join(SITE, "docs", f"{slug}.html"), "w").write(content)
    print(f"[build_site] wrote index.html, benchmarks.html, docs/ ({len(docs)} pages: "
          f"{', '.join(sorted(present)) or 'none — add docs-src/*.md'})")


if __name__ == "__main__":
    main()
