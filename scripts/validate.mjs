#!/usr/bin/env node
import { createHash } from 'node:crypto';
import { readFileSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = join(dirname(fileURLToPath(import.meta.url)), '..');
const dataDir = join(root, 'data');
const index = JSON.parse(readFileSync(join(dataDir, 'index.json'), 'utf8'));
let errors = 0;

function fail(msg) {
  console.error(`✗ ${msg}`);
  errors += 1;
}

function ok(msg) {
  console.log(`✓ ${msg}`);
}

for (const [key, meta] of Object.entries(index.files)) {
  const path = join(root, meta.path);
  if (!existsSync(path)) {
    fail(`${key}: missing ${meta.path}`);
    continue;
  }
  const text = readFileSync(path, 'utf8');
  const hash = createHash('sha256').update(text).digest('hex');
  if (hash !== meta.sha256) fail(`${key}: sha256 mismatch (run build_index.mjs)`);
  else ok(`${key}: hash ok`);

  const json = JSON.parse(text);
  if (json.schemaVersion !== 1) fail(`${key}: schemaVersion must be 1`);

  if (key === 'apparel') {
    if (!Array.isArray(json.brands) || !Array.isArray(json.pieces)) fail('apparel: brands/pieces required');
    continue;
  }

  if (!Array.isArray(json.items)) {
    fail(`${key}: items[] required`);
    continue;
  }
  if (json.items.length !== meta.count) fail(`${key}: count ${meta.count} != items ${json.items.length}`);

  const ids = new Set();
  const names = new Set();
  for (const item of json.items) {
    if (!item.id || !item.brand) {
      fail(`${key}: item missing id/brand`);
      continue;
    }
    const label = key === 'strings' ? item.name : item.model;
    if (!label) {
      fail(`${key}: ${item.id} missing model/name`);
      continue;
    }
    if (ids.has(item.id)) fail(`${key}: duplicate id ${item.id}`);
    ids.add(item.id);
    const pair = `${item.brand.toLowerCase()}|${label.toLowerCase()}`;
    if (names.has(pair)) fail(`${key}: duplicate ${item.brand} ${label}`);
    names.add(pair);

    if (key === 'rackets') {
      const s = item.specs;
      if (!s || typeof s.weightG !== 'number' || typeof s.headSizeSqIn !== 'number') {
        fail(`${key}: ${item.id} missing specs`);
      }
    }
    if (key === 'strings') {
      const s = item.spec;
      if (!s || !s.gauge || typeof s.mainsLbs !== 'number') fail(`${key}: ${item.id} missing spec`);
    }
  }
  ok(`${key}: ${json.items.length} items`);
}

if (errors) {
  console.error(`\n${errors} error(s)`);
  process.exit(1);
}
console.log('\nAll good.');
