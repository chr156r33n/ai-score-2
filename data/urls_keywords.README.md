# `urls_keywords.csv`

Minimal run input for per-URL scoring and SERP-based eligibility.

| Column | Description |
|--------|-------------|
| `url` | Target URL |
| `primary_keyword` | Keyword for DataForSEO top-10 organic SERP (peer corpus) |
| `secondary_keyword` | Optional; not used in V1 SERP |
| `region` | ISO 3166-1 alpha-2 SERP location (default `US`) |
| `language` | BCP-47 language code (default `en`) |
| `device` | `mobile` or `desktop` (default `mobile`) |

Generate from the full CMM export:

```bash
python3 scripts/export_urls_keywords.py
```

Region slugs are defined in `scripts/property_regions.py`. See `spec/v1-spec.md` for full contract.
