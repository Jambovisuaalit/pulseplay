import OpsWorkspace from "./workspace";
import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import { SESSION_COOKIE, verifySession } from "@/lib/session";
export const dynamic="force-dynamic";
export default async function OpsPage(){
 if(!(await verifySession((await cookies()).get(SESSION_COOKIE)?.value)))redirect("/login");
 return <OpsWorkspace/>;
}
