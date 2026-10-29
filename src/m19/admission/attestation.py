"""Keyless verifier port. No verifier implementation, receipt I/O or GO transition."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import StrEnum
import hashlib
import json
from typing import Protocol

from m19.admission import AdmissionResult, ROLES, _text, validate_packet
from m19.contracts import digest, identifier


class AuthorityDecision(StrEnum):
    VERIFIED = "verified"
    DENIED = "denied"
    UNKNOWN = "unknown"


def _aware(value: datetime) -> None:
    if not isinstance(value, datetime) or value.utcoffset() is None:
        raise ValueError("timezone-aware datetime required")


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


@dataclass(frozen=True)
class VerificationContext:
    """Trusted host inputs, never inferred from packet declarations or Git presence."""

    source_snapshot_sha256: str
    policy_sha256: str
    context_id: str
    valid_from: datetime
    valid_until: datetime

    def __post_init__(self) -> None:
        digest(self.source_snapshot_sha256)
        digest(self.policy_sha256)
        identifier(self.context_id)
        _aware(self.valid_from)
        _aware(self.valid_until)
        if self.valid_until <= self.valid_from:
            raise ValueError("nonempty validity window required")


@dataclass(frozen=True)
class ReceiptBinding:
    claim: str
    reference: str
    receipt_sha256: str

    def __post_init__(self) -> None:
        if not _text(self.claim) or not _text(self.reference):
            raise ValueError("non-placeholder claim and exact reference required")
        digest(self.receipt_sha256)


@dataclass(frozen=True)
class VerificationRequest:
    """Canonical packet bytes and one digest bind every claim to this exact context."""

    packet_json: bytes
    packet_sha256: str
    context: VerificationContext
    receipts: tuple[ReceiptBinding, ...]
    request_sha256: str


@dataclass(frozen=True)
class AuthorityReply:
    decision: AuthorityDecision
    authority_id: str
    request_sha256: str
    checked_at: datetime
    valid_until: datetime
    reason: str


class AuthorityVerifier(Protocol):
    def verify(self, request: VerificationRequest) -> AuthorityReply:
        """Authenticate ALL receipts, appointments/exposure and owner scope/order.

        Verify receipt bytes/digests, issuer authority, current revocation and source
        coverage against the trusted context, not merely a caller's JSON assertions.
        Unknown evidence/authority must never produce VERIFIED. No implementation
        or trust provisioning is supplied by this module.
        """
        ...


def _request(packet: dict, context: VerificationContext,
             bindings: tuple[ReceiptBinding, ...]) -> VerificationRequest:
    references = {"originality": packet["originality"]["reference"],
                  "observer_boundaries": packet["observer_boundaries"]["reference"],
                  "scope_approval": packet["scope_approval"]["reference"],
                  "ordering_disposition": packet["ordering_disposition"]["reference"]}
    for role in ROLES:
        references[f"roles/{role}"] = packet["roles"][role]["appointment_reference"]
    for declaration in packet["rights_declarations"]:
        references[f"rights/{declaration['source_id']}"] = declaration["reference"]
    if not isinstance(bindings, tuple) or any(not isinstance(b, ReceiptBinding) for b in bindings):
        raise ValueError("immutable typed receipt bindings required")
    supplied = {binding.claim: binding for binding in bindings}
    if len(supplied) != len(bindings) or set(supplied) != set(references):
        raise ValueError("exactly one binding for every required claim; no duplicates or extras")
    if any(supplied[claim].reference != reference for claim, reference in references.items()):
        raise ValueError("receipt reference differs from exact packet reference")
    packet_json = _canonical(packet)
    packet_hash = hashlib.sha256(packet_json).hexdigest()
    ordered = tuple(supplied[claim] for claim in sorted(supplied))
    envelope = {"contract": "m19-gate-a-attestation-v1", "packet_sha256": packet_hash,
                "source_snapshot_sha256": context.source_snapshot_sha256,
                "policy_sha256": context.policy_sha256, "context_id": context.context_id,
                "valid_from": context.valid_from.astimezone(timezone.utc).isoformat(),
                "valid_until": context.valid_until.astimezone(timezone.utc).isoformat(),
                "receipts": [{"claim": b.claim, "reference": b.reference,
                              "receipt_sha256": b.receipt_sha256} for b in ordered]}
    return VerificationRequest(packet_json, packet_hash, context, ordered,
                               hashlib.sha256(_canonical(envelope)).hexdigest())


def inspect_attestation(packet: object, *, context: VerificationContext | None = None,
                        bindings: tuple[ReceiptBinding, ...] = (),
                        verifier: AuthorityVerifier | None = None,
                        expected_authority: str | None = None) -> AdmissionResult:
    """Fail closed; configured verification can attest declarations, never issue GO.

    The trusted host must provision context/authority/verifier independently of the
    packet. The CLI exposes no verifier flag or environment switch; the trusted
    host must never provision a fake verifier as an authority. Decisions are
    checked fresh each call; there is no approval cache in this module.
    """
    structural = validate_packet(packet)
    if not structural.packet_valid:
        return structural

    def pending(reason: str, decision: str = "unknown") -> AdmissionResult:
        return AdmissionResult("A", "PENDING_ATTESTATION_VERIFICATION", (reason,),
                               packet_valid=True, authority_decision=decision)

    if verifier is None or not _text(expected_authority):
        return pending("Trusted authority verifier is unconfigured; no receipt authenticated", "unconfigured")
    if not isinstance(context, VerificationContext):
        return pending("Trusted source/policy/validity context is missing")
    try:
        checked_now = datetime.now(timezone.utc)
        if not context.valid_from <= checked_now < context.valid_until:
            return pending("Verification context is not yet valid or has expired")
        request = _request(packet, context, bindings)
        reply = verifier.verify(request)
        checked_now = datetime.now(timezone.utc)
        if not context.valid_from <= checked_now < context.valid_until:
            return pending("Verification context expired during verification")
        if not isinstance(reply, AuthorityReply) or not isinstance(reply.decision, AuthorityDecision):
            return pending("Verifier returned an unknown decision format")
        if reply.authority_id != expected_authority or reply.request_sha256 != request.request_sha256:
            return pending("Verifier identity or exact request binding mismatch")
        if not _text(reply.reason):
            return pending("Verifier decision reason missing")
        _aware(reply.checked_at)
        _aware(reply.valid_until)
        if not (context.valid_from <= reply.checked_at <= checked_now < reply.valid_until <= context.valid_until):
            return pending("Verifier decision is stale, future-dated or outside context validity")
        if reply.decision is AuthorityDecision.DENIED:
            return AdmissionResult("A", "SKIPPED_DATA_ADMISSION", ("Trusted verifier denied attestation",),
                                   packet_valid=True, authority_decision="denied")
        if reply.decision is not AuthorityDecision.VERIFIED:
            return pending("Trusted verifier could not authenticate every required claim")
        return AdmissionResult("A", "VERIFIED_ATTESTATION_NO_GO",
                               ("Attestation port accepted configured verifier decision; GO transition remains unavailable",),
                               packet_valid=True, attestation_verified=True, authority_decision="verified")
    except Exception:
        # External adapters and malformed binding data fail closed; do not echo
        # adapter errors that could contain receipt material or credentials.
        return pending("Attestation binding or verifier failed; no authority established")
