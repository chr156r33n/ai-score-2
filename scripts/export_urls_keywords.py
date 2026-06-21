#!/usr/bin/env python3
"""Export simplified url/keyword input from the full CMM keyword matrix CSV."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path


def _field(row: dict[str, str | None], name: str) -> str:
    for key, value in row.items():
        if key and key.strip() == name:
            return (value or "").strip()
    return ""


def _first_primary_keyword(raw: str) -> str:
    """Use the first comma-separated target keyword for SERP lookup."""
    if not raw:
        return ""
    return raw.split(",")[0].strip()


def export(source: Path, dest: Path) -> tuple[int, int]:
    with source.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    out_rows: list[dict[str, str]] = []
    with_primary = 0
    for row in rows:
        url = _field(row, "Page URL")
        if not url:
            continue
        primary_raw = _field(row, "Target keyword (s)")
        primary = _first_primary_keyword(primary_raw)
        secondary = _field(row, "Secondary Keyword")
        if primary:
            with_primary += 1
        out_rows.append(
            {
                "url": url,
                "primary_keyword": primary,
                "secondary_keyword": secondary,
            }
        )

    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["url", "primary_keyword", "secondary_keyword"],
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(out_rows)

    return len(out_rows), with_primary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--source",
        type=Path,
        default=Path("cmm_keywords_0626.csv"),
        help="Full CMM export path",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        default=Path("data/urls_keywords.csv"),
        help="Simplified output path",
    )
    args = parser.parse_args()
    total, with_primary = export(args.source, args.dest)
    print(f"Wrote {total} rows ({with_primary} with primary_keyword) to {args.dest}")


if __name__ == "__main__":
    main()
