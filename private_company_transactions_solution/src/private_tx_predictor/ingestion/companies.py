from __future__ import annotations

import pandas as pd
from private_tx_predictor.schemas import Company


def load_companies(path: str) -> list[Company]:
    df = pd.read_csv(path).fillna("")
    companies: list[Company] = []
    for row in df.to_dict("records"):
        aliases = tuple(a.strip() for a in str(row.get("aliases", "")).split(";") if a.strip())
        companies.append(
            Company(
                company_id=str(row["company_id"]),
                company_name=str(row["company_name"]),
                domain=str(row.get("domain", "")),
                country=str(row.get("country", "")),
                industry=str(row.get("industry", "")),
                aliases=aliases,
            )
        )
    return companies
