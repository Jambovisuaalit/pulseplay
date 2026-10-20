// Integration QA against embedded PostgreSQL, not a Supabase production claim.
// PGLITE_MODULE points to the temporary QA installation, never a runtime dependency.
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { emptyState } from '../lib/domain/model.ts';
const {PGlite}=await import(process.env.PGLITE_MODULE);
const db=new PGlite();
let checks=0;
try {
 await db.exec('create role anon; create role authenticated; create role service_role bypassrls;');
 await db.exec(await readFile(new URL('../docs/ops-database-schema.sql',import.meta.url),'utf8'));
 const state=emptyState();
 for(const role of ['anon','authenticated']){
  await db.exec(`set role ${role}`);
  for(const sql of ["select * from public.urakkaluotsi_ops_state", "insert into public.urakkaluotsi_ops_state values ('forbidden',1,'{}')", "update public.urakkaluotsi_ops_state set storage_version=2", "delete from public.urakkaluotsi_ops_state"]){
   await assert.rejects(db.query(sql),e=>e.code==='42501');checks++;
  }
  await db.exec('reset role');
 }
 await db.exec('set role service_role');
 await db.query('insert into public.urakkaluotsi_ops_state values ($1,1,$2)', ['pilot-simulation',state]);checks++;
 await assert.rejects(db.query('insert into public.urakkaluotsi_ops_state values ($1,1,$2)', ['pilot-simulation',state]),e=>e.code==='23505');checks++;
 const snapshot=await db.query('select state from public.urakkaluotsi_ops_state where workspace_id=$1',['pilot-simulation']);
 assert.deepEqual(snapshot.rows[0].state,state);checks++;
 await db.exec('reset role; grant select on public.urakkaluotsi_ops_state to authenticated; set role authenticated;');
 assert.equal((await db.query('select * from public.urakkaluotsi_ops_state')).rows.length,0);checks++;
 await db.exec('reset role; revoke select on public.urakkaluotsi_ops_state from authenticated; set role service_role;');
 const winner=await db.query('update public.urakkaluotsi_ops_state set storage_version=2 where workspace_id=$1 and storage_version=1 returning storage_version',['pilot-simulation']);
 assert.equal(winner.rows.length,1);checks++;
 const loser=await db.query('update public.urakkaluotsi_ops_state set storage_version=2 where workspace_id=$1 and storage_version=1 returning storage_version',['pilot-simulation']);
 assert.equal(loser.rows.length,0);checks++;
 for(const invalid of [{}, {...state,mode:'REAL'}, {...state,events:null}, {...state,revision:-1}]){
  await assert.rejects(db.query('insert into public.urakkaluotsi_ops_state values ($1,1,$2)',['invalid-test',invalid]),e=>e.code==='23514');checks++;
 }
 await assert.rejects(db.query('delete from public.urakkaluotsi_ops_state'),e=>e.code==='42501');checks++;
 console.log(`PASS embedded PostgreSQL: ${checks} grants, RLS setup, constraints and atomic version checks. Hosted Supabase not tested.`);
}finally{await db.close();}
