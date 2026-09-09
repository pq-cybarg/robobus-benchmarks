/* robobus operator console - catalog-driven, host-adaptive, allowlisted POST /api/run */
(() => {
  const logEl = document.getElementById("log");
  const $ = (id) => document.getElementById(id);
  let host = {};
  let catalog = {};
  let view = {};
  let queue = Promise.resolve();
  let familyFilter = "";
  let STATIC = false;   // set when the /api backend is absent (a static snapshot, e.g. served from the site)

  // Try the live API; if there is no backend (static snapshot), fall back to the baked reference JSON
  // written next to the page at build time. This lets the flight manual populate + browse everywhere,
  // and directs the operator to the live console for actual command execution.
  async function apiGet(path, fallbackFile) {
    try {
      const res = await fetch(path);
      if (res.ok) return await res.json();
      throw new Error("http " + res.status);
    } catch (e) {
      STATIC = true;
      const res = await fetch(fallbackFile);
      if (!res.ok) throw new Error("no live backend and no baked " + fallbackFile);
      return await res.json();
    }
  }
  function staticBanner() {
    if (!STATIC || document.getElementById("static-banner")) return;
    const b = document.createElement("div");
    b.id = "static-banner";
    b.style.cssText = "background:#E8B04B;color:#0B0E12;font:600 13px/1.5 ui-monospace,Menlo,Consolas,monospace;" +
      "padding:9px 14px;text-align:center;position:sticky;top:0;z-index:99999";
    b.innerHTML = "Static snapshot: browse the reference here. To RUN commands live on your machine, start " +
      "the operator console &mdash; <code>python3 operator/server.py</code> &mdash; then open " +
      "<a href='http://127.0.0.1:8765' style='color:#0B0E12;text-decoration:underline'>http://127.0.0.1:8765</a>";
    document.body.insertBefore(b, document.body.firstChild);
  }

  // Each run is its own collapsible block, newest FIRST — so the latest result is always visible at the
  // top without scrolling or clearing, and runs never smear together in one endless stream.
  function newRun(title) {
    const b = document.createElement("details");
    b.className = "run"; b.open = true;
    const s = document.createElement("summary");
    s.className = "run-hd";
    const t = document.createElement("span"); t.className = "run-t"; t.textContent = title;
    const st = document.createElement("span"); st.className = "run-st"; st.textContent = "running…";
    s.append(t, st);
    const pre = document.createElement("pre"); pre.className = "run-out";
    b.append(s, pre);
    logEl.prepend(b);
    return { block: b, status: st, pre: pre };
  }

  function log(line) {                       // one-off note (host probe, target view, errors)
    const p = document.createElement("div");
    p.className = "run-note";
    p.textContent = line;
    logEl.prepend(p);
  }

  function canonFrag(name) {
    if (name === "nasa") return "space";
    if (name === "cypherpunk") return "privacy";
    return name || "space";
  }

  function wantedTarget() {
    const q = new URLSearchParams(location.search).get("target");
    if (q) return q;
    const h = (location.hash.match(/target=([^&]+)/) || [])[1];
    if (h) return decodeURIComponent(h);
    try { return sessionStorage.getItem("rb-target") || "autodetect"; }
    catch (e) { return "autodetect"; }
  }

  function persistTarget(id) {
    try { sessionStorage.setItem("rb-target", id); } catch (e) { /* private mode */ }
    const u = new URL(location.href);
    if (id === "autodetect") u.searchParams.delete("target");
    else u.searchParams.set("target", id);
    history.replaceState(null, "", u.pathname + u.search + u.hash);
  }

  function fillTargetSelects(id) {
    const rows = catalog.targets || [];
    const families = catalog.families || [];
    const groups = {};
    for (const f of families) groups[f[0]] = [];
    groups.other = [];
    for (const t of rows) {
      const k = groups[t.family] ? t.family : "other";
      groups[k].push(t);
    }
    function populate(sel) {
      sel.replaceChildren();
      const auto = document.createElement("option");
      auto.value = "autodetect";
      auto.textContent = "autodetect (" + (host.system || "?") + " " + (host.machine || "") + ")";
      sel.appendChild(auto);
      for (const f of families) {
        const list = groups[f[0]] || [];
        if (!list.length) continue;
        const og = document.createElement("optgroup");
        og.label = f[1];
        for (const t of list) {
          const o = document.createElement("option");
          o.value = t.id;
          o.textContent = t.label;
          og.appendChild(o);
        }
        sel.appendChild(og);
      }
      if ([...sel.options].some((o) => o.value === id)) sel.value = id;
      else sel.value = "autodetect";
    }
    populate($("target"));
    populate($("target-aside"));
  }

  function setText(id, value) {
    const el = $(id);
    if (el) el.textContent = value == null || value === "" ? "-" : String(value);
  }

  function fillHost() {
    const v = view || {};
    const live = (host.system || "?") + " " + (host.machine || "?") +
      "  " + (host.shared_rbcodec || "");
    $("hostline").textContent = v.overridden
      ? ("viewing " + (v.id || "?") + "  ·  this host " + live)
      : live;
    const banner = $("view-banner");
    banner.textContent = v.execute_note || "autodetect";
    banner.classList.toggle("viewing", !!v.overridden);
    setText("h-label", v.label);
    setText("h-family", (v.family || "-") + " / " + (v.kind || "-"));
    setText("h-system", (v.plat || "-") + " / " + (v.machine || "-") +
      (host.release && !v.overridden ? "  " + host.release : ""));
    setText("h-endian", v.endian);
    setText("h-rbcodec", v.shared_rbcodec);
    setText("h-robobus", v.shared_robobus);
    setText("h-pinvoke", v.pinvoke);
    setText("h-loader", v.loader_env);
    setText("h-cc", Array.isArray(v.cc_shared) ? v.cc_shared.join(" ") : v.cc_shared);
    setText("h-lua", Array.isArray(v.cc_lua) ? v.cc_lua.join(" ") : v.cc_lua);
    setText("h-rpath", Array.isArray(v.rpath) ? v.rpath.join(" ") : v.rpath);
    setText("h-shm", v.shm);
    setText("h-ros", v.ros);
    setText("h-lsl", v.lsl);
    setText("h-bus", v.bus);
    setText("h-pqc", v.pqc);
    setText("h-ship", (v.shipset || "") + (v.suite_default ? "  suite=" + v.suite_default : ""));
    setText("h-install", v.install);
    setText("h-tool", v.toolchain);
    setText("h-python", v.python || host.python);
    setText("h-java", v.java_home || host.java_home || "(none)");
    const plat = v.plat || (host.darwin ? "darwin" : host.win32 ? "win32" : "linux");
    $("chip-darwin").classList.toggle("on", plat === "darwin");
    $("chip-linux").classList.toggle("on", plat === "linux");
    $("chip-win32").classList.toggle("on", plat === "win32");
    $("chip-mcu").classList.toggle("on", plat === "mcu" || v.kind === "mcu-static");
    $("chip-mobile").classList.toggle("on", v.family === "mobile" || plat === "ios");
    $("chip-wasm").classList.toggle("on", plat === "wasm" || v.kind === "wasm");
    $("chip-plc").classList.toggle("on", plat === "plc" || v.kind === "plc-st");
    $("fragpath").textContent = v.preview_fragment || "";
    $("fragexec").textContent = v.execute_fragment || "";
    $("fragnote").textContent = v.overridden && !v.runs_on_this_host ? (v.execute_note || "") : "";
    const mcu = $("mcu-card");
    if (v.kind === "mcu-static") {
      mcu.hidden = false;
      $("mcu-transports").textContent = (v.transports_mcu || []).join(", ");
      $("mcu-snippet").textContent = v.rb_config || "";
    } else {
      mcu.hidden = true;
    }
    if (catalog.bind) $("bindline").textContent = catalog.bind;
    fillTargetTable();
  }

  function fillTargetTable() {
    const body = $("target-body");
    if (!body) return;
    body.replaceChildren();
    const rows = catalog.targets || [];
    $("target-count").textContent = rows.length + " catalog targets (plus autodetect)";
    for (const t of rows) {
      if (familyFilter && t.family !== familyFilter) continue;
      const tr = document.createElement("tr");
      if (view && t.id === view.id) tr.className = "ok";
      for (const c of [t.id, t.family, t.kind, (t.plat || "") + " / " + (t.machine || ""), t.label]) {
        const td = document.createElement("td");
        td.textContent = c;
        tr.appendChild(td);
      }
      tr.style.cursor = "pointer";
      tr.addEventListener("click", () => applyTarget(t.id));
      body.appendChild(tr);
    }
  }

  function fillFamilyChips() {
    const el = $("family-chips");
    el.replaceChildren();
    const all = document.createElement("span");
    all.className = "chip" + (familyFilter ? "" : " on");
    all.textContent = "all families";
    all.tabIndex = 0;
    all.addEventListener("click", () => { familyFilter = ""; fillFamilyChips(); fillTargetTable(); });
    el.appendChild(all);
    for (const f of catalog.families || []) {
      const s = document.createElement("span");
      s.className = "chip" + (familyFilter === f[0] ? " on" : "");
      s.textContent = f[1];
      s.tabIndex = 0;
      s.addEventListener("click", () => {
        familyFilter = familyFilter === f[0] ? "" : f[0];
        fillFamilyChips();
        fillTargetTable();
      });
      el.appendChild(s);
    }
  }

  async function applyTarget(id) {
    persistTarget(id);
    $("target").value = id;
    $("target-aside").value = id;
    const frag = canonFrag($("fragment").value);
    try {
      let r;
      if (STATIC) {
        const t = await (await fetch("targets_resolved.json")).json();
        r = { ok: true, target: t[id] || t.autodetect || {} };
        if (frag !== "space") log("static: live per-fragment resolve needs the operator console (showing default)");
      } else {
        const u = "/api/target?id=" + encodeURIComponent(id) + "&fragment=" + encodeURIComponent(frag);
        r = await (await fetch(u)).json();
      }
      if (!r.ok) {
        log("target FAIL " + (r.error || ""));
        return;
      }
      view = r.target || {};
      fillHost();
      log("view " + (view.id || id) + "  kind=" + (view.kind || "") +
          "  codec=" + (view.shared_rbcodec || "") +
          (view.overridden ? "  (preview)" : "  (live)"));
    } catch (err) {
      log("target probe failed: " + err);
    }
  }

  function text(v) {
    return v == null ? "" : String(v);
  }

  function fillShipsets() {
    const body = $("ship-body");
    body.replaceChildren();
    const sets = (catalog.shipsets && catalog.shipsets.sets) || [];
    for (const s of sets) {
      const tr = document.createElement("tr");
      const ads = s.adapters == null ? "all" : String(s.adapters.length);
      const cells = [s.name, s.audience, s.crypto, s.fail_closed ? "yes" : "no", ads];
      for (const c of cells) {
        const td = document.createElement("td");
        td.textContent = text(c);
        tr.appendChild(td);
      }
      body.appendChild(tr);
    }
    const aliases = catalog.aliases || {};
    const parts = Object.keys(aliases).map((k) => k + " = " + aliases[k]);
    $("ship-note").textContent = parts.length ? ("aliases: " + parts.join(", ")) : "";
  }

  function fillIso() {
    const body = $("iso-body");
    body.replaceChildren();
    const iso = catalog.isolation || {};
    for (const name of Object.keys(iso)) {
      const row = iso[name];
      const tr = document.createElement("tr");
      const td0 = document.createElement("td");
      td0.textContent = name;
      const td1 = document.createElement("td");
      td1.textContent = text(row.must_have);
      const td2 = document.createElement("td");
      td2.textContent = (row.must_not || []).join(", ");
      tr.append(td0, td1, td2);
      body.appendChild(tr);
    }
  }

  function fillLangs() {
    const body = $("lang-body");
    body.replaceChildren();
    const langs = catalog.languages || [];
    $("lang-count").textContent = langs.length + " languages in lang_conformance roster";
    for (const L of langs) {
      const name = typeof L === "string" ? L : L.name;
      const tool = typeof L === "string" ? "" : (L.tool || "");
      const tr = document.createElement("tr");
      const td0 = document.createElement("td");
      td0.textContent = name;
      const td1 = document.createElement("td");
      td1.textContent = tool;
      tr.append(td0, td1);
      body.appendChild(tr);
    }
  }

  function fillChips(id, items, cls) {
    const el = $(id);
    el.replaceChildren();
    for (const x of items || []) {
      const s = document.createElement("span");
      s.className = cls || "chip";
      s.textContent = x;
      el.appendChild(s);
    }
  }

  let adapters = [];

  function renderAdapters(filter) {
    const body = $("ad-body");
    body.replaceChildren();
    const q = (filter || "").trim().toLowerCase();
    let n = 0;
    for (const a of adapters) {
      const blob = (a.name + " " + a.tier + " " + a.transport + " " + a.summary).toLowerCase();
      if (q && blob.indexOf(q) < 0) continue;
      n += 1;
      const tr = document.createElement("tr");
      for (const c of [a.name, a.tier, a.transport, a.summary]) {
        const td = document.createElement("td");
        td.textContent = text(c);
        tr.appendChild(td);
      }
      body.appendChild(tr);
    }
    $("ad-count").textContent = n + " / " + adapters.length + " adapters";
  }

  function fillAdapters() {
    adapters = catalog.adapters || [];
    $("space-list").textContent = (catalog.space_adapters || []).join(" ");
    renderAdapters($("ad-filter").value);
  }

  function fillActions() {
    const body = $("act-body");
    body.replaceChildren();
    for (const a of catalog.actions || []) {
      const tr = document.createElement("tr");
      const td0 = document.createElement("td");
      td0.textContent = a.id;
      const td1 = document.createElement("td");
      td1.textContent = a.summary;
      tr.append(td0, td1);
      body.appendChild(tr);
    }
  }

  function fillSelect(id, values, current) {
    const el = $(id);
    if (!values || !values.length) return;
    const keep = current || el.value;
    el.replaceChildren();
    for (const v of values) {
      const o = document.createElement("option");
      o.value = v;
      o.textContent = v;
      el.appendChild(o);
    }
    if ([...el.options].some((o) => o.value === keep)) el.value = keep;
  }

  function argsFor(action) {
    const profile = $("profile").value;
    const fragment = $("fragment").value;
    const policy = $("policy").value;
    if (action === "doctor") return { profile: profile };
    if (action === "shipsets_show" || action === "sbom_exclude") return { name: profile };
    if (action === "fragment" || action === "compile" || action === "verify") return { name: fragment };
    if (action === "checksums") return { policy: policy };
    if (action === "checksums_verify") return { require_cnsa: policy === "cnsa20" };
    return {};
  }

  function run(action, extra) {
    queue = queue.then(() => runNow(action, extra)).catch((err) => log("queue: " + err));
    return queue;
  }

  async function runNow(action, extra) {
    const args = Object.assign(argsFor(action), extra || {});
    const argstr = Object.keys(args).length ? " " + JSON.stringify(args) : "";
    const time = new Date().toLocaleTimeString();
    const r = newRun(action + argstr + "  ·  " + time);
    if (STATIC) {
      r.pre.textContent =
        "This is a static snapshot; commands execute on the LIVE operator console, not here.\n\n" +
        "Start it:   python3 operator/server.py    (then open http://127.0.0.1:8765)\n" +
        "Action:     " + action + (Object.keys(args).length ? "   args " + JSON.stringify(args) : "") + "\n" +
        "Equivalent: robobus " + action + "   (or the matching make target, e.g. make " + action + ")";
      r.status.textContent = "static"; r.status.classList.add("bad");
      return;
    }
    document.body.classList.add("busy");
    let res, body;
    try {
      res = await fetch("/api/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ action: action, args: args }),
      });
      body = await res.json();
    } catch (err) {
      r.pre.textContent = "error: " + err;
      r.status.textContent = "ERROR"; r.status.classList.add("bad");
      document.body.classList.remove("busy");
      return;
    }
    document.body.classList.remove("busy");
    const out = [body.stdout, body.stderr].filter(Boolean).map((s) => s.replace(/\s+$/, "")).join("\n");
    r.pre.textContent = out || "(no output)";
    const rc = body.rc;
    const good = body.ok && (rc == null || rc === 0);
    r.status.textContent = body.ok
      ? (rc != null ? "rc=" + rc : "ok") + (res.status !== 200 ? " http=" + res.status : "")
      : "FAIL " + (body.error || res.status);
    r.status.classList.add(good ? "ok" : "bad");
  }

  async function walk(kind) {
    if (kind === "hobbyist") {
      $("profile").value = "lab";
      await run("doctor", { profile: "lab" });
      await run("shipsets_list");
      await run("census");
      return;
    }
    if (kind === "nasa") {
      $("profile").value = "space";
      $("fragment").value = "space";
      await applyTarget($("target").value || "autodetect");
      await run("doctor", { profile: "space" });
      await run("shipsets_show", { name: "space" });
      await run("fragment", { name: "space" });
      await run("compile", { name: "space" });
      await run("verify", { name: "space" });
      return;
    }
    if (kind === "privacy") {
      $("profile").value = "privacy";
      $("fragment").value = "privacy";
      await applyTarget($("target").value || "autodetect");
      await run("doctor", { profile: "privacy" });
      await run("shipsets_show", { name: "privacy" });
      await run("fragment", { name: "privacy" });
      await run("compile", { name: "privacy" });
      await run("verify", { name: "privacy" });
      return;
    }
    if (kind === "telecom") {
      $("profile").value = "telecom";
      $("fragment").value = "telecom";
      await applyTarget($("target").value || "autodetect");
      await run("doctor", { profile: "telecom" });
      await run("shipsets_show", { name: "telecom" });
      await run("fragment", { name: "telecom" });
      await run("compile", { name: "telecom" });
      await run("verify", { name: "telecom" });
    }
  }

  async function boot() {
    try {
      const h = await apiGet("/api/host", "host.json");
      host = h.host || {};
    } catch (err) {
      log("host probe failed: " + err + " (start operator/server.py for the live console)");
    }
    try {
      const c = await apiGet("/api/catalog", "catalog.json");
      catalog = c.catalog || {};
    } catch (err) {
      log("catalog failed: " + err);
    }
    staticBanner();
    fillShipsets();
    fillIso();
    fillLangs();
    fillAdapters();
    fillActions();
    fillChips("tr-chips", catalog.transports);
    fillChips("suite-chips", catalog.suites);
    fillFamilyChips();
    fillSelect("profile", catalog.profiles, "lab");
    const frags = (catalog.fragments || []).concat(["nasa", "cypherpunk", "ccaas", "liberty", "voip"]);
    fillSelect("fragment", frags.filter((v, i, a) => a.indexOf(v) === i), "space");
    const initial = wantedTarget();
    fillTargetSelects(initial);
    $("fragment").addEventListener("change", () => applyTarget($("target").value || "autodetect"));
    $("target").addEventListener("change", () => applyTarget($("target").value));
    $("target-aside").addEventListener("change", () => applyTarget($("target-aside").value));
    $("target-reset").addEventListener("click", () => applyTarget("autodetect"));
    $("ad-filter").addEventListener("input", () => renderAdapters($("ad-filter").value));
    $("clear-log").addEventListener("click", () => { logEl.textContent = ""; });
    document.querySelectorAll("button[data-action]").forEach((btn) => {
      btn.addEventListener("click", () => run(btn.getAttribute("data-action")));
    });

    // Resizable console: drag the splitter to set the console column width (persisted; dbl-click resets).
    (function initSplitter() {
      const sp = $("splitter");
      if (!sp) return;
      const root = document.documentElement;
      const saved = localStorage.getItem("robobus.consoleW");
      if (saved) root.style.setProperty("--console-w", saved);
      let dragging = false;
      const clientX = (e) => (e.touches && e.touches[0] ? e.touches[0].clientX : e.clientX);
      const move = (e) => {
        if (!dragging) return;
        const w = Math.min(Math.max(window.innerWidth - clientX(e), 260), Math.round(window.innerWidth * 0.72));
        const v = w + "px";
        root.style.setProperty("--console-w", v);
        localStorage.setItem("robobus.consoleW", v);
      };
      const start = (e) => { dragging = true; document.body.classList.add("resizing"); if (e.cancelable) e.preventDefault(); };
      const stop = () => { dragging = false; document.body.classList.remove("resizing"); };
      sp.addEventListener("mousedown", start);
      sp.addEventListener("touchstart", start, { passive: false });
      window.addEventListener("mousemove", move);
      window.addEventListener("touchmove", move, { passive: true });
      window.addEventListener("mouseup", stop);
      window.addEventListener("touchend", stop);
      sp.addEventListener("dblclick", () => {
        root.style.removeProperty("--console-w");
        localStorage.removeItem("robobus.consoleW");
      });
    })();
    document.querySelectorAll("button[data-walk]").forEach((btn) => {
      btn.addEventListener("click", () => walk(btn.getAttribute("data-walk")));
    });
    await applyTarget(initial);
    log("host " + (host.system || "?") + "/" + (host.machine || "?") +
        "  codec=" + (host.shared_rbcodec || "?") +
        "  langs=" + ((catalog.languages || []).length) +
        "  adapters=" + ((catalog.adapters || []).length) +
        "  targets=" + ((catalog.targets || []).length));
  }

  document.addEventListener("DOMContentLoaded", boot);
})();
