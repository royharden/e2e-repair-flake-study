# Administrative admission inspection (P1)

Source construction only; runtime unverified. `m19 status` retains the foundation status.
`m19 admit --gate A --packet admission.json` reads one UTF-8 JSON administrative packet,
prints a JSON disposition and exits 2. It writes no receipts, artifacts or study state.
Gate B returns `SKIPPED_QUALIFICATION` without opening the packet; qualification is not implemented.

`SKIPPED_DATA_ADMISSION` includes explicit missing/invalid-field reasons. A complete declaration
packet returns `PENDING_ATTESTATION_VERIFICATION`, `packet_valid: true`,
`attestation_verified: false`, `execution_authorized: false`. It never returns GO:
JSON assertions cannot authenticate Roy's signature, independence or source rights.
The authorized owner must later verify actual evidence and implement/qualify the admission transition.
This is an explicit remaining integration boundary, not completed scientific admission.

The CLI now routes Gate A through the keyless `inspect_attestation` port with no
configured verifier. `authority_decision` is `unconfigured` by default; structural
refusals still take precedence. No verifier selection flag, receipt file loader,
environment override, fake adapter or GO path is supplied. See
[ATTESTATION-BOUNDARY.md](ATTESTATION-BOUNDARY.md) for the typed future trust contract.
Only a separately configured, actually trusted verifier could return a bound
`VERIFIED_ATTESTATION_NO_GO` through the programmatic port; even that result keeps
`execution_authorized: false`. No such verifier exists in this app or ran here.

## Packet seam

`schemas/admission.schema.json` describes the administrative structure; stdlib
`m19.admission.validate_packet` applies semantic checks without a JSON Schema dependency.
Schema validation alone is insufficient. Top-level unknown fields are refused.
All required text must be nonempty and must not contain placeholder words, angle-bracket
placeholders, PENDING, UNASSIGNED, UNKNOWN, TODO, TBD, DRAFT, NULL or NONE (case insensitive,
including underscore-separated tokens such as `pending_builder`).
Do not place secrets, held-out data or variant content in this packet.

| Field | Required shape and meaning |
| --- | --- |
| `source_inventory` | Nonempty array of `{id, reference, purpose, provenance}`; unique opaque IDs use the existing contracts identifier grammar. Administrative references only. |
| `rights_declarations` | One `{source_id, permitted: true, basis, reference, declared_by}` per inventory ID; no duplicates or uninventoried IDs. These are actual rights declarations, not assumed licenses. |
| `originality` | `{original_sut: true, declaration, reference, declared_by}` with an actual originality receipt. |
| `roles` | Exactly builder, h0_author, h0_reviewer, custodian, labeller. Each has `{actor_id, appointment_reference, exposure: [file references], independence_confirmed: true}`. An empty exposure list is allowed only as an explicit declaration of no files opened. |
| `split_policy` | `{family_split: true, disjoint_families: true, floors: {dev: {R, B, families}, heldout: {R, B, families, R_families}}}`. Numeric floors are planned minimum commitments, never measured counts. |
| `observer_boundaries` | `{worker_no_control_access: true, model_no_oracle_access: true, builder_no_heldout_access: true, custody_outside_repo: true, reference}`. Declarations do not prove containment. |
| `scope_approval` | `{by: "Roy Harden", reference, approved_scope, timestamp}` from Roy's actual personally recorded instruction. Timestamp must include a timezone. Never populate it on Roy's behalf. |
| `ordering_disposition` | `{by: "Roy Harden", reference, disposition, timestamp, prior_code_acknowledged: true}` from the actual decision about P6 source predating Gate A. This additional required seam preserves the current NO-GO caveat; it does not retrospectively satisfy the pre-code ordering. |

Canonical role IDs must identify the actual actor/session, not newly assigned labels that
hide the same author. Builder must differ from custodian and H0 author; H0 reviewer must differ
from H0 author. Identity comparisons ignore case. Explicit builder custody/held-out exposure
and H0 author/reviewer variant/custody/held-out exposure are refused conservatively by path text.
This lexical screen cannot establish absence of semantic exposure: external verification remains mandatory.
Labeller exposure and custodian exposure must be evaluated by that owner against the plan's reveal boundaries.

Dev floors are at least 12 R, 6 B, 4 semantic families. Held-out floors are at least
24 R, 12 B, 8 families, including at least 5 R families. Booleans, floats and numeric
strings are refused. Family counts cannot exceed total variants; R families cannot
exceed either total families or R variants. No actual corpus is authored or inspected here.

## Field examples for later validation (not executed tests)

- Shape-acceptable floor fragment: `"dev": {"R": 12, "B": 6, "families": 4}`.
- Rejected floor fragments: `"R": true`, `"R": "12"`, or heldout `"R_families": 4`.
- Shape-acceptable role exposure fragment: `"exposure": []`; actual appointment and independence still need verification.
- Rejected identity pair: builder `"actor_id": "seat-1"` and custodian `"actor_id": "SEAT-1"`.
- Rejected rights: an inventory item without its declaration, `"permitted": false`, or `"reference": "PENDING"`.
- Rejected scope: absent receipt, agent-authored approval, or a timezone-free timestamp.
  Timestamps use `YYYY-MM-DDTHH:MM:SS[.fraction](Z|+HH:MM|-HH:MM)`; compact ISO forms are refused.
- Even otherwise complete fields yield pending verification, never an execution permission.

No full accepted packet or invented approval is provided. The incomplete packet assembly owner
must preserve null/PENDING fields until the genuine actors supply receipts. INT reconciles
this seam with the rights/inventory and role documentation owners; reserved D3/D4 paths stay untouched.

## Deferred validation and integration

After Dirty Mode closure and explicit authorization: exercise positive/hostile admission cases,
duplicate JSON keys, nonstandard constants, malformed/oversized input and CLI exits; compare schema
and consumer behavior; verify actual appointments/rights/Roy receipts and ordering applicability;
qualify an authenticated GO transition with the authorized owner. Gate B/P4 containment and all
study execution remain unavailable. No runtime tests, CLI executions or external evidence checks
were performed for this source slice. No API key placeholders or credentials are required.
