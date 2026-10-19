import { randomUUID } from "node:crypto";
import type { WorkflowState } from "./model.ts";
import type { Correction, Feedback } from "./metrics.ts";
import { emptyMeasurements } from "./metrics.ts";
import { text, WorkflowError } from "./validation.ts";
export function measure(state:WorkflowState,input:Record<string,unknown>,actor:string,now:number) {
 const m=state.measurements??=emptyMeasurements(),at=new Date(now).toISOString();
 if(input.action==="timer_start") {
  const client_id=text(input.client_id,"Asiakas",100);if(!state.clients.some(c=>c.id===client_id))throw new WorkflowError("Asiakas puuttuu");
  if(m.work_sessions.some(s=>!s.ended_at))throw new WorkflowError("Pysäytä aiempi ajastin",409);
  if(input.phase!=="ONBOARDING"&&input.phase!=="DELIVERY")throw new WorkflowError("Työvaihe puuttuu");
  m.work_sessions.push({id:randomUUID(),client_id,phase:input.phase,started_at:at,ended_at:null,actor});
 }else if(input.action==="timer_stop") {
  const s=m.work_sessions.find(s=>s.id===input.session_id&&s.actor===actor&&!s.ended_at);if(!s)throw new WorkflowError("Käynnissä olevaa ajastinta ei löydy");
  if(now<Date.parse(s.started_at))throw new WorkflowError("Ajastimen kellovirhe");s.ended_at=at;
 }else {
  const event=state.events.find(e=>e.digest_id===input.digest_id&&e.content_hash===input.content_hash&&e.type==="EXPORTED");
  if(!event)throw new WorkflowError("Valitse viety sisältöversio");
  if(input.action==="correction") {
   if(!["SOURCE","PROFILE","CONTENT","EXPORT"].includes(String(input.category)))throw new WorkflowError("Korjausluokka puuttuu");
   const reason=text(input.reason,"Korjauksen syy");
   if(m.corrections.some(c=>c.digest_id===event.digest_id&&c.content_hash===event.content_hash&&c.reason===reason&&c.category===input.category))throw new WorkflowError("Sama korjaus on jo kirjattu",409);
   m.corrections.push({id:randomUUID(),digest_id:event.digest_id,content_hash:event.content_hash,category:input.category as Correction["category"],reason,actor,created_at:at});
  }else if(input.action==="feedback") {
   if(input.source!=="INTERNAL_SIMULATION")throw new WorkflowError("Simulaatioon ei voi kirjata oikeaa asiakaspalautetta");
   if(!["USEFUL","NOT_USEFUL","UNKNOWN"].includes(String(input.label)))throw new WorkflowError("Palauteluokka puuttuu");
   const assessment_id=text(input.assessment_id,"Nosto",100);if(!event.snapshot.items.some(i=>i.assessment_id===assessment_id))throw new WorkflowError("Nosto ei kuulu toimitusversioon");
   m.feedback.push({id:randomUUID(),digest_id:event.digest_id,content_hash:event.content_hash,assessment_id,label:input.label as Feedback["label"],source:"INTERNAL_SIMULATION",reason:text(input.reason,"Palautteen peruste"),actor,created_at:at});
  }else throw new WorkflowError("Tuntematon mittaustoiminto");
 }
}
