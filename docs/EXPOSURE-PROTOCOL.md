# Exposure and observer protocol

P1 declaration only, based on plan sections 4, 6.4/6.5 and P4/P7/P9/P10/P11. Gate A NO-GO. Observer/runner/sanitizer enforcement is not implemented or verified by these files.

## Record actual access

Each appointed seat records its own actual files/artifacts opened, action (read/write), exact actor/session, rooted path or approved opaque artifact reference, content revision/hash when known, timestamp when observed, purpose and applicable access grant. Unknown historical access remains unknown, never an empty list claiming no exposure. Record actual timestamps prospectively; do not invent/backdate prior events. Custodian-sensitive details stay in restricted custody, not in builder-visible records.

The partial observed_preparer_access list in roles.template.json records only this preparer's directly known reads/authorship. It deliberately says complete=false, omits reconstructed timestamps and is not a role attestation. It says nothing about another seat's access or the whole session's exposure. Future authoritative role/exposure records need their own authorized owner and review; a declaration is not evidence that barriers were enforced.

Before role work, authorized owner reviews appointment, prior exposures and access limits. Never infer independence from different callsigns/sessions alone. Builder differs from H0 author/custodian in actual session and eligible exposure. H0 author sees signed spec and clean app before variants; reviewer additionally receives H0 candidate and authorized review materials and produces the clause mapping. Log those inputs; freeze H0 before any variants. Labeller must not see arm results.

## Keep projections separate

admission/observer-boundaries.template.json declares intended boundaries for the final DL1 schema/INT join. Its policy_status=DECLARED_ONLY, missing implementation/verification references and PENDING status are intentional; do not convert policy prose into successful containment evidence.

Worker receives public SUT UI and allowed suite only, never SUT source, custody, oracle/control files, host credentials or Docker socket. No external/host-gateway access. Only approved output artifacts are written. An actual P4 containment receipt is required before ANY suite, fixtures included; this protocol does not supply it.

Future single deterministic sanitizer processes every model-facing crawl/failure artifact and records projection hashes. Strip identity hooks data-oracle-*, scripts/comments, control/source URLs and paths, variant metadata and evaluator content. Sanitized DOM/ARIA text, sanitized screenshots and bounded sanitized error/step summaries are intended projections. Raw traces/videos remain evaluator-side. SUT source/maps, truth/labels/seeds and oracle files are forbidden. R2 alone may receive H0 source as its explicit repair input, not SUT source or hidden truth.

Independent privileged oracle/observer remains custodian-side, outside product/worker, with expected values computed from spec examples and no implementation imports. Host integrity later joins authenticated reset/state/environment/observer identities with discovery inventory, reporter and process exit; missing/conflicting evidence stays UNKNOWN, never a green pass. No runtime observer or sanitizer is authored here.

## If an exposure occurs

Stop affected study use, record the event without spreading restricted content, notify authorized custodian/INT, quarantine or retire exposed held-out cases from future held-out use. Do not silently relabel, erase the event, move the same cases into a new sealed campaign, or strengthen H0 after exposure. Keep custodian prequalification separate from the one-time campaign reveal log; replication after reveal needs a new independently sealed corpus. Any decision stays with its authorized owner; this administrative package grants no custody access.

## Deferred checks

Actual independence/appointments, complete exposure records, role eligibility and admission refusal paths remain pending. Later authorized owners must qualify every model projection, oracle separation, host receipts and P4 containment before runtime study work. No tests/runtime/network/services/containers/credentials or study datasets were used here. No Roy scope/rights/timing signature is fabricated.
