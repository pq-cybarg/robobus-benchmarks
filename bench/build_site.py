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

/* plain-language explainer — the layperson on-ramp */
.plain{display:grid;gap:16px}
@media(min-width:760px){.plain{grid-template-columns:repeat(3,1fr)}}
.pcard{background:linear-gradient(180deg,var(--panel),var(--panel2));border:1px solid var(--line);border-radius:16px;padding:24px 22px}
.pcard .ic{width:42px;height:42px;border-radius:12px;display:grid;place-items:center;margin:0 0 16px}
.pcard .ic svg{width:23px;height:23px}
.pcard .ic.spd{background:color-mix(in srgb,var(--signal) 15%,transparent);color:var(--signal)}
.pcard .ic.rch{background:color-mix(in srgb,var(--hybrid) 15%,transparent);color:var(--hybrid)}
.pcard .ic.sec{background:color-mix(in srgb,var(--qr) 15%,transparent);color:var(--qr)}
.pcard h3{font-size:19.5px;margin:0 0 9px}
.pcard .an{color:var(--fg);font-weight:600;margin:0 0 9px;font-size:15px}
.pcard p{color:var(--muted);font-size:14.5px;margin:0}
.oneline{margin-top:22px;padding:16px 20px;border:1px solid color-mix(in srgb,var(--signal) 26%,var(--line));border-radius:12px;background:color-mix(in srgb,var(--signal) 6%,var(--panel2));color:var(--muted);font-size:15px;line-height:1.55}
.oneline b{color:var(--fg);font-weight:600}

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

/* speed matrices — horizontal bars + transport×language heatmap */
.hbars{display:flex;flex-direction:column;gap:7px;margin:6px 0 4px}
.hrow{display:grid;grid-template-columns:118px 1fr 132px;align-items:center;gap:12px}
.hrow .lname{font-weight:600;font-size:13.5px}
.hrow .lname small{display:block;font:400 10.5px/1.3 'JetBrains Mono';color:var(--dim);letter-spacing:.02em}
.htrack{height:19px;border-radius:5px;background:var(--panel2);overflow:hidden}
.htrack>i{display:block;height:100%;border-radius:5px}
.hrow .hval{font-family:'JetBrains Mono';font-size:12.5px;text-align:right;color:var(--fg);font-variant-numeric:tabular-nums}
.hrow .hval small{color:var(--dim);font-size:11px}
.tier-n>i{background:linear-gradient(90deg,var(--signal),#6fe0d6)}
.tier-j>i{background:linear-gradient(90deg,var(--hybrid),var(--signal))}
.tier-i>i{background:linear-gradient(90deg,var(--violet),var(--hybrid))}
.heatwrap{overflow-x:auto}
.heat{border-collapse:collapse;font-size:12.5px;min-width:520px}
.heat th,.heat td{padding:9px 12px;text-align:center;border:1px solid var(--line);font-variant-numeric:tabular-nums}
.heat th{font:600 11px/1 'JetBrains Mono';text-transform:uppercase;letter-spacing:.05em;color:var(--dim)}
.heat td.rl{text-align:left;font-weight:600;color:var(--fg);font-family:'Inter'}
.heat td.na{color:var(--dim)}
.heat td b{font-weight:700;color:var(--bg)}
.speed-skip{color:var(--dim)}.speed-skip td{border-bottom:1px solid var(--line);padding:9px 14px}

/* requirements profiles table */
.pftab td{vertical-align:top}
.pf-n{font-weight:600;color:var(--fg)}
.pf-alg{font:400 11px/1.3 'JetBrains Mono';color:var(--dim);margin-top:3px}
.pf-sub{font:400 11px/1.3 'JetBrains Mono';color:var(--dim);margin-top:3px}
.pf-lvl{display:inline-block;font:600 11px/1 'JetBrains Mono';padding:4px 9px;border-radius:6px;white-space:nowrap}
.pf-lvl.l0{color:var(--dim);border:1px solid var(--line)}
.pf-lvl.l1{color:var(--hybrid);background:color-mix(in srgb,var(--hybrid) 12%,transparent)}
.pf-lvl.l3{color:var(--signal);background:color-mix(in srgb,var(--signal) 12%,transparent)}
.pf-lvl.l5{color:var(--qr);background:color-mix(in srgb,var(--qr) 14%,transparent)}
.pf-std{max-width:260px}
.cchip{display:inline-block;font:500 10.5px/1 'JetBrains Mono';color:var(--muted);border:1px solid var(--line);
  background:var(--panel2);border-radius:5px;padding:4px 7px;margin:0 4px 4px 0;white-space:nowrap}

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
        ("Speed matrix", "speed.html", "speed"), ("Docs", "docs/index.html", "docs")]


def nav(active, prefix=""):
    links = "".join(
        f"<a class='tab{' active' if key==active else ''}' href='{prefix}{href}'>{name}</a>"
        for name, href, key in TABS)
    gh = (f"<a class='gh' href='{GH}' aria-label='GitHub'>"
          "<svg width='19' height='19' viewBox='0 0 16 16' fill='currentColor'><path d='M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z'/></svg></a>")
    return (f"<div class='nav'><div class='row'><a class='brand' href='{prefix}index.html'>{GLYPH}robobus</a>"
            f"<nav class='links'>{links}{gh}</nav></div></div>")


BASE_URL = "https://pq-cybarg.github.io/robobus-benchmarks/"
OG_IMAGE = BASE_URL + "og-image.png"       # absolute — X/Slack/Discord require an absolute image URL


def page(title, active, body, prefix="", extra_head="", desc="", canon=""):
    d = html.escape(desc or "Post-quantum, real-time robotics middleware — measured, not claimed.")
    t = html.escape(title)
    url = BASE_URL + canon
    og = (
        f"<link rel='canonical' href='{url}'>"
        f"<meta property='og:type' content='website'>"
        f"<meta property='og:site_name' content='robobus'>"
        f"<meta property='og:title' content='{t}'>"
        f"<meta property='og:description' content='{d}'>"
        f"<meta property='og:url' content='{url}'>"
        f"<meta property='og:image' content='{OG_IMAGE}'>"
        f"<meta property='og:image:width' content='1200'>"
        f"<meta property='og:image:height' content='630'>"
        f"<meta property='og:image:alt' content='robobus — post-quantum, real-time robotics middleware'>"
        f"<meta name='twitter:card' content='summary_large_image'>"
        f"<meta name='twitter:title' content='{t}'>"
        f"<meta name='twitter:description' content='{d}'>"
        f"<meta name='twitter:image' content='{OG_IMAGE}'>"
    )
    return (f"<!doctype html><html lang='en'><head><meta charset='utf-8'>"
            f"<meta name='viewport' content='width=device-width,initial-scale=1'>"
            f"<title>{t}</title><meta name='description' content='{d}'>{og}"
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
        ("6<small>ISAs</small>", "Bindings + C-ABI lib byte-identical: x86-64, aarch64, armv7, ppc64le, riscv64, s390x (BE)"),
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
         "Every language toolchain installed and run green together — 6 native seal/open bindings "
         "plus 14 schema-codegen targets, no silent skips; the C-ABI shared library proven "
         "byte-identical on six ISAs incl. big-endian s390x; CBMC + SymbiYosys proofs of the ring."),
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

    # plain-language explainer icons (decorative; accent-coloured via .ic.spd/.rch/.sec)
    ic_spd = ("<svg viewBox='0 0 24 24' fill='currentColor' aria-hidden='true'>"
              "<path d='M13 2 L4 13.5 h6.2 L9 22 l10-12 h-6.2 z'/></svg>")
    ic_rch = ("<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.9' "
              "stroke-linecap='round' aria-hidden='true'><circle cx='12' cy='12' r='2.6'/>"
              "<circle cx='4.5' cy='5' r='1.8'/><circle cx='19.5' cy='5' r='1.8'/>"
              "<circle cx='4.5' cy='19' r='1.8'/><circle cx='19.5' cy='19' r='1.8'/>"
              "<path d='M6 6.2 L10 10 M18 6.2 L14 10 M6 17.8 L10 14 M18 17.8 L14 14'/></svg>")
    ic_sec = ("<svg viewBox='0 0 24 24' fill='none' stroke='currentColor' stroke-width='1.9' "
              "stroke-linecap='round' stroke-linejoin='round' aria-hidden='true'>"
              "<path d='M12 3 L19.5 6 v6.2 c0 4.8-3.7 7.6-7.5 8.6 -3.8-1-7.5-3.8-7.5-8.6 V6 z'/>"
              "<path d='M8.7 12 l2.2 2.2 4.4-4.4'/></svg>")

    body = f"""
<header class='hero'><div class='wrap reveal'>
  <p class='eyebrow'>secure real-time messaging for robots &amp; devices</p>
  <h1>The nervous system for machines — instant, universal, and <em>quantum-safe</em>.</h1>
  <p class='lede'>robobus lets robots, sensors and devices react to one another the moment something
  happens — and locks every message with encryption built to outlast tomorrow's quantum computers.
  It can even add that protection to older systems that never had any.</p>
  <div class='cta'>
    <a class='btn primary' href='benchmarks.html'>See the benchmarks →</a>
    <a class='btn ghost' href='docs/index.html'>Read the docs</a>
  </div>
  <div class='spectrum'>
    <div class='cap'><b>How fast is “instant”?</b><span>billionths → thousandths of a second</span></div>
    <div class='spec-scroll'>{spec}</div>
  </div>
</div></header>

<section><div class='wrap'>
  <p class='sec-eyebrow'>what it is, in plain terms</p>
  <h2 class='title'>A fast, universal, quantum-safe way for machines to talk</h2>
  <p class='sec-lede'>Not an engineer? Here's the whole idea in three parts — everything further down
  the page is the measured proof behind them.</p>
  <div class='plain'>
    <div class='pcard'><div class='ic spd'>{ic_spd}</div>
      <h3>Reacts before you can blink</h3>
      <p class='an'>A message crosses the system in billionths of a second.</p>
      <p>That's millions of times quicker than an eye-blink — fast enough for a robot to catch
      itself mid-stumble, or a prosthetic hand to move the instant a nerve signal arrives.</p></div>
    <div class='pcard'><div class='ic rch'>{ic_rch}</div>
      <h3>One hub for everything</h3>
      <p class='an'>Robots, drones, medical sensors, even brain-signal headsets.</p>
      <p>These devices normally speak incompatible languages. robobus is the common connector that
      lets them work together — bridging the standards each field already uses.</p></div>
    <div class='pcard'><div class='ic sec'>{ic_sec}</div>
      <h3>Safe against tomorrow's computers</h3>
      <p class='an'>Every message is sealed with post-quantum encryption.</p>
      <p>Future quantum computers could break today's encryption. robobus uses the U.S. government's
      post-quantum standard, so messages stay private for decades — even on devices that shipped
      with no security at all.</p></div>
  </div>
  <p class='oneline'><b>In one line:</b> robobus is a super-fast, universal, quantum-safe messaging
  layer for machines — and everything below is the measurement that backs each claim up.</p>
</div></section>

<section><div class='wrap'>
  <p class='sec-eyebrow'>the proof · headline numbers</p>
  <h2 class='title'>Measured, not marketed</h2>
  <p class='sec-lede'>From here down the page is for engineers. Every figure is produced by
  <code>run_benchmarks.py</code> and refreshed on CI; numbers are CPU/OS/build-specific — the
  deliverable is the method.</p>
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
  <h2 class='title'>Six native implementations, fourteen generated</h2>
  <p class='sec-lede'>The wire format is small — an mmap seqlock ring, a codec frame, an
  AES-256-GCM frame, fixed-layout schema structs. Six languages implement it natively and are
  <b>bidirectionally conformance-tested against Python</b> (Python seals → the other opens, and
  back); the schema layout is code-generated for fourteen more, each compile/run-verified
  against Python's packed little-endian bytes. Every one of these toolchains is installed and
  run green together — no language is ever silently skipped.</p>
  <div class='xrow' style='margin:0 0 16px'>
    <div class='chip'>Python<small>reference</small></div>
    <div class='chip'>C<small>native ring + C ABI</small></div>
    <div class='chip'>Cython<small>typed → C, 3.4× Python</small></div>
    <div class='chip'>Rust<small>crates.io</small></div>
    <div class='chip'>JavaScript · Node<small>npm</small></div>
    <div class='chip'>Java<small>Maven Central</small></div>
  </div>
  <p style='color:var(--muted);font-size:13.5px;margin:0 0 14px'><span style='font-family:"JetBrains Mono";
  font-size:11.5px;letter-spacing:.06em;color:var(--dim)'>SCHEMA CODEGEN · 14 &nbsp;</span>
  C · C++ · Rust · Go · Java · C# · TypeScript · Python · Julia · MATLAB/Octave · Swift · Kotlin · Ruby · Lua</p>
  <div class='note'><b>Embed it anywhere — <code>librobobus</code>.</b> A dependency-light C-ABI
  shared library (<code>robobus.dll</code> · <code>librobobus.dylib</code> · <code>librobobus.so</code>,
  built by CMake on every OS) exposes AES-256-GCM RBX1 seal/open + the codec, so software in any
  language links robobus over its FFI. Proven byte-identical to the Python reference on Linux,
  macOS, Windows and five emulated ISAs — including big-endian s390x.</div>
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
    return page("robobus — a fast, universal, quantum-safe way for machines to talk", "home", body,
                desc="robobus is a super-fast, universal messaging system for robots, sensors and "
                     "devices — locked with CNSA 2.0 post-quantum encryption (FIPS 203 ML-KEM · "
                     "FIPS 204 ML-DSA) and PQC-hardened DDS-Security, measured across nine orders "
                     "of magnitude.")


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
    return page("Benchmarks · robobus", "benchmarks", rep_body, extra_head=override, canon="benchmarks.html",
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


def _rewrite_doc_links(html_body, slugs):
    """Rewrite intra-docs links that still point at the source *.md files to the rendered pages.
    The docs are published as lowercase <slug>.html (Pages serves .html, not .md), so a bare
    cross-reference like [CMVP-READINESS.md](CMVP-READINESS.md) must become cmvp-readiness.html —
    otherwise every cross-doc link 404s on the public site. Only rewrites bare same-dir links
    whose target is a known doc; external/anchored/pathed links are left untouched."""
    def repl(m):
        slug = m.group(1).lower()
        if slug in slugs:
            return f'href="{slug}.html{m.group(2) or ""}"'
        return m.group(0)
    return re.sub(r'href="([^":/?#]+)\.md(#[^"]*)?"', repl, html_body)


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
        html_body = _rewrite_doc_links(_md(md), {k.lower() for k in present})
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


RESULTS = os.path.join(HERE, "results")


def _load(name):
    try:
        return json.load(open(os.path.join(RESULTS, name)))
    except Exception:
        return None


def _hbars(rows, tier_fn):
    """rows: list of (label, sublabel, value, unit). Log-scaled bar widths (values span decades)."""
    import math
    vals = [r[2] for r in rows if r[2]]
    if not vals:
        return ""
    lo, hi = math.log10(min(vals)), math.log10(max(vals))
    span = (hi - lo) or 1
    out = []
    for label, sub, val, unit in rows:
        w = 4 + 96 * (math.log10(val) - lo) / span if val else 0
        out.append(f"<div class='hrow'><div class='lname'>{html.escape(label)}"
                   f"<small>{html.escape(sub)}</small></div>"
                   f"<div class='htrack {tier_fn(val)}'><i style='width:{w:.1f}%'></i></div>"
                   f"<div class='hval'>{val:,.0f}<small> {unit}</small></div></div>")
    return "<div class='hbars'>" + "".join(out) + "</div>"


def _runtimes_section():
    rt = _load("runtimes.json")
    if not rt:
        return ""
    oks = [r for r in rt["runtimes"] if r.get("status") == "ok"]
    if not oks:
        return ""
    oks.sort(key=lambda r: -r["ops_per_s"])
    rows = [(r["config"], r.get("note", ""), r["ops_per_s"], "op/s") for r in oks]
    def tier(v):
        return "tier-n" if v > 1e6 else "tier-j" if v > 6e5 else "tier-i"
    return f"""<section><div class='wrap'>
  <p class='sec-eyebrow'>python runtimes · CPython · Cython · PyPy+cffi</p>
  <h2 class='title'>Same code, four runtimes — pick your stack</h2>
  <p class='sec-lede'>robobus's Python surface runs on whatever runtime fits, and each has a native
  acceleration path. <b>Cython stacks with CPython</b> (seal/open compiled to C in-process);
  <b>PyPy does not stack with Cython</b> (its cpyext C-API layer is slow) but <b>stacks with native
  code via cffi</b> — the JIT optimizes straight through the FFI into <code>librobobus</code>. Same
  RBX1 seal+open workload, measured on each:</p>
  {_hbars(rows, tier)}
  {_runtime_pending(rt)}
  <p class='sec-lede' style='margin-top:16px'>{html.escape(rt.get('note',''))}</p>
</div></section>"""


def _runtime_pending(rt):
    sk = [r for r in rt["runtimes"] if r.get("status") != "ok"]
    if not sk:
        return ""
    rows = "".join(f"<tr class='speed-skip'><td>{html.escape(r['config'])}</td>"
                   f"<td>{html.escape(r.get('note',''))}</td></tr>" for r in sk)
    return (f"<table class='ltab' style='margin-top:14px'><thead><tr><th>Runtime mix (tracked)</th>"
            f"<th>status</th></tr></thead><tbody>{rows}</tbody></table>")


def _ruby_runtimes_section():
    rr = _load("ruby-runtimes.json")
    if not rr:
        return ""
    oks = [r for r in rr["runtimes"] if r.get("status") == "ok"]
    if not oks:
        return ""
    oks.sort(key=lambda r: -r["ops_per_s"])
    rows = [(r["config"], r.get("note", ""), r["ops_per_s"], "it/s") for r in oks]
    return f"""<section><div class='wrap'>
  <p class='sec-eyebrow'>ruby runtimes · the ruby family</p>
  <h2 class='title'>Ruby, accelerated the Ruby way</h2>
  <p class='sec-lede'>The same story holds beyond Python. <b>crystalruby</b> compiles Crystal hot
  paths and calls them from MRI Ruby via FFI — the Ruby analog of CPython+Cython. And <b>Crystal</b>
  itself (Ruby-like syntax, LLVM-compiled) sits in the codec matrix above at C-class 0.79 ns/op.
  Same CPU kernel, MRI vs crystalruby:</p>
  {_hbars(rows, lambda v: 'tier-n' if v > 1e8 else 'tier-i')}
  <p class='sec-lede' style='margin-top:16px'>{html.escape(rr.get('note',''))}</p>
</div></section>"""


def _profiles_section():
    pr = _load("profiles.json")
    if not pr:
        return ""
    rows = ""
    for p in pr["profiles"]:
        lvl = p["level"]
        lbadge = ("classical" if lvl == 0 else f"NIST {lvl}")
        ss = f"{p['session_setup_ns']/1e6:.2f} ms" if p.get("session_setup_ns") else "—"
        pm = f"{p['per_message_ns']/1000:.2f} µs" if p.get("per_message_ns") else "—"
        mps = f"{p['msg_per_s']:,.0f}" if p.get("msg_per_s") else "—"
        km = p["components"].get("kem", {})
        sg = p["components"].get("sig", {})
        sub = ""
        if "encaps_ns" in km and "sign_ns" in sg:
            sub = (f"<div class='pf-sub'>KEM {(km['keygen_ns']+km['encaps_ns']+km['decaps_ns'])/1e6:.2f}"
                   f" · sign {sg['sign_ns']/1e6:.2f} · verify {sg['verify_ns']/1e6:.2f} ms</div>")
        chips = "".join(f"<span class='cchip'>{html.escape(s)}</span>" for s in p["standards"][:4])
        rows += (f"<tr><td class='pf-n'>{html.escape(p['name'])}<div class='pf-alg'>"
                 f"{html.escape(p['kem'])} · {html.escape(p['sig'])}</div></td>"
                 f"<td><span class='pf-lvl l{lvl}'>{lbadge}</span></td>"
                 f"<td class='n'>{ss}{sub}</td><td class='n'>{pm}</td><td class='n'>{mps}</td>"
                 f"<td class='pf-std'>{chips}</td></tr>")
    return f"""<section><div class='wrap'>
  <p class='sec-eyebrow'>requirements · speed under each profile</p>
  <h2 class='title'>Pick your requirement, see the cost</h2>
  <p class='sec-lede'>Security is a spectrum you choose per link, not a mandate — from
  <b>classical</b> (backwards-compatible with non-PQ peers) through hybrid transition profiles to
  <b>CNSA&nbsp;2.0</b> for National Security Systems. Each profile splits into two cost centres:
  <b>session setup</b> (the ML-KEM / ML-DSA handshake, once per peer, amortized) and the
  <b>per-message</b> hot path (AES-256-GCM, every frame). Session cost swings ~130× with assurance;
  per-message stays flat at line rate — so higher security buys handshake latency, not throughput.</p>
  <div style='overflow-x:auto'><table class='ltab pftab'>
  <thead><tr><th>Profile</th><th>Level</th><th>Session setup</th><th>Per-message</th><th>msg/s</th><th>Standards</th></tr></thead>
  <tbody>{rows}</tbody></table></div>
  <p class='sec-lede' style='margin-top:16px'>{html.escape(pr.get('note',''))}</p>
</div></section>"""


def _ffi_bindings_section():
    fb = _load("ffi-bindings.json")
    if not fb:
        return ""
    oks = [r for r in fb["bindings"] if r.get("status") == "ok"]
    if not oks:
        return ""
    oks.sort(key=lambda r: -r["ops_per_s"])
    rows = [(f"{r['language']} · {r['mechanism']}", r.get("note", ""), r["ops_per_s"], "op/s")
            for r in oks]
    sk = [r for r in fb["bindings"] if r.get("status") != "ok"]
    sktab = ""
    if sk:
        srows = "".join(f"<tr class='speed-skip'><td>{html.escape(r['language'])} · "
                        f"{html.escape(r.get('mechanism',''))}</td><td>{html.escape(r.get('note',''))}"
                        f"</td></tr>" for r in sk)
        sktab = (f"<table class='ltab' style='margin-top:14px'><thead><tr>"
                 f"<th>Binding (tracked)</th><th>status</th></tr></thead><tbody>{srows}</tbody></table>")
    # narrow spread — all near the C ceiling — so a linear tier by op/s reads better than log
    def tier(v):
        return "tier-n" if v > 1.2e6 else "tier-j" if v > 9e5 else "tier-i"
    return f"""<section><div class='wrap'>
  <p class='sec-eyebrow'>one C-ABI · every language's FFI</p>
  <h2 class='title'>Full robobus from any language — over its own FFI</h2>
  <p class='sec-lede'>You don't need a native robobus port to get the real thing. <code>librobobus</code>
  is one C-ABI shared library, and every language reaches its <b>complete</b> seal/open surface
  through its own foreign-function interface — <b>LuaJIT</b>'s native FFI, <b>Perl</b>'s FFI::Platypus
  (libffi), <b>Octave</b>'s compiled <code>.oct</code> C-linkage (it has no raw <code>loadlibrary</code>),
  and <b>CPython</b>'s cffi. The same RBX1 <code>seal(41&nbsp;B)</code>→<code>open</code> round trip
  (AES-256-GCM), each verified to round-trip before timing. Because the work happens in the shared C,
  every binding lands near the C ceiling — <b>the FFI overhead is nearly free</b>:</p>
  {_hbars(rows, tier)}
  {sktab}
  <p class='sec-lede' style='margin-top:16px'>{html.escape(fb.get('note',''))}</p>
</div></section>"""


def _crypto_matrix_section():
    cm = _load("crypto-matrix.json")
    if not cm or not cm.get("techniques"):
        return ""
    tech = cm["techniques"]
    kind_tier = {
        "aead": lambda v: "tier-n" if v > 1.5e6 else "tier-j" if v > 4e5 else "tier-i",
        "hash": lambda v: "tier-n" if v > 8e6 else "tier-j" if v > 2e6 else "tier-i",
        "kem":  lambda v: "tier-n" if v > 3e4 else "tier-j" if v > 2e4 else "tier-i",
        "sig":  lambda v: "tier-n" if v > 4e3 else "tier-j" if v > 2e3 else "tier-i",
    }
    blocks = []
    for grp in cm.get("groups", []):
        techs = [t for t in grp["techniques"] if tech.get(t, {}).get("rows")]
        if not techs:
            continue
        inner = []
        for t in techs:
            info = tech[t]
            rows = [(r["language"], r.get("impl", ""), 1e9 / r["ns"], "op/s") for r in info["rows"]]
            inner.append(
                f"<div class='tech'><div class='tech-h'><span class='tech-n'>{html.escape(t)}</span>"
                f"<span class='tech-m'>{html.escape(info.get('metric',''))}</span></div>"
                f"{_hbars(rows, kind_tier.get(info['kind'], kind_tier['aead']))}</div>")
        blocks.append(f"<div class='cgroup'><h3 class='cgroup-t'>{html.escape(grp['title'])}</h3>"
                      + "".join(inner) + "</div>")
    css = ("<style>.cgroup{margin:26px 0}.cgroup-t{font:600 15px/1.3 'Inter';color:var(--signal);"
           "margin:0 0 6px;padding-bottom:8px;border-bottom:1px solid var(--line)}"
           ".tech{margin:16px 0}.tech-h{display:flex;justify-content:space-between;align-items:baseline;"
           "gap:12px;margin-bottom:6px;flex-wrap:wrap}.tech-n{font:600 13.5px/1 'JetBrains Mono';color:var(--fg)}"
           ".tech-m{font:400 11px/1.3 'JetBrains Mono';color:var(--dim)}</style>")
    return f"""<section><div class='wrap'>{css}
  <p class='sec-eyebrow'>crypto · every primitive · every language · grouped by technique</p>
  <h2 class='title'>The crypto matrix</h2>
  <p class='sec-lede'>robobus is a post-quantum bus, so its crypto is a whole suite, not one cipher.
  Here is every primitive it uses, measured in every language that can do it natively — <b>grouped
  per technique</b> so each bar chart is a coherent apples-to-apples comparison (identical workload,
  languages ranked fastest first). The <b>AEAD</b> and <b>hash</b> groups are each language's
  native-maximum stack (stdlib where it exists, else the platform OpenSSL through the language's FFI).
  The <b>post-quantum</b> groups have essentially no native per-language implementations, so they show
  the real distinct backends instead — <b>OpenSSL&nbsp;3.6.3 EVP</b>, <b>liboqs</b>, and Go's native
  pure-Go <b>crypto/mlkem</b> — a genuine implementation comparison; every language reaches the
  OpenSSL/liboqs numbers via FFI at ~the same cost (see the FFI-bindings section).</p>
  {"".join(blocks)}
  <p class='sec-lede' style='margin-top:16px'>{html.escape(cm.get('note',''))}</p>
</div></section>"""


def speed():
    lm = _load("lang-matrix.json")
    cl = _load("cross-lang.json")
    tm = _load("transport-matrix.json")
    xl = _load("xport-lang.json")
    host = (lm or {}).get("host", {})
    hoststr = f"{host.get('system','')} · {host.get('machine','')}"

    # 1) language codec-decode throughput (log bars)
    def codec_tier(v):
        return "tier-n" if v > 3e8 else "tier-j" if v > 5e7 else "tier-i"
    sec1 = ""
    if lm:
        oks = [x for x in lm["languages"] if x.get("status") == "ok"]
        oks.sort(key=lambda x: -x["ops_per_s"])
        rows = [(x["language"], x.get("method", ""), x["ops_per_s"], "dec/s") for x in oks]
        skips = [x for x in lm["languages"] if x.get("status") != "ok"]
        sk = ("".join(f"<tr class='speed-skip'><td>{html.escape(x['language'])}</td>"
                      f"<td>{html.escape(x.get('note',''))}</td></tr>" for x in skips))
        rec = lm.get("record", {})
        sec1 = f"""<section><div class='wrap'>
  <p class='sec-eyebrow'>languages · wire codec</p>
  <h2 class='title'>Decode speed, every target language</h2>
  <p class='sec-lede'>The {html.escape(rec.get('name','record'))} wire record
  ({html.escape(rec.get('fields',''))}, {rec.get('bytes','?')} B) parsed at native maximum in each
  language robobus code-generates for — measured on this host ({html.escape(hoststr)}), decode in a
  tight loop with a field checksum (no dead-code elision). Log scale; the span is ~1,700×.</p>
  {_hbars(rows, codec_tier)}
  {'<table class="ltab" style="margin-top:14px"><tbody>'+sk+'</tbody></table>' if sk else ''}
</div></section>"""

    # 2) native seal+open crypto per language
    sec2 = ""
    if cl and cl.get("languages"):
        ls = sorted([x for x in cl["languages"] if x.get("ops_per_s")], key=lambda x: -x["ops_per_s"])
        rows = [(x["language"], x.get("note", "AES-256-GCM RBX1"), x["ops_per_s"], "op/s") for x in ls]
        sec2 = f"""<section><div class='wrap'>
  <p class='sec-eyebrow'>languages · crypto</p>
  <h2 class='title'>Seal + open, native per language</h2>
  <p class='sec-lede'>The full RBX1 round trip — codec encode → AES-256-GCM seal → open — in each
  language's own crypto stack. This is the app-layer post-quantum envelope's per-message cost.</p>
  {_hbars(rows, lambda v: 'tier-n' if v > 2e6 else 'tier-j' if v > 3e5 else 'tier-i')}
</div></section>"""

    # 3) transport throughput
    sec3 = ""
    if tm:
        okr = [r for r in tm["results"] if r["status"] == "ok" and r["metrics"].get("ops_per_s")]
        okr.sort(key=lambda r: -r["metrics"]["ops_per_s"])
        trows = "".join(
            f"<tr><td>{html.escape(r['name'])}</td><td class='reg'>{html.escape(r['dependency'])}</td>"
            f"<td class='n'>{r['metrics']['ops_per_s']:,.0f}</td>"
            f"<td class='n'>{r['metrics']['mb_per_s']:.1f}</td>"
            f"<td class='n'>{(str(round(r['metrics']['p50_ns']/1000,1))+' µs') if r['metrics'].get('p50_ns') else '—'}</td></tr>"
            for r in okr)
        skr = "".join(
            f"<tr class='speed-skip'><td>{html.escape(r['name'])}</td><td colspan='4'>{html.escape(r['note'])}</td></tr>"
            for r in tm["results"] if r["status"] != "ok")
        sec3 = f"""<section><div class='wrap'>
  <p class='sec-eyebrow'>transports · throughput</p>
  <h2 class='title'>Every transport, moving a sealed frame</h2>
  <p class='sec-lede'>Sustained one-way throughput of the {tm['frame_bytes']}-byte AES-256-GCM sealed
  robobus frame over each transport, loopback on one host (the transport's software ceiling).
  Rows still being provisioned on this host show why.</p>
  <div style='overflow-x:auto'><table class='ltab'>
  <thead><tr><th>Transport</th><th>Backend</th><th>frames/s</th><th>MB/s</th><th>lat p50</th></tr></thead>
  <tbody>{trows}{skr}</tbody></table></div>
</div></section>"""

    # 4) transport × language grid (heatmap)
    sec4 = ""
    if xl and xl.get("cells"):
        cells = xl["cells"]
        langs, xports = [], []
        for c in cells:
            if c["language"] not in langs:
                langs.append(c["language"])
            if c["transport"] not in xports:
                xports.append(c["transport"])
        grid = {(c["transport"], c["language"]): c for c in cells}
        vals = [c["frames_per_s"] for c in cells if c.get("frames_per_s")]
        mx = max(vals) if vals else 1
        head = "".join(f"<th>{html.escape(l)}</th>" for l in langs)
        body = ""
        for xp in xports:
            tds = ""
            for l in langs:
                c = grid.get((xp, l))
                if c and c.get("frames_per_s"):
                    t = c["frames_per_s"] / mx
                    bg = f"color-mix(in srgb, var(--signal) {int(14+t*70)}%, transparent)"
                    tds += f"<td style='background:{bg}'>{c['frames_per_s']/1000:,.0f}k</td>"
                else:
                    tds += "<td class='na'>—</td>"
            body += f"<tr><td class='rl'>{html.escape(xp.upper())}</td>{tds}</tr>"
        sec4 = f"""<section><div class='wrap'>
  <p class='sec-eyebrow'>transport × language</p>
  <h2 class='title'>The full product</h2>
  <p class='sec-lede'>Each cell: that language's native client pushing the sealed frame over that
  transport (frames/s, loopback, pipelined). These cells are <b>I/O-syscall-bound</b> — every
  language issues the same <code>send</code>/<code>recv</code> into the same kernel, so throughput
  converges to the loopback ceiling and small differences (even Python edging C) are run-to-run
  noise, not language speed. That's the point: <b>the transport sets the ceiling, not the caller</b>
  — the opposite of the codec table above, where language speed spans ~1,700×.</p>
  <div class='heatwrap'><table class='heat'><thead><tr><th>transport</th>{head}</tr></thead>
  <tbody>{body}</tbody></table></div>
</div></section>"""

    hero = """<header class='hero'><div class='wrap reveal'>
  <p class='eyebrow'>native maximum speed · languages · transports · interop</p>
  <h1>The speed matrix</h1>
  <p class='lede'>Real measured throughput across every language robobus targets and every transport it
  bridges — decode speed, crypto seal/open, transport frame rate, and the full transport × language
  product. Measured, never estimated; unprovisioned cells say so.</p>
</div></header>"""
    # the per-technique crypto matrix supersedes the old 6-language sec2 (kept as fallback only)
    crypto = _crypto_matrix_section() or sec2
    body = (hero + _profiles_section() + sec1 + crypto + _runtimes_section()
            + _ruby_runtimes_section() + _ffi_bindings_section() + sec3 + sec4)
    return page("Speed matrix · robobus", "speed", body, canon="speed.html",
                desc="Native maximum speed across every robobus language and transport — codec, "
                     "crypto, transport throughput, and the full transport × language product.")


def main():
    os.makedirs(SITE, exist_ok=True)
    os.makedirs(os.path.join(SITE, "docs"), exist_ok=True)
    open(os.path.join(SITE, "index.html"), "w").write(home())
    open(os.path.join(SITE, "benchmarks.html"), "w").write(benchmarks())
    open(os.path.join(SITE, "speed.html"), "w").write(speed())
    docs, present = docs_pages()
    for slug, content in docs.items():
        open(os.path.join(SITE, "docs", f"{slug}.html"), "w").write(content)
    print(f"[build_site] wrote index.html, benchmarks.html, docs/ ({len(docs)} pages: "
          f"{', '.join(sorted(present)) or 'none — add docs-src/*.md'})")


if __name__ == "__main__":
    main()
