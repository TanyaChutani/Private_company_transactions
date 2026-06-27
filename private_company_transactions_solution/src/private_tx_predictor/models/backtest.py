from __future__ import annotations

import pandas as pd


def precision_at_k(scored: pd.DataFrame, label_col: str, k: int) -> float:
    top = scored.sort_values("transaction_probability", ascending=False).head(k)
    if len(top) == 0:
        return 0.0
    return float(top[label_col].sum() / len(top))


def recall_at_k(scored: pd.DataFrame, label_col: str, k: int) -> float:
    positives = scored[label_col].sum()
    if positives == 0:
        return 0.0
    top = scored.sort_values("transaction_probability", ascending=False).head(k)
    return float(top[label_col].sum() / positives)


def temporal_backtest_stub() -> dict[str, str]:
    return {
        "train_window": "2018-2023",
        "test_window": "2024",
        "primary_metrics": "Precision@100, Recall@500, NDCG@100",
        "business_metric": "Share of announced transactions surfaced at least 90 days before announcement",
        "leakage_control": "features computed only from documents published before as_of_date",
    }
