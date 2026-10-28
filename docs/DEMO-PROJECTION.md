# Authored demo projection

`m19.demo_pipeline.prepare_demo_run(scenario)` is a pure stdlib transformation.
It consumes schema version 1, `origin=AUTHORED`, `mode=fixture`, and
`runtime_verified=false`. It never opens fixture paths, fetches URLs, runs suites,
applies patches, invokes providers, resets a SUT or creates containment receipts.
Scientific Gate A stays NO_GO; execution remains unauthorized.

The provisional producer contract requires `run_id`, `cases`, `metrics`, and a
ledger explicitly declaring `known_usd=0`, `unknown_liability=0`, and
`live_dispatch_enabled=false`. Cases carry `id`, `label`, `category`, `requirement`,
`origin`, `before`, `after`, `original_inventory`, `patch_tags`, `expected_business`,
`observed_business`, and `explanation`. Attempts use `test_id` and `outcome` with
pass/fail/skipped/infra_error/unknown vocabulary. Outcomes are invented source
values, never collected evidence. Optional `fixture_text` supplies visible HTML.

For each phase the compatible addition `before_evidence` / `after_evidence`
contains authored `process_exit` (integer or null), `external_evidence` (bool or
null), and `status` (valid/invalid/unknown/infra_error). Missing evidence yields
unknown. The engine must supply these explicitly to illustrate a coherent green
fixture. They are illustrative flags, not OS or external-observer attestations.
Zero inventories/attempts, mismatched or duplicate attempts, deleted tests,
skips, false external evidence and explicit invalid status cannot green.
Infrastructure errors and unknowns retain distinct states. A pass/exit conflict
is invalid. Supervisor green means only an internally consistent authored example;
it never authorizes execution or demonstrates a genuine repair.

Contract v1.1 optional `repetitions` is an array of run arrays, each validated
against the original inventory separately. Repeated IDs across runs are allowed;
duplicates within one run are invalid. Optional `repetition_evidence` is an aligned
array of the same authored evidence objects. Absent evidence remains unknown.
`repetition_supervisors` retains per-run states; the case supervisor combines
after plus repetitions, prioritizing invalid, infra_error, then unknown. Empty
declared repetitions cannot green. Fractions under metrics require integer
`0 <= numerator <= denominator`, null value at denominator zero, and otherwise a
finite value matching numerator/denominator. This checks declared consistency,
not scientific eligibility or actual measurement.

`model_projection` is the only model-facing object. It contains generated task
IDs, sanitized requirement and optional visible text, and honest origin/mode.
Original IDs, labels, patch tags, business expectations, inventories, evidence,
metrics and source/control metadata remain evaluator-side in `cases`. Do not send
the whole result to a model. All HTML attributes (including hooks/data-oracle),
comments, and script/style/template/embedded payloads are discarded. Known visible
path/URL/metadata tokens are redacted. Benign visible text is preserved where
possible. This text allowlist is not a universal secret/prompt-injection detector:
authors must keep free-text fixture fields free of evaluator secrets. Consumers
must HTML-escape returned plain text. No DOM, CSS, accessibility-tree equivalence
or browser containment claim is made.

Hashes use SHA256 of UTF-8 JSON with sorted keys, compact separators,
`ensure_ascii=False`, and `allow_nan=False`. `source_hash` binds the complete
authored input; `projection_hash` binds only the model projection, and each case
has a corresponding projection hash. Hashes prove byte identity, not authority.
Input is copied rather than mutated. JSON-only finite bounds include 12 nesting
levels, 16,384 JSON nodes, 64 KiB strings, 1 MiB aggregate string/key bytes before
serialization, 1 MiB canonical scenario, and 128 cases. Outputs are
bounded by these finite inputs; no measured metrics are inferred or recomputed.

Construction status: runtime unverified. Deferred checks after explicit runtime
authorization: producer/report API integration, malformed/hostile input refusals,
sanitizer nested/malformed/entity/path cases, deterministic hashes, immutability,
all supervisor counterexamples, and actual containment/reset/admission. None has
run in Dirty Mode. This source creates no real H0/P0/held-out data or credentials.
