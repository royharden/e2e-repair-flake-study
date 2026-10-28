# Study integration seams

`src/m19/contracts` is dependency-free Python source. The final orchestration
stack may wrap these dataclasses with Pydantic at the transport boundary. No
runner, model provider, reset implementation or network access is included.

| Contract | Producer → consumer | Invariant |
| --- | --- | --- |
| VariantRef | custody manifest projection → host schedule | opaque id only; no label/source |
| TaskSpec | frozen schedule → local ResetRecipe | uint64 seed; off or one N1/N2/N3 profile |
| ResetReceipt | future reset adapter → host supervisor | exact hashes and separate SUT/worker identities |
| TestAttempt / RunOutcome | trusted supervisor → future evaluator | explicit infra/unknown; zero, duplicate, missing, skipped or conflicting evidence cannot be green |
| PatchProposal | healer → future sandbox adapter | exact base hash; bounded diff or abstain |
| ObservationBundle | future sanitizer → generator/healer | bounded app-relative projection; type does not attest sanitization |
| DataOrigin | provenance → report | AUTHORED and RECORDED barred from measured panels |

`RunOutcome.green()` covers the retries=0 cohort only. It checks internal
consistency of supplied trusted evidence, not its authenticity, containment,
oracle agreement, reset equality or study admission. Artifact bytes must later
be re-hashed and pinned against the supervisor receipts. A caller-controlled
MEASURED flag alone is never proof of actual measurement. The report layer must
join independent provenance, admission and execution receipts.

DL4 owns these seams until INT integrates them. Later runner/sanitizer/report
owners must reconcile serializers, SHA256 construction and file-qualified test
identities before use. testlens ids are lowercase SHA256, compatible with the
opaque test identifier grammar here. Retry cohorts need a separate attempt-index
contract; never pool their outcomes with the headline reset cohort.

Study Gate A and Gate B remain pending. No scope signature, exposure record,
custodian appointment, containment receipt or result is synthesized by this
package. `m19 status` is a read-only status command, never admission or execution.
