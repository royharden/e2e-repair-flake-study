# Harbour source handoff

Original authored demo source, schema_version 1, origin AUTHORED, mode fixture,
runtime_verified false. No executed app, browser, database, reset, suite, fixture-report
or independent oracle result is claimed. Scientific Gates A/B remain held. This optional
standalone SUT is separate from the D2 → D3 → D4 authored report pipeline.

## Source map and interfaces

- `sut/store.py`: parameterized SQLite business state, `Store.create`, `cancel`,
  `slots`, `bookings`, `booking`; integer-cent `quote` and one authoritative seed function.
  Mutations use `BEGIN IMMEDIATE`, capacity checks and effects share the transaction.
  Cancellation retains records. There is no mutable authoritative module-level business state.
- `sut/server.py`: loopback-only HTTP server, fixed asset routes, escaped server HTML,
  POST-only bounded forms, ephemeral per-instance form token, explicit foreign-Origin
  refusal and conservative CSP. This is a local toy with shared booking visibility,
  no user accounts, ownership checks, real reservations, payments or authentication.
  Anyone with local app access can cancel a displayed demo booking. Do not use real data.
- `sut/static/app.js` enhances form busy state; server validates all business fields.
  CSS and UI are original local assets, without downloaded fonts/images/dependencies.
- `sut/hooks.js` checks duplicate hooks; server emits unique `data-oracle-id` attributes
  in business markup on all relevant routes. These are always-present instrumentation,
  not a scientific oracle. D3 owns sanitization of every model-facing projection;
  raw app/HTML/hooks/control/state data must not go directly to a model.
- Exec-only `sut/control/reset.py`, `state_hash.py`, `observe.py`. No HTTP control
  route, database download or static path traversal handler exists. The asset map is fixed.

State lives only in an explicitly supplied local directory as `harbour.sqlite`.
No `.env`, keys, account, remote service, Dockerfile, Compose, deployment or CI scaffolding.
The form token is generated only in a future running server instance and is not persisted
as a credential. HTTP mutations are toy-scoped, not an assertion of security qualification.

## Out-of-band seam

Effect journal is an SQLite `events` table, not a JSONL file: each create/first cancel
adds exactly one ordered event atomically with the business change. This explicit
provisional deviation from the scientific plan's JSONL journal avoids split-commit
inconsistency in the minimal demo. INT must reconcile any future journal consumer;
no scientific observer interface compatibility or containment is claimed.

`observation_start` returns `{schema_version, origin, mode, runtime_verified, epoch, cursor}`.
`observe(epoch, since)` returns those metadata fields, latest cursor and ordered
`events[{seq, kind, booking_id}]` after the supplied cursor. Epoch mismatch, negative
or future cursor is refused. A reset rotates epoch and starts a fresh effect journal.
Observers see no independent labels/expected values, and this source never enters custody.

`state_hash` returns metadata, `state_sha256` and scope. SHA256 covers sorted-key compact
JSON of slots ordered by ID and bookings ordered by position. Epoch/effects are excluded
from the logical business hash; reset empties bookings and restores exactly the fixed
seed. Read paths use SQLite read-only URI mode and do not initialize a missing database.
This is a logical-state identity, not proof of container reset, recipe identity or isolation.

`reset` returns metadata, a reset label and new epoch. **Future destructive action held:**
the exec-only reset source clears authored booking/event/slot rows and the booking sequence
inside a transaction, then restores slots. It deletes no filesystem files, and it was
not executed here. The owner must explicitly authorize any later reset. No deletion
has been performed during construction. Reset source has an explicit confirmation flag.

The standalone server binds 127.0.0.1 only. It is not a container worker/SUT topology.
Later topology changes and actual P4 containment need their own grant and validation.
No model/provider/runner or network call is made by this SUT code other than the explicitly
started future HTTP server. No request path fetches external URLs or opens arbitrary files.

## Later authorized commands — not executed

First obtain explicit runtime authorization and an `agent-ports` reservation; this
document reserves no port. From the inner repo root, after choosing a dedicated
invented-data directory and the actual authorized port:

```text
python -m sut.server --port <RESERVED_PORT> --state-dir <DEMO_STATE_DIRECTORY>
python -m sut.control.state_hash --state-dir <DEMO_STATE_DIRECTORY>
python -m sut.control.observe --state-dir <DEMO_STATE_DIRECTORY>
python -m sut.control.observe --state-dir <DEMO_STATE_DIRECTORY> --epoch <OBSERVED_EPOCH> --since <OBSERVED_CURSOR>
python -m sut.control.reset --state-dir <DEMO_STATE_DIRECTORY> --confirm-authored-demo-reset
```

Angle-bracket items are configuration/cursor names, not credentials or observed receipts.
No process, port, database or environment was created by these examples. The CLI refuses
ports outside 20000–29999 but does not itself establish reservation/authorization.
Startup initializes only the explicitly supplied demo store. Do not point it at existing
personal/project databases; no real data belongs in this app.

## Static inspection and deferred checks

Static syntax/dataflow review cannot prove SQLite concurrency, HTTP parsing, hook uniqueness,
CSRF protection, escaping, business arithmetic or reset/observer behavior. Later authorized
checks must exercise all 24 clauses and 12 journeys in `SUT.md`, invalid bodies/UTF-8,
token/origin/size/duplicate fields, capacity races and rollback, idempotent cancel,
stable logical reset hash, epoch/cursor consistency, asset route boundaries and model
projection removal. The demo row cap is 1000 total bookings between resets; disclose the
cap and never silently hide a measured panel. No actual tests/results are authored here.

No dependency installation required by this stdlib source. No runtime security, authenticated
admission, independent study review, rights transfer, scientific qualification or paid run
is completed. Spend USD 0, no keys, push, publication or deletion performed.
