# Assembled source snapshot inventory

Pinned assembled commit: 5452ed3a4664d5aaab445e9a2072a93029873e81. This records 26 explicitly included material files at that historical snapshot. SHA256 values cover exact Git blob bytes, before checkout line-ending conversion. This is content identification, not rights, authorship, independent evidence, data admission or an attestation of the new candidate tree.

## Coverage contract

Every tracked path at the pinned snapshot is either included below or explicitly excluded:
- admission.json: inventory-bearing packet, excluded to avoid recursive self-hash coverage.
- admission/source-inventory.template.json: inventory metadata/hashes, excluded for the same reason.
- docs/SOURCE-INVENTORY.md: inventory table/coverage contract, excluded for the same reason.

No private OUTER files, custody, transcripts, secrets, dependencies outside Git or later/untracked files are included or inspected. This finite contract is not a license to discover more files. The empty data-provenance.jsonl is included only as observed ledger source; it supplies no study dataset.

All included rows reference the pinned commit, not working-copy bytes. In particular docs/DATA.md is changed by this reconciliation: its row identifies the pre-change bytes at the pinned commit, not the new document. The three other changed inventory-bearing files are excluded. Thus no row purports to self-hash this new commit. Future material source changes need an explicitly pinned later inventory revision; do not describe this snapshot as covering every byte of a future integration.

## Included paths and exact Git-blob SHA256

| Stable id | Path at pinned commit | SHA256 |
|---|---|---|
| source-001 | .gitignore | 3a24c79c71989f2ac80eae70a95066f7086f33aa314f5bbb568c5c33d0bc4ca2 |
| source-002 | README.md | 3d43efe7db53cc6b7a2aa8c976243362ebfc65769f3981b8cadbef04565fa926 |
| source-003 | docs/CONTRACTS.md | 9fe25c12004baa9b787479310edcf909f9e49ff313e55d1e309ff30ed3c00789 |
| source-004 | docs/GRAMMAR.md | 481826391c65063cafc06d0e5c471bbd475e74e122d6e24e331133e0c8865e39 |
| source-005 | node/testlens/package.json | b97e5fdac19463ad157a26b4d1e9d8263fdda0a783417aac0db88cca54e5361d |
| source-006 | node/testlens/src/cli.mjs | c90d7bd5e631d397f4841405eeba5c8c5f0011b8cf81f5087f9e85fa39eb351e |
| source-007 | node/testlens/src/index.mjs | 26316888fefd751c912784de2edac807b2127b889bf321027542c931d7c917df |
| source-008 | pyproject.toml | 89943105e374dadf7cddb0cb61bb470db9f97aa696814ee02df3547ab65018f5 |
| source-009 | src/m19/__init__.py | b71535dbbba6f8a6b35e0171426ac076ce6603008674ab6d951fb6c8ed3769fc |
| source-010 | src/m19/cli.py | 2200b422f2061ae610e766bfa151e5d041f34c0642c5f504dbab21e01118ab7e |
| source-011 | src/m19/contracts/__init__.py | 9f61a58453f5cc0ce715890347099260f68b7e469c3ffde1bf37e8a8dbb3ffce |
| source-012 | admission/observer-boundaries.template.json | 9cc358c02138f70813c5d2e4c7b7d2c6bf6e7a535ee949b3d748c1184b82236f |
| source-013 | admission/roles.template.json | 2f444e6d544735d02fa125b4ecbdcaef4803c828037d3267bea2be9ec017aded |
| source-014 | admission/split-policy.template.json | b59741e38716859e8608e1d9520349ea769ad2499c914cc33994051d0a54af54 |
| source-015 | data-provenance.jsonl | e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855 |
| source-016 | docs/ACTIVATION.md | 74936ebb9c54e6a7e3a730e8beae24b81fe6699d922e5f09302fb9838eebdb6b |
| source-017 | docs/ADMISSION.md | c2fbe89fadc34f68aff88f78f00921c7a269f3b9957a168d9a6ae978c6c35452 |
| source-018 | docs/DATA.md | bbadd7d22009788ea7b7c1f4cc0b0df3d52d0ceb1ae33c1a679589df8c1b7ce9 |
| source-019 | docs/EMPTY-REPORT-STATES.md | 00a220645d80dd163772c1d37782d20049482fa68ce7d240092dc9fdb5d239e3 |
| source-020 | docs/EXPOSURE-PROTOCOL.md | d904eb9c3633b365c3124bb21c7ffcc1b1bed9377366b4dff10d51281d6688cd |
| source-021 | docs/GATE-CHECKLIST.md | 48e9e785bffc1820588a9f30a448b1891c8d585950a8b2fdc05ef20a282398d3 |
| source-022 | docs/STUDY-ROLES.md | 9334615d77b01357464243ffb15fad717da1332cfad442d59492255aa857939b |
| source-023 | schemas/admission.schema.json | 37b753ab5467286d481874725c8e079e3f16d7fabbd59788a4895de08b780b56 |
| source-024 | src/m19/admission/__init__.py | febe304c2f7cd3b71a6118b714112922cbfe62db17b6b25afd175e1dcf2ae18e |
| source-025 | docs/ATTESTATION-BOUNDARY.md | f86ebaa9334651763305048455fa91f3be66aa2d4b564b8ee043437e7a21258f |
| source-026 | src/m19/admission/attestation.py | cfe82aac93dac59ba3aa14b9a03343d473fd0c78e7b565a6d641670c553d11a7 |

admission/source-inventory.template.json supplies structured snapshot metadata and source_observations; its source_inventory array exactly matches admission.json with D1 id/reference/purpose/provenance fields. SHA256 appears both in each row's provenance and in structured observations. Metadata is not copied into the packet's top level. Preserve source-001..024 by their original paths even if file bytes change. New source-025 is docs/ATTESTATION-BOUNDARY.md and source-026 is src/m19/admission/attestation.py, assigned in lexicographic path order. IDs identify paths in this administrative inventory, not rights or study corpus identity.

Reproduce one content digest by capturing git show COMMIT:PATH as raw bytes and hashing with SHA256; decoded/re-encoded PowerShell text is not equivalent. Git hashes/provenance prove only observed content identity. Author, acquisition method and rights receipts remain unknown; no external source was acquired, no license commitment made, and no per-source permission asserted.

Each source has one matching rights_declarations row with permitted/basis/reference/declared_by null. Git possession, summary PENDING, plan license descriptions and hashes are not authentic per-source rights receipts. Originality remains all null. Actual licenses/notices for dependencies, browser/images and any future vendoring require separate verified evidence.

Role and boundary objects are copied from the integrated D1-shaped fragments, preserving all null identities/appointment/exposure/independence and boundary declaration/reference fields. Partial preparer metadata and design_policy stay outside admission evidence. Numeric split floors remain policy commitments, not measured corpus counts. scope_approval and ordering_disposition remain all-null receipts, never agent-authored approvals.

Gate A remains NO-GO: the deliberately incomplete packet requires refusal. Even structurally complete declarations only reach PENDING_ATTESTATION_VERIFICATION, not GO or execution authority. Prior P6 predates Gate A; no retrospective timing compliance is claimed. Authentic evidence verification and a qualified admission transition remain unfinished required work. No validator/runtime was executed for this snapshot; static consistency is not a runtime join or study admission.

## Attestation-source refresh boundary

This separately granted snapshot includes the installed attestation source and documentation, and updated admission/CLI/document bytes, at the pinned commit. It supersedes the prior d04e524 snapshot for these rows; it does not rewrite that historical report or extend to source changed after this pin. Inclusion/hashes do not authenticate attestations or install a trusted verifier. No real receipts, trust roots, credentials or custody content were read. The real verifier/GO transition remains absent; schema/CLI still refuse this null-authority packet. No product execution was used to derive that disposition, which is a source-only construction limit.
