# Predicting Private-Company Transactions from Public Data

Proof of concept for Third Bridge's take-home assignment.

The POC predicts which private companies are most likely to enter a transaction in the next ~12 months using only public signals. It is designed as an **early-warning ranking system**, not a generic classifier.

## What this includes

- Public-news ingestion through GDELT Doc API
- Offline demo mode so the solution runs without internet/API keys
- Entity resolution using company aliases, domain, country and industry
- Hybrid event extraction: keyword filter -> rule/NER-like extraction -> LLM-ready JSON prompt template
- Time-windowed feature engineering: 30/90/180-day signals
- Explainable ranking model with LightGBM Ranker fallback to transparent weighted scoring
- Calibration-ready scoring contract
- Evidence trail for every score
- Backtest module using temporal train/test split
- Streamlit analyst dashboard
- Config-driven weights, thresholds and source reliability

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Offline demo: deterministic sample articles, no internet needed
python -m private_tx_predictor.cli score \
  --companies data/companies_sample.csv \
  --out outputs/predictions.csv \
  --offline-demo

# Open dashboard
streamlit run app.py
```

## Online mode

```bash
python -m private_tx_predictor.cli score \
  --companies data/companies_sample.csv \
  --out outputs/predictions.csv \
  --days 365
```

Online mode queries GDELT for public news snippets. It does not scrape private or restricted sources.


The POC is intentionally public-data-only. Offline mode ships with deterministic sample articles; online mode calls the public GDELT Doc API. In a production build, each source below becomes a separately cached collector so terms of use, coverage and freshness can be managed independently.

| Signal area | Public source in POC / production path | What it contributes | Notes |
|---|---|---|---|
| News and press | GDELT Doc API, Google News/RSS, company press pages | IPO, advisor, refinancing, strategic review, growth investment mentions | Used in runnable POC via GDELT/offline demo |
| Company identity | Company name, website, country, industry, aliases; OpenCorporates/Companies House where available | Entity resolution and ambiguity control | Avoids false matches like Bolt mobility vs Bolt fintech |
| Leadership/board | Company leadership pages, press releases, Companies House officer filings | CFO hires, board additions, founder exits | Web snapshots are stored and diffed |
| Hiring | Public career pages, Greenhouse, Lever, Ashby job boards | Hiring velocity, corp-dev/IR/CFO roles | No restricted LinkedIn scraping required |
| Patents | USPTO, EPO, Google Patents public pages/APIs | Innovation velocity and acquisition attractiveness | Optional collector in production |
| Public filings | SEC EDGAR, Companies House | debt, subsidiary, director and listing-preparation signals | Region-specific coverage |

## Architecture

```text
100k private companies
        |
Public signal collection: GDELT, RSS, EDGAR, patents, company sites, job boards
        |
Entity resolution: alias/domain/country/industry matching
        |
Hybrid extraction: keyword filter -> event extraction -> LLM-ready JSON
        |
Feature store: 30/90/180-day event counts, source reliability, trend signals
        |
Ranking engine: LightGBM LambdaRank / fallback weighted ranker
        |
Analyst workbench: ranked opportunities + evidence + confidence
```

## Why ranking instead of classification?

The commercial job is not to perfectly classify every private company. It is to help analysts review the right companies first. That makes the target metric Precision@100, Recall@500 and NDCG@100 rather than F1.

## Expected output

`outputs/predictions.csv` contains:

- company_name
- transaction_probability
- rank_score
- confidence
- strongest_signals
- evidence
- predicted_window

## Production path to 100k companies

For 100k companies:

- Run ingestion as Airflow DAGs
- Store raw/processed events as S3 Parquet
- Query with Athena or DuckDB for POC
- Maintain features in Feast or a warehouse feature table
- Batch inference daily on CPU
- Use LLM only after keyword/NER filtering, reducing cost by ~90%
- Capture analyst feedback and retrain monthly
