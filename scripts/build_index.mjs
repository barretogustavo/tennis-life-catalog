#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { readdirSync, readFileSync, writeFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const dataDir = join(root, 'data');
const files = {};

for (const name of readdirSync(dataDir).filter((f) => f.endsWith('.json') && f !== 'index.json').sort()) {
  const text = readFileSync(join(dataDir, name), 'utf8');
  const json = JSON.parse(text);
  const key = name.replace(/\.json$/, '');
  const count = Array.isArray(json.items)
    ? json.items.length
    : Array.isArray(json.brands)
      ? json.brands.length
      : 0;
  files[key] = {
    path: `data/${name}`,
    sha256: createHash('sha256').update(text).digest('hex'),
    count,
  };
}

const index = {
  schemaVersion: 1,
  version: 1,
  updatedAt: new Date().toISOString().replace(/\.\d{3}Z$/, 'Z'),
  files,
};

writeFileSync(join(dataDir, 'index.json'), `${JSON.stringify(index, null, 2)}\n`);
console.log('index.json updated', Object.fromEntries(Object.entries(files).map(([k, v]) => [k, v.count])));
