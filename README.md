# TenderPulse MVP

TenderPulse turns Hilma procurement notices into a decision-support feed for Finnish B2B suppliers.

## Architecture

```text
Hilma
  ↓
workers/fetch_hilma.py
  ↓
data/hilma_raw.json + /tmp/attachments
  ↓
workers/extract_pdfs.py
  ↓
data/attachment_texts.json
  ↓
LLM analysis layer (next step)
  ↓
data/hilma_analysoitu.json
  ↓
Next.js dashboard
  ↓
Vercel
```

## Repository structure

```text
app/
  globals.css
  layout.tsx
  page.tsx

components/
  TenderDashboard.tsx

data/
  hilma_analysoitu.json

schemas/
  tender_analysis.schema.json

types/
  tender.ts

workers/
  fetch_hilma.py
  extract_pdfs.py

.github/workflows/
  tenderpulse-ingest.yml

.env.example
requirements-worker.txt
package.json
```

## Dashboard

The dashboard provides:

- KPI cards for new notices and GO recommendations
- buyer filter
- maximum revenue-requirement filter
- GO / NO-GO filter
- clickable tender rows
- mandatory requirements highlighted in green
- contract risks highlighted in red

## Local dashboard

```bash
npm install
npm run dev
```

Open http://localhost:3000.

## Python ingest

System dependency for OCR:

```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-fin
```

Install Python dependencies:

```bash
python -m pip install -r requirements-worker.txt
```

Run:

```bash
python workers/fetch_hilma.py
python workers/extract_pdfs.py
```

The manual GitHub Action `TenderPulse ingest` runs the same ingest/OCR stages and uploads the generated JSON files as an artifact.

## Data contract

The dashboard reads:

```text
data/hilma_analysoitu.json
```

Analysis items should conform to:

```text
schemas/tender_analysis.schema.json
```

Do not infer mandatory requirements that are not supported by the source material. Unknown requirements should remain missing/null instead of being invented.

## Vercel

Recommended deployment target: the Next.js dashboard only.

The PDF/OCR ingest should remain in GitHub Actions or another worker environment rather than running during a Vercel page request.

### Production flow

1. ingest Hilma data
2. extract PDF/OCR text
3. analyze and validate JSON
4. update `data/hilma_analysoitu.json`
5. commit/push
6. Vercel deploys the dashboard

## Current MVP gate

Before automation is expanded:

- manually label 100 notices
- target ≥80% precision in the top 30
- require zero fabricated hard-gate requirements
- target <5 min human verification time per relevant tender
