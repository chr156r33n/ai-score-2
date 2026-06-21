# Spec Q&A — handoff for new agent runs

**Process:** Refine `spec/v1-spec.md` with the user **one question at a time**. Do not implement the full product until the spec pass is far enough along (unless the user asks).

**Read first:** `instructions.md` (original vision), `spec/v1-spec.md` (locked decisions), this file (progress).

**Repo state:** Draft spec and inputs live on branch `slack-cursor/url-keywords-input-c913` (PR #1). `data/urls_keywords.csv` is the canonical run input.

---

## Locked (questions 1–7)

| Q | Summary |
|---|---------|
| 1 | Score **per URL** (topics only support eligibility). |
| 2 | Eligibility corpus = **facts aggregated from comparison URLs**, not external PAA-first. |
| 3 | Peers = **top 10 organic SERP** via **DataForSEO**. |
| 4 | Keywords from **`data/urls_keywords.csv`** (exported from `cmm_keywords_0626.csv`). |
| 5 | SERP locale columns: **`region`**, **`language`**, **`device`**; defaults US / en / mobile; region inferred from URL slug (`scripts/property_regions.py`). |
| 6 | If target in top 10: **exclude, no backfill** (0–9 peers). |
| 7 | **Always score eligibility**; use **`eligibility_caveats`** (`no_peers`, `too_few_peers`, `corpus_too_thin`, `peer_not_accessible`, `target_not_accessible`, `serp_incomplete`). |
| 8 | **Interpretability = separate module, on hold** — defer SF/export/rules; pipeline runs without it. |
| 9 | **Facts = benchmark corpus only** — peer-derived fact list; target scored on coverage of that list, not an external taxonomy. |
| 10 | **Structured claim** — `topic`, `subject`, `predicate`, `object`, `statement`, `source_peer_urls`, stable `id`. |

---

## Blocked / in progress

### Question 8 — content fetch (network)

**Topic:** How to fetch peer + target HTML/content for fact extraction.

**Direction (pending validation):** Prefer **DataForSEO On-Page Instant Pages** so we avoid a custom scrape pipeline — **do not lock until spike passes**.

**Validation:**

```bash
python3 scripts/check_dataforseo_credentials.py
python3 scripts/spike_dataforseo_on_page.py \
  --keyword "four seasons abu dhabi" \
  --region AE \
  --language en \
  --device mobile \
  --target-url "https://www.fourseasons.com/abudhabi/"
```

- Checklist: `spec/spikes/dataforseo-on-page-validation.md`
- Cloud Agent env vars: **`dataforseo_user`**, **`dataforseo_pass`**
- After spike: record go/no-go in `spec/v1-spec.md` decision table; if no-go → hybrid (e.g. SF + On-Page for off-domain peers).

---

## Next questions (suggested order)

Ask **one at a time** (interpretability Q&A **paused — module on hold**):

1. **Fact representation** — Minimal JSON shape for corpus facts so dedup + target matching work (still **corpus-sourced**, not a global taxonomy).
2. **Coverage → eligibility_score** — Overlap % vs LLM-weighted missing **corpus** facts (per `instructions.md`).
3. **Opportunity formula** — Normalize gaps before × attention; behavior when interpretability/others skipped.
4. **AI attention** — Minimum viable signal for V1 (logs upload, placeholder, defer)?
5. **Credibility** — DataForSEO backlinks vs defer / domain-level stub?
6. **Deliverable** — CLI batch → JSON/CSV on disk for ~1.4k URLs?

---

## Prompt to paste when starting a fresh Cloud Agent

> Continue the AI Opportunity Framework **spec Q&A** from `spec/q-and-a-progress.md`. Ask the **next unanswered question only** (or run the DataForSEO spike first if credentials are available and Q8 is still open). Update `spec/v1-spec.md` when the user answers.
