# TenderPulse MVP

TenderPulse turns Hilma procurement notices into a decision-support feed for Finnish B2B suppliers.

## Current architecture

```text
Hilma AVP REST API
  ↓
workers/fetch_hilma.py
  ↓
data/hilma_raw.json + /tmp/full_notices + /tmp/attachments
  ↓
workers/extract_pdfs.py
  ↓
data/attachment_texts.json
  ↓
100-notice manual ground truth
  ↓
LLM extraction layer (after relevance validation)
  ↓
data/hilma_analysoitu.json
  ↓
Company profile + deterministic Hard Gate Engine
  ↓
Next.js dashboard
  ↓
Vercel
```

## Key data rules

- `null` means the requirement/value was not found or has not been verified.
- `0` means an actual verified numeric zero. Never use zero as a missing-value placeholder.
- Mandatory requirements must have source evidence.
- The source analysis GO/NO-GO and company-profile fit are shown separately.
- Unknown hard gates produce `CONDITIONAL_GO`, not an invented PASS.

## Company profile

Active profile:

```text
data/company_profile.json
```

Schema:

```text
schemas/company_profile.schema.json
```

Set `profile_status` to `ACTIVE` only after the customer's turnover, operating regions, capabilities, certifications, response time and financial-guarantee ability have been verified.

## Hilma ingest

TenderPulse uses the official Hilma AVP read API. A subscription key is required in:

```text
HILMA_API_KEY
```

GitHub Actions expects it as a repository secret with the same name.

Run locally:

```bash
export HILMA_API_KEY="..."
python workers/fetch_hilma.py
python workers/extract_pdfs.py
python workers/build_validation_set.py
```

The daily GitHub Action runs the same path and uploads artifacts. Hilma's search index does not contain the complete tender documentation, so the worker also attempts to retrieve the full eForms notice and follows document URLs where possible. External tender portals may still require a separate document-fetching integration.

## 100-notice validation — blinded frozen source, 19.10.2026

```text
data/validation/snapshot_2026-10-19/hilma_raw.json
data/validation/snapshot_2026-10-19/validation/hilma_collection_audit.json
data/validation/independent_100/blind_review.csv
data/validation/independent_100/predictions.csv
data/validation/independent_100/gold_labels.csv
```

Source: GitHub Actions artifact 12155822339, 100 unique official Hilma search-index
records captured 2026-10-19 00:12 UTC by a previously executed one-call
collector. No additional Hilma API calls were used here. Search metadata is not
equivalent to full tender annexes.

`blind_review.csv` contains source metadata only. An independent human reviewer
checks the original source and separately fills `gold_labels.csv`: reviewer ID,
review time, label, rationale, cited evidence, and `source_checked=YES`.
Predictions are held in `predictions.csv`, never used as gold truth.

Manual labels:

- Relevantti
- Mahdollinen
- Epärelevantti

Build and assess:

```bash
python workers/build_validation_set.py
python workers/score_validation.py
python -B -m unittest discover -s tests -p 'test_*.py' -v
node --test tests/*.test.mjs
```

Primary gate:

- 100 independently source-reviewed decisive labels
- top-30 precision >= 80%
- positive-prediction precision >= 80%; report false positives, false negatives and unreviewed
- fabricated hard requirements = 0

The 100 rows are sampled uniformly, not by scoring. The top-30 is frozen before
any gold join. If even one item is unreviewed or only conditionally classified,
the complete precision gate is `NOT MEASURED`. Rebuilding preserves gold rows.

## Release safety rules

- A past deadline is `EXPIRED` even if the archived analysis says GO.
- A date-only deadline on the current day, missing timezone, or invalid date
  is `UNKNOWN`; it is not assumed open.
- A hard gate requires a nonempty original requirement quote *and* separately
  recorded evidence confirming the corresponding company-profile field.
- Annex review is `UNKNOWN` by default. `COMPLETE` with a documented audit is
  required before the delivery recommendation can become GO.
- These controls reduce false claims; they do **not** verify that evidence text
  is authentic. Independent source checks remain obligatory.

Do not wire automatic LLM publishing before this gate passes.

## Hard Gate Engine

Two implementations use the same deterministic policy:

- UI: `lib/hardGate.ts`
- pipeline: `workers/hard_gate_engine.py`

Decision policy:

```text
any FAIL    -> NO-GO
any UNKNOWN -> CONDITIONAL_GO
all PASS    -> GO
```

## Dashboard

The dashboard provides:

- deadline
- source / original notice link
- buyer and turnover filters
- source-analysis GO/NO-GO
- company-profile fit
- deterministic hard-gate checks
- mandatory requirements and evidence
- contract risks and evidence

## Deployment

The Next.js interface runs on Vercel. Python ingest/OCR remains in GitHub Actions.

Current production URL:

```text
https://tenderpulse-neon.vercel.app
```

## Next commercial gate

After the 100-notice validation:

1. configure three real company profiles
2. run a 14-day design-partner pilot
3. measure time saved, missed-opportunity recovery and GO/NO-GO accuracy
4. only then decide whether to build tender-drafting automation


<!-- deploy-trigger: 2026-09-03 TenderPulse production sync -->
