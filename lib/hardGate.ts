import type { TenderHardGate } from "@/types/tender";

export interface CompanyProfile {
  profile_status: "UNCONFIGURED" | "ACTIVE";
  company_name: string | null;
  turnover_eur: number | null;
  regions: string[];
  capabilities: string[];
  certifications: string[];
  response_time_hours: number | null;
  can_provide_financial_guarantee: boolean | null;
}

export type GateStatus = "PASS" | "FAIL" | "UNKNOWN";

export interface GateResult {
  id: string;
  label: string;
  status: GateStatus;
  reason: string;
}

const normalize = (value: string) => value.trim().toLowerCase();

export function evaluateHardGates(
  gates: TenderHardGate[] = [],
  profile: CompanyProfile,
): { decision: "GO" | "CONDITIONAL_GO" | "NO-GO"; results: GateResult[] } {
  if (profile.profile_status !== "ACTIVE") {
    return {
      decision: "CONDITIONAL_GO",
      results: gates.map((gate) => ({
        id: gate.id,
        label: gate.label,
        status: "UNKNOWN",
        reason: "Yritysprofiilia ei ole vielä konfiguroitu.",
      })),
    };
  }

  const capabilities = new Set(profile.capabilities.map(normalize));
  const certifications = new Set(profile.certifications.map(normalize));
  const regions = new Set(profile.regions.map(normalize));

  const results: GateResult[] = gates.map((gate) => {
    switch (gate.type) {
      case "turnover_min": {
        if (typeof gate.required_value !== "number" || profile.turnover_eur == null) {
          return { id: gate.id, label: gate.label, status: "UNKNOWN", reason: "Liikevaihtotieto puuttuu." };
        }
        const pass = profile.turnover_eur >= gate.required_value;
        return {
          id: gate.id,
          label: gate.label,
          status: pass ? "PASS" : "FAIL",
          reason: pass
            ? `Liikevaihto ${profile.turnover_eur} € täyttää rajan ${gate.required_value} €.`
            : `Liikevaihto ${profile.turnover_eur} € alittaa rajan ${gate.required_value} €.`,
        };
      }

      case "capability": {
        if (typeof gate.required_value !== "string") {
          return { id: gate.id, label: gate.label, status: "UNKNOWN", reason: "Vaatimusarvo puuttuu." };
        }
        const pass = capabilities.has(normalize(gate.required_value));
        return { id: gate.id, label: gate.label, status: pass ? "PASS" : "FAIL", reason: pass ? "Kyvykkyys löytyy profiilista." : "Kyvykkyys puuttuu profiilista." };
      }

      case "capability_any": {
        if (!Array.isArray(gate.required_value) || gate.required_value.length === 0) {
          return { id: gate.id, label: gate.label, status: "UNKNOWN", reason: "Vaatimusarvot puuttuvat." };
        }
        const pass = gate.required_value.some((value) => capabilities.has(normalize(String(value))));
        return { id: gate.id, label: gate.label, status: pass ? "PASS" : "FAIL", reason: pass ? "Vähintään yksi vaadituista kyvykkyyksistä löytyy." : "Yksikään vaadituista kyvykkyyksistä ei löydy." };
      }

      case "capability_all": {
        if (!Array.isArray(gate.required_value) || gate.required_value.length === 0) {
          return { id: gate.id, label: gate.label, status: "UNKNOWN", reason: "Vaatimusarvot puuttuvat." };
        }
        const missing = gate.required_value.filter((value) => !capabilities.has(normalize(String(value))));
        return { id: gate.id, label: gate.label, status: missing.length ? "FAIL" : "PASS", reason: missing.length ? `Puuttuvat: ${missing.join(", ")}.` : "Kaikki vaaditut kyvykkyydet löytyvät." };
      }

      case "certification": {
        if (typeof gate.required_value !== "string") {
          return { id: gate.id, label: gate.label, status: "UNKNOWN", reason: "Pätevyysarvo puuttuu." };
        }
        const pass = certifications.has(normalize(gate.required_value));
        return { id: gate.id, label: gate.label, status: pass ? "PASS" : "FAIL", reason: pass ? "Pätevyys löytyy profiilista." : "Pätevyys puuttuu profiilista." };
      }

      case "region": {
        if (typeof gate.required_value !== "string") {
          return { id: gate.id, label: gate.label, status: "UNKNOWN", reason: "Aluearvo puuttuu." };
        }
        const pass = regions.has(normalize(gate.required_value));
        return { id: gate.id, label: gate.label, status: pass ? "PASS" : "FAIL", reason: pass ? "Toiminta-alue täsmää." : "Toiminta-alue ei täsmää." };
      }

      case "response_time_max_hours": {
        if (typeof gate.required_value !== "number" || profile.response_time_hours == null) {
          return { id: gate.id, label: gate.label, status: "UNKNOWN", reason: "Vasteaikatieto puuttuu." };
        }
        const pass = profile.response_time_hours <= gate.required_value;
        return { id: gate.id, label: gate.label, status: pass ? "PASS" : "FAIL", reason: pass ? "Vasteaikavaatimus täyttyy." : "Vasteaikavaatimus ei täyty." };
      }

      case "financial_guarantee": {
        if (profile.can_provide_financial_guarantee == null) {
          return { id: gate.id, label: gate.label, status: "UNKNOWN", reason: "Vakuuskykyä ei ole vahvistettu." };
        }
        const required = gate.required_value !== false;
        const pass = !required || profile.can_provide_financial_guarantee;
        return { id: gate.id, label: gate.label, status: pass ? "PASS" : "FAIL", reason: pass ? "Vakuusvaatimus voidaan täyttää." : "Vakuusvaatimusta ei voida täyttää." };
      }
    }
  });

  if (results.some((result) => result.status === "FAIL")) {
    return { decision: "NO-GO", results };
  }
  if (results.length === 0 || results.some((result) => result.status === "UNKNOWN")) {
    return { decision: "CONDITIONAL_GO", results };
  }
  return { decision: "GO", results };
}
