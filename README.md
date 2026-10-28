# e2e-repair-flake-study

M19 foundation: study boundary contracts plus a non-executing positive grammar
checker, inventory and patch diagnostics. Source-only, runtime unverified.

Authoritative adopted plan: `../planning/promoted/PLAN-M19-v1.md`. Coordination and transcripts remain outside this product repository.

Python contracts live in `src/m19/contracts`; the read-only CLI offers `m19 status`.
See [contract seams](docs/CONTRACTS.md). The Node checker lives in
`node/testlens/src` and uses the TypeScript compiler AST. See its
[grammar and explicit subset limits](docs/GRAMMAR.md).

After dependency activation is authorized, install the package locally and run
`node node/testlens/src/cli.mjs inventory <suite.ts>` or
`node node/testlens/src/cli.mjs diff <before.ts> <after.ts>`.
The checker reads source bytes and prints JSON; rejected input exits 2. It does
not import or run suites. TypeScript 5.9.3 is an exact provisional dependency pin;
availability and lock resolution have not been verified. No Playwright version
or image is claimed qualified.

This is a partial foundation, not completed P1/P6 or an executable study. No
containers, held-out variants, H0/P0, independent evaluations or study results
exist in this package. Human-independent gates remain pending Roy. All metrics
are **not yet measured**. No installs, tests, live/model calls, spend or publication
performed. OS containment must be independently qualified before any suite runs;
an AST check is not a security sandbox. License/release decisions remain pending.
