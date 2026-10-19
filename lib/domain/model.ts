import type { Measurements } from "./metrics.ts";
export type Verification = "UNKNOWN" | "INFERRED" | "CONFIRMED";
export interface ProfileFact {
 key: string; value: string | number | boolean | null; verification: Verification;
 source: string | null; verified_at: string | null;
}
export interface ProfileVersion {
 id: string; client_id: string; version: number; services: string[]; regions: string[];
 facts: ProfileFact[]; created_at: string;
}
export interface Client { id: string; name: string; delivery_email: string; }
export interface NoticeVersion {
 id: string; notice_id: string; version: number; source_hash: string; title: string; buyer: string;
 source_url: string; deadline: string | null; checked_at: string; cancelled: boolean | null;
 evidence: string; missing: string[]; created_at: string;
}
export interface Assessment {
 id: string; client_id: string; profile_version_id: string; notice_version_id: string;
 row_version: number; summary: string; next_action: string; missing: string[];
 coverage: "NONE" | "PARTIAL" | "COMPLETE"; reviewed: boolean;
}
export interface DeliveryItem {
 assessment_id: string; notice_version_id: string; source_hash: string; title: string; buyer: string;
 source_url: string; evidence: string; deadline: string; checked_at: string; summary: string;
 missing: string[]; next_action: string;
}
export interface DeliverySnapshot {
 schema_version: 1; mode: "SIMULATION" | "REAL"; client: Client; profile: ProfileVersion;
 template_version: "urakkaluotsi-1.1"; items: DeliveryItem[];
}
export interface Digest {
 id: string; client_id: string; assessment_ids: string[]; row_version: number;
 status: "DRAFT" | "QA_BLOCKED" | "APPROVED" | "EXPORTED" | "NEEDS_REVIEW";
 approved_snapshot: DeliverySnapshot | null; approved_hash: string | null;
 approved_at: string | null; approved_by: string | null;
}
export interface DeliveryEvent {
 id: string; digest_id: string; content_hash: string; type: "APPROVED" | "EXPORTED" | "SENT_RECORDED";
 snapshot: DeliverySnapshot; actor: string; occurred_at: string; reference: string;
}
export interface WorkflowState {
 measurements?: Measurements; schema_version: 1; mode: "SIMULATION"; revision: number; clients: Client[]; profiles: ProfileVersion[];
 notices: NoticeVersion[]; assessments: Assessment[]; digests: Digest[]; events: DeliveryEvent[];
}
export const emptyState = (): WorkflowState => ({schema_version:1,mode:"SIMULATION",revision:0,clients:[],profiles:[],notices:[],assessments:[],digests:[],events:[]});
