import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { randomUUID } from 'node:crypto';
import { syntheticBackupState } from './helpers/pr12-qa.mjs';

test('test-only cleanup removes only the owning run without granting table DELETE',async()=>{
 const {PGlite}=await import(process.env.PGLITE_MODULE),db=new PGlite();
 const run=randomUUID(),workspace=`pr12-e2e-source-${run}`,state=syntheticBackupState(run);
 try{
  await db.exec('create role anon; create role authenticated; create role service_role bypassrls;');
  await db.exec(await readFile(new URL('../docs/ops-database-schema.sql',import.meta.url),'utf8'));
  await db.exec(await readFile(new URL('../docs/ops-test-cleanup.sql',import.meta.url),'utf8'));
  await db.query('insert into public.urakkaluotsi_ops_state values ($1,1,$2),($3,1,$2)',[workspace,state,'unrelated-workspace']);
  for(const role of ['anon','authenticated']){
   await db.exec(`set role ${role}`);
   await assert.rejects(db.query('select public.urakkaluotsi_cleanup_e2e($1,$2,1)',[workspace,run]),e=>e.code==='42501');
   await db.exec('reset role');
  }
  await db.exec('set role service_role');
  await assert.rejects(db.query('delete from public.urakkaluotsi_ops_state'),e=>e.code==='42501');
  await assert.rejects(db.query('select public.urakkaluotsi_cleanup_e2e($1,$2,1)',['unrelated-workspace',run]),e=>e.code==='22023');
  await assert.rejects(db.query('select public.urakkaluotsi_cleanup_e2e($1,$2,1)',[workspace,randomUUID()]),e=>e.code==='22023');
  await assert.rejects(db.query('select public.urakkaluotsi_cleanup_e2e($1,null,1)',[workspace]),e=>e.code==='22023');
  await assert.rejects(db.query('select public.urakkaluotsi_cleanup_e2e($1,$2,2)',[workspace,run]),e=>e.code==='40001');
  assert.equal((await db.query('select public.urakkaluotsi_cleanup_e2e($1,$2,1) as removed',[workspace,run])).rows[0].removed,true);
  assert.deepEqual((await db.query('select workspace_id from public.urakkaluotsi_ops_state')).rows.map(r=>r.workspace_id),['unrelated-workspace']);
  await assert.rejects(db.query('delete from public.urakkaluotsi_ops_state'),e=>e.code==='42501');
 }finally{await db.close();}
});
