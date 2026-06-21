# AI Opportunity Framework — V1 specification (draft)

Living document built via Q&A. Supersedes ambiguous parts of `instructions.md` where noted.

**New agent?** Read `spec/q-and-a-progress.md` for Q&A state and the next question to ask.

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
| 7 | Sparse / failed peer set | **Always emit an eligibility score** when the pipeline runs, including 0 peers or failed crawls. Pair the score with explicit **quality caveats** (see below) so consumers know when to trust it. |
| 8 | Interpretability | **Separate module**, spec **on hold** — Screaming Frog / rules deferred. Pipeline must not depend on it for other modules to run. See [Architecture](#architecture-modules). |
| 9 | Fact inventory | **Corpus-defined** — The facts eligibility uses are **those in the benchmark corpus** (aggregated from SERP peers). No separate global taxonomy or external question list defines the fact set in V1. The target is scored on **coverage of corpus facts** only. |

### Eligibility flow (per target URL)

1. Read `primary_keyword`, `region`, `language`, and `device` for the target URL from input file (defaults: `US`, `en`, `mobile`).
2. Fetch top 10 organic results from DataForSEO for that keyword and locale.
3. **Remove the target URL** from that list if present. **Do not backfill** with additional SERP positions. Use the remaining URLs as peers (0–10).
4. Extract facts from peer URLs → **benchmark corpus** (union across peers).
5. Extract facts from **target URL**.
6. Coverage analysis → eligibility score / gaps (details TBD).

**Note:** Corpus is built from SERP peers only (never the target).

### Eligibility scoring when data is weak

- **Always compute and output `eligibility_score`** (0–100) for each URL that enters the eligibility step, even when peers or crawls are weak. Do not drop the URL solely for sparse peers.
- **Edge case — empty benchmark:** If there are **no usable peer pages** or **zero benchmark facts** after extraction, set `eligibility_score` to **0** and add caveats explaining why (not a null score).
- **Edge case — target not crawlable:** If the target cannot be fetched/parsed, set `eligibility_score` to **0** and add `target_not_accessible` (interpretability may also flag the same URL).

### Eligibility data quality fields (per URL)

Every eligibility result includes counts plus a machine-readable caveat list.

| Field | Type | Description |
|--------|------|-------------|
| `peer_count_serp` | int | Organic results returned (up to 10). |
| `peer_count_excluded_target` | int | Peers after removing the target URL. |
| `peer_count_crawled` | int | Peers successfully fetched and parsed for fact extraction. |
| `benchmark_fact_count` | int | Facts in the aggregated peer corpus after dedup. |
| `eligibility_caveats` | array | Zero or more caveat objects (below). |

**Caveat object:**

```json
{
  "code": "too_few_peers",
  "message": "Human-readable explanation for reports",
  "context": { "peer_count_excluded_target": 2, "threshold": 3 }
}
```

**V1 caveat codes** (extend as needed):

| Code | When |
|------|------|
| `no_peers` | `peer_count_excluded_target` is 0 after SERP + exclusion. |
| `too_few_peers` | `peer_count_excluded_target` (or `peer_count_crawled`) is below configured minimum (default **3**, TBD in config). |
| `corpus_too_thin` | `benchmark_fact_count` below configured minimum (default TBD). |
| `peer_not_accessible` | One or more peer URLs failed fetch/render/extract; `context.failed_peer_urls` lists them. |
| `target_not_accessible` | Target URL failed fetch/render/extract. |
| `serp_incomplete` | Fewer than 10 results returned from DataForSEO for the query. |

Caveats are **non-blocking**: they explain reliability; they do not suppress the score.

## Architecture (modules)

V1 is composed of **independent modules** orchestrated by a thin runner (no agent orchestration). Each module owns its inputs, scoring, and explainability payload.

| Module | Status | Role |
|--------|--------|------|
| **eligibility** | Spec in progress | SERP peers → corpus → coverage / gaps |
| **interpretability** | **On hold** | Technical page quality (planned: Screaming Frog). **No Q&A or implementation detail pinned yet.** |
| **attention** | Open | AI-related demand signals |
| **credibility** | Open | Observable trust / authority signals |
| **opportunity** | Open | Combines module outputs (formula TBD) |

### Interpretability module (hold)

- **Boundary:** Own package/module (e.g. `interpretability/`). Accepts crawl-derived inputs (format **TBD**). Returns `interpretability_score` (0–100) and `issues[]` per URL.
- **Hold:** Export format, check catalog, and SF workflow are **explicitly deferred**. Other modules must not assume interpretability has run.
- **Pipeline contract while on hold:**
  - Runner may **skip** the interpretability step.
  - Per-URL output includes `interpretability: null` (or omitted) and `modules.interpretability.status: "hold"` | `"skipped"` | `"ok"` when implemented later.
  - **Opportunity** when interpretability is skipped: **TBD** (e.g. renormalize gap weights across remaining components, or omit composite until module is live).

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

- Opportunity behavior when interpretability (or other modules) are skipped / on hold
- Default thresholds for `too_few_peers` and `corpus_too_thin`
- Fact schema, coverage math
- Content fetch for eligibility (Q8 — blocked on network spike)
- AI attention and credibility data sources for V1
- Deliverable shape (CLI, outputs on disk)

## Components (from instructions.md)

Unchanged unless noted above:

- **Opportunity** = AI Attention × weighted gap combination (weights/config TBD)
- **Interpretability** — Screaming Frog, deterministic
- **Credibility** — observable off-page signals (TBD for V1)
- **LLM** — judgement only (e.g. missing-fact importance), not orchestration
