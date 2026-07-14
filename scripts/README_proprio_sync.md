# Sync Proprio Direct listings (Sabrina Lagassé)

Discovers listings from [Sabrina’s Proprio Direct page](https://propriodirect.com/sabrina-lagasse/), downloads full photo galleries from Centris (fallback: Proprio Direct CDN for sold listings), generates a **1200×630** social share image per property, rebuilds `proprietes.html` + SEO detail pages, and updates homepage map pins.

> Note: Sabrina lists with **Proprio Direct** (not DuProprio). Same sync engine as the Mélanie Fafard site.

## Local run

```bash
pip install -r scripts/requirements.txt
python scripts/proprio_sync.py
```

Useful flags:

- `--exclude-sold` — active listings only
- `--max-listings 10`
- `--skip-generate` — sync images/JSON only

## Outputs

- `data/properties.json` — registry
- `data/listings_sync.json` — sync report
- `data/transaction_pins.json` — map pins (street name only)
- `assets/img/proprietes/<uls>/`
- `proprietes.html` + `ca/qc/.../`

## GitHub Actions

Workflow: `.github/workflows/proprio-sync.yml` (daily + manual).

Optional repo variable: `PROPRIO_AGENT_URL` (default `https://propriodirect.com/sabrina-lagasse/`).
