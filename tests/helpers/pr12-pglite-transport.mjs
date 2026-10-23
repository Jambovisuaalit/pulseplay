// Local runner regression only. All fetches are intercepted; no external network.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
const { PGlite } = await import(process.env.PGLITE_MODULE);
assert.ok(process.env.PR12_QA_DATABASE_DIRECTORY, 'Missing isolated PGlite directory');

globalThis.fetch = async (input, init) => {
  const url = new URL(input);
  assert.equal(url.origin, 'https://kzcmzelxydrhxxhcmmua.supabase.co');
  assert.equal(url.pathname, '/rest/v1/urakkaluotsi_ops_state');
  assert.equal(init.headers.apikey, 'synthetic-local-runner-only');
  assert.equal(init.redirect, 'error');
  const db = new PGlite(process.env.PR12_QA_DATABASE_DIRECTORY);
  try {
    if (!(await db.query("select to_regclass('public.urakkaluotsi_ops_state') as name")).rows[0].name) {
      await db.exec('create role anon; create role authenticated; create role service_role bypassrls;');
      await db.exec(await readFile(new URL('../../docs/ops-database-schema.sql', import.meta.url), 'utf8'));
    }
    await db.exec('set role service_role');
    if (init.method === 'GET') {
      const filter = url.searchParams.get('workspace_id');
      assert.ok(filter?.startsWith('eq.'));
      return Response.json((await db.query('select workspace_id,storage_version,state from public.urakkaluotsi_ops_state where workspace_id=$1', [filter.slice(3)])).rows);
    }
    assert.equal(init.method, 'POST', 'Runner regression must not UPDATE or DELETE a workspace');
    const row = JSON.parse(init.body);
    try {
      return Response.json((await db.query('insert into public.urakkaluotsi_ops_state values ($1,$2,$3) returning workspace_id,storage_version,state', [row.workspace_id, row.storage_version, row.state])).rows, { status: 201 });
    } catch (error) {
      if (error.code === '23505') return Response.json({ code: '23505' }, { status: 409 });
      throw error;
    }
  } finally { await db.close(); }
};
