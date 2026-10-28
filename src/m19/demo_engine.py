"""Pure deterministic AUTHORED examples; no suites, patches or providers execute."""
from math import isfinite
import re

from m19.demo_ledger import DemoLedger
from m19.demo_pipeline import supervise_demo_run

_CATEGORIES = {"baseline_clean", "benign_repair", "false_repair", "silenced", "intermittent", "infra_error"}


def _id(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value) is not None


def classify_outcomes(inventory: list[str], outcomes: list[dict], *,
                      origin: str = "AUTHORED", evidence: dict | None = None) -> dict:
    """One pure authored run via D3's public supervisor; absent flags stay unknown."""
    if origin != "AUTHORED":
        raise ValueError("only authored fixture outcomes are supported")
    return supervise_demo_run(inventory, outcomes, evidence)


def _authored_flags(outcomes: list[dict]) -> dict:
    """Invent flags for the fixed toy producer only, never for caller-supplied cases."""
    values = [row["outcome"] for row in outcomes]
    flags = {"origin": "AUTHORED", "runtime_verified": False,
             "process_exit": None, "external_evidence": None, "status": "unknown"}
    if not outcomes or "skipped" in values:
        return {**flags, "status": "invalid", "external_evidence": False}
    if "infra_error" in values:
        return {**flags, "status": "infra_error", "external_evidence": True}
    if "unknown" in values:
        return flags
    return {**flags, "status": "valid", "external_evidence": True,
            "process_exit": 0 if all(v == "pass" for v in values) else 1}


def _case_supervisors(case: dict) -> tuple[dict, dict, list[dict]]:
    """Match D3 phase/run aggregation using only the declared public helper."""
    inventory = case["original_inventory"]
    before = classify_outcomes(inventory, case["before"], evidence=case.get("before_evidence"))
    after = classify_outcomes(inventory, case["after"], evidence=case.get("after_evidence"))
    summaries = []
    if "repetitions" in case:
        runs = case["repetitions"]
        if not isinstance(runs, list) or len(runs) > 32:
            raise ValueError("bounded authored repetition vectors required")
        flags = case.get("repetition_evidence", [None] * len(runs))
        if not isinstance(flags, list) or len(flags) != len(runs):
            raise ValueError("repetition evidence must align with run arrays")
        summaries = [classify_outcomes(inventory, row, evidence=flag)
                     for row, flag in zip(runs, flags)]
        overall = dict(after)
        if not summaries:
            overall.update(status="invalid", green=False, reasons=["zero_repetitions"])
        else:
            all_summaries = [after, *summaries]
            for state in ("invalid", "infra_error", "unknown"):
                if any(row["status"] == state for row in all_summaries):
                    overall["status"] = state
                    break
            overall["green"] = all(row["green"] for row in all_summaries)
            overall["reasons"] = list(dict.fromkeys(
                reason for row in all_summaries for reason in row["reasons"]))
        after = overall
    return before, after, summaries


def _edit_similarity(left: object, right: object) -> float:
    """One minus Levenshtein distance / max length for bounded text or token paths."""
    if not left and not right:
        return 1.0
    row = list(range(len(right) + 1))
    for i, a in enumerate(left, 1):
        next_row = [i]
        for j, b in enumerate(right, 1):
            next_row.append(min(next_row[-1] + 1, row[j] + 1, row[j - 1] + (a != b)))
        row = next_row
    return 1.0 - row[-1] / max(len(left), len(right))


def _snapshot(value: object) -> dict:
    if (not isinstance(value, dict)
            or set(value) != {"id", "role", "name", "ancestors", "origin"}
            or value["origin"] != "AUTHORED" or not _id(value["id"])):
        raise ValueError("authored locator snapshot required")
    if (not isinstance(value["role"], str) or not 1 <= len(value["role"]) <= 64 or not value["role"].strip()
            or not isinstance(value["name"], str) or not 1 <= len(value["name"]) <= 256 or not value["name"].strip()
            or not isinstance(value["ancestors"], list) or len(value["ancestors"]) > 8
            or any(not isinstance(x, str) or not 1 <= len(x) <= 64 or not x.strip() for x in value["ancestors"])):
        raise ValueError("bounded role/name/ancestor path required")
    return {"id": value["id"], "role": value["role"].strip().casefold(),
            "name": " ".join(value["name"].casefold().split()),
            "ancestors": [x.strip().casefold() for x in value["ancestors"]]}


def score_locator_candidates(original: dict, candidates: list[dict], *,
                             threshold: float = 0.8, margin: float = 0.1) -> dict:
    """Toy R1 locator choice only; assertions and executable patches are not inputs."""
    for number in (threshold, margin):
        if type(number) not in (int, float) or not isfinite(number) or not 0 < number <= 1:
            raise ValueError("finite threshold/margin in (0,1] required")
    anchor = _snapshot(original)
    if not isinstance(candidates, list) or len(candidates) > 16:
        raise ValueError("at most sixteen authored candidates required")
    parsed = [_snapshot(candidate) for candidate in candidates]
    if len({candidate["id"] for candidate in parsed}) != len(parsed):
        raise ValueError("duplicate candidate identities")
    ranked = []
    for candidate in parsed:
        score = (0.5 * (anchor["role"] == candidate["role"])
                 + 0.3 * _edit_similarity(anchor["name"], candidate["name"])
                 + 0.2 * _edit_similarity(anchor["ancestors"], candidate["ancestors"]))
        ranked.append({"candidate_id": candidate["id"], "score": score})
    ranked.sort(key=lambda item: (-item["score"], item["candidate_id"]))
    decision = {"verdict": "abstain", "candidate_id": None, "origin": "AUTHORED",
                "threshold": threshold, "required_margin": margin, "assertions_preserved": True,
                "patch_scope": "locator_only", "ranked": ranked, "runtime_verified": False}
    if not ranked:
        return {**decision, "reason": "no candidates"}
    lead = ranked[0]["score"]
    gap = lead - (ranked[1]["score"] if len(ranked) > 1 else 0.0)
    if lead < threshold:
        return {**decision, "reason": "top score below threshold", "score_gap": gap}
    if gap <= 1e-12 or gap < margin:
        return {**decision, "reason": "tie or insufficient sibling margin", "score_gap": gap}
    return {**decision, "verdict": "repair", "candidate_id": ranked[0]["candidate_id"],
            "reason": "unique score above threshold and margin", "score_gap": gap}


def _fraction(numerator: int, denominator: int) -> dict:
    return {"numerator": numerator, "denominator": denominator,
            "value": numerator / denominator if denominator else None}


def compute_demo_metrics(cases: list[dict]) -> dict:
    """Derive fixture fractions and attrition, never statistical study results."""
    if not isinstance(cases, list) or not 1 <= len(cases) <= 16:
        raise ValueError("bounded authored cases required")
    seen = set()
    after_states = {"valid": 0, "invalid": 0, "unknown": 0, "infra_error": 0}
    green = benign = benign_n = false = false_n = flake = flake_n = 0
    flake_states = {"invalid": 0, "unknown": 0, "infra_error": 0, "insufficient_repetitions": 0}
    for case in cases:
        if (not isinstance(case, dict) or case.get("origin") != "AUTHORED"
                or case.get("mode", "fixture") != "fixture"
                or case.get("runtime_verified", False) is not False
                or not _id(case.get("id")) or case["id"] in seen
                or not isinstance(case.get("category"), str) or case["category"] not in _CATEGORIES):
            raise ValueError("unique authored fixture cases only, no measured inputs")
        seen.add(case["id"])
        required = {"original_inventory", "before", "after", "expected_business", "observed_business"}
        if not required <= case.keys():
            raise ValueError("explicit inventories, outcomes and business fixtures required")
        before, after, repetition_summaries = _case_supervisors(case)
        after_states[after["status"]] += 1
        green += int(after["green"])
        eligible = before["status"] == after["status"] == "valid" and not before["green"]
        business_match = case["expected_business"] == case["observed_business"]
        if case["category"] == "benign_repair" and eligible:
            benign_n += 1
            benign += int(after["green"] and business_match)
        if case["category"] == "false_repair" and eligible:
            false_n += 1
            false += int(after["green"] and not business_match)
        if "repetitions" in case:
            repetitions = case["repetitions"]
            if len(repetition_summaries) < 2:
                flake_states["insufficient_repetitions"] += 1
                continue
            if after["status"] != "valid":
                flake_states[after["status"]] += 1
                continue
            flake_n += 1
            by_test = {test: set() for test in case["original_inventory"]}
            for row in repetitions:
                for attempt in row:
                    by_test[attempt["test_id"]].add(attempt["outcome"])
            flake += int(any(values == {"pass", "fail"} for values in by_test.values()))
    return {
        "origin": "AUTHORED", "label": "fixture-derived; not scientific results",
        "mode": "fixture", "runtime_verified": False, "not_measured": True,
        "metric_scope": "invented vectors only; invalid/unknown/infra counts shown, no study estimate",
        "total_cases": len(cases), "after_status_counts": after_states,
        "green_after_fraction": _fraction(green, after_states["valid"]),
        "benign_repair_fraction": _fraction(benign, benign_n),
        "false_repair_fraction": _fraction(false, false_n),
        "flake_block_fraction": _fraction(flake, flake_n), "excluded_flake_blocks": flake_states,
    }


def _outcome(test_id: str, outcome: str) -> list[dict]:
    return [{"test_id": test_id, "outcome": outcome}]


def _case(case_id: str, label: str, category: str, test: str, before: str, after: str,
          expected: dict, observed: object, tags: list[str], explanation: str) -> dict:
    return {"id": case_id, "label": label, "category": category, "origin": "AUTHORED",
            "mode": "fixture", "runtime_verified": False,
            "requirement": "AUTHORED Harbour Bookings toy: preserve confirmation, total and original test inventory",
            "original_inventory": [test], "before": _outcome(test, before),
            "after": _outcome(test, after), "patch_tags": tags,
            "expected_business": expected, "observed_business": observed, "explanation": explanation}


def build_demo_scenario() -> dict:
    """Construct five authored descriptors and derived values without executing any target."""
    original = {"id": "confirm-old", "role": "button", "name": "Confirm booking",
                "ancestors": ["main", "form"], "origin": "AUTHORED"}
    target = {**original, "id": "confirm-new"}
    sibling = {**original, "id": "cancel", "name": "Cancel", "ancestors": ["main", "dialog"]}
    locator = score_locator_candidates(original, [target, sibling])
    tie = score_locator_candidates(original, [{**target, "id": "sibling-a"}, {**target, "id": "sibling-b"}])
    benign = _case(
        "demo-benign", "Benign locator repair", "benign_repair", "confirmation-visible", "fail",
        "pass" if locator["verdict"] == "repair" else "fail", {"total_cents": 9000}, {"total_cents": 9000},
        ["locator_only"], "Invented renamed locator; R1 selects one candidate, assertion values stay unchanged.")
    benign.update({"r1_decision": locator, "r1_sibling_tie_example": tie,
                   "assertion_expected_before": 9000, "assertion_expected_after": 9000})
    wrong = _case(
        "demo-wrong-total", "Wrong-total assertion rewrite", "false_repair", "discount-total", "fail", "pass",
        {"total_cents": 9000}, {"total_cents": 10000}, ["expected_value_rewritten"],
        "AUTHORED counterexample: rewriting expected9000 to wrong10000 makes fixture suite green; business stays wrong. R1 never rewrites assertions.")
    wrong.update({"assertion_expected_before": 9000, "assertion_expected_after": 10000})
    silenced = _case(
        "demo-silenced", "Silenced and zero-inventory rejection", "silenced", "booking-confirmation", "fail", "skipped",
        {"confirmation": True}, {"confirmation": False}, ["silenced", "assertion_removed"],
        "Dropped original test produces zero completions, never green. An empty original inventory is also invalid.")
    silenced.update({"after": [], "zero_inventory_example": classify_outcomes([], [])})
    intermittent = _case(
        "demo-intermittent", "Intermittent seeded fixture vector", "intermittent", "booking-list", "pass", "pass",
        {"ready": True}, {"ready": True}, [],
        "Twenty invented descriptors from seed19 arithmetic, not resets/browser runs; mixed valid outcomes form one demo flake block.")
    seed = 19
    intermittent.update({"fixture_seed": seed,
                         "repetitions": [_outcome("booking-list", "fail" if (seed + i * 3) % 7 < 2 else "pass")
                                         for i in range(20)]})
    infra = _case(
        "demo-infra", "Infrastructure error is not flake", "infra_error", "availability", "infra_error", "infra_error",
        {"ready": True}, None, [],
        "Invented worker-unavailable descriptors stay infra_error, excluded from valid/flake denominators, never green.")
    infra["repetitions"] = [_outcome("availability", "infra_error") for _ in range(2)]
    cases = [benign, wrong, silenced, intermittent, infra]
    ledger = DemoLedger()
    for case in cases:
        case["before_evidence"] = _authored_flags(case["before"])
        case["after_evidence"] = _authored_flags(case["after"])
        if "repetitions" in case:
            case["repetition_evidence"] = [_authored_flags(row) for row in case["repetitions"]]
        before, after, repetitions = _case_supervisors(case)
        case["fixture_evaluation"] = {"before": before, "after": after,
                                      "repetition_supervisors": repetitions}
        for phase in ("before", "after"):
            ledger.record_attempt(case["id"], phase, case[phase])
        for row in case.get("repetitions", []):
            ledger.record_attempt(case["id"], "repetition", row)
    return {
        "schema_version": 1, "origin": "AUTHORED", "mode": "fixture", "run_id": "m19-authored-demo",
        "runtime_verified": False, "not_measured": True,
        "disclaimer": "Invented local fixture descriptors, not observed runs, H0/P0, held-out data, an oracle or scientific results.",
        "cases": cases, "metrics": compute_demo_metrics(cases), "ledger": ledger.to_dict(),
    }
