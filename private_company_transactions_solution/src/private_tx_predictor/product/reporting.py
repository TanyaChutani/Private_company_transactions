from __future__ import annotations

import pandas as pd


def analyst_columns(scored: pd.DataFrame) -> pd.DataFrame:
    cols = [
        "rank",
        "company_name",
        "transaction_probability",
        "confidence",
        "predicted_window",
        "rank_score_raw",
        "evidence",
    ]
    out = scored[cols].copy()
    out["transaction_probability"] = (out["transaction_probability"] * 100).round(1).astype(str) + "%"
    out["confidence"] = (out["confidence"] * 100).round(1).astype(str) + "%"
    return out
