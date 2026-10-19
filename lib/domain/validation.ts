import type { ProfileFact } from "./model.ts";
export class WorkflowError extends Error {
 status: number;
 constructor(message: string, status = 400) { super(message); this.status=status; }
}
export function text(value: unknown, name: string, max = 2000): string {
 if (typeof value !== "string" || !value.trim() || value.length > max) throw new WorkflowError(`${name}: virheellinen arvo`);
 return value.trim();
}
export function timestamp(value: unknown, name: string): string {
 const result = text(value,name,64);
 if (!/T.*(Z|[+-]\d{2}:\d{2})$/.test(result) || !Number.isFinite(Date.parse(result))) throw new WorkflowError(`${name}: aikavyöhyke puuttuu tai aika on virheellinen`);
 return new Date(result).toISOString();
}
export function https(value: unknown): string {
 const result=text(value,"Lähde",2000); let url: URL;
 try {url=new URL(result);} catch {throw new WorkflowError("Lähde: virheellinen URL");}
 if(url.protocol!=="https:" || url.username || url.password) throw new WorkflowError("Lähde: HTTPS vaaditaan");
 return result;
}
export function strings(value: unknown, name: string): string[] {
 if(!Array.isArray(value) || value.length>100) throw new WorkflowError(`${name}: lista vaaditaan`);
 return value.map(v=>text(v,name,500));
}
export function profileFacts(value: unknown): ProfileFact[] {
 if(!Array.isArray(value)||value.length>100) throw new WorkflowError("Profiilitiedot: lista vaaditaan");
 const keys=new Set<string>();
 return value.map(f=>{
  if(!f||typeof f!=="object") throw new WorkflowError("Profiilitieto: olio vaaditaan");
  const key=text(f.key,"Avain",100);if(keys.has(key)) throw new WorkflowError("Profiilitiedon avain toistuu");keys.add(key);
  if(!["UNKNOWN","INFERRED","CONFIRMED"].includes(f.verification)) throw new WorkflowError("Vahvistustila puuttuu");
  if(f.verification==="UNKNOWN") {
   if(f.value!==null||f.source!==null||f.verified_at!==null) throw new WorkflowError("Tuntematon tieto ei saa sisältää vahvistusta");
  } else {
   if(!["string","boolean","number"].includes(typeof f.value)||typeof f.value==="number"&&!Number.isFinite(f.value)) throw new WorkflowError("Profiilitiedon arvo virheellinen");
   text(f.source,"Vahvistuksen lähde",1000);
   if(f.verification==="CONFIRMED") timestamp(f.verified_at,"Vahvistusaika");
   else if(f.verified_at!==null) throw new WorkflowError("Oletus ei saa sisältää vahvistusaikaa");
  }
  return {key,value:f.value,verification:f.verification,source:f.source,verified_at:f.verified_at};
 });
}
