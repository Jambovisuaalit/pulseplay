"""Freeze real, previously unseen Hilma metadata, without reading model scores.

Source is an already archived GitHub Actions ZIP, not a live Hilma request.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import zipfile
from pathlib import Path

from prepare_independent_review import title_fingerprint

OLD = Path("data/validation/snapshot_2026-10-19/hilma_raw.json")
ARCHIVE = Path("/workspace/scratch/609a16a83065/pr4_holdout_candidate.zip")
OUT = Path("data/validation/holdout_52_2026-10-19")
ARCHIVE_ARTIFACT_ID = 12155344561


def prepare(old: dict, new: dict) -> tuple[dict, list[dict]]:
    old_notices = old["notices"]
    new_notices = new["notices"]
    if len(old_notices) != 100 or len(new_notices) != 152:
        raise ValueError("Unexpected source counts; review archive provenance")
    old_ids = {str(n["id"]) for n in old_notices}
    old_procs = {str(n["procedure_id"]) for n in old_notices if n.get("procedure_id")}
    old_titles = {title_fingerprint(n["title"]) for n in old_notices if n.get("title")}
    holdout = [n for n in new_notices if str(n["id"]) not in old_ids]
    ids = [str(n["id"]) for n in holdout]
    if len(holdout) != 52 or len(set(ids)) != 52:
        raise ValueError("Holdout count or unique ID property changed")
    reused_procs = [n["id"] for n in holdout if n.get("procedure_id") and str(n["procedure_id"]) in old_procs]
    reused_titles = [n["id"] for n in holdout if n.get("title") and title_fingerprint(n["title"]) in old_titles]
    if reused_procs or reused_titles:
        raise ValueError(f"Cross-set duplicate procurement: {reused_procs}, {reused_titles}")
    return {
        "retrievedAt": new["retrievedAt"],
        "notices": sorted(holdout, key=lambda n: str(n["id"])),
    }, holdout


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--old", type=Path, default=OLD)
    parser.add_argument("--archive", type=Path, default=ARCHIVE)
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args()
    old_bytes = args.old.read_bytes()
    archive_bytes = args.archive.read_bytes()
    with zipfile.ZipFile(args.archive) as archive:
        source_bytes = archive.read("hilma_raw.json")
    old = json.loads(old_bytes)
    new = json.loads(source_bytes)
    payload, records = prepare(old, new)
    args.output.mkdir(parents=True, exist_ok=True)
    raw_bytes = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    (args.output / "holdout_raw.json").write_bytes(raw_bytes)
    manifest = {
        "source_kind": "previously_archived_github_actions_hilma_search_metadata_only",
        "source_artifact_id": ARCHIVE_ARTIFACT_ID,
        "source_archive_sha256": hashlib.sha256(archive_bytes).hexdigest(),
        "source_hilma_json_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "old_100_sha256": hashlib.sha256(old_bytes).hexdigest(),
        "holdout_raw_sha256": hashlib.sha256(raw_bytes).hexdigest(),
        "retrieved_at": payload["retrievedAt"],
        "old_source_count": len(old["notices"]),
        "candidate_source_count": len(new["notices"]),
        "holdout_count": len(records),
        "id_overlap": 0,
        "procedure_id_overlap": 0,
        "normalised_title_overlap": 0,
        "missing_procedure_count": sum(not n.get("procedure_id") for n in records),
        "id_selection": "all distinct IDs after cross-procedure and normalised-title disjointness checks; sorted",
        "temporal_independence": "NO – source retrieved ~1 minute after old snapshot; same broad search period",
        "independent_gold": "NONE – no external source adjudicator or full annex review",
        "live_hilma_requests_in_this_step": 0,
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    fields = ["notice_id", "title", "organisation", "description", "deadline", "estimated_value", "procedure_id", "source_pointer"]
    with (args.output / "blind_source.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for n in payload["notices"]:
            writer.writerow({
                "notice_id": str(n["id"]), "title": n.get("title") or "",
                "organisation": n.get("organisation") or "", "description": n.get("description") or "",
                "deadline": n.get("deadline") or "", "estimated_value": n.get("estimated_value") if n.get("estimated_value") is not None else "",
                "procedure_id": n.get("procedure_id") or "",
                "source_pointer": f"holdout_raw.json#id={n['id']}",
            })
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
