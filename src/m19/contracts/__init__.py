"""Local host/worker seam. No truth labels, transport, or execution authority."""

from dataclasses import dataclass
from enum import StrEnum
import re
from typing import Protocol


def digest(value: str) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError("expected lowercase SHA256")


def identifier(value: str) -> None:
    if not isinstance(value, str) or re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value) is None:
        raise ValueError("expected bounded opaque identifier")


class Outcome(StrEnum):
    PASS = "pass"
    FAIL = "fail"
    SKIPPED = "skipped"
    INFRA_ERROR = "infra_error"
    UNKNOWN = "unknown"


class DataOrigin(StrEnum):
    AUTHORED = "AUTHORED"
    RECORDED = "RECORDED"
    MEASURED = "MEASURED"


@dataclass(frozen=True)
class VariantRef:
    opaque_id: str

    def __post_init__(self) -> None:
        identifier(self.opaque_id)


@dataclass(frozen=True)
class TaskSpec:
    id: str
    seed: int
    perturbations: tuple[str, ...]

    def __post_init__(self) -> None:
        identifier(self.id)
        if type(self.seed) is not int or not 0 <= self.seed < 2**64:
            raise ValueError("seed must be an unsigned 64-bit integer")
        if not isinstance(self.perturbations, tuple):
            raise ValueError("perturbations must be immutable")
        if any(p not in {"N1-moderate", "N1-stress", "N2-moderate", "N2-stress", "N3-moderate", "N3-stress"} for p in self.perturbations):
            raise ValueError("unknown noise profile")
        if len(self.perturbations) > 1:
            raise ValueError("MVP profiles contain at most one noise class/level")


@dataclass(frozen=True)
class ResetReceipt:
    variant_hash: str
    recipe_hash: str
    state_hash: str
    seed: int
    sut_container: str
    worker_container: str
    environment_hash: str
    observer_hash: str

    def __post_init__(self) -> None:
        for value in (self.variant_hash, self.recipe_hash, self.state_hash, self.environment_hash, self.observer_hash):
            digest(value)
        identifier(self.sut_container)
        identifier(self.worker_container)
        if self.sut_container == self.worker_container:
            raise ValueError("SUT and worker identities must differ")
        if type(self.seed) is not int or not 0 <= self.seed < 2**64:
            raise ValueError("seed must be an unsigned 64-bit integer")


@dataclass(frozen=True)
class TestAttempt:
    test_id: str
    outcome: Outcome

    def __post_init__(self) -> None:
        identifier(self.test_id)
        if not isinstance(self.outcome, Outcome):
            raise ValueError("outcome must use the explicit vocabulary")


@dataclass(frozen=True)
class RunOutcome:
    cell_id: str
    suite_hash: str
    expected_test_ids: tuple[str, ...]
    attempts: tuple[TestAttempt, ...]
    process_exit: int | None
    supervisor_status: str
    artifact_hashes: tuple[str, ...]
    reason: str | None = None

    def __post_init__(self) -> None:
        identifier(self.cell_id)
        digest(self.suite_hash)
        if self.supervisor_status not in {"valid", "invalid", "unknown"}:
            raise ValueError("unknown supervisor status")
        if self.supervisor_status != "valid" and not self.reason:
            raise ValueError("invalid/unknown outcomes require a reason")
        for values in (self.expected_test_ids, self.attempts, self.artifact_hashes):
            if not isinstance(values, tuple):
                raise ValueError("run inventories must be immutable tuples")
        for test_id in self.expected_test_ids:
            identifier(test_id)
        if len(set(self.expected_test_ids)) != len(self.expected_test_ids):
            raise ValueError("duplicate expected test ids")
        if any(not isinstance(a, TestAttempt) for a in self.attempts):
            raise ValueError("invalid attempt record")
        for value in self.artifact_hashes:
            digest(value)

    def green(self) -> bool:
        """Conflicting, missing, skipped and zero-test evidence can never be green.

        This seam covers the retries=0 cohort. Retry cohorts require separate logic.
        This is evidence consistency only, never scientific or release acceptance.
        """
        completed = tuple(a.test_id for a in self.attempts)
        return (
            self.supervisor_status == "valid"
            and self.reason is None
            and type(self.process_exit) is int
            and self.process_exit == 0
            and bool(self.expected_test_ids)
            and len(completed) == len(set(completed))
            and set(completed) == set(self.expected_test_ids)
            and all(a.outcome is Outcome.PASS for a in self.attempts)
            and bool(self.artifact_hashes)
        )


@dataclass(frozen=True)
class PatchProposal:
    base_suite_hash: str
    diff: str | None  # None means abstain, never an empty successful repair.

    def __post_init__(self) -> None:
        digest(self.base_suite_hash)
        if self.diff is not None and (not isinstance(self.diff, str) or not self.diff.strip() or len(self.diff.encode("utf-8")) > 65536):
            raise ValueError("patch must be nonempty and at most 64 KiB")


@dataclass(frozen=True)
class ObservationBundle:
    projection_hash: str
    accessibility_text: str
    url: str

    def __post_init__(self) -> None:
        digest(self.projection_hash)
        if not isinstance(self.accessibility_text, str) or len(self.accessibility_text.encode("utf-8")) > 262144:
            raise ValueError("accessibility projection exceeds 256 KiB")
        if not isinstance(self.url, str) or not self.url.startswith("/") or self.url.startswith("//") or "\\" in self.url:
            raise ValueError("observation URL must be app-relative")
        # The producer MUST sanitize and hash the projection. This type alone does
        # not attest sanitization; no sanitization receipt is fabricated here.


class ResetRecipe(Protocol):
    def reset(self, spec: TaskSpec) -> ResetReceipt: ...


class StateObserver(Protocol):
    def observe(self) -> ObservationBundle: ...


def require_measured(origin: DataOrigin) -> None:
    """Report seam: fixture origins cannot enter measured panels."""
    if origin is not DataOrigin.MEASURED:
        raise ValueError("AUTHORED/RECORDED fixtures are not study results")
