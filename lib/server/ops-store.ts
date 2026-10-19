import { promises as fs } from "node:fs";
import path from "node:path";
import { emptyState } from "../domain/model.ts";
import type { WorkflowState } from "../domain/model.ts";
import { WorkflowError } from "../domain/validation.ts";
function location() {
 if(process.env.NODE_ENV==="production"||process.env.TP_OPS_LOCAL_ENABLED!=="true")throw new WorkflowError("Tuotantotyötila odottaa erillisen tietokannan ja Supabase-kirjautumisen kytkentää. Paikallinen simulaatio: TP_OPS_LOCAL_ENABLED=true ja npm run dev.",503);
 return path.join(process.env.TP_OPS_LOCAL_DIRECTORY?path.resolve(process.env.TP_OPS_LOCAL_DIRECTORY):path.join(process.cwd(),".local"),"ops-state.json");
}
export async function readState():Promise<WorkflowState> {
 const file=location();try{return JSON.parse(await fs.readFile(file,"utf8"));}catch(e){if((e as NodeJS.ErrnoException).code==="ENOENT")return emptyState();throw e;}
}
export async function transaction<T>(run:(s:WorkflowState)=>Promise<T>|T):Promise<T> {
 const file=location();await fs.mkdir(path.dirname(file),{recursive:true,mode:0o700});
 let lock;try{lock=await fs.open(file+".lock","wx",0o600);}catch{throw new WorkflowError("Työtila on lukittu. Yritä uudelleen.",409);}
 const temporary=file+".tmp";
 try{
  const state=await readState(),result=await run(state);
  const handle=await fs.open(temporary,"w",0o600);try{await handle.writeFile(JSON.stringify(state));await handle.sync();}finally{await handle.close();}
  await fs.rename(temporary,file);return result;
 } finally {await fs.rm(temporary,{force:true});await lock.close();await fs.rm(file+".lock",{force:true});}
}
