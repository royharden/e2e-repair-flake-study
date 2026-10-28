"""Bounded local AUTHORED reports. Hash consistency is not study evidence."""

from collections import Counter
import hashlib
from html import escape
import json
import math
from pathlib import Path

from m19.demo_admission import reject_constant, unique_object


SCOPE = "m19-authored-fixture-report-v1"
BANNER = "AUTHORED fixtures · runtime unverified · not study results"
FILES = frozenset({"report.json", "report.html", "manifest.json"})
MAX_BYTES = 2 * 1024 * 1024
MAX_CASES = 100
CATEGORIES = frozenset({"baseline_clean", "benign_repair", "false_repair", "silenced",
                        "intermittent", "infra_error"})
OUTCOMES = frozenset({"pass", "fail", "skipped", "infra_error", "unknown"})
_FALSE_FLAGS = frozenset({
    "runtime_verified", "execution_authorized", "measured_results",
    "attestation_verified", "scientific_independence_claimed", "human_independent",
    "live_dispatch_enabled", "measured", "containment_verified",
})


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2,
                       allow_nan=False) + "\n").encode("utf-8")


def _check_value(value: object, depth: int = 0) -> None:
    if depth > 16:
        raise ValueError("report nesting exceeds 16")
    if isinstance(value, dict):
        for key, child in value.items():
            if not isinstance(key, str) or len(key) > 128:
                raise ValueError("invalid object key")
            if key in _FALSE_FLAGS and child is not False:
                raise ValueError(f"{key} must be false in authored reports")
            if key == "origin" and child != "AUTHORED":
                raise ValueError("unsupported origin")
            if key == "study_results" and child != "not yet measured":
                raise ValueError("study results are not yet measured")
            if key in {"measured_metrics", "study_metrics", "measured_panels"}:
                raise ValueError("measured panels are unsupported")
            _check_value(child, depth + 1)
    elif isinstance(value, list):
        if len(value) > 1000:
            raise ValueError("array too large")
        for child in value:
            _check_value(child, depth + 1)
    elif isinstance(value, str):
        if len(value) > 16384:
            raise ValueError("string too large")
    elif value is None or isinstance(value, bool):
        pass
    elif type(value) in (int, float):
        if abs(value) > 1e12 or not math.isfinite(value):
            raise ValueError("number outside finite report bounds")
    else:
        raise ValueError("report contains non-JSON data")


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or len(value) > 16384:
        raise ValueError(f"invalid {field}")
    return value


def _validate_metrics(metrics: object) -> None:
    if not isinstance(metrics, dict) or not metrics:
        raise ValueError("missing fixture-derived metrics")
    if metrics.get("origin") != "AUTHORED" or "fixture" not in _text(metrics.get("label"), "metrics label").lower():
        raise ValueError("metrics require AUTHORED origin and fixture-derived label")

    def visit(value: object, key: str = "") -> None:
        if isinstance(value, dict):
            if {"numerator", "denominator", "value"} & value.keys():
                if not {"numerator", "denominator", "value"} <= value.keys():
                    raise ValueError("incomplete fraction metric")
                numerator, denominator, fraction = value["numerator"], value["denominator"], value["value"]
                if (type(numerator) is not int or type(denominator) is not int
                        or not 0 <= numerator <= denominator):
                    raise ValueError("invalid fraction counters")
                if denominator == 0:
                    if fraction is not None:
                        raise ValueError("empty denominator requires null value")
                elif (type(fraction) not in (int, float) or not math.isfinite(fraction)
                      or not math.isclose(fraction, numerator / denominator, rel_tol=1e-12, abs_tol=1e-12)):
                    raise ValueError("fraction does not match counters")
                for child_key, child in value.items():
                    if child_key not in {"numerator", "denominator", "value"}:
                        visit(child, child_key)
            else:
                for child_key, child in value.items():
                    visit(child, child_key)
        elif isinstance(value, list):
            for child in value:
                visit(child, key)
        elif type(value) in (int, float):
            if type(value) is not int or value < 0:
                raise ValueError("metric counters must be nonnegative integers")
        elif not isinstance(value, str) and value is not None:
            raise ValueError("unsupported metric metadata")

    visit(metrics)


def _attempts(value: object, inventory: set[str]) -> set[str]:
    if not isinstance(value, list):
        raise ValueError("outcome run must be an array")
    seen: set[str] = set()
    for attempt in value:
        if not isinstance(attempt, dict) or not {"test_id", "outcome"} <= attempt.keys():
            raise ValueError("outcome requires test_id and outcome")
        identifier = _text(attempt["test_id"], "test_id")
        if identifier not in inventory or identifier in seen or attempt["outcome"] not in OUTCOMES:
            raise ValueError("unknown/duplicate test id or unsupported outcome")
        seen.add(identifier)
    return seen


def _validate_run(run: dict) -> None:
    if not isinstance(run, dict):
        raise ValueError("run must be an object")
    _check_value(run)
    if len(_json_bytes(run)) > MAX_BYTES:
        raise ValueError("run too large")
    if (type(run.get("schema_version")) is not int or run["schema_version"] != 1
            or run.get("origin") != "AUTHORED" or run.get("mode") != "fixture"
            or run.get("runtime_verified") is not False
            or run.get("run_id") != "m19-authored-demo"):
        raise ValueError("unsupported run scope/origin/mode/runtime state")
    ledger = run.get("ledger")
    if not isinstance(ledger, dict):
        raise ValueError("missing authored ledger")
    liabilities = [ledger[key] for key in ("unknown_liability", "liability") if key in ledger]
    if (type(ledger.get("known_usd")) not in (int, float) or ledger["known_usd"] != 0
            or not liabilities or any(type(value) not in (int, float) or value != 0 for value in liabilities)
            or ledger.get("live_dispatch_enabled") is not False):
        raise ValueError("only zero-cost no-live fixture ledger supported")
    _validate_metrics(run.get("metrics"))
    cases = run.get("cases")
    if not isinstance(cases, list) or not 1 <= len(cases) <= MAX_CASES:
        raise ValueError("expected 1..100 authored cases")
    seen: set[str] = set()
    for case in cases:
        if not isinstance(case, dict) or case.get("origin") != "AUTHORED":
            raise ValueError("case origin must be AUTHORED")
        identifier = _text(case.get("id"), "case id")
        if identifier in seen:
            raise ValueError("duplicate case id")
        seen.add(identifier)
        for field in ("label", "category", "requirement", "explanation"):
            _text(case.get(field), field)
        if case["category"] not in CATEGORIES:
            raise ValueError("unsupported authored category")
        for field in ("before", "after", "original_inventory", "patch_tags"):
            if not isinstance(case.get(field), list):
                raise ValueError(f"case {field} must be a list")
        inventory = case["original_inventory"]
        if not inventory or any(not isinstance(item, str) or not item.strip() for item in inventory):
            raise ValueError("inventory requires nonempty test-id strings")
        inventory_ids = set(inventory)
        if len(inventory_ids) != len(inventory):
            raise ValueError("duplicate inventory test id")
        if _attempts(case["before"], inventory_ids) != inventory_ids:
            raise ValueError("before run must account for every original test")
        after_ids = _attempts(case["after"], inventory_ids)
        # Deliberate deletion is an authored silencing example, never a green run.
        if after_ids != inventory_ids and case["category"] != "silenced":
            raise ValueError("missing after evidence outside explicit silencing case")
        if any(not isinstance(tag, str) or not tag.strip() for tag in case["patch_tags"]):
            raise ValueError("patch tags must be nonempty strings")
        if "repetitions" in case:
            if not isinstance(case["repetitions"], list) or not case["repetitions"]:
                raise ValueError("repetitions must contain outcome runs")
            for repetition in case["repetitions"]:
                if _attempts(repetition, inventory_ids) != inventory_ids:
                    raise ValueError("repetition missing original test evidence")
        if not {"expected_business", "observed_business"} <= case.keys():
            raise ValueError("missing authored business comparison")


def _report(run: dict) -> dict:
    _validate_run(run)
    return {
        "schema_version": 1, "scope": SCOPE, "origin": "AUTHORED", "mode": "fixture",
        "runtime_verified": False, "measured_results": False,
        "scientific_gate_a": "NO_GO", "execution_authorized": False,
        "banner": BANNER, "study_results": "not yet measured",
        "case_counts": dict(sorted(Counter(c["category"] for c in run["cases"]).items())),
        "cost": {"known_usd": 0, "basis": "authored no-live ledger; not a billing observation"},
        "run": run,
    }


def _display(value: object) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, sort_keys=True)
    return escape(text, quote=True)


def _html(report: dict) -> bytes:
    cards = []
    for case in report["run"]["cases"]:
        def field(name: str) -> str:
            return _display(case[name])
        cards.append(
            '<article><p class="eyebrow">AUTHORED · ' + field("category") + '</p>'
            '<h2>' + field("label") + '</h2><p class="id">' + field("id") + '</p>'
            '<p>' + field("requirement") + '</p><div class="strips"><section><h3>Before</h3><pre>'
            + field("before") + '</pre></section><section><h3>After</h3><pre>' + field("after")
            + '</pre></section></div><p><b>Repair tags:</b> ' + field("patch_tags")
            + '</p><p><b>Original inventory:</b> ' + field("original_inventory")
            + '</p><p><b>Business fixture:</b> expected ' + field("expected_business")
            + ' / observed ' + field("observed_business") + '</p><p>' + field("explanation")
            + '</p></article>'
        )
        if "repetitions" in case:
            cards.append('<article><h3>Authored repeated-run strips · ' + field("id")
                         + '</h3><pre>' + field("repetitions") + '</pre></article>')
    document = '''<!doctype html><html lang="en"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'unsafe-inline'; base-uri 'none'; form-action 'none'">
<title>M19 · Authored repair walkthrough</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#101a27;color:#e7edf4;font:16px/1.6 system-ui,sans-serif}
main{max-width:1100px;margin:auto;padding:40px 24px}h1{font-size:clamp(2rem,5vw,3.5rem);line-height:1.15;margin:12px 0}
.banner{padding:14px 20px;background:#473c19;border:1px solid #c7a44c;border-radius:10px}
.eyebrow{color:#7edac7;text-transform:uppercase;letter-spacing:.1em;font-size:12px}.id{color:#9aaabd}
article{background:#172536;border:1px solid #30475e;border-radius:16px;padding:24px;margin:24px 0}
.strips{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:16px}pre{white-space:pre-wrap;overflow-wrap:anywhere;background:#101a27;padding:16px;border-radius:10px}
h2,h3{line-height:1.3}footer{color:#9aaabd}b{color:#a9d7f0}</style><main>
<p class="eyebrow">M19 / Repair & flake study / Authored walkthrough</p>
<h1>When green can hide a broken journey</h1>'''
    document += '<p class="banner">' + escape(BANNER) + '</p>'
    document += '<p>Invented outcomes compare repair, false repair, silencing, flake and infrastructure explanations. No suite, browser or model was run.</p>'
    document += '<p><b>Authored case counts:</b> ' + _display(report["case_counts"]) + '</p>'
    document += '<p><b>Known fixture cost:</b> USD 0 · live dispatch disabled. Study results: not yet measured.</p>'
    document += '<article><h2>Fixture-derived metrics · not study results</h2><pre>' + _display(report["run"]["metrics"]) + '</pre></article>'
    document += ''.join(cards)
    # Preserve the supervisor/attempt account without inventing a sibling's field names.
    document += '<article><h2>Authored transformation account</h2><pre>' + _display(report["run"]) + '</pre></article>'
    document += '<footer>Scientific Gate A: NO_GO. No execution authority, observed containment, human independence or study result is asserted. Local digest checks establish consistency, not authenticity.</footer></main></html>\n'
    return document.encode("utf-8")


def _safe_path(path: Path) -> Path:
    absolute = Path(path).absolute()
    if absolute.drive.startswith("\\\\") or str(absolute).startswith("//"):
        raise ValueError("network/device paths refused")
    if ".." in absolute.parts:
        raise ValueError("parent traversal refused")
    for part in (absolute, *absolute.parents):
        if part.is_symlink() or (hasattr(part, "is_junction") and part.is_junction()):
            raise ValueError("symlink/junction paths refused")
    return absolute


def _digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def write_demo_report(run: dict, out: Path) -> dict:
    """Create a NEW directory only. Failure leaves partial evidence for inspection."""
    report = _report(run)
    artifacts = {"report.json": _json_bytes(report), "report.html": _html(report)}
    if any(len(raw) > MAX_BYTES for raw in artifacts.values()):
        raise ValueError("rendered artifact too large")
    manifest = {
        "schema_version": 1, "scope": SCOPE, "origin": "AUTHORED",
        "mode": "fixture", "runtime_verified": False,
        "artifacts": {name: {"sha256": _digest(raw), "bytes": len(raw)}
                      for name, raw in artifacts.items()},
    }
    artifacts["manifest.json"] = _json_bytes(manifest)
    target = _safe_path(out)
    if not target.parent.is_dir():
        raise ValueError("output parent must already exist")
    target.mkdir(exist_ok=False)
    for name, raw in artifacts.items():
        _safe_path(target / name)
        with (target / name).open("xb") as stream:
            stream.write(raw)
    return {"origin": "AUTHORED", "scope": SCOPE, "runtime_verified": False,
            "manifest_sha256": _digest(artifacts["manifest.json"]),
            "artifacts": sorted(artifacts), "study_results": "not yet measured"}


def _load(raw: bytes) -> dict:
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=unique_object,
                       parse_constant=reject_constant)
    if not isinstance(value, dict):
        raise ValueError("artifact must be an object")
    _check_value(value)
    return value


def verify_demo_report(out: Path, *, expected_manifest_sha256: str | None = None) -> dict:
    """Check closed artifacts and semantics; optionally bind to an external digest."""
    target = _safe_path(out)
    if not target.is_dir() or {p.name for p in target.iterdir()} != FILES:
        raise ValueError("missing or extra report artifacts")
    artifacts = {}
    for name in FILES:
        path = _safe_path(target / name)
        if not path.is_file() or path.stat().st_nlink != 1 or path.stat().st_size > MAX_BYTES:
            raise ValueError("nonregular/linked/oversize artifact")
        artifacts[name] = path.read_bytes()
        if len(artifacts[name]) > MAX_BYTES:
            raise ValueError("artifact grew beyond bound")
    manifest_digest = _digest(artifacts["manifest.json"])
    if expected_manifest_sha256 is not None and expected_manifest_sha256 != manifest_digest:
        raise ValueError("manifest differs from external expected digest")
    manifest = _load(artifacts["manifest.json"])
    expected_manifest = {
        "schema_version": 1, "scope": SCOPE, "origin": "AUTHORED", "mode": "fixture",
        "runtime_verified": False,
        "artifacts": {name: {"sha256": _digest(artifacts[name]), "bytes": len(artifacts[name])}
                      for name in ("report.json", "report.html")},
    }
    if _json_bytes(manifest) != _json_bytes(expected_manifest):
        raise ValueError("manifest scope/inventory/digest mismatch")
    report = _load(artifacts["report.json"])
    if _json_bytes(report) != _json_bytes(_report(report.get("run"))):
        raise ValueError("unsupported report panels or changed derived evidence")
    if artifacts["report.html"] != _html(report):
        raise ValueError("HTML differs from required escaped report")
    return {"status": "CONSISTENT_AUTHORED_ARTIFACTS", "origin": "AUTHORED",
            "scope": SCOPE, "runtime_verified": False, "execution_authorized": False,
            "study_results": "not yet measured", "authenticity_verified": False,
            "external_digest_matched": expected_manifest_sha256 is not None,
            "manifest_sha256": manifest_digest}
