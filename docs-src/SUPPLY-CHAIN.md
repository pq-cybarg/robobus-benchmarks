# Supply-chain integrity

National-security supply-chain hardening (aligns with SLSA, NIST SSDF / SP 800-218, EO 14028).

## 1. SBOM (Software Bill of Materials)

A CycloneDX 1.6 SBOM of robobus's dependencies is generated with:

```bash
make sbom            # -> sbom/robobus.cdx.json  (CycloneDX 1.6, PURLs for every dep)
```

CI regenerates it on every run and uploads it as a build artifact, so every release has a
verifiable component inventory (feed it to Dependency-Track, `grype`, `osv-scanner`, etc.).

## 2. Vulnerability gating

`pip-audit` (deps) + `bandit` (code) run in `make audit` and the CI `audit` job — a finding
is visible on every build. Native code is gated by ASan/UBSan/TSan; parsers by fuzzing;
resources by the fd/thread leak test.

## 3. Dependency pinning

For reproducible, tamper-evident installs, pin hashes:

```bash
pip install --require-hashes -r requirements.lock   # rejects any dependency whose hash differs
```

Generate the lock with `pip-compile --generate-hashes` (pip-tools) or `pip freeze` + hashes.
The conda side is already pinned by exact build strings in the RoboStack channels + our
`scripts/install_*.sh`.

## 4. Artifact signing (Sigstore) + provenance — the live release pipeline

A tag push (`v*`) runs `.github/workflows/release.yml`,
which with **OIDC identity only (no long-lived secrets)**:

1. builds wheels + sdist (`python -m build`) and a CycloneDX SBOM;
2. emits **SLSA build provenance** (`actions/attest-build-provenance`);
3. **keyless Sigstore-signs** the wheels, sdist, and SBOM
   (`sigstore/gh-action-sigstore-python` → `.sigstore` bundles: cert + signature +
   Rekor transparency-log entry);
4. attaches everything to the GitHub Release; and
5. optionally publishes to **PyPI via Trusted Publishing** (OIDC, no API token) when
   the `PUBLISH_PYPI` repo variable is set.

Verify a downloaded artifact against its bundle:

```bash
python -m pip install sigstore
python -m sigstore verify identity \
    --cert-identity 'https://github.com/<org>/<repo>/.github/workflows/release.yml@refs/tags/v0.1.0' \
    --cert-oidc-issuer 'https://token.actions.githubusercontent.com' \
    --bundle robobus-0.1.0-py3-none-any.whl.sigstore robobus-0.1.0-py3-none-any.whl
```

The build + SBOM steps are validated locally (`python -m build`, `cyclonedx-py environment`);
the signing/attestation steps require the CI OIDC identity and run on tag.

## 5. Module integrity (runtime)

`robobus crypto compliance` prints a SHA3-256 over all robobus sources
(`compliance.module_integrity()`). Pin the digest at release and compare on start-up — the
software-integrity self-test a FIPS 140-3 module runs at load (see
[CMVP-READINESS.md](CMVP-READINESS.md)).

## 6. Provenance

For SLSA build provenance, emit an in-toto attestation from CI (`slsa-github-generator`) tying
the artifact to the exact commit + builder. Combined with the Sigstore signature and SBOM
attestation, a consumer can verify *what* was built, *from where*, and *by whom*.
