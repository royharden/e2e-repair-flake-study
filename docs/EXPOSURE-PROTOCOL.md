# Exposure and observer protocol

P1 declaration only, based on plan sections 4, 6.4/6.5 and P4/P7/P9/P10/P11. Gate A NO-GO. Observer/runner/sanitizer enforcement is not implemented or verified by these files.

## Record actual access

Each appointed seat records its own actual files/artifacts opened, action (read/write), exact actor/session, rooted path or approved opaque artifact reference, content revision/hash when known, timestamp when observed, purpose and applicable access grant. Unknown historical access remains unknown, never an empty list claiming no exposure. Record actual timestamps prospectively; do not invent/backdate prior events. Custodian-sensitive details stay in restricted custody, not in builder-visible records.

The partial observed_preparer_access list in roles.template.json records only this preparer's directly known reads/authorship. It deliberately says complete=false, omits reconstructed timestamps and is not a role attestation. It says nothing about another seat's access or the whole session's exposure. Future authoritative role/exposure records need their own authorized owner and review; a declaration is not evidence that barriers were enforced.

Before role work, authorized owner reviews appointment, prior exposures and access limits. Never infer independence from different callsigns/sessions alone. Builder differs from H0 author/custodian in actual session and eligible exposure. H0 author sees signed spec and clean app before variants; reviewer additionally receives H0 candidate and authorized review materials and produces the clause mapping. Log those inputs; freeze H0 before any variants. Labeller must not see arm results.

## Keep projections separate

admission/observer-boundaries.template.json declares intended boundaries for the final DL1 schema/INT join. Its separate design_policy has policy_status=DECLARED_ONLY and null implementation/verification references; the final-shaped observer_boundaries fields remain null/PENDING; do not convert policy prose into successful containment evidence.

Worker receives public SUT UI and allowed suite only, never SUT source, custody, oracle/control files, host credentials or Docker socket. No external/host-gateway access. Only approved output artifacts are written. An actual P4 containment receipt is required before ANY suite, fixtures included; this protocol does not supply it.

Future single deterministic sanitizer processes every model-facing crawl/failure artifact and records projection hashes. Strip identity hooks data-oracle-*, scripts/comments, control/source URLs and paths, variant metadata and evaluator content. Sanitized DOM/ARIA text, sanitized screenshots and bounded sanitized error/step summaries are intended projections. Raw traces/videos remain evaluator-side. SUT source/maps, truth/labels/seeds and oracle files are forbidden. R2 alone may receive H0 source as its explicit repair input, not SUT source or hidden truth.

Independent privileged oracle/observer remains custodian-side, outside product/worker, with expected values computed from spec examples and no implementation imports. Host integrity later joins authenticated reset/state/environment/observer identities with discovery inventory, reporter and process exit; missing/conflicting evidence stays UNKNOWN, never a green pass. No runtime observer or sanitizer is authored here.

## If an exposure occurs

Stop affected study use, record the event without spreading restricted content, notify authorized custodian/INT, quarantine or retire exposed held-out cases from future held-out use. Do not silently relabel, erase the event, move the same cases into a new sealed campaign, or strengthen H0 after exposure. Keep custodian prequalification separate from the one-time campaign reveal log; replication after reveal needs a new independently sealed corpus. Any decision stays with its authorized owner; this administrative package grants no custody access.

## Deferred checks

Actual independence/appointments, complete exposure records, role eligibility and admission refusal paths remain pending. Later authorized owners must qualify every model projection, oracle separation, host receipts and P4 containment before runtime study work. No tests/runtime/network/services/containers/credentials or study datasets were used here. No Roy scope/rights/timing signature is fabricated.

## Mapping to D1 schema at 6798459

Only the fragment's roles or observer_boundaries object is a candidate input to D1's final packet; metadata/constraints/preparer records/design_policy remain outside the packet because unknown top-level packet fields are refused. D1 retains packet/checklist ownership; no packet assembly or inventory refresh is performed here.

Each role now uses actor_id, appointment_reference, exposure and independence_confirmed. Every value is null: unappointed identities, unknown historical exposure and unverified independence are not fabricated. Unknown exposure MUST NOT become [] (which asserts no files opened); null independence MUST NOT become true. Actual canonical actor/session identity is needed, with builder distinct from custodian/H0 author and H0 reviewer distinct from H0 author. The partial preparer list cannot populate an appointed role's exposure automatically.

Observer declaration fields are worker_no_control_access, model_no_oracle_access, builder_no_heldout_access, custody_outside_repo and reference. All remain null because no actual declaration/reference is supplied. Intended boundaries live separately in design_policy; do not turn design intent into true assertions or claim live containment. The schema's reference is the authentic boundary design declaration reference, not a substitute runtime containment receipt.

These null fragments deliberately fail admission. Even a later structurally valid complete declaration packet returns PENDING_ATTESTATION_VERIFICATION, never GO; packet_valid does not imply attestation_verified or execution_authorized. Actual external receipt/exposure/rights verification and a qualified GO transition remain unfinished. scope_approval and ordering_disposition require genuine personally recorded Roy decisions; no builder populates them. Ordering disposition acknowledges earlier P6 source and cannot retroactively meet pre-code timing. Null rights never imply permission. D1/INT must reconcile the final packet and later exercise schema/validator behavior after Dirty closure/authorization.
