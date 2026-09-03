export type GoNoGo = "GO" | "NO-GO" | "CONDITIONAL_GO" | string;

export type HardGateType =
  | "turnover_min"
  | "capability"
  | "capability_any"
  | "capability_all"
  | "certification"
  | "region"
  | "response_time_max_hours"
  | "financial_guarantee";

export interface TenderHardGate {
  id: string;
  type: HardGateType;
  label: string;
  required_value: string | string[] | number | boolean | null;
  evidence?: string | null;
}

export interface Tender {
  id?: string | number;
  notice_id?: string | number;
  title?: string;
  hankinta?: string;
  ostaja?: string;
  buyer?: string;
  organisation?: { name?: string } | string;
  tiivistelma?: string;
  pakolliset_vaatimukset?: string[];
  vaatimukset_evidenssi?: string;
  liikevaihto_vaatimus_eur?: number | null;
  liikevaihto_evidenssi?: string;
  sopimusriskit?: string[];
  riskit_evidenssi?: string;
  vasteaika_vaatimus?: string | null;
  go_no_go_suositus?: GoNoGo;
  perustelu?: string;
  publishedAt?: string;
  published_at?: string;
  deadline?: string | null;
  hilma_url?: string | null;
  source_url?: string | null;
  hard_gates?: TenderHardGate[];
}
