# Material certificate document parsing (EN 10204)

Parse **metallic product inspection documents** (material certificates / mill test reports), especially those that follow **EN 10204**, so you can answer questions like:

- What heat / cast / cert number is this?
- What are chemistry and mechanical results?
- Do measured values meet Min/Max (or Req’t) limits on the certificate?

PDFs are messy: cover sheets, multi-language tables, and long NDT / metallography **appendices** after the primary certificate pages. This repo explores two Azure approaches and keeps the outputs comparable.

---

## Problem

| Challenge | Why it hurts |
|-----------|----------------|
| Spec vs result rows in tables | OCR markdown alone often cannot tell “414 Min” (limit) from “450” (actual). |
| Multi-page packs | Page 1 may be the cert; pages 2–20 may be PT/UT/hardness enclosures. |
| Mixed layouts | Howco / VDM / MELESI / Spanish mills use different table shapes. |
| Two useful product shapes | Humans need readable tables; systems need JSON fields. |

---

## Approach (two active pipelines)

```
raw-docs/*.pdf
       │
       ├──────────────────────────────┐
       ▼                              ▼
notebooks/01  Mistral Document AI          notebooks/02  Azure Content Understanding
       OCR + field annotation              prebuilt-layout
       │                              │
       ▼                              ▼
extraction-output/                extraction-output/
  mistral-ocr/   (.md)              cu-layout/   (raw API JSON)
  mistral-fields/ (.json)           cu-tables/   (parsed tables JSON)
                                    cu-reports/  (.html for humans)
```

| Notebook | Service | Best for | Output types | Current Status |
|----------|---------|----------|--------------|----------------|
| `notebooks/01-mistral-ocr-and-fields.ipynb` | Mistral Document AI on Azure AI Foundry | Cert type gate, OCR text, structured **field** JSON | `.md` + `.json` | **Not working** (Azure deployment not ready) |
| `notebooks/02-content-understanding-tables.ipynb` | Azure Content Understanding `prebuilt-layout` | **Tables** with headers / spec / result rows; HTML review | `.json` + `.html` | **Working** (live tested) |

> **Note on Notebook 01:**
> - **Execution status:** Does not work currently. When calling `process()`, the Mistral Document AI endpoint returns HTTP 400: `DeploymentError: The API deployment for the resource is not ready, please wait until provisioningState becomes Succeeded.` (the model deployment `mistral-document-ai-2505-1` in Azure AI Foundry is not in a succeeded provisioning state).
> - **Are outputs present in `extraction-output/`? YES.** Outputs from previous runs are already saved and committed under:
>   - `extraction-output/mistral-ocr/` (`.md` for all 3 sample PDFs)
>   - `extraction-output/mistral-fields/` (`.json` for all 3 sample PDFs)
>   You can inspect and consume these files without running the notebook.

**Use both when comparing methods.** Prefer **02** when the question is “does this heat pass Min/Max in the chemistry or tensile table?” Prefer **01** for free-text OCR and annotated field schemas.

Older experiments live under `archive/` — do **not** run them for day-to-day work.

---

## How Content Understanding is used here

### What we call

- **Analyzer:** `prebuilt-layout`
- **SDK:** `azure-ai-contentunderstanding`
- **Env:** `AZURE_CONTENT_UNDERSTANDING_ENDPOINT`, `AZURE_CONTENT_UNDERSTANDING_KEY`
- **API version** (notebook): `2025-11-01`

### What comes back

The analysis result is a JSON document. Important shape:

- `contents[0].markdown` — full document as markdown (includes HTML `<table>` blocks). Useful for reading; **not** the primary table API.
- `contents[0].tables[]` — **structured tables** (what the Azure UI “Tables” tab shows).
  - Each table: `rowCount`, `columnCount`, `cells[]`
  - Each cell: `rowIndex`, `columnIndex`, `content`, `kind` (`columnHeader` or `content`)
  - Page number is encoded in cell `source` as `D(<page>, x1, y1, …)`

### How this repo uses it

1. Send the PDF bytes with `begin_analyze(analyzer_id="prebuilt-layout", …)`.
2. Save the full response → `extraction-output/cu-layout/<stem>.json`.
3. Rebuild each table as a grid; treat rows with any `kind=columnHeader` cell as headers.
4. Classify remaining rows as **spec** (Req’t / Min / Max / …) or **result** (Result / heat IDs / …) → `extraction-output/cu-tables/<stem>.json`.
5. Render tables **grouped by page** to HTML → `extraction-output/cu-reports/<stem>.html` (local only; no API). Hooked into `save_layout`, or run:

```bash
python scripts/layout_json_to_html.py
```

UI tip: the Foundry / Content Understanding UI often shows tables **for the page you are viewing**. A 20-page PDF can contain many tables overall; page 1 of a MELESI cert may show ~6 clean tables while later pages hold appendix tables.

---

## How Mistral Document AI is used here

- **Endpoint pattern:** `https://<resource>.services.ai.azure.com/providers/mistral/azure/ocr`
- **Env:** `AZURE_MISTRAL_DOCUMENT_AI_ENDPOINT`, `AZURE_MISTRAL_DOCUMENT_AI_KEY`, `AZURE_AI_DEPLOYMENT_NAME`
- Notebook **01** OCRs selected pages and asks for structured fields via `document_annotation_format` (schema in the notebook).
- Saves OCR markdown → `mistral-ocr/`; fields → `mistral-fields/`.

Mistral is strong at reading pages into text/fields. It is **weaker** than layout at reliably separating specification limit rows from measured result rows inside dense mill tables — that is why notebook **02** exists.

---

## Repository layout

```
mat-cert-doc-parsing/
├── README.md                          ← this file
├── .env                               ← secrets (not committed)
├── raw-docs/                          ← input PDFs
├── notebooks/                                ← ACTIVE notebooks (run these)
│   ├── 01-mistral-ocr-and-fields.ipynb
│   └── 02-content-understanding-tables.ipynb
├── archive/                           ← historical notebooks (do not run)
│   ├── 01-mistral-ocr-smoke-test.ipynb
│   └── 02-mistral-foundry-early-pipeline.ipynb
├── guides/
│   └── EN10204-reference.md           ← EN 10204 types / fields notes
├── scripts/
│   ├── layout_json_to_html.py         ← cu-layout JSON → cu-reports HTML
│   └── validate_pipeline.py           ← live/offline CU + HTML fixture checks
└── extraction-output/                 ← all generated artifacts
    ├── mistral-ocr/                   ← .md   from notebook 01
    ├── mistral-fields/                ← .json from notebook 01
    ├── cu-layout/                     ← .json raw layout API (notebook 02)
    ├── cu-tables/                     ← .json parsed tables (notebook 02)
    ├── cu-reports/                    ← .html human review (notebook 02 / script)
    └── validation-report.json         ← last validate_pipeline.py result
```

### Folder cheat sheet

| Path | Type | How to read it |
|------|------|----------------|
| `raw-docs/` | PDF | Source certificates; open in a PDF viewer next to reports. |
| `extraction-output/mistral-ocr/` | Markdown | OCR text; open in editor/preview. |
| `extraction-output/mistral-fields/` | JSON | Structured fields from Mistral annotation. |
| `extraction-output/cu-layout/` | JSON | Full layout API dump (large). Inspect `contents[0].tables`. |
| `extraction-output/cu-tables/` | JSON | Array of `{ headers, spec_rows, result_rows }` per table. |
| `extraction-output/cu-reports/` | HTML | Open in a browser; tables grouped by page — best human check vs PDF. |
| `guides/EN10204-reference.md` | Markdown | Domain notes on EN 10204 types and expected data. |
| `archive/` | Notebooks | Old smoke-test / early Foundry pipeline. Banner at top of each. |

---

## Quick start

1. Copy credentials into `.env` (see below). Never commit `.env`.
2. Put PDFs in `raw-docs/`.
3. Open **`notebooks/02-content-understanding-tables.ipynb`** (tables) and/or **`notebooks/01-mistral-ocr-and-fields.ipynb`** (fields).
4. Run Setup, then process one file (or batch when you intend to spend API quota).
5. Review:
   - Humans: `extraction-output/cu-reports/<name>.html` beside the PDF.
   - Machines: `cu-tables/` and/or `mistral-fields/`.

Notebooks resolve the **repo root** automatically (works if the kernel cwd is the repo root or `notebooks/`).

### Required environment variables

**Content Understanding (notebook 02)**

```env
AZURE_CONTENT_UNDERSTANDING_ENDPOINT=https://<resource>.services.ai.azure.com/
AZURE_CONTENT_UNDERSTANDING_KEY=<key>
```

**Mistral Document AI (notebook 01)**

```env
AZURE_MISTRAL_DOCUMENT_AI_ENDPOINT=https://<resource>.services.ai.azure.com/...
AZURE_MISTRAL_DOCUMENT_AI_KEY=<key>
AZURE_AI_DEPLOYMENT_NAME=<deployment-name>
```

---

## Suggested reading order for a new contributor

1. This `README.md` (problem + which notebook).
2. `guides/EN10204-reference.md` (what a Type 3.1 cert should contain).
3. Open one PDF from `raw-docs/` and the matching `cu-reports/*.html`.
4. Skim `cu-tables/*.json` for the same stem — look for `spec_rows` vs `result_rows`.
5. Only then open `cu-layout/*.json` if you need raw API detail.
6. Ignore `archive/` unless you are studying history.

---

## Validation (ready-to-use check)

### Automated (notebook 02 + HTML)

From the repo root:

```bash
# Live: call Content Understanding on every PDF in raw-docs/, rewrite outputs, run fixtures
python scripts/validate_pipeline.py

# Offline: reuse existing cu-layout JSON, rebuild cu-tables + cu-reports, re-check fixtures
python scripts/validate_pipeline.py --offline
```

Writes `extraction-output/validation-report.json` (`ok: true/false` per file).

**Fixture checks (stable across API table-count variance):**

| Cert | What must pass |
|------|----------------|
| EUR-472273 | Tensile table with `Req't` (414 / 693) and `Result` (450 / 900); HTML has Page 1 |
| MELESI DH44 | Page 1 has chemistry + mechanical titles; chemistry limit row + `SR*` heat results; HTML Page 1 |
| FMT-22-1454-EZ17 | `Min. Max.` + `EZ*` heat rows; HTML Page 1 |

Also checks: API returned tables, HTML contains `<table>`, HTML size not empty.

**HTML report review (human):** open `extraction-output/cu-reports/<stem>.html` next to `raw-docs/<stem>.pdf`. Confirm Page 1 matches the cert face (not only appendices).

### Last validation run (Content Understanding)

| File | API tables | Page-1 tables | HTML pages with tables | Result |
|------|------------|---------------|------------------------|--------|
| MELESI DH44 | 26 | 4 | 18 | PASS |
| EUR-472273 | 36 | 7 | 10 | PASS |
| FMT-22-1454-EZ17 | 40 | 2 | 13 | PASS |

Notes:

- Page-1 table **counts can change** between API runs (merge/split of small label tables). Fixtures check content, not a fixed count of 6.
- Regenerating HTML: `python scripts/layout_json_to_html.py` (no API).

### Mistral (notebook 01)

Notebook **01** will currently **not work** if executed. Live calls against the Foundry OCR endpoint (`/providers/mistral/azure/ocr`) return:

```json
{
  "error": {
    "code": "DeploymentError",
    "message": "The API deployment for the resource is not ready, please wait until provisioningState becomes Succeeded."
  }
}
```

- **Cause**: The deployment `mistral-document-ai-2505-1` exists in Azure AI Foundry under resource `emb-doc-parsing-dev`, but its Azure `provisioningState` is not `Succeeded` (e.g. provisioning, stopped, or failed state).
- **Existing outputs present? YES**: Full results generated from successful earlier runs are already present in the repository:
  - `extraction-output/mistral-ocr/` contains OCR Markdown (`.md`) for all 3 sample certs.
  - `extraction-output/mistral-fields/` contains structured EN 10204 JSON (`.json`) for all 3 sample certs.
- **Fix**: Once the administrator ensures the deployment is active and healthy in Azure AI Foundry, re-run Setup and `process(target)` in `notebooks/01-mistral-ocr-and-fields.ipynb`.

### Manual notebook check

1. Open `notebooks/02-content-understanding-tables.ipynb` → run Setup → expect repo root + key set.
2. Process one PDF → files appear under `cu-layout/`, `cu-tables/`, `cu-reports/`.
3. Open the HTML report beside the PDF.

---

## Cost / token hygiene

- Content Understanding and Mistral calls are **paid**.
- Regenerating HTML from existing `cu-layout` JSON is **local** (`scripts/layout_json_to_html.py`) — no Azure tokens.
- `validate_pipeline.py --offline` is also local after a live run.

---

## EN 10204 (short)

| Type | Meaning (simplified) |
|------|----------------------|
| 2.1 | Declaration of compliance — little/no test data |
| 2.2 | Test results based on non-specific testing |
| 3.1 | Specific testing; manufacturer’s authorized inspection rep |
| 3.2 | Specific testing; manufacturer + independent inspection |

Notebook 01 tries to detect type early and skip 2.1 / 2.2 when there is nothing useful to extract. Details: `guides/EN10204-reference.md`.
