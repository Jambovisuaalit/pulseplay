import { randomUUID } from "node:crypto";
import type { Digest, WorkflowState } from "./model.ts";
import { approve, assessmentFor, contentHash, currentProfile, invalidate } from "./workflow.ts";
import { https, profileFacts, strings, text, timestamp, WorkflowError } from "./validation.ts";
export function command(state:WorkflowState,input:Record<string,unknown>,actor:string,now=Date.now()) {
 if(input.expected_revision!==state.revision)throw new WorkflowError("Työtila muuttui. Lataa uusi tila.",409);
 const at=new Date(now).toISOString(),action=input.action;
 if(action==="client") {
  const email=text(input.delivery_email,"Sähköposti",254);if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)||/[\r\n]/.test(email))throw new WorkflowError("Sähköposti on virheellinen");
  const existing=state.clients.find(c=>c.id===input.client_id);
  if(existing){existing.name=text(input.name,"Yritys",200);existing.delivery_email=email;}
  else state.clients.push({id:randomUUID(),name:text(input.name,"Yritys",200),delivery_email:email});
 } else if(action==="profile") {
  const client_id=text(input.client_id,"Asiakas",100);if(!state.clients.some(c=>c.id===client_id))throw new WorkflowError("Asiakas puuttuu");
  const versions=state.profiles.filter(p=>p.client_id===client_id);
  state.profiles.push({id:randomUUID(),client_id,version:Math.max(0,...versions.map(p=>p.version))+1,services:strings(input.services,"Palvelut"),regions:strings(input.regions,"Alueet"),facts:profileFacts(input.facts),created_at:at});
 } else if(action==="notice") {
  const notice_id=text(input.notice_id,"Hilma-tunniste",30);if(!/^\d+$/.test(notice_id))throw new WorkflowError("Hilma-tunniste on virheellinen");
  const data={title:text(input.title,"Otsikko",300),buyer:text(input.buyer,"Ostaja",300),source_url:https(input.source_url),deadline:input.deadline===null?null:timestamp(input.deadline,"Määräaika"),evidence:typeof input.evidence==="string"?input.evidence.slice(0,5000):"",missing:strings(input.missing,"Puuttuvat tiedot"),cancelled:input.cancelled===true?true:input.cancelled===false?false:null};
  const checked_at=timestamp(input.checked_at,"Lähdetarkistus");if(Date.parse(checked_at)>now)throw new WorkflowError("Tarkistusaika on tulevaisuudessa");
  const versions=state.notices.filter(n=>n.notice_id===notice_id),source_hash=contentHash(data);
  const latest=versions.sort((a,b)=>b.version-a.version)[0];
  if(latest?.source_hash===source_hash)latest.checked_at=checked_at;
  else state.notices.push({...data,id:randomUUID(),notice_id,version:(latest?.version??0)+1,source_hash,checked_at,created_at:at});
 } else if(action==="review") {
  const client_id=text(input.client_id,"Asiakas",100),notice_version_id=text(input.notice_version_id,"Ilmoitus",100);
  if(!state.notices.some(n=>n.id===notice_version_id))throw new WorkflowError("Ilmoitus puuttuu");
  const profile=currentProfile(state,client_id);
  let a=state.assessments.find(a=>a.client_id===client_id&&a.notice_version_id===notice_version_id&&a.profile_version_id===profile.id);
  if(!a){a=assessmentFor(state,client_id,notice_version_id);state.assessments.push(a);}
  a.summary=text(input.summary,"Arvio");a.next_action=text(input.next_action,"Seuraava toimi");a.missing=strings(input.missing,"Puuttuvat tiedot");
  if(input.coverage!=="PARTIAL"&&input.coverage!=="COMPLETE")throw new WorkflowError("Tarkistuksen kattavuus puuttuu");
  a.coverage=input.coverage;a.reviewed=true;a.row_version++;
 } else if(action==="compose") {
  const client_id=text(input.client_id,"Asiakas",100);currentProfile(state,client_id);
  const ids=strings(input.assessment_ids,"Nostot");if(ids.length>10||new Set(ids).size!==ids.length)throw new WorkflowError("Virheellinen nostovalinta");
  const d:Digest={id:randomUUID(),client_id,assessment_ids:ids,row_version:1,status:"DRAFT",approved_snapshot:null,approved_hash:null,approved_at:null,approved_by:null};
  state.digests.push(d);
 } else if(action==="approve") {
  const d=state.digests.find(d=>d.id===input.digest_id);if(!d)throw new WorkflowError("Kooste puuttuu");
  approve(state,d,text(input.expected_hash,"Sisältöhash",64),actor,now);
 } else if(action==="sent") {
  // Simulations cannot be counted as external customer deliveries.
  throw new WorkflowError("Simulaatiosta ei voi kirjata oikeaa lähetystä",422);
 } else throw new WorkflowError("Tuntematon toiminto");
 invalidate(state);state.revision++;
 return state;
}
