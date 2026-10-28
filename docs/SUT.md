# Harbour Bookings — authored demo contract v1

Origin AUTHORED; mode fixture; schema_version 1; runtime_verified false.
Delegated demo construction only, not a study result or personally signed owner approval.
All slot labels and booking labels are invented. Enter only nonpersonal demo labels.
No payment, account, real reservation, independent H0/P0 or held-out corpus exists.

## Business clauses

| ID | Required behavior and worked example |
| --- | --- |
| HB01 | The seed exposes exactly `harbour-a` (Harbour A, capacity 8, unit 2500 cents) and `harbour-b` (Harbour B, capacity 12, unit 1800 cents). |
| HB02 | Slot list shows label, unit price, capacity and current remaining seats; fresh Harbour A shows 8 remaining. |
| HB03 | The booking page accepts only an existing slot ID; absent/unknown slot is refused. |
| HB04 | Demo label is stripped and must be 1–40 ASCII letters/digits/spaces/hyphens; ` Demo-7 ` becomes `Demo-7`. Whitespace-only labels are refused. |
| HB05 | Party is a canonical decimal integer 1–8; `2` valid, `02`, `2.0`, `+2`, missing, `0` and `9` invalid. |
| HB06 | Capacity is shared by active bookings; Harbour A with parties 3 and 4 has 1 remaining. |
| HB07 | A transaction refuses a booking larger than remaining seats; a party of 2 cannot take Harbour A's last seat. No partial booking or event is committed. |
| HB08 | Subtotal is unit cents × party; Harbour A × 3 = 7500 cents. No floating-point money. |
| HB09 | Exactly one discount: parties of 4–8 receive 10% of subtotal, rounded down in cents; Harbour B × 4 subtotal 7200, discount 720, total 6480. Parties 1–3 discount 0. |
| HB10 | Total = subtotal − discount; Harbour A × 4 = 10000 − 1000 = 9000 cents. |
| HB11 | Successful creation returns an opaque UUID booking ID, stores the chosen slot/normalized label/party/cents, and redirects to its confirmation. |
| HB12 | Confirmation displays that booking's stored amounts and current status, never a recomputed client quote; unknown IDs are refused. |
| HB13 | Booking list contains active and cancelled bookings in creation order, with slot label, demo label, party, amounts and status. |
| HB14 | Cancel changes only active → cancelled; no booking row is erased and money fields stay fixed. |
| HB15 | Cancellation restores exactly that booking's party seats; cancelling a Harbour A party of 3 changes remaining 5 → 8 if no other booking exists. |
| HB16 | Repeat cancellation is idempotent: no additional capacity release and no second cancellation event. Unknown ID refused. |
| HB17 | Every successful create and first cancel commits one effect event atomically with its booking change. Validation/capacity failure commits neither. |
| HB18 | User-visible strings are HTML-escaped. Inputs outside the label grammar, including markup, are refused before persistence. |
| HB19 | Mutations use POST form bodies only, bounded at 2048 bytes, required unique fields and URL-encoded content. GET cannot create/cancel/reset. |
| HB20 | Form POST requires the server instance's form token and rejects an explicitly foreign Origin; this toy mitigation is not user authentication or tenant isolation. |
| HB21 | SQLite transactions serialize capacity check + insert/cancel + event; concurrent successful bookings must never oversell. Parameterized SQL only for user values. |
| HB22 | Business elements have always-present unique `data-oracle-id` values within each page. Hooks are instrumentation, not authorization or an independent oracle. |
| HB23 | Reset/state-hash/observe are exec-only control source, with no HTTP route. Reset empties authored bookings/events, restores the fixed slots and changes observation epoch; identical fresh business state hashes identically. |
| HB24 | Observer uses `(epoch, since)` to return ordered events; wrong epoch or invalid/future cursor is refused. No model projection contains control or oracle metadata; that projection is owned by the separate D3 seam, unverified here. |

## Twelve intended journeys — not executed tests

1. Fresh slot list: HB01–02; Harbour A 8 seats, Harbour B 12.
2. Open Harbour A booking form and refuse unknown slot: HB03.
3. Submit normalized demo label and party 1: HB04–05, HB11.
4. Reject empty/markup/overlong labels and noncanonical party text: HB04–05, HB18.
5. Book party 3 without discount: HB08–09, total Harbour A 7500.
6. Book party 4 with 10% discount: HB08–10, total Harbour B 6480.
7. Inspect stored confirmation, including unknown-ID refusal: HB11–12.
8. List active and cancelled booking amounts in order: HB13–14.
9. Fill/reject remaining capacity, including later concurrent-check qualification: HB06–07, HB21.
10. Cancel once then again; restore seats exactly once: HB14–17.
11. Refuse GET mutations, missing token, foreign Origin, malformed/oversized POST: HB19–20.
12. Under later explicit control authorization, reset/hash/observe epoch and inspect unique hooks/projection boundaries: HB22–24.

This contract precedes the D1 implementation in this source slice, but the agents already know
the shared authored scenario design. No historical clean-room, blinded or human-independent
authoring is claimed. Future toy variant examples are not study variants. The optional SUT
does not execute D2/D3 fixture reports or substitute for P4 containment or scientific admission.
