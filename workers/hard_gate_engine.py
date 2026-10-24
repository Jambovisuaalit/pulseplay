from __future__ import annotations

import json
from pathlib import Path
from delivery_safety import delivery_decision

TENDERS_PATH = Path("data/hilma_analysoitu.json")
PROFILE_PATH = Path("data/company_profile.json")
OUTPUT_PATH = Path("data/profile_fit.json")


def norm(value: str) -> str:
    return value.strip().lower()


def evaluate_gate(gate: dict, profile: dict) -> dict:
    gate_type = gate["type"]
    required = gate.get("required_value")
    capabilities = {norm(v) for v in profile.get("capabilities", [])}
    certifications = {norm(v) for v in profile.get("certifications", [])}
    regions = {norm(v) for v in profile.get("regions", [])}

    status = "UNKNOWN"
    reason = "Tietoa ei voida arvioida."

    evidence_key = {
        "turnover_min": "turnover_eur",
        "capability": "capabilities",
        "capability_any": "capabilities",
        "capability_all": "capabilities",
        "certification": "certifications",
        "region": "regions",
        "response_time_max_hours": "response_time_hours",
        "financial_guarantee": "can_provide_financial_guarantee",
    }.get(gate_type)

    source_evidence = gate.get("evidence")
    company_evidence = (profile.get("verification_evidence") or {}).get(evidence_key)
    if not isinstance(source_evidence, str) or not source_evidence.strip():
        reason = "Pakollisen vaatimuksen lähde-evidenssi puuttuu."
    elif not isinstance(company_evidence, str) or not company_evidence.strip():
        reason = "Yritystiedon riippumaton vahvistus puuttuu."

    if profile.get("profile_status") != "ACTIVE":
        reason = "Yritysprofiilia ei ole konfiguroitu."
    elif not isinstance(source_evidence, str) or not source_evidence.strip():
        pass
    elif not isinstance(company_evidence, str) or not company_evidence.strip():
        pass
    elif gate_type == "turnover_min":
        turnover = profile.get("turnover_eur")
        if turnover is not None and isinstance(required, (int, float)):
            status = "PASS" if turnover >= required else "FAIL"
            reason = f"Liikevaihto {turnover} €, vaatimus {required} €."
    elif gate_type == "capability" and required is not None:
        status = "PASS" if norm(str(required)) in capabilities else "FAIL"
        reason = "Kyvykkyys löytyy." if status == "PASS" else "Kyvykkyys puuttuu."
    elif gate_type == "capability_any" and isinstance(required, list) and required:
        values = [norm(str(v)) for v in (required or [])]
        status = "PASS" if any(v in capabilities for v in values) else "FAIL"
        reason = "Vähintään yksi kyvykkyys löytyy." if status == "PASS" else "Vaadittu kyvykkyys puuttuu."
    elif gate_type == "capability_all" and isinstance(required, list) and required:
        values = [norm(str(v)) for v in (required or [])]
        missing = [v for v in values if v not in capabilities]
        status = "PASS" if not missing else "FAIL"
        reason = "Kaikki kyvykkyydet löytyvät." if not missing else "Puuttuvat: " + ", ".join(missing)
    elif gate_type == "certification" and required is not None:
        status = "PASS" if norm(str(required)) in certifications else "FAIL"
        reason = "Pätevyys löytyy." if status == "PASS" else "Pätevyys puuttuu."
    elif gate_type == "region" and required is not None:
        status = "PASS" if norm(str(required)) in regions else "FAIL"
        reason = "Toiminta-alue täsmää." if status == "PASS" else "Toiminta-alue ei täsmää."
    elif gate_type == "response_time_max_hours":
        actual = profile.get("response_time_hours")
        if actual is not None and isinstance(required, (int, float)):
            status = "PASS" if actual <= required else "FAIL"
            reason = f"Vaste {actual} h, vaatimus enintään {required} h."
    elif gate_type == "financial_guarantee":
        actual = profile.get("can_provide_financial_guarantee")
        if actual is not None:
            status = "PASS" if actual or required is False else "FAIL"
            reason = "Vakuus voidaan antaa." if status == "PASS" else "Vakuutta ei voida antaa."

    return {
        "id": gate.get("id"),
        "label": gate.get("label"),
        "status": status,
        "reason": reason,
    }


def evaluate_tender(tender: dict, profile: dict) -> dict:
    results = [
        evaluate_gate(gate, profile)
        for gate in tender.get("hard_gates", [])
    ]

    if any(item["status"] == "FAIL" for item in results):
        decision = "NO-GO"
    elif not results or any(item["status"] == "UNKNOWN" for item in results):
        decision = "CONDITIONAL_GO"
    else:
        decision = "GO"

    return {
        "id": tender.get("id"),
        "profile_decision": decision,
        "hard_gate_results": results,
        **delivery_decision(tender, decision),
    }


def main() -> None:
    tenders = json.loads(TENDERS_PATH.read_text(encoding="utf-8"))
    profile = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))

    output = {
        "company_name": profile.get("company_name"),
        "profile_status": profile.get("profile_status"),
        "results": [evaluate_tender(tender, profile) for tender in tenders],
    }

    OUTPUT_PATH.write_text(
        json.dumps(output, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Wrote {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
