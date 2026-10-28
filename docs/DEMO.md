# Authored local walkthrough

The stdlib report consumer accepts schema_version 1, origin AUTHORED, mode fixture,
run_id m19-authored-demo and runtime_verified false. It consumes the provisional
engine/pipeline API; integration remains INT-owned and runtime unverified.

Every case supplies id, label, category, requirement, origin, before/after
outcome arrays, original_inventory, patch_tags, expected_business,
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

Contract v1.1 validation requires each outcome entry to contain a nonempty test_id
from the unique original inventory and an outcome in pass/fail/skipped/infra_error/
unknown. IDs are unique within each run. Before and repetition runs account for
all original IDs; after can omit IDs only in an explicitly silenced authored case.
Optional repetitions are displayed per run. The report does not treat silencing
or omitted evidence as a green outcome. Other invalid inventory examples are
rejected, rather than accepted as evidence. Categories use the declared finite
set. Metrics require AUTHORED origin and label fixture-derived; not scientific results, nonnegative
integer counters, and complete numerator/denominator/value fractions. Fractions
match their counters; a zero denominator has null value. Unknown/infra evidence
is retained in the source account, never recast as measured green results.
Scientific eligibility/denominator computation remains the engine's declared
algorithm and requires later integrated validation. No scientific score is inferred.
The ledger also accepts the contract's compatibility liability key only at zero.

## Supervisor reconciliation (contract v1.3)

Dedicated invented-fixture supervisor panels sit beside before, after/overall and
each repetition strip. They display status, green, reasons, AUTHORED origin,
runtime_verified false, process_exit and external_evidence fixture flags. These
are invented toy declarations, never process observations or containment proof.
After/overall is the D3 aggregate account when repetitions exist; individual
repetition supervisors stay visible. Unknown, invalid and infra states remain
explicit, and missing supervisors display unknown/false with a missing-source
reason. Nothing fills null evidence with green.

Supplied flag objects have exactly origin, runtime_verified, process_exit,
external_evidence and status. Supervisors add exactly green and reasons. Status
is valid/invalid/unknown/infra_error; exits are null or bounded integers -255..255;
external flags are null or booleans. Reasons are bounded strings. Green requires
valid, complete nonempty inventory, all-pass outcomes, fixture exit0 and explicit
true external fixture evidence, and cannot contradict a repeated-run supervisor.
Valid phases require explicit valid authored flags with a process/outcome account
that agrees. No real execution or external-evidence claim is made. Repetition
metadata must align with its individual runs; orphan metadata rejects.

Zero inventory is retained only with explicit invalid before/after supervisors.
Missing outcome evidence can be retained as unknown/invalid/infra, never as valid
or green. Malformed outcome entries, duplicate/unexpected IDs and invalid flag
shapes still reject. This supersedes earlier generic nonempty-inventory and
complete-run wording where a disclosed invalid authored example is retained.
The metrics root label is exactly `fixture-derived; not scientific results`.
D2 declarations use the common D3 helper; this report validates declaration shape
and renders them as authored, without recomputing measured eligibility/statistics.
Actual engine/helper/report integration and rendering remain runtime unverified.

Installed producer metadata compatibility: the metrics root may additionally
declare `runtime_verified: false` and `not_measured: true`, only with these exact
boolean values. These two root fields are authored metadata, not counters. The
opposite values, numeric lookalikes, nested copies and other boolean metadata
reject. Boolean counters, fraction numerators/denominators/values still reject;
the existing AUTHORED origin, exact label, finite numbers and fraction/null
rules remain. This source repair was traced against the installed engine and
shared helper; no function, command, test or report rendering was executed.
