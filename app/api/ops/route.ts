import { metrics } from "@/lib/domain/metrics";
import { NextRequest, NextResponse } from "next/server";
import { verifySession, SESSION_COOKIE } from "@/lib/session";
import { sameOrigin } from "@/lib/login-auth";
import { readState, transaction } from "@/lib/server/ops-store";
import { command } from "@/lib/domain/commands";
import { contentHash, exportSnapshot, qa, snapshot } from "@/lib/domain/workflow";
import { renderEml, renderHtml, renderText } from "@/lib/domain/exports";
import { WorkflowError } from "@/lib/domain/validation";
import type { WorkflowState } from "@/lib/domain/model";
import { renderPdf } from "@/lib/domain/pdf";
import { randomUUID } from "node:crypto";
export const runtime="nodejs";
export const dynamic="force-dynamic";
function view(s:WorkflowState) {
 return {...s,storage_mode:process.env.TP_OPS_STORE==="supabase"?"persistent":"local",metrics:metrics(s),digests:s.digests.map(d=>{
  let hash=null,preview=null;try{preview=snapshot(s,d);hash=contentHash(preview);}catch{}
  return {...d,qa:qa(s,d),current_hash:hash,preview};
 })};
}
function failure(e:unknown) {
 const known=e instanceof WorkflowError;
 return NextResponse.json({error:known?e.message:"Työtilan käsittely epäonnistui"},{status:known?e.status:500,headers:{"Cache-Control":"no-store"}});
}
async function allowed(r:NextRequest) {return verifySession(r.cookies.get(SESSION_COOKIE)?.value);}
export async function GET(r:NextRequest) {
 if(!(await allowed(r)))return new NextResponse(null,{status:401});
 try{return NextResponse.json(view(await readState()),{headers:{"Cache-Control":"no-store"}});}catch(e){return failure(e);}
}
export async function POST(r:NextRequest) {
 if(!(await allowed(r)))return new NextResponse(null,{status:401});
 if(!sameOrigin(r))return new NextResponse(null,{status:403});
 try{
  const raw=await r.text();if(Buffer.byteLength(raw)>100000)throw new WorkflowError("Pyyntö on liian suuri",413);
  let input:Record<string,unknown>;try{input=JSON.parse(raw);}catch{throw new WorkflowError("Virheellinen JSON");}
  if(!input||Array.isArray(input)||typeof input!=="object")throw new WorkflowError("Virheellinen pyyntö");
  const actor=process.env.TP_AUTH_USERNAME!;
  if(input.action!=="export")return NextResponse.json(await transaction(s=>view(command(s,input,actor))),{headers:{"Cache-Control":"no-store"}});
  const output=await transaction(s=>{
   if(input.expected_revision!==s.revision)throw new WorkflowError("Työtila muuttui. Lataa uusi tila.",409);
   const d=s.digests.find(d=>d.id===input.digest_id);if(!d)throw new WorkflowError("Kooste puuttuu");
   const snapshot=exportSnapshot(s,d),hash=d.approved_hash!,format=input.format;
   if(!["pdf","html","txt","eml","json"].includes(String(format)))throw new WorkflowError("Tuntematon vientimuoto");
   const body=format==="pdf"?renderPdf(snapshot):format==="html"?renderHtml(snapshot):format==="txt"?renderText(snapshot):format==="eml"?renderEml(snapshot,hash):JSON.stringify(snapshot,null,2);
   const reference=`${hash}.${format}`;
   if(!s.events.some(e=>e.digest_id===d.id&&e.type==="EXPORTED"&&e.reference===reference)){
    s.events.push({id:randomUUID(),digest_id:d.id,content_hash:hash,type:"EXPORTED",snapshot,actor,occurred_at:new Date().toISOString(),reference});s.revision++;
   }
   d.status="EXPORTED";
   return {body,format};
  });
  return new NextResponse(typeof output.body==="string"?output.body:new Uint8Array(output.body),{headers:{"Content-Type":output.format==="pdf"?"application/pdf":output.format==="html"?"text/html; charset=utf-8":output.format==="eml"?"message/rfc822":"text/plain; charset=utf-8","Content-Disposition":`attachment; filename="urakkaluotsi-simulaatio.${output.format}"`,"Cache-Control":"no-store","X-Content-Type-Options":"nosniff"}});
 }catch(e){return failure(e);}
}
