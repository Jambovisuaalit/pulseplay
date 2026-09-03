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

## 100-notice validation

```text
data/validation/hilma_100_luokiteltavaksi.csv
```

Manual labels:

- Relevantti
- Mahdollinen
- Epärelevantti

After labeling:

```bash
python workers/score_validation.py
```

Primary gate:

- 100 manually labeled notices
- top-30 precision >= 80%
- fabricated hard requirements = 0

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
