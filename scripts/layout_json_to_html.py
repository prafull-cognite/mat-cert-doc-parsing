#!/usr/bin/env python3
"""
Turn Content Understanding layout JSON into HTML grouped by page.

Reads:  extraction-output/cu-layout/<name>.json  (contents[0].tables)
Writes: extraction-output/cu-reports/<name>.html

Page number comes from each cell's `source` field: D(<page>, x1, y1, ...).
No API calls — local files only.
"""
from __future__ import annotations

import argparse
import json
import re
from collections import defaultdict
from pathlib import Path


def _table_page(table: dict) -> int:
    for cell in table.get("cells", []):
        m = re.match(r"D\((\d+)", cell.get("source", "") or "")
        if m:
            return int(m.group(1))
    return 0


def _table_to_html(table: dict) -> str:
    rc = table.get("rowCount", 0)
    cc = table.get("columnCount", 0)
    grid = [[""] * cc for _ in range(rc)]
    is_header = [[False] * cc for _ in range(rc)]
    for cell in table.get("cells", []):
        r = cell.get("rowIndex", 0)
        c = cell.get("columnIndex", 0)
        if r < rc and c < cc:
            grid[r][c] = (cell.get("content", "") or "").replace("\n", "<br>")
            is_header[r][c] = cell.get("kind") == "columnHeader"

    rows: list[str] = ["<table>"]
    for ri in range(rc):
        rows.append("<tr>")
        for ci in range(cc):
            tag = "th" if is_header[ri][ci] else "td"
            rows.append(f"<{tag}>{grid[ri][ci]}</{tag}>")
        rows.append("</tr>")
    rows.append("</table>")
    return "".join(rows)


def layout_to_html(layout: dict, title: str) -> str:
    tables = layout.get("contents", [{}])[0].get("tables", [])
    total_pages = layout.get("contents", [{}])[0].get("endPageNumber", "?")

    by_page: dict[int, list[dict]] = defaultdict(list)
    for t in tables:
        by_page[_table_page(t)].append(t)

    css = """
body{font-family:Arial,sans-serif;font-size:12px;margin:24px;background:#f5f5f5;color:#222}
h1{background:#1a252f;color:#fff;padding:12px 16px;font-size:15px;margin:0 0 16px}
h2{background:#2980b9;color:#fff;padding:5px 12px;font-size:12px;margin:24px 0 0}
h3{margin:6px 0 2px;font-size:11px;color:#555}
table{border-collapse:collapse;width:100%;background:#fff;margin-bottom:2px}
th{background:#1a252f;color:#fff;padding:5px 8px;font-size:11px;text-align:left;white-space:nowrap}
td{border:1px solid #ccc;padding:4px 8px;font-size:11px;vertical-align:top}
tr:nth-child(even) td{background:#f9f9f9}
.page-block{background:#fff;border:1px solid #ddd;padding:12px;margin-bottom:20px}
"""

    parts = [f"<h1>{title} &nbsp;|&nbsp; {total_pages} pages (endPageNumber)</h1>"]
    for page in sorted(by_page.keys()):
        parts.append(f'<div class="page-block"><h2>Page {page}</h2>')
        for t in by_page[page]:
            hdrs = [
                (c.get("content") or "").strip().replace("\n", " ")
                for c in t.get("cells", [])
                if c.get("kind") == "columnHeader"
            ]
            subtitle = hdrs[0][:80] if hdrs else f'{t.get("rowCount", 0)}r × {t.get("columnCount", 0)}c'
            parts.append(f"<h3>{subtitle}</h3>")
            parts.append(_table_to_html(t))
        parts.append("</div>")

    body = "".join(parts)
    return (
        "<!DOCTYPE html><html><head><meta charset=\"utf-8\">"
        f"<title>{title}</title><style>{css}</style></head><body>{body}</body></html>"
    )


def convert_file(layout_json: Path, out_dir: Path) -> Path:
    layout = json.loads(layout_json.read_text(encoding="utf-8"))
    html = layout_to_html(layout, layout_json.stem)
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{layout_json.stem}.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path


def main() -> None:
    root = Path(__file__).resolve().parent.parent
    p = argparse.ArgumentParser(description="Layout JSON → HTML (tables by page)")
    p.add_argument(
        "--layout-dir",
        type=Path,
        default=root / "extraction-output" / "cu-layout",
        help="Folder with layout *.json from Content Understanding",
    )
    p.add_argument(
        "--out-dir",
        type=Path,
        default=root / "extraction-output" / "cu-reports",
        help="Folder to write *.html",
    )
    p.add_argument(
        "files",
        nargs="*",
        type=Path,
        help="Optional specific layout JSON paths (default: all in layout-dir)",
    )
    args = p.parse_args()

    layout_dir = args.layout_dir
    out_dir = args.out_dir

    if args.files:
        paths = [Path(f) for f in args.files]
    else:
        paths = sorted(layout_dir.glob("*.json"))

    if not paths:
        print(f"No JSON files in {layout_dir}")
        return

    for path in paths:
        if not path.is_file():
            print(f"Skip (not a file): {path}")
            continue
        out = convert_file(path, out_dir)
        print(out)


if __name__ == "__main__":
    main()
