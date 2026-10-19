import { createHash, randomUUID } from "node:crypto";
import type { Assessment, DeliverySnapshot, Digest, WorkflowState } from "./model.ts";
import { WorkflowError } from "./validation.ts";
function canonical(value: unknown): string {
 if(Array.isArray(value))return `[${value.map(canonical).join(",")}]`;
 if(value!==null&&typeof value==="object")return `{${Object.entries(value).sort(([a],[b])=>a<b?-1:a>b?1:0).map(([k,v])=>`${JSON.stringify(k)}:${canonical(v)}`).join(",")}}`;
 return JSON.stringify(value);
}
export const contentHash=(value: unknown)=>createHash("sha256").update(canonical(value)).digest("hex");
export function currentProfile(state: WorkflowState, client: string) {
 const p=state.profiles.filter(p=>p.client_id===client).sort((a,b)=>b.version-a.version)[0];
 if(!p)throw new WorkflowError("Yritysprofiili puuttuu");return p;
}
export function snapshot(state: WorkflowState,digest: Digest): DeliverySnapshot {
 const client=state.clients.find(c=>c.id===digest.client_id);if(!client)throw new WorkflowError("Asiakas puuttuu");
 const profile=currentProfile(state,client.id);
 return {schema_version:1,mode:state.mode,client:{...client},profile:structuredClone(profile),template_version:"urakkaluotsi-1.1",items:digest.assessment_ids.map(id=>{
  const a=state.assessments.find(a=>a.id===id&&a.client_id===client.id);
  if(!a||a.profile_version_id!==profile.id)throw new WorkflowError("Arvio ei vastaa nykyistä asiakasta ja profiilia");
  const n=state.notices.find(n=>n.id===a.notice_version_id);if(!n)throw new WorkflowError("Ilmoitusversio puuttuu");
  return {assessment_id:a.id,notice_version_id:n.id,source_hash:n.source_hash,title:n.title,buyer:n.buyer,source_url:n.source_url,evidence:n.evidence,deadline:n.deadline??"",checked_at:n.checked_at,summary:a.summary,missing:[...n.missing,...a.missing,...profile.facts.filter(f=>f.verification!=="CONFIRMED").map(f=>`Yritysprofiili ${f.key}: vahvistamatta`)],next_action:a.next_action};
 })};
}
export function qa(state: WorkflowState,digest: Digest,now=Date.now()) {
 const errors:string[]=[];
 let s:DeliverySnapshot;try{s=snapshot(state,digest);}catch(e){return [(e as Error).message];}
 if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(s.client.delivery_email))errors.push("Vastaanottajan sähköposti puuttuu tai on virheellinen");
 if(s.items.length>10||new Set(digest.assessment_ids).size!==digest.assessment_ids.length)errors.push("Nostoja liikaa tai sama arvio toistuu");
 for(const item of s.items) {
  const a=state.assessments.find(a=>a.id===item.assessment_id)!;
  const n=state.notices.find(n=>n.id===item.notice_version_id)!;
  const latest=state.notices.filter(v=>v.notice_id===n.notice_id).sort((a,b)=>b.version-a.version)[0];
  if(latest.id!==n.id)errors.push(`${n.title}: lähdeversio on muuttunut`);
  if(!a.reviewed||a.coverage==="NONE")errors.push(`${n.title}: tarkistus tekemättä`);
  if(!n.evidence.trim()||!n.source_url.startsWith("https://"))errors.push(`${n.title}: lähde tai lähdeote puuttuu`);
  const age=now-Date.parse(n.checked_at),deadline=n.deadline?Date.parse(n.deadline):NaN;
  if(!Number.isFinite(age)||age<0||age>86400000)errors.push(`${n.title}: lähdetarkistus yli 24 h vanha tai virheellinen`);
  if(!Number.isFinite(deadline)||deadline<=now)errors.push(`${n.title}: määräaika puuttuu tai on päättynyt`);
  if(deadline-now<86400000&&age>3600000)errors.push(`${n.title}: lähellä määräaikaa tarvitaan alle tunnin lähdetarkistus`);
  if(n.cancelled!==false)errors.push(`${n.title}: peruutustila tarkistamatta tai ilmoitus peruttu`);
  if(!a.summary.trim()||!a.next_action.trim())errors.push(`${n.title}: arvio tai seuraava toimi puuttuu`);
  if(a.coverage==="PARTIAL"&&!item.missing.length)errors.push(`${n.title}: osittaisen tarkistuksen rajaus puuttuu`);
 }
 return errors;
}
export function invalidate(state: WorkflowState) {
 for(const digest of state.digests) {
  if(!digest.approved_hash)continue;
  let changed=true;try{changed=contentHash(snapshot(state,digest))!==digest.approved_hash;}catch{}
  if(changed||qa(state,digest).length){digest.status="NEEDS_REVIEW";digest.row_version++;digest.approved_hash=null;digest.approved_at=null;digest.approved_by=null;digest.approved_snapshot=null;}
 }
}
export function approve(state: WorkflowState,digest: Digest,expectedHash: string,actor: string,now=Date.now()) {
 const issues=qa(state,digest,now);if(issues.length)throw new WorkflowError(issues.join("; "),422);
 const s=snapshot(state,digest),hash=contentHash(s);if(hash!==expectedHash)throw new WorkflowError("Kooste muuttui. Lataa uusi versio.",409);
 digest.approved_snapshot=structuredClone(s);digest.approved_hash=hash;digest.approved_at=new Date(now).toISOString();digest.approved_by=actor;digest.status="APPROVED";digest.row_version++;
 state.events.push({id:randomUUID(),digest_id:digest.id,content_hash:hash,type:"APPROVED",snapshot:structuredClone(s),actor,occurred_at:digest.approved_at,reference:hash});
}
export function exportSnapshot(state: WorkflowState,digest: Digest,now=Date.now()) {
 if(!digest.approved_hash||!digest.approved_snapshot||!["APPROVED","EXPORTED"].includes(digest.status))throw new WorkflowError("Hyväksy kooste ennen vientiä",409);
 if(qa(state,digest,now).length||contentHash(snapshot(state,digest))!==digest.approved_hash||contentHash(digest.approved_snapshot)!==digest.approved_hash)throw new WorkflowError("QA tai sisältö on muuttunut. Uusi hyväksyntä vaaditaan.",409);
 return structuredClone(digest.approved_snapshot);
}
export function assessmentFor(state: WorkflowState,client_id:string,notice_version_id:string):Assessment {
 return {id:randomUUID(),client_id,notice_version_id,profile_version_id:currentProfile(state,client_id).id,row_version:1,summary:"",next_action:"",missing:[],coverage:"NONE",reviewed:false};
}
