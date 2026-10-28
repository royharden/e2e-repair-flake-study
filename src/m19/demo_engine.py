"""Pure deterministic AUTHORED examples; no suites, patches or providers execute."""
from math import isfinite
import re

from m19.demo_ledger import DemoLedger

_OUTCOMES = {"pass", "fail", "skipped", "infra_error", "unknown"}
_CATEGORIES = {"baseline_clean", "benign_repair", "false_repair", "silenced", "intermittent", "infra_error"}


def _id(value: object) -> bool:
    return isinstance(value, str) and re.fullmatch(r"[A-Za-z0-9_-]{1,128}", value) is not None


def classify_outcomes(inventory: list[str], outcomes: list[dict], *, origin: str = "AUTHORED") -> dict:
    """Classify one invented run; zero/missing/skipped/infra never become green."""
    if origin != "AUTHORED":
        raise ValueError("only authored fixture outcomes are supported")
    if (not isinstance(inventory, list) or len(inventory) > 32
            or any(not _id(item) for item in inventory)
            or not isinstance(outcomes, list) or len(outcomes) > 64):
        raise ValueError("bounded explicit fixture inventory and outcomes required")
    for item in outcomes:
        if (not isinstance(item, dict) or set(item) != {"test_id", "outcome"}
                or not _id(item["test_id"]) or not isinstance(item["outcome"], str)
                or item["outcome"] not in _OUTCOMES):
            raise ValueError("explicit supported fixture outcome required")
    completed = [item["test_id"] for item in outcomes]
    values = [item["outcome"] for item in outcomes]
    result = {"status": "invalid", "green": False, "expected": len(inventory),
              "completed": len(completed), "origin": "AUTHORED", "runtime_verified": False}
    if not inventory or len(inventory) != len(set(inventory)):
        return {**result, "reason": "zero or duplicate original inventory"}
    if len(completed) != len(set(completed)) or set(completed) != set(inventory):
        return {**result, "reason": "missing, duplicate or unexpected test inventory"}
    if "infra_error" in values:
        return {**result, "status": "infra_error", "reason": "infrastructure error, never flake or green"}
    if "unknown" in values:
        return {**result, "status": "unknown", "reason": "unknown outcome, never green"}
    if "skipped" in values:
        return {**result, "reason": "skipped inventory, never green"}
    return {**result, "status": "valid", "green": all(v == "pass" for v in values), "reason": None}


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
    if (not isinstance(value["role"], str) or not 1 <= len(value["role"].strip()) <= 64
            or not isinstance(value["name"], str) or not 1 <= len(value["name"].strip()) <= 256
            or not isinstance(value["ancestors"], list) or len(value["ancestors"]) > 8
            or any(not isinstance(x, str) or not 1 <= len(x.strip()) <= 64 for x in value["ancestors"])):
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
    flake_states = {"invalid": 0, "unknown": 0, "infra_error": 0}
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
        before = classify_outcomes(case["original_inventory"], case["before"])
        after = classify_outcomes(case["original_inventory"], case["after"])
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
        repetitions = case.get("repetitions", [])
        if not isinstance(repetitions, list) or len(repetitions) > 32:
            raise ValueError("bounded authored repetition vectors required")
        if repetitions:
            inspected = [classify_outcomes(case["original_inventory"], row) for row in repetitions]
            statuses = {row["status"] for row in inspected}
            if statuses != {"valid"}:
                key = ("infra_error" if "infra_error" in statuses else
                       "unknown" if "unknown" in statuses else "invalid")
                flake_states[key] += 1
                continue
            flake_n += 1
            by_test = {test: set() for test in case["original_inventory"]}
            for row in repetitions:
                for attempt in row:
                    by_test[attempt["test_id"]].add(attempt["outcome"])
            flake += int(any(values == {"pass", "fail"} for values in by_test.values()))
    return {
        "origin": "AUTHORED", "mode": "fixture", "runtime_verified": False, "not_measured": True,
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
        case["fixture_evaluation"] = {
            phase: classify_outcomes(case["original_inventory"], case[phase]) for phase in ("before", "after")}
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
