export type GoNoGo = "GO" | "NO-GO" | "CONDITIONAL_GO" | string;

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
  liikevaihto_vaatimus_eur?: number | null;
  sopimusriskit?: string[];
  vasteaika_vaatimus?: string | null;
  go_no_go_suositus?: GoNoGo;
  perustelu?: string;
  publishedAt?: string;
  published_at?: string;
  deadline?: string | null;
}
