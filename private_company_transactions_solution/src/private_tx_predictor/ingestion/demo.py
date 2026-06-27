from __future__ import annotations

from datetime import datetime
import pandas as pd
from private_tx_predictor.schemas import Company, PublicDocument


def load_demo_documents(path: str, companies: list[Company]) -> list[PublicDocument]:
    company_ids = {c.company_name.lower(): c.company_id for c in companies}
    df = pd.read_csv(path).fillna("")
    docs: list[PublicDocument] = []
    for r in df.to_dict("records"):
        name = str(r["company_name"])
        docs.append(
            PublicDocument(
                company_id=company_ids.get(name.lower(), name.lower().replace(" ", "_")),
                company_name=name,
                source=str(r["source"]),
                publication_date=datetime.strptime(str(r["publication_date"]), "%Y-%m-%d").date(),
                title=str(r["title"]),
                url=str(r["url"]),
                snippet=str(r["snippet"]),
            )
        )
    return docs
