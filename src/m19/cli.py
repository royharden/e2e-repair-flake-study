"""Read-only status and administrative inspection; no study execution authority."""

import argparse
import json
from pathlib import Path

from m19.admission import AdmissionResult, validate_packet
from m19.admission.attestation import inspect_attestation


def _unique_object(pairs: list[tuple[str, object]]) -> dict:
    result: dict = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-JSON constant: {value}")


def main() -> int:
    parser = argparse.ArgumentParser(description="M19 source foundation — runtime unverified")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("status")
    admit = commands.add_parser("admit", help="Inspect declarations; never issue GO")
    admit.add_argument("--gate", choices=["A", "B"], required=True)
    admit.add_argument("--packet", type=Path, default=Path("admission.json"))
    args = parser.parse_args()
    if args.command == "admit":
        if args.gate == "B":
            result = validate_packet(None, "B")
        else:
            try:
                if args.packet.stat().st_size > 1048576:
                    raise ValueError("packet exceeds 1 MiB")
                packet = json.loads(args.packet.read_text(encoding="utf-8"),
                                    object_pairs_hook=_unique_object, parse_constant=_reject_constant)
                result = inspect_attestation(packet)
            except (OSError, UnicodeError, ValueError, RecursionError) as exc:
                result = AdmissionResult("A", "SKIPPED_DATA_ADMISSION", (f"packet unreadable or invalid: {exc}",))
        print(json.dumps(result.as_dict(), indent=2))
        return 2  # No executable GO path in this construction-only slice.
    print(json.dumps({
        "phase": "construction",
        "runtime": "unverified",
        "gate_a": "pending Roy and independent seats",
        "gate_b": "not_run",
        "study_results": "not yet measured",
        "execution_available": False,
    }, indent=2))
    return 0
