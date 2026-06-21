# Spike: DataForSEO for SERP + page content (go / no-go)

**Goal:** Confirm we can rely on DataForSEO for **top-10 SERP** and **peer/target page content** so V1 does not need a custom scrape pipeline.

**Not a spec lock** until this spike passes the criteria below.

## APIs under test

| Step | API | Typical endpoint | Purpose |
|------|-----|------------------|---------|
| Peers | SERP Google Organic | `v3/serp/google/organic/live/advanced` | Top 10 for `primary_keyword` + locale |
| Content | On-Page **Instant Pages** | `v3/on_page/instant_pages` | Fetch + parse a single URL (good for SERP peers) |
| Content (alt) | On-Page Task | `v3/on_page/task_post` + `task_get` | Heavier; use only if Instant Pages fails too often |

Instant Pages is the first choice for validation: one URL per task, structured fields in the response, optional `enable_javascript`.

Official reference: [On-Page API](https://dataforseo.com/apis/on-page-api) and [SERP API](https://dataforseo.com/apis/serp-api) (use their docs for exact request bodies).

## Sample URLs (suggested)

Run against **15–25 URLs** total:

1. **5 Four Seasons targets** from `data/urls_keywords.csv` (mix US + non-US `region`).
2. **10 SERP peers** — take 2 keywords, run SERP, exclude target (per spec), crawl remaining peers.
3. **5 “hard” pages** — known JS-heavy or bot-sensitive URLs in your vertical (competitor booking engines, etc.).

Record keyword, region, language, device for each SERP call.

## Pass / fail criteria

### Must pass (go)

- [ ] **SERP:** ≥ 90% of sample keywords return 10 organic results (or caveat `serp_incomplete` is acceptable if documented).
- [ ] **Fetch:** ≥ **80%** of peer + target URLs return **200** with parseable body via Instant Pages (`enable_javascript: true`).
- [ ] **Fields:** Response includes enough structure for **deterministic fact extraction** without raw HTML soup as the only source — e.g. `title`, `meta`, heading list, `main_topic` / `plain_text` or `content` (exact keys per API version), and **JSON-LD / microdata** when present on page.
- [ ] **Cost:** Document **$/URL** and **$/keyword** (SERP + 10 peers + 1 target) from API `cost` fields; acceptable for ~1.4k URL batch (or agreed subset).
- [ ] **Latency:** Order-of-magnitude time for 1 full eligibility unit (1 SERP + up to 10 peers + 1 target) is acceptable for batch (note seconds per unit).

### Should pass (prefer go)

- [ ] JS on vs off: material difference on FS pages documented; default chosen (`enable_javascript: true` recommended for hospitality).
- [ ] Failed URLs align with spec caveats (`peer_not_accessible`, `target_not_accessible`) — no silent empty success.
- [ ] Same URL fetched twice within 24h gives **stable enough** text for fact overlap (not necessarily byte-identical).

### Fail (no-go → hybrid)

- [ ] Widespread blocks, empty content, or paywall shells on **>30%** of hospitality peers.
- [ ] Schema/headings consistently missing; only useless boilerplate in text fields.
- [ ] Cost or rate limits make full 1.4k run impractical without a different architecture.

**No-go fallback (spec option C):** SF export for on-domain targets + Instant Pages only for off-domain peers, or limited live fetch for failures only.

## How to run the automated spike

**Cloud Agent secrets** (Runtime Secret, scoped to this repo environment):

| Name | Value |
|------|--------|
| `DATAFORSEO_LOGIN` | API login |
| `DATAFORSEO_PASSWORD` | API password |

Names must match exactly. After adding secrets, **start a new Cloud Agent run** so they are injected (they may not appear in `printenv`).

```bash
python3 scripts/check_dataforseo_credentials.py

python3 scripts/spike_dataforseo_on_page.py \
  --keyword "four seasons abu dhabi" \
  --region AE \
  --language en \
  --device mobile \
  --target-url "https://www.fourseasons.com/abudhabi/"
```

Output: `artifacts/spike/dataforseo_<timestamp>.json` with SERP URLs, per-URL fetch status, field presence checklist, and costs.

Repeat for 2–3 keywords manually, then spot-check JSON against the criteria above.

## Manual validation (no code)

1. DataForSEO dashboard → API Explorer / trial requests for **Instant Pages** on one FS URL and one Marriott/Hilton peer.
2. Confirm response JSON structure matches what the script expects; adjust field mapping in the spike script if names differ.
3. Compare one page to “what you’d want in benchmark facts” (policies, amenities, location facts) — qualitative gut check.

## Decision record

After spike, update `spec/v1-spec.md`:

- Lock **On-Page Instant Pages** (or task-based crawl), **or**
- Lock **hybrid** with explicit rules.

Link the artifact JSON path and date in the spec decision table.
