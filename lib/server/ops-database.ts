import { emptyState } from "../domain/model.ts";
import type { WorkflowState } from "../domain/model.ts";
import { WorkflowError } from "../domain/validation.ts";
import { isDeepStrictEqual } from "node:util";

// Server route only. The browser never receives the database key or raw endpoint.
type Config = { origin: string; key: string; workspace: string };
type Stored = { state: WorkflowState; version: number | null };
const unavailable = () => new WorkflowError("Pysyvä työtila ei ole käytettävissä. Tietoja ei tallennettu.", 503);
const conflict = () => new WorkflowError("Työtila muuttui. Lataa uusi tila ennen uutta yritystä.", 409);

export function databaseConfig(env: NodeJS.ProcessEnv = process.env): Config {
  const origin = env.TP_SUPABASE_URL || "";
  const key = env.TP_SUPABASE_SECRET_KEY || "";
  const workspace = env.TP_OPS_WORKSPACE || "";
  // Explicit project + workspace, never inferred from another business's settings.
  if (!/^https:\/\/[a-z0-9]{20}\.supabase\.co$/.test(origin) ||
      !/^sb_secret_[A-Za-z0-9_-]+$/.test(key) ||
      !/^[a-z0-9][a-z0-9_-]{2,79}$/.test(workspace)) throw unavailable();
  return { origin, key, workspace };
}

function stateValue(value: unknown): WorkflowState {
  if (!value || typeof value !== "object") throw unavailable();
  const state = value as WorkflowState;
  if (state.schema_version !== 1 || state.mode !== "SIMULATION" ||
      !Number.isSafeInteger(state.revision) || state.revision < 0 ||
      ![state.clients, state.profiles, state.notices, state.assessments, state.digests, state.events].every(Array.isArray)) throw unavailable();
  return state;
}

export function createDatabaseStore(config: Config, fetcher: typeof fetch = fetch) {
  const base = `${config.origin}/rest/v1/urakkaluotsi_ops_state`;
  async function request(url: string, method: string, body?: unknown): Promise<unknown[]> {
    let response: Response;
    try {
      response = await fetcher(url, {
        method, redirect: "error", cache: "no-store", signal: AbortSignal.timeout(10_000),
        headers: { apikey: config.key, "Content-Type": "application/json", Prefer: "return=representation" },
        ...(body === undefined ? {} : { body: JSON.stringify(body) }),
      });
    } catch { throw unavailable(); }
    // An insert conflict means another instance created this workspace first.
    if (method === "POST" && response.status === 409) throw conflict();
    if (!response.ok) throw unavailable();
    let rows: unknown;
    try { rows = await response.json(); } catch { throw unavailable(); }
    if (!Array.isArray(rows) || rows.length > 1) throw unavailable();
    return rows;
  }
  async function load(): Promise<Stored> {
    const rows = await request(`${base}?workspace_id=eq.${config.workspace}&select=state,storage_version`, "GET");
    if (!rows.length) return { state: emptyState(), version: null };
    const row = rows[0] as { state: unknown; storage_version: number };
    if (!row || !Number.isSafeInteger(row.storage_version) || row.storage_version < 1) throw unavailable();
    return { state: stateValue(row.state), version: row.storage_version };
  }
  return {
    async readState(): Promise<WorkflowState> { return (await load()).state; },
    async transaction<T>(run: (state: WorkflowState) => Promise<T> | T): Promise<T> {
      const { state, version } = await load();
      const result = await run(state);
      stateValue(state);
      if (Buffer.byteLength(JSON.stringify(state)) > 5_000_000) throw new WorkflowError("Työtila ylittää tallennusrajan.", 413);
      const next = (version ?? 0) + 1;
      if (!Number.isSafeInteger(next)) throw unavailable();
      const rows = version === null
        ? await request(base, "POST", { workspace_id: config.workspace, storage_version: next, state })
        : await request(`${base}?workspace_id=eq.${config.workspace}&storage_version=eq.${version}`, "PATCH", { storage_version: next, state });
      // Compare-and-swap is atomic in Postgres. Do not retry a command or export
      // after an uncertain write: the operator must reload the committed state.
      if (!rows.length) throw conflict();
      const saved = rows[0] as { state: unknown; storage_version: number };
      if (!saved || saved.storage_version !== next || !isDeepStrictEqual(stateValue(saved.state), state)) throw unavailable();
      return result;
    },
  };
}
