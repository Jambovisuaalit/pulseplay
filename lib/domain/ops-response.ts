// Browser-safe response handling. Never display an upstream HTML page or parser error.
export function opsErrorMessage(error: unknown): string {
 if(error instanceof TypeError)return "Yhteys katkesi. Päivitä tila ennen uutta yritystä.";
 if(error instanceof SyntaxError)return "Syötteen muoto ei kelpaa. Tarkista kentät.";
 return error instanceof Error && error.message ? error.message : "Toiminto epäonnistui. Päivitä tila.";
}

export function checkOpsResponse(response: Response, fallback: string): void {
 if(response.redirected || response.type === "opaqueredirect" || [0,301,302,303,307,308,401].includes(response.status))
  throw new Error("Istunto on päättynyt. Kirjaudu uudelleen ja päivitä tila.");
 if(response.status === 403)throw new Error("Toimintoa ei sallittu. Päivitä sivu ja kirjaudu tarvittaessa uudelleen.");
 if(response.status === 409)throw new Error("Työtila muuttui toisessa istunnossa. Päivitä tila ennen uutta yritystä.");
 if(response.status >= 500)throw new Error("Tallennuksen tilaa ei voitu varmistaa. Päivitä tila ennen uutta yritystä.");
 if(!response.ok && !(response.headers.get("content-type") ?? "").includes("application/json"))throw new Error(fallback);
}

export async function opsJson<T>(response: Response, fallback: string): Promise<T> {
 checkOpsResponse(response,fallback);
 let value: unknown;
 try {value=await response.json();}catch{throw new Error(fallback);}
 if(!response.ok){
  const error=value && typeof value === "object" && "error" in value ? value.error : null;
  throw new Error(typeof error === "string" && error.length < 4000 ? error : fallback);
 }
 if(!value || typeof value !== "object" || !("revision" in value) || !Number.isSafeInteger(value.revision) || !("clients" in value) || !Array.isArray(value.clients))throw new Error(fallback);
 return value as T;
}
