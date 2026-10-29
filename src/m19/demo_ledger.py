"""No-live authored-fixture bookkeeping, not billing or runtime accounting."""
from copy import deepcopy
from dataclasses import dataclass, field
import re

_OUTCOMES = {"pass", "fail", "skipped", "infra_error", "unknown"}


def _identifier(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value) is not None


@dataclass(slots=True)
class DemoLedger:
    """Local fixture ledger with no provider or dispatch capability."""
    _attempts: list[dict] = field(default_factory=list, init=False, repr=False)

    def record_attempt(self, case_id: str, phase: str, outcomes: list[dict]) -> None:
        if (not _identifier(case_id) or not isinstance(phase, str)
                or phase not in {"before", "after", "repetition"}):
            raise ValueError("bounded fixture case and phase required")
        if not isinstance(outcomes, list) or len(outcomes) > 64 or len(self._attempts) >= 1024:
            raise ValueError("fixture ledger bounds exceeded")
        for item in outcomes:
            if (not isinstance(item, dict) or set(item) != {"test_id", "outcome"}
                    or not _identifier(item["test_id"]) or not isinstance(item["outcome"], str)
                    or item["outcome"] not in _OUTCOMES):
                raise ValueError("explicit bounded fixture outcome required")
        self._attempts.append({
            "sequence": len(self._attempts) + 1, "case_id": case_id, "phase": phase,
            "origin": "AUTHORED", "mode": "fixture", "runtime_verified": False,
            "provenance": "invented outcome descriptors; no test/provider dispatched",
            "outcomes": deepcopy(outcomes), "known_usd": 0, "unknown_liability": 0, "liability": 0,
        })

    def request_live(self, *args: object, **kwargs: object) -> None:
        raise PermissionError("live dispatch is disabled; fixture ledger cannot authorize spending")

    def to_dict(self) -> dict:
        return {
            "schema_version": 1, "origin": "AUTHORED", "mode": "fixture", "runtime_verified": False,
            "live_dispatch_enabled": False, "known_usd": 0, "unknown_liability": 0, "liability": 0,
            "accounting_scope": "authored fixture bookkeeping, not real billing or validated accounting",
            "attempt_count": len(self._attempts), "attempts": deepcopy(self._attempts),
        }
