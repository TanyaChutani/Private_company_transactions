# Public data sourcing plan

This POC uses public and legitimately available sources only. The runnable offline mode uses `data/demo_articles.csv`. Online mode uses the public GDELT Doc API.

Production collectors should be independently rate-limited, cached and logged:

1. News and press: GDELT, RSS feeds, company press pages.
2. Company identity: company name, domain, country, industry and aliases, optionally enriched with OpenCorporates or Companies House.
3. Leadership and board changes: company leadership page snapshots, press releases and public officer filings.
4. Hiring signals: public career pages and ATS endpoints such as Greenhouse, Lever and Ashby.
5. Patents: USPTO, EPO and public Google Patents pages/APIs.
6. Filings: SEC EDGAR and Companies House where relevant.

Each collected document keeps `source`, `url`, `publication_date`, `company_id`, `raw_text_hash` and `terms_classification` metadata so quality and provenance can be audited.
