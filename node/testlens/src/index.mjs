import ts from 'typescript';
import { createHash } from 'node:crypto';

const hash = text => createHash('sha256').update(text).digest('hex');
const methods = new Set(['getByRole', 'getByLabel', 'getByText', 'getByTestId', 'getByPlaceholder', 'locator']);
const actions = new Set(['click', 'fill', 'check', 'selectOption', 'press']);
const matchers = new Map([
  ['toBeVisible', [0, 0]], ['toBeHidden', [0, 0]], ['toBeEnabled', [0, 0]],
  ['toBeDisabled', [0, 0]], ['toBeChecked', [0, 0]], ['toBeEmpty', [0, 0]],
  ['toHaveText', [1, 1]], ['toContainText', [1, 1]], ['toHaveValue', [1, 1]],
  ['toHaveCount', [1, 1]], ['toHaveAttribute', [2, 2]],
]);
const annotations = new Set(['skip', 'fixme', 'fail', 'slow']);

export class GrammarError extends Error {
  constructor(node, source, message) {
    const position = source.getLineAndCharacterOfPosition(node.getStart(source));
    super(`${position.line + 1}:${position.character + 1}: ${message}`);
    this.name = 'GrammarError';
  }
}

/** Parses bytes only. Never transpiles, imports or executes submitted suites. */
export function inspectSuite(text) {
  if (typeof text !== 'string' || Buffer.byteLength(text) > 262144) throw new Error('suite exceeds 256 KiB');
  const source = ts.createSourceFile('suite.ts', text, ts.ScriptTarget.ES2022, true, ts.ScriptKind.TS);
  const fail = (node, message) => { throw new GrammarError(node, source, message); };
  if (source.parseDiagnostics.length) fail(source, 'TypeScript parse error');
  if (source.referencedFiles.length || source.typeReferenceDirectives.length || source.libReferenceDirectives.length) fail(source, 'reference directives forbidden');
  function rejectOptionalChains(node) {
    if (node.questionDotToken) fail(node, 'optional chaining forbidden');
    ts.forEachChild(node, rejectOptionalChains);
  }
  rejectOptionalChains(source);
  const inventory = { schema: 'm19.testlens.v1', sourceHash: hash(text), tests: [], hooks: [], locators: [] };
  const ids = new Set();
  let imported = false;
  const plain = node => {
    if (!ts.isStringLiteral(node) || node.text.length > 4096) fail(node, 'bounded string literal required');
    return node.text;
  };
  const sensitive = value => /oracle|custody|sourceMappingURL/i.test(value);
  const safeString = node => {
    const value = plain(node);
    if (sensitive(value)) fail(node, 'evaluator identity/source reference forbidden');
    return value;
  };
  function literal(node, depth = 0) {
    if (depth > 8) fail(node, 'literal nesting exceeds 8');
    if (ts.isStringLiteral(node)) return safeString(node);
    if (ts.isNumericLiteral(node)) {
      const value = Number(node.text);
      if (!Number.isFinite(value) || Math.abs(value) > 1e9) fail(node, 'number out of bounds');
      return value;
    }
    if (node.kind === ts.SyntaxKind.TrueKeyword) return true;
    if (node.kind === ts.SyntaxKind.FalseKeyword) return false;
    if (ts.isArrayLiteralExpression(node) && node.elements.length <= 100) return node.elements.map(n => literal(n, depth + 1));
    // Objects are accepted only at explicitly typed method option sites below.
    fail(node, 'unknown literal syntax');
  }
  function options(node, allowed, scope) {
    if (!ts.isObjectLiteralExpression(node) || node.properties.length > 8) fail(node, 'option object required');
    const result = {};
    for (const prop of node.properties) {
      if (!ts.isPropertyAssignment(prop) || !ts.isIdentifier(prop.name)) fail(prop, 'plain option property required');
      const key = prop.name.text;
      if (!allowed.has(key) || Object.hasOwn(result, key)) fail(prop, 'unknown or duplicate option');
      const kind = allowed.get(key);
      const value = kind === 'locator' ? locator(prop.initializer, scope) : literal(prop.initializer);
      if (kind === 'string' && typeof value !== 'string') fail(prop, 'string option required');
      if (kind === 'boolean' && typeof value !== 'boolean') fail(prop, 'boolean option required');
      result[key] = value;
    }
    return result;
  }
  function selector(node) {
    const value = safeString(node);
    // Only a deliberately small CSS dialect: tag, #id, .class, descendant,
    // child and exact test-id attribute. No escapes, regex, pseudos, substring
    // attributes or alternate engines can obfuscate evaluator hooks.
    const atom = '(?:[A-Za-z][A-Za-z0-9_-]*|[.#][A-Za-z_][A-Za-z0-9_-]*|\\[data-testid="[A-Za-z0-9_-]+"\\])';
    if (!new RegExp(`^${atom}(?:${atom}|[ >]+${atom})*$`).test(value)) fail(node, 'selector outside positive CSS dialect');
    return value;
  }
  function locator(node, scope) {
    if (ts.isIdentifier(node) && scope.get(node.text)?.kind === 'locator') return scope.get(node.text).value;
    if (!ts.isCallExpression(node) || node.typeArguments?.length || !ts.isPropertyAccessExpression(node.expression)) fail(node, 'locator required');
    const receiver = node.expression.expression;
    const name = node.expression.name.text;
    let parent;
    if (ts.isIdentifier(receiver) && receiver.text === 'page') parent = 'page';
    else parent = locator(receiver, scope);
    const args = node.arguments;
    if (methods.has(name)) {
      if (args.length < 1 || args.length > (name === 'locator' || name === 'getByTestId' ? 1 : 2)) fail(node, 'locator argument count');
      const value = name === 'locator' ? selector(args[0]) : safeString(args[0]);
      const allowed = name === 'getByRole' ? new Map([['name', 'string'], ['exact', 'boolean']]) : new Map([['exact', 'boolean']]);
      const checkedOptions = args[1] ? options(args[1], allowed, scope) : null;
      const result = `${parent}.${name}(${JSON.stringify(value)}${checkedOptions ? `,${JSON.stringify(checkedOptions)}` : ''})`;
      inventory.locators.push(result);
      return result;
    }
    if (parent === 'page') fail(node, 'unknown page method');
    if ((name === 'first' || name === 'last') && args.length === 0) return `${parent}.${name}()`;
    if (name === 'nth' && args.length === 1 && ts.isNumericLiteral(args[0]) && Number.isInteger(Number(args[0].text)) && Number(args[0].text) <= 1000) return `${parent}.nth(${args[0].text})`;
    if (name === 'filter' && args.length === 1) {
      const checkedOptions = options(args[0], new Map([['hasText', 'string'], ['hasNotText', 'string'], ['has', 'locator'], ['hasNot', 'locator']]), scope);
      return `${parent}.filter(${JSON.stringify(checkedOptions)})`;
    }
    fail(node, 'unknown locator operation');
  }
  function assertion(node, scope, record) {
    if (!ts.isCallExpression(node) || node.typeArguments?.length || !ts.isPropertyAccessExpression(node.expression)) return false;
    const name = node.expression.name.text;
    if (!matchers.has(name)) return false;
    let base = node.expression.expression;
    let negated = false;
    if (ts.isPropertyAccessExpression(base) && base.name.text === 'not') { negated = true; base = base.expression; }
    if (!ts.isCallExpression(base) || base.typeArguments?.length || base.arguments.length !== 1) fail(node, 'expect(locator) required');
    const soft = ts.isPropertyAccessExpression(base.expression) && ts.isIdentifier(base.expression.expression) && base.expression.expression.text === 'expect' && base.expression.name.text === 'soft';
    if (!(ts.isIdentifier(base.expression) && base.expression.text === 'expect') && !soft) fail(base, 'unknown expectation');
    const subject = locator(base.arguments[0], scope);
    const [min, max] = matchers.get(name);
    if (node.arguments.length < min || node.arguments.length > max) fail(node, 'matcher argument count');
    const args = node.arguments.map(n => literal(n));
    if (name === 'toHaveAttribute' && (typeof args[0] !== 'string' || !/^(?:aria-[a-z-]+|value|title|role|href|class|id|data-testid)$/.test(args[0]))) fail(node, 'attribute outside allowlist');
    if (name === 'toHaveCount' && (!Number.isInteger(args[0]) || args[0] < 0)) fail(node, 'count must be nonnegative integer');
    if (name !== 'toHaveCount' && args.some(a => typeof a !== 'string' && !(['toHaveText', 'toContainText'].includes(name) && Array.isArray(a) && a.every(v => typeof v === 'string')))) fail(node, 'string matcher values required');
    record.assertions.push({ subject, matcher: name, not: negated, soft, poll: false, args });
    return true;
  }
  function callback(node, hook = false) {
    if (!ts.isArrowFunction(node) || node.typeParameters?.length || node.type || node.modifiers?.some(m => m.kind !== ts.SyntaxKind.AsyncKeyword) || !ts.isBlock(node.body)) fail(node, 'block arrow callback required');
    if (!node.modifiers?.some(m => m.kind === ts.SyntaxKind.AsyncKeyword) || node.parameters.length !== 1) fail(node, 'async ({ page }) callback required');
    const param = node.parameters[0];
    if (param.type || param.initializer || param.dotDotDotToken || param.questionToken || param.modifiers?.length || !ts.isObjectBindingPattern(param.name) || param.name.elements.length !== 1) fail(param, 'page fixture only');
    const element = param.name.elements[0];
    if (element.propertyName || element.dotDotDotToken || element.initializer || !ts.isIdentifier(element.name) || element.name.text !== 'page') fail(param, 'page aliases forbidden');
    const record = { assertions: [], actions: [], annotations: [], waits: [], constants: [], zeroAssertions: true };
    statements(node.body.statements, new Map(), record, hook);
    record.zeroAssertions = record.assertions.length === 0;
    return record;
  }
  function statements(nodes, scope, record, hook) {
    for (const node of nodes) {
      if (ts.isVariableStatement(node) && !node.modifiers?.length && node.declarationList.flags === ts.NodeFlags.Const && node.declarationList.declarations.length === 1) {
        const d = node.declarationList.declarations[0];
        if (!ts.isIdentifier(d.name) || d.type || d.exclamationToken || !d.initializer || scope.has(d.name.text) || ['page', 'test', 'expect'].includes(d.name.text)) fail(node, 'simple unique const binding required');
        if (ts.isCallExpression(d.initializer) || ts.isIdentifier(d.initializer)) scope.set(d.name.text, { kind: 'locator', value: locator(d.initializer, scope) });
        else {
          const value = literal(d.initializer);
          scope.set(d.name.text, { kind: 'literal', value });
          record.constants.push({ name: d.name.text, value });
        }
        continue;
      }
      if (!ts.isExpressionStatement(node)) fail(node, 'unknown statement syntax');
      let expr = node.expression;
      const awaited = ts.isAwaitExpression(expr);
      if (awaited) expr = expr.expression;
      if (!ts.isCallExpression(expr) || expr.typeArguments?.length) fail(expr, 'call required');
      if (awaited && assertion(expr, scope, record)) continue;
      if (!ts.isPropertyAccessExpression(expr.expression)) fail(expr, 'unknown call');
      const receiver = expr.expression.expression;
      const method = expr.expression.name.text;
      const args = expr.arguments;
      if (ts.isIdentifier(receiver) && receiver.text === 'test' && annotations.has(method) && !awaited && !hook && args.length === 0) {
        record.annotations.push(method); continue;
      }
      if (!awaited) fail(expr, 'browser/assertion calls must be awaited');
      if (ts.isIdentifier(receiver) && receiver.text === 'page') {
        if (method === 'goto' && args.length === 1) {
          const url = safeString(args[0]);
          if (!/^\/(?!\/)[A-Za-z0-9/_?=&.-]*$/.test(url)) fail(expr, 'app-relative URL required');
          record.actions.push({ method, target: url, args: [] }); continue;
        }
        if (method === 'waitForTimeout' && args.length === 1 && ts.isNumericLiteral(args[0]) && Number(args[0].text) <= 5000) {
          record.waits.push(Number(args[0].text)); continue;
        }
        fail(expr, 'unknown page action');
      }
      if (!actions.has(method)) fail(expr, 'unknown action');
      const expected = ['fill', 'selectOption', 'press'].includes(method) ? 1 : 0;
      if (args.length !== expected) fail(expr, 'action argument count');
      const values = args.map(n => safeString(n));
      record.actions.push({ method, target: locator(receiver, scope), args: values });
    }
  }
  function declarations(nodes, path = []) {
    for (const node of nodes) {
      if (ts.isImportDeclaration(node) && path.length === 0 && !imported) {
        const clause = node.importClause;
        if (plain(node.moduleSpecifier) !== '@playwright/test' || node.attributes || clause?.isTypeOnly || clause?.name || !clause?.namedBindings || !ts.isNamedImports(clause.namedBindings)) fail(node, 'exact Playwright import required');
        const names = clause.namedBindings.elements;
        if (names.length !== 2 || names.some(n => n.isTypeOnly || n.propertyName) || new Set(names.map(n => n.name.text)).size !== 2 || names.some(n => !['test', 'expect'].includes(n.name.text))) fail(node, 'import only unaliased test and expect');
        imported = true; continue;
      }
      if (!imported || !ts.isExpressionStatement(node) || !ts.isCallExpression(node.expression) || node.expression.typeArguments?.length) fail(node, 'test declaration required');
      const call = node.expression;
      const args = call.arguments;
      if (ts.isPropertyAccessExpression(call.expression) && ts.isIdentifier(call.expression.expression) && call.expression.expression.text === 'test') {
        const name = call.expression.name.text;
        if (name === 'describe' && args.length === 2) {
          const title = safeString(args[0]);
          const body = args[1];
          if (!ts.isArrowFunction(body) || body.parameters.length || body.modifiers?.length || body.type || body.typeParameters?.length || !ts.isBlock(body.body) || path.length >= 8) fail(body, 'plain describe callback required; depth <= 8');
          declarations(body.body.statements, [...path, title]); continue;
        }
        if (name === 'beforeEach' && args.length === 1) {
          inventory.hooks.push({ path, ...callback(args[0], true) }); continue;
        }
        fail(call, 'unknown test declaration');
      }
      if (!ts.isIdentifier(call.expression) || call.expression.text !== 'test' || args.length !== 2) fail(call, 'test(title, callback) required');
      const title = safeString(args[0]);
      const fullTitle = [...path, title];
      const id = hash(JSON.stringify(fullTitle));
      if (ids.has(id)) fail(call, 'duplicate test title path');
      ids.add(id);
      inventory.tests.push({ id, title: fullTitle, ...callback(args[1]) });
    }
  }
  declarations(source.statements);
  if (!imported || !inventory.tests.length) fail(source, 'nonempty suite required');
  return inventory;
}

/** Conservative multi-label diagnostic. No tag is an oracle or green verdict. */
export function diffSuites(beforeText, afterText) {
  const before = inspectSuite(beforeText);
  const after = inspectSuite(afterText);
  const tags = new Set();
  const changed = JSON.stringify(before.tests) !== JSON.stringify(after.tests) || JSON.stringify(before.hooks) !== JSON.stringify(after.hooks);
  const next = new Map(after.tests.map(t => [t.id, t]));
  for (const test of before.tests) {
    const updated = next.get(test.id);
    if (!updated) { tags.add('silenced'); tags.add('assertion_removed'); continue; }
    if (updated.annotations.some(a => ['skip', 'fixme', 'fail'].includes(a) && !test.annotations.includes(a))) tags.add('silenced');
    if (updated.assertions.length < test.assertions.length) tags.add('assertion_removed');
    if (test.assertions.length && !updated.assertions.length) tags.add('silenced');
    for (let i = 0; i < Math.min(test.assertions.length, updated.assertions.length); i++) {
      const old = test.assertions[i], current = updated.assertions[i];
      if (JSON.stringify(old.args) !== JSON.stringify(current.args)) tags.add('expected_value_rewritten');
      if ((!old.not && current.not) || (!old.soft && current.soft) || (old.matcher === 'toHaveText' && current.matcher === 'toContainText')) tags.add('assertion_weakened');
      if (old.matcher !== current.matcher && !(old.matcher === 'toHaveText' && current.matcher === 'toContainText')) tags.add('other');
    }
    if (updated.waits.length > test.waits.length || updated.waits.some((v, i) => v > (test.waits[i] ?? 0))) tags.add('wait_added');
  }
  // Hook changes can affect every test: do not hide them as locator-only edits.
  if (JSON.stringify(before.hooks) !== JSON.stringify(after.hooks)) tags.add('other');
  const withoutLocators = inv => JSON.stringify(inv.tests.map(t => ({ ...t,
    actions: t.actions.map(a => ({ ...a, target: a.method === 'goto' ? a.target : '<locator>' })),
    assertions: t.assertions.map(a => ({ ...a, subject: '<locator>' })),
  })));
  if (changed && tags.size === 0) tags.add(withoutLocators(before) === withoutLocators(after) ? 'locator_only' : 'other');
  if (!changed && beforeText !== afterText) tags.add('other');
  return { schema: 'm19.testlens.diff.v1', beforeHash: before.sourceHash, afterHash: after.sourceHash, tags: [...tags].sort(), before, after };
}
