"""Fail-closed provenance gate for public procurement evaluation candidates.

A decision or indexed document listing cannot substitute for a complete
source tender. This module never assigns a positive gold label automatically.
"""
from __future__ import annotations
import json
from pathlib import Path

REQUIRED_DOC_TYPES = {"tender_request", "eligibility_terms", "pricing_scope", "annex_index"}

def assess(candidate: dict) -> dict:
    docs = candidate.get("documents") or []
    verified = [d for d in docs if d.get("access") == "VERIFIED_FULL_TEXT"
                and d.get("source_url") and d.get("sha256") and d.get("retrieved_at")]
    kinds = {d.get("type") for d in verified}
    missing = sorted(REQUIRED_DOC_TYPES - kinds)
    in_region = candidate.get("region_icp") == "IN"
    in_scope = candidate.get("scope_icp") == "MATCH"
    single_value = candidate.get("individual_contract_value_verified") is True
    eligibility = candidate.get("eligibility_terms_reviewed") is True
    open_or_historical = candidate.get("evaluation_use") in {"HISTORICAL", "CURRENT"}
    ready = not missing and in_region and in_scope and single_value and eligibility and open_or_historical
    return {
        "candidate_id": candidate.get("candidate_id"),
        "document_coverage": "COMPLETE" if not missing else "PARTIAL_OR_MISSING",
        "missing_verified_document_types": missing,
        "icp_region_pass": in_region, "icp_scope_pass": in_scope,
        "individual_contract_value_verified": single_value,
        "eligibility_terms_reviewed": eligibility,
        "source_review_ready": ready,
        "gold_label": "UNREVIEWED",  # Independent source reviewer must label it.
        "positive_gold_count_increment": 0,
    }

def evaluate_registry(path: Path) -> dict:
    records = json.loads(path.read_text(encoding="utf-8"))["candidates"]
    decisions = [assess(r) for r in records]
    return {"total": len(decisions),
            "source_review_ready": sum(x["source_review_ready"] for x in decisions),
            "gold_positive": 0,
            "decisions": decisions}

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--registry", type=Path, required=True)
    args = p.parse_args()
    print(json.dumps(evaluate_registry(args.registry), ensure_ascii=False, indent=2))
