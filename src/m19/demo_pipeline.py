"""Pure AUTHORED fixture transformations; never an execution/admission API."""

import hashlib
import json
import math
import re

from m19.sanitize import project_fixture_text


_OUTCOMES = {"pass", "fail", "skipped", "infra_error", "unknown"}
_CATEGORIES = {"baseline_clean", "benign_repair", "false_repair", "silenced", "intermittent", "infra_error"}


def _canonical(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False).encode("utf-8")


def _bounded(value: object, depth: int = 0, budget: list[int] | None = None) -> None:
    if budget is None:
        budget = [0, 0]
    budget[0] += 1
    if budget[0] > 16384:
        raise ValueError("fixture node budget exceeded")
    if depth > 12:
        raise ValueError("fixture nesting exceeds limit")
    if value is None or type(value) is bool:
        return
    if type(value) in (int, float):
        if abs(value) > 10**12 or not math.isfinite(value):
            raise ValueError("nonfinite or unbounded number")
        return
    if type(value) is str:
        size = len(value.encode("utf-8"))
        budget[1] += size
        if size > 65536 or budget[1] > 1048576:
            raise ValueError("oversized fixture string")
        return
    if type(value) is list:
        if len(value) > 2048:
            raise ValueError("oversized fixture array")
        for item in value:
            _bounded(item, depth + 1, budget)
        return
    if type(value) is dict:
        if len(value) > 128 or any(type(k) is not str or len(k) > 128 for k in value):
            raise ValueError("invalid fixture object keys")
        budget[1] += sum(len(k.encode("utf-8")) for k in value)
        if budget[1] > 1048576:
            raise ValueError("fixture text budget exceeded")
        for item in value.values():
            _bounded(item, depth + 1, budget)
        return
    raise ValueError("fixture must contain only bounded JSON data")


def _id(value: object) -> str:
    if type(value) is not str or re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value) is None:
        raise ValueError("expected bounded opaque identifier")
    return value


def _attempts(value: object) -> list[dict]:
    if type(value) is not list:
        raise ValueError("before/after attempts must be arrays")
    result = []
    for attempt in value:
        if type(attempt) is not dict:
            raise ValueError("attempt must be an object")
        test_id = _id(attempt.get("test_id"))
        outcome = attempt.get("outcome")
        if type(outcome) is not str or outcome not in _OUTCOMES:
            raise ValueError("unsupported authored outcome")
        if attempt.get("origin", "AUTHORED") != "AUTHORED":
            raise ValueError("non-authored attempt")
        result.append({"test_id": test_id, "outcome": outcome})
    return result


def _metrics(value: object) -> None:
    """Validate declared authored fractions without inventing study statistics."""
    if type(value) is dict:
        if "origin" in value and value["origin"] != "AUTHORED":
            raise ValueError("metrics must remain AUTHORED")
        if {"numerator", "denominator", "value"}.intersection(value):
            numerator, denominator, fraction = (value.get(k) for k in ("numerator", "denominator", "value"))
            if type(numerator) is not int or type(denominator) is not int or not 0 <= numerator <= denominator:
                raise ValueError("invalid fraction counts")
            if denominator == 0:
                if fraction is not None:
                    raise ValueError("zero-denominator fraction must be null")
            elif type(fraction) not in (int, float) or not math.isclose(fraction, numerator / denominator, rel_tol=1e-9, abs_tol=1e-12):
                raise ValueError("fraction value disagrees with counts")
        for item in value.values():
            _metrics(item)
    elif type(value) is list:
        for item in value:
            _metrics(item)


def _supervise(inventory: list[str], attempts: list[dict], evidence: object) -> dict:
    """Classify source consistency only, never actual OS/process evidence."""
    ids = [a["test_id"] for a in attempts]
    outcomes = [a["outcome"] for a in attempts]
    problems = []
    if not inventory or not attempts:
        problems.append("zero_inventory_or_attempts")
    if len(ids) != len(set(ids)):
        problems.append("duplicate_or_conflicting_attempts")
    if set(ids) != set(inventory):
        problems.append("missing_deleted_or_unexpected_tests")
    if "skipped" in outcomes:
        problems.append("skipped_tests")
    if type(evidence) is not dict:
        evidence = {}
    exit_code = evidence.get("process_exit")
    external = evidence.get("external_evidence")
    status = evidence.get("status")
    if exit_code is not None and (type(exit_code) is not int or not -255 <= exit_code <= 255):
        raise ValueError("invalid authored process_exit")
    if external is not None and type(external) is not bool:
        raise ValueError("invalid authored external_evidence flag")
    if status not in (None, "valid", "invalid", "unknown", "infra_error"):
        raise ValueError("invalid authored supervisor status")
    if problems or status == "invalid" or external is False:
        state = "invalid"
    elif "infra_error" in outcomes or status == "infra_error":
        state = "infra_error"
    elif "unknown" in outcomes or status != "valid" or external is not True or exit_code is None:
        state = "unknown"
    elif exit_code != 0 and all(o == "pass" for o in outcomes):
        state = "invalid"
        problems.append("process_outcome_conflict")
    else:
        state = "valid"
    return {
        "status": state,
        "green": state == "valid" and exit_code == 0 and bool(outcomes) and all(o == "pass" for o in outcomes),
        "reasons": problems,
        "origin": "AUTHORED",
        "runtime_verified": False,
        "process_exit": exit_code,
        "external_evidence": external,
    }


def prepare_demo_run(scenario: dict) -> dict:
    """Validate and project invented fixtures without importing/executing a SUT.

    Model-facing data is a separate strict allowlist. All labels, supervisor
    decisions and inventories remain evaluator-side. No input path is opened.
    """
    if type(scenario) is not dict:
        raise ValueError("scenario must be an object")
    _bounded(scenario)
    source_bytes = _canonical(scenario)
    if len(source_bytes) > 1048576:
        raise ValueError("scenario exceeds 1 MiB")
    if type(scenario.get("schema_version")) is not int or scenario["schema_version"] != 1:
        raise ValueError("unsupported demo schema")
    if scenario.get("origin") != "AUTHORED" or scenario.get("mode") != "fixture" or scenario.get("runtime_verified") is not False:
        raise ValueError("only unverified AUTHORED fixture scenarios are allowed")
    run_id = _id(scenario.get("run_id"))
    ledger = scenario.get("ledger")
    if type(ledger) is not dict or type(ledger.get("known_usd")) not in (int, float) or ledger["known_usd"] != 0 or ledger.get("live_dispatch_enabled") is not False or type(ledger.get("unknown_liability")) not in (int, float) or ledger["unknown_liability"] != 0:
        raise ValueError("fixture ledger must explicitly declare zero cost/liability and no live dispatch")
    if type(scenario.get("metrics")) is not dict:
        raise ValueError("authored metrics object required")
    _metrics(scenario["metrics"])
    cases = scenario.get("cases")
    if type(cases) is not list or not 1 <= len(cases) <= 128:
        raise ValueError("expected 1..128 authored cases")
    prepared, projected, seen = [], [], set()
    for index, case in enumerate(cases):
        if type(case) is not dict or case.get("origin") != "AUTHORED":
            raise ValueError("every case must be explicitly AUTHORED")
        case_id = _id(case.get("id"))
        if case_id in seen:
            raise ValueError("duplicate case identifier")
        seen.add(case_id)
        if type(case.get("category")) is not str or case["category"] not in _CATEGORIES:
            raise ValueError("unknown authored category")
        for field in ("label", "requirement", "explanation"):
            if type(case.get(field)) is not str or not case[field].strip():
                raise ValueError(f"case requires nonempty {field}")
        for field in ("expected_business", "observed_business", "patch_tags"):
            if field not in case:
                raise ValueError(f"case requires {field}")
        if type(case["patch_tags"]) is not list or any(type(t) is not str for t in case["patch_tags"]):
            raise ValueError("patch_tags must be strings")
        inventory = case.get("original_inventory")
        if type(inventory) is not list:
            raise ValueError("original inventory required")
        inventory = [_id(i) for i in inventory]
        if len(set(inventory)) != len(inventory):
            raise ValueError("duplicate original inventory")
        before, after = _attempts(case.get("before")), _attempts(case.get("after"))
        # Generate projection identifiers instead of exposing fixture/variant IDs.
        view = {"id": f"task-{index + 1:03d}", "requirement": project_fixture_text(case["requirement"])}
        fixture_text = case.get("fixture_text", "")
        view["text"] = project_fixture_text(fixture_text)
        projected.append(view)
        record = json.loads(_canonical(case))
        record["before_supervisor"] = _supervise(inventory, before, case.get("before_evidence"))
        record["supervisor"] = _supervise(inventory, after, case.get("after_evidence"))
        if "repetitions" in case:
            runs = case["repetitions"]
            if type(runs) is not list:
                raise ValueError("repetitions must be an array of run arrays")
            evidence = case.get("repetition_evidence", [None] * len(runs))
            if type(evidence) is not list or len(evidence) != len(runs):
                raise ValueError("repetition evidence must align with runs")
            summaries = [_supervise(inventory, _attempts(run), flags) for run, flags in zip(runs, evidence)]
            record["repetition_supervisors"] = summaries
            # Repeated IDs across distinct runs are valid. Each run is checked
            # against the original inventory independently; nothing is flattened.
            all_summaries = [record["supervisor"], *summaries]
            overall = dict(record["supervisor"])
            if not summaries:
                overall.update(status="invalid", green=False, reasons=["zero_repetitions"])
            else:
                for state in ("invalid", "infra_error", "unknown"):
                    if any(s["status"] == state for s in all_summaries):
                        overall["status"] = state
                        break
                overall["green"] = all(s["green"] for s in all_summaries)
                overall["reasons"] = list(dict.fromkeys(reason for s in all_summaries for reason in s["reasons"]))
            record["supervisor"] = overall
        record["projection_id"] = view["id"]
        record["projection_hash"] = hashlib.sha256(_canonical(view)).hexdigest()
        prepared.append(record)
    projection = {"schema_version": 1, "origin": "AUTHORED", "mode": "fixture", "runtime_verified": False, "cases": projected}
    return {
        "schema_version": 1, "origin": "AUTHORED", "mode": "fixture", "run_id": run_id,
        "runtime_verified": False, "execution_authorized": False,
        "scientific_gate_a": "NO_GO", "study_result": False,
        "disclaimer": "Invented AUTHORED demo fixtures; not measured observations or containment evidence.",
        "source_hash": hashlib.sha256(source_bytes).hexdigest(),
        "cases": prepared, "metrics": json.loads(_canonical(scenario["metrics"])),
        "metrics_origin": "AUTHORED", "ledger": json.loads(_canonical(ledger)),
        "model_projection": projection,
        "projection_hash": hashlib.sha256(_canonical(projection)).hexdigest(),
    }
