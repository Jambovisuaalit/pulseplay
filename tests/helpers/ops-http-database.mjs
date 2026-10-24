// Isolated PostgreSQL transport for the real Next HTTP workflow. No hosted claim.
import assert from 'node:assert/strict';
import { mkdtemp, readFile, rm } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import path from 'node:path';

export async function databaseTransport() {
 const {PGlite}=await import(process.env.PGLITE_MODULE);
 const directory=await mkdtemp(path.join(tmpdir(),'urakkaluotsi-http-db-'));
 const db=new PGlite(directory), original=global.fetch;
 let failed=false;
 await db.exec('create role anon; create role authenticated; create role service_role bypassrls;');
 await db.exec(await readFile(new URL('../../docs/ops-database-schema.sql',import.meta.url),'utf8'));
 await db.exec('set role service_role');
 process.env.TP_OPS_STORE='supabase';
 process.env.TP_SUPABASE_URL='https://abcdefghijklmnopqrst.supabase.co';
 process.env.TP_SUPABASE_SECRET_KEY='sb_secret_synthetic';
 process.env.TP_OPS_WORKSPACE='pr12-e2e-http-synthetic';
 global.fetch=async(input,init)=>{
  if(!String(input).startsWith(process.env.TP_SUPABASE_URL))return original(input,init);
  if(failed)throw new Error('Synthetic database outage');
  assert.equal(init.headers.apikey,'sb_secret_synthetic');assert.equal(init.redirect,'error');
  const url=new URL(input), workspace=url.searchParams.get('workspace_id')?.slice(3);
  try{
   if(init.method==='GET')return Response.json((await db.query('select state,storage_version from public.urakkaluotsi_ops_state where workspace_id=$1',[workspace])).rows);
   const row=JSON.parse(init.body);
   if(init.method==='POST')return Response.json((await db.query('insert into public.urakkaluotsi_ops_state values ($1,$2,$3) returning state,storage_version',[row.workspace_id,row.storage_version,row.state])).rows,{status:201});
   assert.equal(init.method,'PATCH');
   const version=Number(url.searchParams.get('storage_version')?.slice(3));
   return Response.json((await db.query('update public.urakkaluotsi_ops_state set state=$1,storage_version=$2 where workspace_id=$3 and storage_version=$4 returning state,storage_version',[row.state,row.storage_version,workspace,version])).rows);
  }catch(error){if(error.code==='23505')return Response.json({code:'23505'},{status:409});throw error;}
 };
 return {fail(){failed=true;},async close(){global.fetch=original;await db.close();await rm(directory,{recursive:true,force:true});}};
}
