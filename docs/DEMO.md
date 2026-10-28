# Authored local walkthrough

The stdlib report consumer accepts schema_version 1, origin AUTHORED, mode fixture,
run_id m19-authored-demo and runtime_verified false. It consumes the provisional
engine/pipeline API; integration remains INT-owned and runtime unverified.

Every case supplies id, label, category, requirement, origin, nonempty before/after
outcome arrays, nonempty original_inventory, patch_tags, expected_business,
observed_business and explanation. Nested projected/supervisor/attempt fields may
be supplied by the pipeline and remain explicitly authored. IDs must be unique.
The ledger requires known_usd 0, unknown_liability 0 and live_dispatch_enabled
false. No real billing observation or model call is implied. Study metrics are
not yet measured; report case counts are counts of authored examples only.

The writer creates a new directory with exactly `report.html`, `report.json` and
`manifest.json`. Each artifact is bounded to 2 MiB, runs to 100 cases, arrays to
1,000 elements and nesting to 16. HTML escapes all supplied text; an embedded CSP
disables scripts, connections, external resources and forms. The page presents
authored before/after strips, repair tags, business comparisons, explanations,
an explicit runtime-unverified banner and the pipeline's transformation account.

The verifier refuses duplicate JSON keys, nonfinite numbers, missing/extra files,
subdirectories, linked artifacts, symlink/junction ancestors, traversal, changed
digests, wrong origin/scope/mode, positive verification/measurement/independence
flags and changed derived panels. It regenerates HTML from validated report JSON
and compares exact bytes. Manifest artifact names are a closed fixed set;
untrusted inventory/source strings are displayed as text and never opened. There
is no source-path resolution, external source loading or real-study input route.

Use `verify-report --manifest-sha256` with a separately retained writer digest to
bind the bundle to earlier bytes. Without that anchor, a coordinated replacement
of the report and manifest cannot be detected. Even a matched digest establishes
byte identity only, never truth, rights, authentic custody or study correctness.
The verifier returns CONSISTENT_AUTHORED_ARTIFACTS, never scientific GO.

Output requires a trusted local parent directory. Concurrent hostile filesystem
mutation is outside this stdlib source's containment claim: path checks are not
an OS sandbox or an atomic no-follow tree capability. Partial writes are retained
on error; retry with a fresh directory, never clear or overwrite the old one.

Future validation, currently deferred: run intended commands on the integrated
source; verify real sibling shapes; exercise malicious HTML/JSON, traversal,
symlinks/junctions/hardlinks, changed/missing/extra artifacts and pinned/unpinned
tampering; inspect the rendered page; qualify filesystem containment and any
runtime authorization boundary before activation. No test or runtime check ran
during Dirty Mode construction.
