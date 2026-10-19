import test from "node:test";
import assert from "node:assert/strict";
import fs from "node:fs";
import { deadlineStatus, safeSourceDecision } from "../lib/deliverySafety.ts";
import { evaluateHardGates } from "../lib/hardGate.ts";

const now = new Date("2026-10-19T12:00:00Z");
const active = { profile_status: "ACTIVE", company_name: "Test", turnover_eur: null,
  capabilities: ["maalaus"], certifications: [], regions: [], response_time_hours: null,
  can_provide_financial_guarantee: null };
const gate = { id: "g", type: "capability", label: "Maalaus", required_value: "maalaus", evidence: "Source excerpt" };

test("stale, date-only today and timezone deadlines are safe", () => {
  assert.equal(deadlineStatus("2026-10-18", now), "EXPIRED");
  assert.equal(deadlineStatus("2026-10-19", now), "UNKNOWN");
  assert.equal(deadlineStatus("2026-10-20", now), "OPEN");
  assert.equal(deadlineStatus("2026-10-19T11:00:00Z", now), "EXPIRED");
  assert.equal(deadlineStatus("2026-10-19T13:00:00Z", now), "OPEN");
  assert.equal(deadlineStatus("2026-10-19T14:00:00", now), "UNKNOWN");
});

test("source GO cannot override an expired deadline or missing annexes", () => {
  const item = { deadline: "2026-10-18", go_no_go_suositus: "GO" };
  assert.equal(safeSourceDecision(item, now).decision, "EXPIRED");
  item.deadline = "2026-11-01T12:00:00+02:00";
  assert.equal(safeSourceDecision(item, now).decision, "CONDITIONAL_GO");
  item.attachment_review_status = "COMPLETE";
  assert.equal(safeSourceDecision(item, now).decision, "CONDITIONAL_GO");
  item.attachment_review_evidence = "Checked all annexes";
  assert.equal(safeSourceDecision(item, now).decision, "GO");
});

test("raw search metadata stays NOT_EVALUATED", () => {
  assert.equal(safeSourceDecision({ deadline: "2026-11-01T12:00:00+02:00" }, now).decision, "NOT_EVALUATED");
});

test("PASS requires source and separately verified company evidence", () => {
  assert.equal(evaluateHardGates([gate], active).results[0].status, "UNKNOWN");
  const verified = { ...active, verification_evidence: { capabilities: "Signed and checked" } };
  assert.equal(evaluateHardGates([gate], verified).results[0].status, "PASS");
  assert.equal(evaluateHardGates([{ ...gate, evidence: "" }], verified).results[0].status, "UNKNOWN");
  assert.equal(evaluateHardGates([{ ...gate, required_value: "sähkötyöt" }], verified).results[0].status, "FAIL");
});

test("the eight historical repository tenders are all expired, never GO", () => {
  const old = JSON.parse(fs.readFileSync(new URL("../data/hilma_analysoitu.json", import.meta.url), "utf8"));
  assert.equal(old.length, 8);
  assert.ok(old.every(item => safeSourceDecision(item, now).decision === "EXPIRED"));
});
