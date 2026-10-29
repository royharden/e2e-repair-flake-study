"""Inspect the exact delegated source receipt; never grant execution authority."""

import hashlib
import json
from pathlib import Path


ADOPTED_SHA256 = "70c0a4f73c79eb4368c0f3e2fdcd1554e6eec503e6bdfef065d5b1ad7c237380"
DISCLAIMER = "DELEGATED — delegated, not personally signed by the owner"


def unique_object(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value: str) -> None:
    raise ValueError(f"non-JSON constant: {value}")


def inspect_demo_admission(path: Path) -> dict:
    """Byte consistency with t77u adoption, not authentication or a GO token."""
    result = {
        "purpose": "demo_construction", "construction_scope_accepted": False,
        "scientific_gate_a": "NO_GO", "gate_b": "UNAVAILABLE",
        "execution_authorized": False, "runtime": "unverified",
        "attestation_verified": False, "measured_results": False,
        "disclaimer": DISCLAIMER, "order_reference": "t77u",
        "status": "REJECTED", "reason": "receipt unavailable or changed",
    }
    try:
        if path.is_symlink() or (hasattr(path, "is_junction") and path.is_junction()):
            raise ValueError("linked receipt refused")
        if path.stat().st_size > 131072:
            raise ValueError("receipt too large")
        raw = path.read_bytes()
        if hashlib.sha256(raw).hexdigest() != ADOPTED_SHA256:
            raise ValueError("receipt differs from adopted t77u bytes")
        receipt = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                             parse_constant=reject_constant)
        # Exact pinned bytes carry the full decisions, held actions and provenance.
        if receipt["status"] != "ADOPTED" or receipt["purpose"] != "demo_construction":
            raise ValueError("wrong receipt purpose/status")
        if receipt["authority"]["order_reference"] != "t77u":
            raise ValueError("wrong owner order")
        result.update({
            "construction_scope_accepted": True,
            "status": "DEMO_CONSTRUCTION_ACCEPTED_DELEGATED",
            "reason": "matches historical source adoption only; revocation not checked",
            "receipt_sha256": ADOPTED_SHA256,
            "authority": receipt["authority"],
            "scope_approval_delegated": receipt["scope_approval_delegated"],
        })
    except (OSError, ValueError, UnicodeError, KeyError, TypeError, RecursionError) as exc:
        result["reason"] = str(exc)
    return result
