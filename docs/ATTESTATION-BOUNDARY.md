# External attestation boundary — incomplete trust integration

Dirty Mode source construction only; runtime unverified. No receipt was opened,
authenticated, signed or generated. No configured trusted authority verifier exists
in this app. Gate A remains NO-GO; authentic GO remains blocked/incomplete.

`m19.admission.attestation` provides immutable request/context/receipt/reply types and
`AuthorityVerifier.verify(request) -> AuthorityReply`. It supplies no verifier, keys,
accounts, signature scheme, network transport, file reader or trust provisioning.
The CLI invokes `inspect_attestation(packet)` without a verifier and remains pending
for complete structural declarations; malformed declarations remain refused.
The existing packet schema and D2-owned `admission.json` are unchanged.

## What is bound

The trusted integrating host must provide `VerificationContext` independently of the
packet: lowercase SHA256 pins for the source snapshot and admission policy; an opaque
context ID; timezone-aware `valid_from` and exclusive `valid_until`. A nonempty window
is required. This pin is an identity claim, not proof of inventory completeness or
source authenticity. The authority must verify it against an independently trusted
source snapshot and policy. Changed source/policy/context must receive new verification.

The packet is serialized as sorted-key, compact, ASCII-escaped JSON with nonfinite
numbers refused; SHA256 identifies these canonical parsed JSON bytes, not the input
file's whitespace. The request retains those immutable bytes. Arrays retain their
order, and changed declaration content changes the packet pin. Canonical formatting
does not authenticate the packet or its author.

Each `ReceiptBinding` carries an exact `claim`, exact packet `reference`, and lowercase
`receipt_sha256`. These are opaque identity bindings, never filesystem paths to open.
Required claim keys are:

- `originality`, `observer_boundaries`, `scope_approval`, `ordering_disposition`;
- `roles/builder`, `roles/h0_author`, `roles/h0_reviewer`, `roles/custodian`, `roles/labeller`;
- one `rights/<source_id>` per structurally valid rights declaration.

The tuple must contain exactly one binding per required key, with no extras, duplicates
or reference substitution. Receipt digests must identify the actual external evidence,
not a hash of the packet masquerading as authentication. The external verifier must
establish that correspondence. Multiple claims may refer to one real receipt if that
receipt actually supports them; the verifier must check each claim rather than count files.

One request SHA256 binds contract revision `m19-gate-a-attestation-v1`, canonical packet
hash, source snapshot hash, policy hash, context ID, UTC validity window and the sorted
claim/reference/receipt-digest list. The verifier receives the exact packet bytes and
must authenticate every supported claim, including actual appointments/identity lineage,
exposure/independence, rights, originality, observer design and Roy scope/ordering.
Declared boundary evidence is distinct from P4 runtime containment.

## Decisions and freshness

Only code-provisioned `verifier` and `expected_authority` can activate the port. These
are trusted host dependencies, not packet fields, CLI flags or environment switches.
Passing an object that implements the Python protocol is not evidence it is trusted.
A future integration must establish that trust separately; never install a permissive
or mock adapter as a production authority. This source does not solve that prerequisite.

The external verifier returns an `AuthorityReply` with enum decision `verified`, `denied`
or `unknown`; authority ID; exact request SHA256; timezone-aware checked-at and expiry;
and a non-placeholder reason. Authority ID must match the independently configured
authority, not an identifier from the packet. This is a consistency check on a trusted
adapter reply, not cryptographic authentication of an arbitrary caller-supplied reply.

Missing/unconfigured verifier or context, invalid receipt bindings, an exception,
unknown decision, stale/future/out-of-window reply, request mismatch or authority mismatch
cannot establish attestation. They yield `PENDING_ATTESTATION_VERIFICATION` with
`attestation_verified: false`. Structurally valid packets retain `packet_valid: true`.
A bound current denial yields `SKIPPED_DATA_ADMISSION`, `authority_decision: denied`;
missing or unusable denial context still fails closed as pending, never verified.

The host samples its clock before and after verification; the context must be valid
at both points. Reply timing requires context start <= checked_at <= current time <
reply expiry <= context expiry. There is no decision cache; every invocation requires
a new verifier call. The adapter must check current revocation/authority and must not
return a stale cached approval as fresh evidence. A trustworthy host clock and proper
context rotation are integration assumptions, not proven properties of this module.

A configured trusted adapter's valid `verified` reply yields
`VERIFIED_ATTESTATION_NO_GO`, `attestation_verified: true`, `packet_valid: true` and
`execution_authorized: false`. This branch is source only and has never been exercised.
It does not satisfy pre-code timing, grant Gate A GO, authorize P2+, prove containment,
qualify Gate B or supply study acceptance. No persisted approval receipt or execution
token is emitted. Adapter exceptions are not echoed, to avoid exposing private evidence.

## Exact blocked remainder

The owner must appoint genuine study roles and provide actual rights/originality,
exposure/independence, scope approval and prior-P6 ordering applicability evidence.
`by: Roy Harden`, booleans, a hash, Git possession, file existence, a renamed callsign,
source acceptance or DL child review cannot substitute. The pre-code ordering caveat
is preserved and cannot be retrospectively met by this port.

A later explicit grant must select and qualify an actually trusted existing authority
integration (or resolve its absence), bind trusted policy/source/context provisioning,
implement an authenticated Gate A GO transition with appropriate evidence, and reconcile
inventory/packet inputs with D2. Until then the genuine GO path is blocked, not completed.
No missing trust capability is bypassed and no key acquisition is requested by this slice.

Deferred until runtime authorization: positive/hostile binding and stale/replay checks;
packet/source/policy mutation and substitution cases; unknown/denied/exception adapter
outcomes; missing verifier/context; clock/expiry behavior; CLI refusal/default behavior;
actual trusted adapter authentication, revocation, inventory coverage and GO transition.
No product imports, CLI invocations or tests ran here. USD 0; no secrets or key placeholders.
