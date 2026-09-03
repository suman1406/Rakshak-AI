import assert from 'node:assert/strict';
import { readdirSync, readFileSync } from 'node:fs';
import { join } from 'node:path';
import test from 'node:test';

const sourceRoot = join(process.cwd(), 'src');
const banned = ['mockApi', 'mockData', 'MOCK_', 'demoFields', 'demoScans'];

function sourceFiles(directory) {
  return readdirSync(directory, { withFileTypes: true }).flatMap((entry) => entry.isDirectory() ? sourceFiles(join(directory, entry.name)) : /\.(ts|tsx)$/.test(entry.name) ? [join(directory, entry.name)] : []);
}

test('web application source contains no mock-data integration', () => {
  const violations = sourceFiles(sourceRoot).flatMap((file) => {
    const content = readFileSync(file, 'utf8');
    return banned.filter((term) => content.includes(term)).map((term) => `${file}: ${term}`);
  });
  assert.deepEqual(violations, []);
});
