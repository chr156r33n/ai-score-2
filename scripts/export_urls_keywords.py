#!/usr/bin/env python3
"""Export simplified url/keyword input from the full CMM keyword matrix CSV."""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from property_regions import (  # noqa: E402
    DEFAULT_DEVICE,
    DEFAULT_LANGUAGE,
    REGION_BY_SLUG,
    region_for_url,
    url_slug,
)


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


FIELDNAMES = [
    "url",
    "primary_keyword",
    "secondary_keyword",
    "region",
    "language",
    "device",
]


def export(source: Path, dest: Path) -> tuple[int, int, list[str]]:
    with source.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    out_rows: list[dict[str, str]] = []
    with_primary = 0
    unknown_slugs: list[str] = []
    seen_slugs: set[str] = set()

    for row in rows:
        url = _field(row, "Page URL")
        if not url:
            continue
        primary_raw = _field(row, "Target keyword (s)")
        primary = _first_primary_keyword(primary_raw)
        secondary = _field(row, "Secondary Keyword")
        if primary:
            with_primary += 1

        slug = url_slug(url)
        if slug and slug not in REGION_BY_SLUG and slug not in seen_slugs:
            unknown_slugs.append(slug)
            seen_slugs.add(slug)

        out_rows.append(
            {
                "url": url,
                "primary_keyword": primary,
                "secondary_keyword": secondary,
                "region": region_for_url(url),
                "language": DEFAULT_LANGUAGE,
                "device": DEFAULT_DEVICE,
            }
        )

    dest.parent.mkdir(parents=True, exist_ok=True)
    with dest.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=FIELDNAMES,
            lineterminator="\n",
        )
        writer.writeheader()
        writer.writerows(out_rows)

    return len(out_rows), with_primary, unknown_slugs


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
    total, with_primary, unknown_slugs = export(args.source, args.dest)
    if unknown_slugs:
        print(
            "Warning: unknown URL slugs (defaulted region to US):",
            ", ".join(sorted(unknown_slugs)),
            file=sys.stderr,
        )
    print(f"Wrote {total} rows ({with_primary} with primary_keyword) to {args.dest}")


if __name__ == "__main__":
    main()
