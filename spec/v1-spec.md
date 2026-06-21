# AI Opportunity Framework — V1 specification (draft)

Living document built via Q&A. Supersedes ambiguous parts of `instructions.md` where noted.

## Objective

Score and explain **AI optimisation opportunity per URL** using observable signals. See `instructions.md` for component definitions and non-goals.

## Locked decisions

| # | Topic | Decision |
|---|--------|----------|
| 1 | Primary grain | **URL** — rank, compare, and explain opportunity per URL. |
| 2 | Eligibility benchmark | **Peer-derived corpus** — for each target URL, aggregate facts from comparison URLs; measure target coverage against that corpus (not external PAA/AlsoAsked as the primary corpus in V1). |
| 3 | Comparison set | **Top 10 organic SERP URLs** for a keyword, via **DataForSEO** (may change later). |
| 4 | SERP keyword source | **`data/urls_keywords.csv`** — explicit `url` + `primary_keyword` (and optional `secondary_keyword`). Derived from CMM; see below. |
| 5 | SERP locale | **`region`** (ISO 3166-1 alpha-2), **`language`** (BCP-47), **`device`** per row. Run defaults: missing values → `US`, `en`, `mobile`. CMM export infers **region from URL property slug**; **language `en`**; **device `mobile`** for all rows. |
| 6 | Target in SERP top 10 | **Exclude target, no backfill** — If the target URL appears in the top 10 organic results, remove it from the peer set. Do **not** fetch position 11+ to refill. The benchmark corpus may contain **fewer than 10** URLs. |

### Eligibility flow (per target URL)

1. Read `primary_keyword`, `region`, `language`, and `device` for the target URL from input file (defaults: `US`, `en`, `mobile`).
2. Fetch top 10 organic results from DataForSEO for that keyword and locale.
3. **Remove the target URL** from that list if present. **Do not backfill** with additional SERP positions. Use the remaining URLs as peers (0–10).
4. Extract facts from peer URLs → **benchmark corpus** (union across peers).
5. Extract facts from **target URL**.
6. Coverage analysis → eligibility score / gaps (details TBD).

**Note:** Corpus is built from SERP peers only (never the target).

## Run input: URL / keywords

**Canonical file:** `data/urls_keywords.csv`

| Column | Required | Purpose |
|--------|----------|---------|
| `url` | Yes | Target page to score (must match crawl URLs). |
| `primary_keyword` | Yes for eligibility/SERP | Keyword passed to DataForSEO for top-10 organic URLs. |
| `secondary_keyword` | No | Reserved for future use (e.g. second SERP set or enrichment). **V1 SERP uses `primary_keyword` only.** |
| `region` | Yes (may be inferred) | SERP location as **ISO 3166-1 alpha-2** country/territory code (e.g. `US`, `AE`, `GB`). Mapped to DataForSEO `location_name` / `location_code` at runtime. |
| `language` | Yes | SERP language, **BCP-47** (e.g. `en`). |
| `device` | Yes | SERP device: `mobile` or `desktop`. **V1 default: `mobile`.** |

**Rules:**

- One row per target URL.
- If `primary_keyword` is empty, the URL may still receive interpretability / attention / credibility scores, but **eligibility and full opportunity** require a keyword (TBD: skip vs fail run).
- When the CMM has multiple target keywords in one cell (`"kw a, kw b"`), export keeps the **first** comma-separated value as `primary_keyword`.
- **Region inference (CMM export):** first URL path segment (e.g. `abudhabi` from `/abudhabi/...`) → property country via `scripts/property_regions.py`. Unknown slugs → `US`.

**Regenerate from CMM:**

```bash
python3 scripts/export_urls_keywords.py \
  --source cmm_keywords_0626.csv \
  --dest data/urls_keywords.csv
```

**Source matrix (reference only):** `cmm_keywords_0626.csv` — full content matrix; not required at runtime if `data/urls_keywords.csv` is provided.

## Open (not yet decided)

- Whether target URL is excluded from peer set if it ranks in top 10
- Fact schema, coverage math, opportunity formula wiring
- AI attention and credibility data sources for V1
- Deliverable shape (CLI, outputs on disk)

## Components (from instructions.md)

Unchanged unless noted above:

- **Opportunity** = AI Attention × weighted gap combination (weights/config TBD)
- **Interpretability** — Screaming Frog, deterministic
- **Credibility** — observable off-page signals (TBD for V1)
- **LLM** — judgement only (e.g. missing-fact importance), not orchestration
