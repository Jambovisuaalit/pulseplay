import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validateContact, createContactDraft, PILOT_EMAIL } from '../app/esittely/contact.ts';
const valid = { company: 'Testiyritys & Poika Oy', name: 'Testaaja Ääkkönen', email: 'qa+pilot@example.invalid', region: 'Uusimaa', work: 'Saneeraus\nIkkunat + ovet & korjaus' };
function form(values) { const data = new FormData(); for (const [key, value] of Object.entries(values)) data.set(key, value); return data; }
test('All required values reject blank and whitespace; no email draft is opened', () => {
  const { errors } = validateContact(form({ company: '  ', name: '', email: '', region: '', work: '' }));
  assert.equal(Object.keys(errors).length, 5);
});
test('Malformed emails, newlines and excessive field lengths are rejected', () => {
  for (const email of ['bad', 'a@', 'a b@example.fi', 'a@example']) assert.ok(validateContact(form({ ...valid, email })).errors.email);
  assert.ok(validateContact(form({ ...valid, company: 'a\nb' })).errors.company);
  assert.ok(validateContact(form({ ...valid, work: 'a'.repeat(601) })).errors.work);
});
test('Valid input is trimmed and Finnish characters and multiline work survive mailto encoding', () => {
  const { values, errors } = validateContact(form({ ...valid, company: '  '+valid.company+' ' }));
  assert.deepEqual(errors, {}); assert.equal(values.company, valid.company);
  const draft = createContactDraft(values); const url = new URL(draft.url);
  assert.equal(url.pathname, PILOT_EMAIL); assert.equal(url.searchParams.get('subject'), draft.subject);
  assert.equal(url.searchParams.get('body'), draft.body); assert.ok(draft.body.includes(valid.work));
  assert.equal([...url.searchParams.keys()].length, 2);
});
test('Wrong-type FormData values are not coerced into contact details', () => {
  const data = form(valid); data.set('company', new Blob(['not a company']));
  assert.ok(validateContact(data).errors.company);
});
