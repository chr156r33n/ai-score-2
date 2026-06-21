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

### Eligibility flow (per target URL)

1. Read `primary_keyword` for the target URL from input file.
2. Fetch top 10 organic results from DataForSEO for that keyword (SERP params TBD).
3. Extract facts from those 10 URLs → **benchmark corpus** (union across peers).
4. Extract facts from **target URL**.
5. Coverage analysis → eligibility score / gaps (details TBD).

**Note:** Corpus is built from SERP peers only, not from merging target into the corpus unless we decide otherwise (TBD).

## Run input: URL / keywords

**Canonical file:** `data/urls_keywords.csv`

| Column | Required | Purpose |
|--------|----------|---------|
| `url` | Yes | Target page to score (must match crawl URLs). |
| `primary_keyword` | Yes for eligibility/SERP | Keyword passed to DataForSEO for top-10 organic URLs. |
| `secondary_keyword` | No | Reserved for future use (e.g. second SERP set or enrichment). **V1 SERP uses `primary_keyword` only.** |

**Rules:**

- One row per target URL.
- If `primary_keyword` is empty, the URL may still receive interpretability / attention / credibility scores, but **eligibility and full opportunity** require a keyword (TBD: skip vs fail run).
- When the CMM has multiple target keywords in one cell (`"kw a, kw b"`), export keeps the **first** comma-separated value as `primary_keyword`.

**Regenerate from CMM:**

```bash
python3 scripts/export_urls_keywords.py \
  --source cmm_keywords_0626.csv \
  --dest data/urls_keywords.csv
```

**Source matrix (reference only):** `cmm_keywords_0626.csv` — full content matrix; not required at runtime if `data/urls_keywords.csv` is provided.

## Open (not yet decided)

- DataForSEO locale: location, language, device
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
