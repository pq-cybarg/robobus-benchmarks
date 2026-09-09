# robobus operator console

Local flight-manual webpage for the full stack. Bind `127.0.0.1` only.
Allowlisted compile / doctor / checksum / census / bundle tasks - not a shell.

```bash
python3 operator/server.py          # http://127.0.0.1:8765/
make operator
```

Unpack a portable zip (`make bundle`), then the same command from the snapshot
root. Autodetect fills this OS (`librbcodec.dylib` / `.so` / `rbcodec.dll`). The
target selector overrides that view for other desktops, privacy distros, phones,
MCU boards, PLCs, QEMU ISAs, and WASM - compile/doctor still run on this host.

```
http://127.0.0.1:8765/?target=mcu-esp32
http://127.0.0.1:8765/?target=android-termux&fragment=space
```

## What the page will run

`POST /api/run` with `{"action": "<id>", "args": {...}}`. Unknown action -> 400.

| action | args | effect |
|---|---|---|
| doctor | profile=lab\|hobbyist\|privacy\|... | `robobus doctor --profile` (lab does not fail-close) |
| shipsets_list / shipsets_show | name= | named slices |
| fragment / compile / verify | name=space\|ics\|avionics\|privacy (nasa, cypherpunk aliases) | C sources, `cc` to `/tmp`, isolation probes |
| verify_all / export / sbom_exclude | | JSON / SBOM drop list |
| checksums | policy=all\|cnsa20\|fips202 | hash `dist/` (CNSA 2.0 is SHA-384/512, not SHA-256) |
| checksums_verify | require_cnsa= | `--verify-all` |
| bundle | | portable source zip (`--no-hash` from the page) |
| census | | filesystem census |
| target | id=autodetect\|linux-x64\|mcu-esp32\|... | preview ABI/config (no cross-compile) |

Do not expose the port. The process runs as your user and can write `/tmp` and `dist/`.

Guidebook body is `index.html` (static tutorial of every profile, language class,
transport, hashing policy, persona). Tables for ship-sets, languages, and adapters
are filled from `/api/catalog` so counts match this checkout.

Static product pages on the same site (open as files or via the server):

- `datasheet.html` - RB-DS-001
- `specification.html` - RB-SPEC-001
- `fips-sidecar.html` - RB-FIPS-SIDECAR-001 (architecture, not a CMVP certificate)
