// Frozen ReportLab fixture: page dictionaries are uncompressed. This is not a general PDF parser.
const fs = require('node:fs');
const assert = require('node:assert/strict');
const { createHash } = require('node:crypto');
const bytes = fs.readFileSync('qa-output/esimerkkikooste.pdf');
const sha256 = createHash('sha256').update(bytes).digest('hex');
assert.equal(sha256, '36762a526ae0a7299098c77e8e64a9ca78d15b4a3ac0b9a4624b7b9e4ad1e69b');
const pages = (bytes.toString('latin1').match(/\/Type\s*\/Page\b/g) || []).length;
assert.equal(pages, 4);
const evidence = { fixture: 'Urakkaluotsi public demo v1', pages, bytes: bytes.length, sha256, status: 'PASS' };
fs.writeFileSync('qa-output/pdf-verification.json', JSON.stringify(evidence, null, 2));
console.log(JSON.stringify(evidence));
