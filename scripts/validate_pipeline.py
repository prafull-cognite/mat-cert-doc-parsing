#!/usr/bin/env python3
"""
End-to-end validation for notebook 02 (Content Understanding) + HTML reports.

Re-runs prebuilt-layout on every PDF in raw-docs/, writes cu-layout / cu-tables /
cu-reports, then checks known cert fixtures (spec/result rows + HTML page groups).

Usage (repo root):
  python scripts/validate_pipeline.py
"""
from __future__ import annotations

import json
import os
import re
import sys
from collections import defaultdict
from pathlib import Path

from azure.ai.contentunderstanding import ContentUnderstandingClient
from azure.ai.contentunderstanding.models import AnalysisInput
from azure.core.credentials import AzureKeyCredential
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
load_dotenv(ROOT / ".env")

from scripts.layout_json_to_html import convert_file, _table_page  # noqa: E402

INPUT_DIR = ROOT / "raw-docs"
LAYOUT_DIR = ROOT / "extraction-output" / "cu-layout"
TABLES_DIR = ROOT / "extraction-output" / "cu-tables"
REPORTS_DIR = ROOT / "extraction-output" / "cu-reports"

_SPEC_KEYWORDS = re.compile(
    r"^\s*(req|min|max|limit|spec|minimum|maximum|shall|required)",
    re.IGNORECASE,
)
_RESULT_KEYWORDS = re.compile(
    r"^\s*(result|actual|achieved|measured|test\s*value)",
    re.IGNORECASE,
)


def _cells_to_grid(cells: list[dict], row_count: int, col_count: int) -> list[list[str]]:
    grid = [[""] * col_count for _ in range(row_count)]
    for cell in cells:
        r = cell.get("rowIndex", 0)
        c = cell.get("columnIndex", 0)
        if r < row_count and c < col_count:
            grid[r][c] = cell.get("content", "").strip()
    return grid


def _classify_row(row: list[str]) -> str:
    first = row[0] if row else ""
    if _SPEC_KEYWORDS.search(first):
        return "spec"
    if (
        not first.strip()
        and any(re.search(r"^\d", c) for c in row[1:] if c)
        and not any(re.search(r"[A-Za-z]", c) for c in row[1:] if c)
    ):
        return "spec"
    if _RESULT_KEYWORDS.search(first):
        return "result"
    if re.match(r"^[A-Z0-9]{3,}", first, re.IGNORECASE):
        return "result"
    return "result"


def parse_tables(layout_result: dict) -> list[dict]:
    api_tables = layout_result.get("contents", [{}])[0].get("tables", [])
    tables: list[dict] = []
    for t in api_tables:
        row_count = t.get("rowCount", 0)
        col_count = t.get("columnCount", 0)
        cells = t.get("cells", [])
        grid = _cells_to_grid(cells, row_count, col_count)
        header_row_indices = {
            cell.get("rowIndex", 0)
            for cell in cells
            if cell.get("kind") == "columnHeader"
        }
        headers: list[list[str]] = []
        spec_rows: list[list[str]] = []
        result_rows: list[list[str]] = []
        for row_idx, row in enumerate(grid):
            if row_idx in header_row_indices:
                headers.append(row)
            elif _classify_row(row) == "spec":
                spec_rows.append(row)
            else:
                result_rows.append(row)
        tables.append(
            {"headers": headers, "spec_rows": spec_rows, "result_rows": result_rows}
        )
    return tables


def extract_layout(client: ContentUnderstandingClient, pdf_path: Path) -> dict:
    poller = client.begin_analyze(
        analyzer_id="prebuilt-layout",
        inputs=[AnalysisInput(data=pdf_path.read_bytes(), mime_type="application/pdf")],
    )
    return poller.result().as_dict()


def _page1_table_count(layout: dict) -> int:
    tables = layout.get("contents", [{}])[0].get("tables", [])
    return sum(1 for t in tables if _table_page(t) == 1)


def _html_has_page_sections(html: str) -> list[int]:
    return [int(m) for m in re.findall(r"<h2>Page (\d+)</h2>", html)]


def validate_eur(tables: list[dict], layout: dict, html: str) -> list[str]:
    errs: list[str] = []
    # Tensile: Req't + Result
    found_tensile = False
    for t in tables:
        specs = t.get("spec_rows") or []
        results = t.get("result_rows") or []
        if any(r and r[0].lower().startswith("req") for r in specs) and any(
            r and r[0].lower().startswith("res") for r in results
        ):
            found_tensile = True
            spec = next(r for r in specs if r[0].lower().startswith("req"))
            result = next(r for r in results if r[0].lower().startswith("res"))
            joined_s = " ".join(spec)
            joined_r = " ".join(result)
            if "414" not in joined_s or "693" not in joined_s:
                errs.append(f"EUR tensile spec missing 414/693: {spec}")
            if "450" not in joined_r or "900" not in joined_r:
                errs.append(f"EUR tensile result missing 450/900: {result}")
            break
    if not found_tensile:
        errs.append("EUR: no Req't/Result tensile table found")
    if _page1_table_count(layout) < 1:
        errs.append("EUR: no page-1 tables in layout")
    if 1 not in _html_has_page_sections(html):
        errs.append("EUR HTML: missing Page 1 section")
    return errs


def validate_melesi(tables: list[dict], layout: dict, html: str) -> list[str]:
    errs: list[str] = []
    p1 = _page1_table_count(layout)
    # API may merge/split small label tables; expect the main cert block on page 1.
    if p1 < 4:
        errs.append(f"MELESI: expected >= 4 tables on page 1, got {p1}")

    page1_blob = " ".join(
        (c.get("content") or "")
        for t in layout.get("contents", [{}])[0].get("tables", [])
        if _table_page(t) == 1
        for c in t.get("cells", [])
    ).upper()
    if "ANALISI CHIMICA" not in page1_blob and "CHEMICAL ANALYSIS" not in page1_blob:
        errs.append("MELESI page 1: chemical analysis table title missing")
    if "PROVE MECCANICHE" not in page1_blob and "MECHANICAL" not in page1_blob:
        errs.append("MELESI page 1: mechanical tests table title missing")

    # Chemistry: Max and/or unlabeled Min row + heat-like result (SR*)
    chem_ok = False
    for t in tables:
        specs = t.get("spec_rows") or []
        results = t.get("result_rows") or []
        has_limit = any(
            (r and r[0].lower().startswith("max"))
            or (r and not r[0].strip() and any(re.search(r"\d", c) for c in r[1:] if c))
            for r in specs
        )
        has_heat = any(r and re.match(r"^SR\d+", r[0], re.I) for r in results)
        if has_limit and has_heat:
            chem_ok = True
            break
    if not chem_ok:
        errs.append("MELESI: chemistry limit row + SR* heat rows not found")
    if 1 not in _html_has_page_sections(html):
        errs.append("MELESI HTML: missing Page 1")
    return errs


def validate_fmt(tables: list[dict], layout: dict, html: str) -> list[str]:
    errs: list[str] = []
    found = False
    for t in tables:
        specs = t.get("spec_rows") or []
        results = t.get("result_rows") or []
        has_minmax = any("min" in (r[0] or "").lower() for r in specs)
        heats = [r[0] for r in results if r and re.match(r"^EZ\d+", r[0], re.I)]
        if has_minmax and len(heats) >= 2:
            found = True
            break
    if not found:
        errs.append("FMT: Min.Max. chemistry/mechanical + EZ* heats not found")
    if 1 not in _html_has_page_sections(html):
        errs.append("FMT HTML: missing Page 1")
    if _page1_table_count(layout) < 1:
        errs.append("FMT: no page-1 tables")
    return errs


VALIDATORS = {
    "EUR-472273": validate_eur,
    "147149__02 MELESI MA-00351 mds-DH44": validate_melesi,
    "FMT-22-1454-EZ17": validate_fmt,
}


def main() -> int:
    offline = "--offline" in sys.argv
    endpoint = os.getenv("AZURE_CONTENT_UNDERSTANDING_ENDPOINT", "")
    key = os.getenv("AZURE_CONTENT_UNDERSTANDING_KEY", "")
    if not offline and (not endpoint or not key):
        print("FAIL: CU endpoint/key missing in .env")
        return 1

    client = None
    if not offline:
        client = ContentUnderstandingClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key),
            api_version="2025-11-01",
        )
    for d in (LAYOUT_DIR, TABLES_DIR, REPORTS_DIR):
        d.mkdir(parents=True, exist_ok=True)

    pdfs = sorted(INPUT_DIR.glob("*.pdf"))
    if not pdfs:
        print("FAIL: no PDFs in raw-docs/")
        return 1

    report: dict = {"ok": True, "offline": offline, "files": {}}
    all_errs: list[str] = []

    for pdf in pdfs:
        print(f"\n=== {pdf.name} ===")
        layout_path = LAYOUT_DIR / f"{pdf.stem}.json"
        tables_path = TABLES_DIR / f"{pdf.stem}.json"
        if offline:
            if not layout_path.is_file():
                print(f"FAIL: missing {layout_path}")
                return 1
            print("Offline: reusing cu-layout JSON...")
            layout = json.loads(layout_path.read_text(encoding="utf-8"))
        else:
            print("Calling prebuilt-layout...")
            assert client is not None
            layout = extract_layout(client, pdf)
            layout_path.write_text(
                json.dumps(layout, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        tables = parse_tables(layout)
        tables_path.write_text(json.dumps(tables, indent=2, ensure_ascii=False), encoding="utf-8")
        html_path = convert_file(layout_path, REPORTS_DIR)
        html = html_path.read_text(encoding="utf-8")

        api_n = len(layout.get("contents", [{}])[0].get("tables", []))
        by_page: dict[int, int] = defaultdict(int)
        for t in layout.get("contents", [{}])[0].get("tables", []):
            by_page[_table_page(t)] += 1

        print(f"  API tables: {api_n}  page1: {by_page.get(1, 0)}")
        print(f"  parsed tables: {len(tables)}")
        print(f"  HTML: {html_path.relative_to(ROOT)}")

        errs: list[str] = []
        if api_n == 0:
            errs.append("zero tables from API")
        if html_path.stat().st_size < 500:
            errs.append("HTML too small")
        if "<table>" not in html:
            errs.append("HTML has no <table>")
        validator = VALIDATORS.get(pdf.stem)
        if validator:
            errs.extend(validator(tables, layout, html))
        else:
            print("  (no fixture validator for this stem)")

        report["files"][pdf.stem] = {
            "api_tables": api_n,
            "page1_tables": by_page.get(1, 0),
            "parsed_tables": len(tables),
            "html_pages": _html_has_page_sections(html),
            "errors": errs,
        }
        if errs:
            report["ok"] = False
            all_errs.extend(f"{pdf.stem}: {e}" for e in errs)
            for e in errs:
                print(f"  FAIL: {e}")
        else:
            print("  PASS")

    out = ROOT / "extraction-output" / "validation-report.json"
    out.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(f"\nWrote {out.relative_to(ROOT)}")
    if all_errs:
        print(f"\nOVERALL FAIL ({len(all_errs)} errors)")
        return 1
    print("\nOVERALL PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
