"""Administrative packet inspection, without execution or attestation authority."""

from dataclasses import dataclass
from datetime import datetime
import re

from m19.contracts import identifier


ROLES = ("builder", "h0_author", "h0_reviewer", "custodian", "labeller")
FLOORS = {"dev": {"R": 12, "B": 6, "families": 4},
          "heldout": {"R": 24, "B": 12, "families": 8, "R_families": 5}}
BOUNDARIES = ("worker_no_control_access", "model_no_oracle_access",
              "builder_no_heldout_access", "custody_outside_repo")
_PENDING = re.compile(r"(?<![A-Za-z0-9])(pending|placeholder|unassigned|unknown|todo|tbd|draft|null|none)(?![A-Za-z0-9])", re.I)
_TIMESTAMP = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(?:\.[0-9]+)?(?:Z|[+-][0-9]{2}:[0-9]{2})")


def _text(value: object) -> bool:
    return (isinstance(value, str) and bool(value.strip())
            and _PENDING.search(value) is None and "<" not in value and ">" not in value)


def _timestamp(value: object) -> bool:
    if not _text(value) or _TIMESTAMP.fullmatch(str(value)) is None:
        return False
    try:
        return datetime.fromisoformat(str(value).replace("Z", "+00:00")).utcoffset() is not None
    except ValueError:
        return False


def _opaque(value: object) -> bool:
    if not _text(value):
        return False
    try:
        identifier(value)
    except ValueError:
        return False
    return True


def _object(value: object) -> dict:
    return value if isinstance(value, dict) else {}


@dataclass(frozen=True)
class AdmissionResult:
    gate: str
    status: str
    reasons: tuple[str, ...]
    packet_valid: bool = False
    execution_authorized: bool = False

    def as_dict(self) -> dict:
        return {"gate": self.gate, "status": self.status, "reasons": list(self.reasons),
                "packet_valid": self.packet_valid, "execution_authorized": self.execution_authorized,
                "runtime": "unverified", "attestation_verified": False}


def validate_packet(packet: object, gate: str = "A") -> AdmissionResult:
    """Check declarations only. Never mint a signature, GO receipt or study authority.

    Even a complete packet requires external verification by the authorized owner.
    Gate B qualification is deliberately unavailable in this P1 source slice.
    """
    if gate != "A":
        return AdmissionResult(gate, "SKIPPED_QUALIFICATION", ("Gate B qualification is unavailable",))
    reasons: list[str] = []
    if not isinstance(packet, dict):
        return AdmissionResult(gate, "SKIPPED_DATA_ADMISSION", ("packet must be an object",))
    required = {"rights_declarations", "originality", "roles", "split_policy",
                "observer_boundaries", "source_inventory", "scope_approval", "ordering_disposition"}
    for key in sorted(required - packet.keys()):
        reasons.append(f"{key}: missing")
    for key in sorted(packet.keys() - required, key=str):
        reasons.append(f"unexpected packet field: {key}")

    roles = _object(packet.get("roles"))
    actors: dict[str, str] = {}
    for role in ROLES:
        seat = _object(roles.get(role))
        actor = seat.get("actor_id")
        if not _opaque(actor):
            reasons.append(f"roles.{role}.actor_id: assigned opaque identity required")
        else:
            actors[role] = actor.casefold()
        if not _text(seat.get("appointment_reference")):
            reasons.append(f"roles.{role}: actual appointment reference required")
        exposure = seat.get("exposure")
        if not isinstance(exposure, list) or any(not _text(p) for p in exposure):
            reasons.append(f"roles.{role}.exposure: explicit file list required (empty allowed)")
        if seat.get("independence_confirmed") is not True:
            reasons.append(f"roles.{role}: independence declaration required; labels alone are insufficient")
        if isinstance(exposure, list):
            # Reject explicit forbidden exposure; semantic attestation remains external.
            denied = {"builder": ("custody", "heldout", "held-out"),
                      "h0_author": ("variant", "custody", "heldout", "held-out"),
                      "h0_reviewer": ("variant", "custody", "heldout", "held-out")}.get(role, ())
            if any(isinstance(p, str) and any(word in p.casefold() for word in denied) for p in exposure):
                reasons.append(f"roles.{role}.exposure: forbidden material declared")
    for left, right in (("builder", "custodian"), ("builder", "h0_author"), ("h0_author", "h0_reviewer")):
        if left in actors and actors.get(left) == actors.get(right):
            reasons.append(f"roles: {left} must differ from {right}")
    if set(roles) - set(ROLES):
        reasons.append("roles: unknown role")

    inventory = packet.get("source_inventory")
    source_ids: set[str] = set()
    if not isinstance(inventory, list) or not inventory:
        reasons.append("source_inventory: nonempty administrative inventory required")
    else:
        for index, source in enumerate(inventory):
            source = _object(source)
            source_id = source.get("id")
            if not _opaque(source_id) or source_id in source_ids:
                reasons.append(f"source_inventory[{index}].id: unique opaque id required")
            else:
                source_ids.add(source_id)
            if not all(_text(source.get(k)) for k in ("reference", "purpose", "provenance")):
                reasons.append(f"source_inventory[{index}]: reference/purpose/provenance required")

    rights = packet.get("rights_declarations")
    covered: set[str] = set()
    if not isinstance(rights, list) or not rights:
        reasons.append("rights_declarations: nonempty declarations required")
    else:
        for index, declaration in enumerate(rights):
            declaration = _object(declaration)
            source_id = declaration.get("source_id")
            if not isinstance(source_id, str) or source_id not in source_ids or source_id in covered:
                reasons.append(f"rights_declarations[{index}]: unique inventoried source_id required")
            else:
                covered.add(source_id)
            if (declaration.get("permitted") is not True
                    or not all(_text(declaration.get(k)) for k in ("basis", "reference", "declared_by"))):
                reasons.append(f"rights_declarations[{index}]: explicit permission, basis and receipt required")
    if source_ids - covered:
        reasons.append("rights_declarations: every inventory item needs rights coverage")
    originality = _object(packet.get("originality"))
    if (originality.get("original_sut") is not True
            or not all(_text(originality.get(k)) for k in ("declaration", "reference", "declared_by"))):
        reasons.append("originality: original SUT declaration and receipt required")

    split = _object(packet.get("split_policy"))
    if split.get("family_split") is not True or split.get("disjoint_families") is not True:
        reasons.append("split_policy: split by semantic family with disjoint dev/heldout families required")
    floors = _object(split.get("floors"))
    for group, limits in FLOORS.items():
        counts = _object(floors.get(group))
        for name, minimum in limits.items():
            value = counts.get(name)
            if type(value) is not int or value < minimum:
                reasons.append(f"split_policy.floors.{group}.{name}: integer >= {minimum} required")
        family_count = counts.get("families")
        r_families = counts.get("R_families")
        r_count = counts.get("R")
        if (type(r_families) is int and type(family_count) is int and type(r_count) is int
                and (r_families > family_count or r_families > r_count)):
            reasons.append(f"split_policy.floors.{group}: inconsistent R family count")
        b_count = counts.get("B")
        if (type(family_count) is int and type(r_count) is int and type(b_count) is int
                and family_count > r_count + b_count):
            reasons.append(f"split_policy.floors.{group}: more families than variants")
    boundaries = _object(packet.get("observer_boundaries"))
    for key in BOUNDARIES:
        if boundaries.get(key) is not True:
            reasons.append(f"observer_boundaries.{key}: explicit declaration required")
    if not _text(boundaries.get("reference")):
        reasons.append("observer_boundaries.reference: boundary design reference required")
    approval = _object(packet.get("scope_approval"))
    if (approval.get("by") != "Roy Harden"
            or not all(_text(approval.get(k)) for k in ("reference", "approved_scope"))
            or not _timestamp(approval.get("timestamp"))):
        reasons.append("scope_approval: genuine Roy receipt, scope and timezone-aware timestamp required")
    ordering = _object(packet.get("ordering_disposition"))
    if (ordering.get("by") != "Roy Harden" or ordering.get("prior_code_acknowledged") is not True
            or not all(_text(ordering.get(k)) for k in ("reference", "disposition"))
            or not _timestamp(ordering.get("timestamp"))):
        reasons.append("ordering_disposition: actual Roy decision on prior P6-before-Gate-A ordering required")
    if reasons:
        return AdmissionResult(gate, "SKIPPED_DATA_ADMISSION", tuple(reasons))
    return AdmissionResult(gate, "PENDING_ATTESTATION_VERIFICATION",
                           ("Authorized owner must verify receipts, exposure and ordering disposition; no GO issued",),
                           packet_valid=True)
