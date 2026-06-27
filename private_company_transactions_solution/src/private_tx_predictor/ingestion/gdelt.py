from __future__ import annotations

from datetime import date, datetime, timedelta
import requests

from private_tx_predictor.schemas import Company, PublicDocument


GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"


def _safe_date(value: str) -> date:
    # GDELT sometimes returns YYYYMMDDHHMMSS
    for fmt in ("%Y%m%d%H%M%S", "%Y%m%d"):
        try:
            return datetime.strptime(value[: len(datetime.now().strftime(fmt))], fmt).date()
        except Exception:
            pass
    return date.today()


def fetch_gdelt_documents(companies: list[Company], days: int = 365, max_per_company: int = 10) -> list[PublicDocument]:
    """Fetch public news snippets from GDELT.

    This uses only the public GDELT API. In production, this would be wrapped in retry,
    caching and rate-limit controls and materialized into S3 parquet partitions.
    """
    docs: list[PublicDocument] = []
    start = (date.today() - timedelta(days=days)).strftime("%Y%m%d%H%M%S")
    end = date.today().strftime("%Y%m%d%H%M%S")

    for company in companies:
        query = f'"{company.company_name}" private company'
        params = {
            "query": query,
            "mode": "ArtList",
            "format": "json",
            "maxrecords": max_per_company,
            "sort": "HybridRel",
            "startdatetime": start,
            "enddatetime": end,
        }
        try:
            resp = requests.get(GDELT_DOC_API, params=params, timeout=12)
            resp.raise_for_status()
            payload = resp.json()
        except Exception:
            continue

        for item in payload.get("articles", []):
            title = item.get("title", "") or ""
            url = item.get("url", "") or ""
            source = item.get("domain", "") or item.get("sourcecountry", "unknown")
            seen = item.get("seendate", "")
            docs.append(
                PublicDocument(
                    company_id=company.company_id,
                    company_name=company.company_name,
                    source=source,
                    publication_date=_safe_date(seen),
                    title=title,
                    url=url,
                    snippet=item.get("seendate", "") + " " + title,
                )
            )
    return docs
