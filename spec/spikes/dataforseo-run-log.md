# DataForSEO spike run log

## 2025-06-21 — Cloud Agent (incomplete)

**Environment:** Cursor Cloud Agent, branch `main` at time of run.

**Commands:**

```bash
python3 scripts/check_dataforseo_credentials.py

python3 scripts/spike_dataforseo_on_page.py \
  --keyword "four seasons abu dhabi" \
  --region AE \
  --language en \
  --device mobile \
  --target-url "https://www.fourseasons.com/abudhabi/"
```

### Credentials

| Check | Result |
|-------|--------|
| `DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD` in env | Not set under those names |
| Runtime Secrets `dataforseo_user` / `dataforseo_pass` | Present (`CLOUD_AGENT_ALL_SECRET_NAMES`) |
| After client alias support (same run session, manual export) | Login/password available to scripts |

**Conclusion:** Secrets were configured in the agent environment but under legacy names; scripts now accept both naming schemes.

### API connectivity

| Host | Result |
|------|--------|
| `https://api.dataforseo.com` | TLS handshake fails: `SSL_ERROR_SYSCALL` / `UNEXPECTED_EOF_WHILE_READING` (TCP connects, no server certificate) |
| `https://dataforseo.com` | Same TLS failure |
| `https://api.github.com` | OK (control: general HTTPS from VM works) |

**Conclusion:** Could not validate credentials or run SERP/Instant Pages from this Cloud Agent network. Blocker is **egress to DataForSEO**, not missing secrets.

### Spike criteria (go / no-go)

| Criterion | Status |
|-----------|--------|
| SERP ≥ 90% with 10 organics | **Not tested** |
| Fetch ≥ 80% via Instant Pages | **Not tested** |
| Fields for fact extraction | **Not tested** |
| Cost / latency | **Not tested** |

**Decision:** **No-go for automated validation in Cloud Agent** until `api.dataforseo.com` is reachable from the agent VM (or spike is re-run locally / CI with allowed egress).

### Follow-up

1. Re-run `check_dataforseo_credentials.py` after network fix; expect exit `0` and balance line if auth is valid.
2. Re-run `spike_dataforseo_on_page.py` for 2–3 keywords; commit artifact summaries or paste key metrics into this log.
3. Optionally rename Runtime Secrets to `DATAFORSEO_LOGIN` / `DATAFORSEO_PASSWORD` for consistency with docs.

### `check_dataforseo_credentials.py` exit codes

| Code | Meaning |
|------|---------|
| 1 | Credentials not in environment |
| 2 | HTTP/API error from DataForSEO |
| 3 | Unexpected API `status_code` |
| 4 | Network/TLS failure reaching `api.dataforseo.com` |
