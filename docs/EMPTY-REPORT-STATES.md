# Empty report states

This is vocabulary for future report consumers, not a report execution or measured result.
No report generator is implemented by this packet slice. Unknown metrics must not become
numeric zero, empty successful panels or a claimed passing gate.

| Field or state | Empty representation | Meaning |
| --- | --- | --- |
| Run or arm | `status: "not_run"`, nonempty `reason`, `value: null` | No execution; absence of an effect is not a measured zero effect. |
| Metric | `display: "not yet measured"`, `value: null`, numerator/denominator/interval null | No observations or valid denominator. Never print 0%, zero failures or a confidence interval. |
| Gate A refusal | `SKIPPED_DATA_ADMISSION`, reasons | Administrative declarations absent/invalid; no fixture substitute. |
| Structurally complete declarations | `PENDING_ATTESTATION_VERIFICATION` | Authenticity and authority remain unverified; no GO. |
| Gate B unavailable/refused | `SKIPPED_QUALIFICATION`, reasons | No qualification; not a zero-detection result. |
| Fixture-only artifact | Explicit `AUTHORED` or `RECORDED`, separate from measured panels | Demonstration provenance, never a measured study result. |
| Dispatched cell with unresolved outcome | `unknown`, reason, retained cell identity | A dispatched ambiguity is retained; do not silently redispatch or convert to not_run. |
| Infrastructure fault after dispatch | `infra_error`, reason and available provenance | Separate from flake, regression detection or passing output. |
| Conditional A4 comparator | `status: "not_run"`, `reason: "integration not qualified"` | No account, driver or approval inferred from a subscription. |

Illustrative unexecuted report fragment:

```json
{
  "status": "not_run",
  "reason": "Gate A NO-GO; authentic receipts and GO transition incomplete",
  "metric": {
    "display": "not yet measured",
    "value": null,
    "numerator": null,
    "denominator": null,
    "interval": null
  },
  "runtime": "unverified",
  "execution_authorized": false
}
```

No counts, seeds, variants, labels, H0/P0 cases, oracle outputs or held-out data are authored
here. Planned floor commitments in the packet must never populate measured count cells.
Future reports require actual provenance and expected/completed inventory checks; syntax,
source acceptance, authored examples and declared boundaries cannot make a panel measured.
