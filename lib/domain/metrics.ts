import type { WorkflowState } from "./model.ts";
export interface WorkSession {id:string;client_id:string;phase:"ONBOARDING"|"DELIVERY";started_at:string;ended_at:string|null;actor:string;}
export interface Correction {id:string;digest_id:string;content_hash:string;reason:string;category:"SOURCE"|"PROFILE"|"CONTENT"|"EXPORT";created_at:string;actor:string;}
export interface Feedback {id:string;digest_id:string;content_hash:string;assessment_id:string;label:"USEFUL"|"NOT_USEFUL"|"UNKNOWN";source:"INTERNAL_SIMULATION"|"CUSTOMER";reason:string;created_at:string;actor:string;}
export interface Measurements {work_sessions:WorkSession[];corrections:Correction[];feedback:Feedback[];}
export const emptyMeasurements=():Measurements=>({work_sessions:[],corrections:[],feedback:[]});
export function metrics(state:WorkflowState,client_id?:string) {
 const m=state.measurements??emptyMeasurements(),clients=new Set(state.clients.filter(c=>!client_id||c.id===client_id).map(c=>c.id));
 const relevant=state.events.filter(e=>clients.has(e.snapshot.client.id));
 const versions=new Set(relevant.filter(e=>e.type==="EXPORTED").map(e=>`${e.digest_id}:${e.content_hash}`));
 const latest=new Map<string,typeof state.events[number]>();
 for(const e of relevant)if(e.type==="EXPORTED")latest.set(e.digest_id,e);
 const sessions=m.work_sessions.filter(s=>clients.has(s.client_id));
 const closed=sessions.filter(s=>s.ended_at!==null);
 const seconds=(phase:WorkSession["phase"])=>closed.filter(s=>s.phase===phase).reduce((sum,s)=>sum+(Date.parse(s.ended_at!)-Date.parse(s.started_at))/1000,0);
 const deliverySessions=closed.filter(s=>s.phase==="DELIVERY");
 const clientDays=new Set(deliverySessions.map(s=>`${s.client_id}:${new Date(s.started_at).toLocaleDateString("en-CA",{timeZone:"Europe/Helsinki"})}`));
 let useful=0,not_useful=0,unknown=0,pending=0;
 for(const e of latest.values())for(const item of e.snapshot.items) {
  const f=m.feedback.filter(f=>f.digest_id===e.digest_id&&f.content_hash===e.content_hash&&f.assessment_id===item.assessment_id&&f.source==="INTERNAL_SIMULATION").at(-1);
  if(!f)pending++;else if(f.label==="USEFUL")useful++;else if(f.label==="NOT_USEFUL")not_useful++;else unknown++;
 }
 const corrections=m.corrections.filter(c=>latest.has(c.digest_id)),corrected=new Set(corrections.map(c=>c.digest_id));
 const assessed=useful+not_useful;
 return {mode:state.mode,delivery_count:latest.size,exported_versions:versions.size,correction_events:corrections.length,corrected_deliveries:corrected.size,correction_rate:latest.size?corrected.size/latest.size:null,
 active_delivery_seconds:deliverySessions.length?seconds("DELIVERY"):null,onboarding_seconds:closed.some(s=>s.phase==="ONBOARDING")?seconds("ONBOARDING"):null,
 timed_client_days:clientDays.size,active_seconds_per_client_day:clientDays.size?seconds("DELIVERY")/clientDays.size:null,open_timers:sessions.filter(s=>!s.ended_at).length,
 internal_feedback:{useful,not_useful,unknown,pending,final_items:useful+not_useful+unknown+pending,useful_share_assessed:assessed?useful/assessed:null},
 customer_usefulness:{status:"NOT_MEASURED",useful:null,precision:null},
 target_human_seconds_per_client_day:600,human_time_target_status:deliverySessions.length?"REQUIRES_REAL_PILOT":"NOT_MEASURED"};
}
