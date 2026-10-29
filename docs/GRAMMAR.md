# testlens foundation grammar

Construction only; no suite has run. This parser uses TypeScript's AST and a
positive grammar. It never executes submitted code. An accepted file still needs
the separately qualified OS containment boundary before any execution.

The foundation intentionally implements a smaller subset of P6. Unsupported
constructs fail closed. This is not the full P6 acceptance gate.

Accepted declarations are one exact `import { test, expect } from '@playwright/test'`,
`test('literal title', async ({ page }) => { ... })`, nested synchronous
`test.describe('literal', () => { ... })` (at most eight levels), and
`test.beforeEach(async ({ page }) => { ... })`. Test identity is SHA256 of the
JSON title path; duplicate paths fail. Renaming/deleting a test changes the fixed
inventory and is tagged silenced. Multiple suite files require a later file-qualified
inventory adapter; this version inspects one complete source file per invocation.

Within callbacks, one simple `const` declaration per statement may bind a locator
or a bounded literal. Locator aliases are resolved to their chain; fixture/import
aliases and shadowing are refused. Literal constants are inventoried only at their
declaration; arguments currently require inline literals. No arbitrary expression
or callback is evaluated.

Locators: `page.getByRole`, `getByLabel`, `getByText`, `getByTestId`,
`getByPlaceholder`, `locator`, and corresponding chained calls; `first`, `last`,
`nth` (integer 0–1000), `filter` with `hasText`, `hasNotText`, `has`, `hasNot`.
Options permit string `name` and boolean `exact` for role, boolean `exact` for
other text locators. CSS is restricted to tags, ids, classes, exact double-quoted
`[data-testid="id"]`, descendants and child combinators. CSS escapes, pseudos,
substring attributes, arbitrary attributes, alternate selector engines and
attribute enumeration are rejected. Literal text referring to oracle, custody
or sourceMappingURL is rejected conservatively.

Awaited actions: `page.goto('/relative/path')`, locator `click`, `check` with no
arguments; `fill`, `selectOption`, `press` with one literal string. No options,
external URLs, interpolation or dynamic values. Awaited `page.waitForTimeout`
accepts literal 0–5000 ms and is tagged. Annotations are zero-argument
`test.skip()`, `test.fixme()`, `test.fail()`, `test.slow()` inside a test.

Awaited assertions: `expect(locator)` or `expect.soft(locator)`, optionally `.not`,
with these exact matchers:

| Matcher | Arguments |
| --- | --- |
| toBeVisible, toBeHidden, toBeEnabled, toBeDisabled, toBeChecked, toBeEmpty | none |
| toHaveText, toContainText | literal string or string array |
| toHaveValue | literal string |
| toHaveCount | nonnegative integer |
| toHaveAttribute | allowlisted attribute name and literal string |

Attributes: `aria-*`, value, title, role, href, class, id, data-testid.
Arrays are bounded to 100 entries, nesting to eight levels, strings to 4096
characters, numbers to finite 1e9, source to 256 KiB.

Inventory includes source hash, stable ids, assertion subjects/matchers/negation/
soft flag/arguments, actions, annotations, waits, locators, hook bodies and
zero-assertion flags. Zero-assertion tests never establish coverage. This inventory
does not replace the independent test-to-clause map or trusted runner discovery.

Diff is a conservative diagnostic, comparing fixed ids and ordered assertions.
It emits assertion_removed, assertion_weakened (exact text to contains, added
negation or soft), expected_value_rewritten, silenced, wait_added, locator_only,
other. Assertion reorderings can over-tag; hook changes always emit other and
require review. Tags do not decide true/false repair. Unknown matcher changes
emit other rather than inventing an ordering.

Deferred P6 work: regex literals/exact-to-regex weakening, `expect.poll` with a
restricted callback grammar, conditional annotations, literal-value aliases in
arguments, full matcher ordering, hook-aware semantic diff, multi-file identity,
all accepted/rejected conformance cases and an exact dependency lockfile. These
constructs are rejected until implemented; they are never silently admitted.

Example checker input (AUTHORED syntax example, not H0 or study evidence):

```ts
import { test, expect } from '@playwright/test';
test('syntax example', async ({ page }) => {
  await page.goto('/');
  const total = page.getByTestId('total');
  await expect(total).toHaveText('Example');
});
```

After Dirty Mode closes, verify this accepts, then verify `page.evaluate`, loops,
unknown methods, dynamic import, optional chaining, selector escape/substring
attacks, swallowed timeouts, config edits, duplicate ids and zero-test files
reject. Exercise every documented tag with authored conformance pairs. These
checks have not been run and do not provide independent study data.
