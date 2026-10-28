# Repair versus a green test strip

M19 is source for a small, keyless walkthrough of benign repair, false repair,
silencing, intermittent failure and infrastructure failure. Its invented cases
show why a passing test strip can hide a broken business journey.

**AUTHORED fixtures · runtime unverified · not study results.** No demonstration,
suite, browser, provider or model has been executed to validate this source.
Scientific Gate A remains NO_GO; human-independent roles, rights, containment,
authenticated approval and Gate B remain held.

The intended source journey is `demo_engine.build_demo_scenario()` →
`demo_pipeline.prepare_demo_run()` → `demo_report.write_demo_report()`.
The report is escaped, self-contained HTML plus JSON and a relative SHA-256
artifact manifest. It shows fixture outcomes, repair tags, explanations and a
zero-cost no-live ledger. It makes no measured study claims.

After separate runtime authorization and environment activation, the intended
commands are:

```text
m19 status
m19 demo-admission --packet demo-admission.json
m19 demo --fixture --out <new-local-directory>
m19 verify-report --out <report-directory> --manifest-sha256 <externally-retained-digest>
```

These commands are prospective documentation, not executed examples. The report
parent directory must already exist; the output directory must not exist. No
overwrite, deletion, external assets, live input or network path is supported.
Retain the returned manifest digest separately if later tamper binding matters.
An unpinned self-contained manifest proves internal consistency only.

`m19 admit --gate A` and `--gate B` retain scientific refusal behavior. The
separate [delegated demo receipt](docs/DEMO-ADMISSION.md) matches a historical
source-only adoption under owner order t77u; it is not authentication, a personal
owner signature, a current revocation check or permission to run anything.

See [walkthrough and report limits](docs/DEMO.md), [contract seams](docs/CONTRACTS.md)
and [positive grammar subset](docs/GRAMMAR.md). The existing Node AST checker is
source only; dependency availability and lock resolution are unverified. OS
containment must be separately qualified before suites run. No dependencies,
credentials, environments, CI or deployment were activated. USD 0 spent. No
publication or source-license clearance is implied. Coordination and transcripts
remain outside this product repository.
