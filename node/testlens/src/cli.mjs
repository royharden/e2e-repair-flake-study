#!/usr/bin/env node
import { readFileSync } from 'node:fs';
import { inspectSuite, diffSuites } from './index.mjs';

const [command, first, second, ...extra] = process.argv.slice(2);
try {
  if (!first || extra.length || !['inventory', 'diff'].includes(command) || (command === 'diff') !== Boolean(second)) {
    throw new Error('usage: testlens inventory suite.ts | testlens diff before.ts after.ts');
  }
  const before = readFileSync(first, 'utf8');
  const result = command === 'inventory' ? inspectSuite(before) : diffSuites(before, readFileSync(second, 'utf8'));
  console.log(JSON.stringify({ accepted: true, ...result }, null, 2));
} catch (error) {
  console.error(JSON.stringify({ accepted: false, error: error.message }));
  process.exitCode = 2;
}
