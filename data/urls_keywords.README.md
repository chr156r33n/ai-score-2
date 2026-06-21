# `urls_keywords.csv`

Minimal run input for per-URL scoring and SERP-based eligibility.

| Column | Description |
|--------|-------------|
| `url` | Target URL |
| `primary_keyword` | Keyword for DataForSEO top-10 organic SERP (peer corpus) |
| `secondary_keyword` | Optional; not used in V1 SERP |

Generate from the full CMM export:

```bash
python3 scripts/export_urls_keywords.py
```

See `spec/v1-spec.md` for full contract.
