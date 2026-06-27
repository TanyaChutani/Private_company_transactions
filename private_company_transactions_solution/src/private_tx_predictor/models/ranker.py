from __future__ import annotations

import numpy as np
import pandas as pd


def score_features(features: pd.DataFrame, alpha: float = 0.018) -> pd.DataFrame:
    """Explainable calibrated fallback scorer.

    This is deterministic and works without historical labels. In production, replace the raw_score
    with LightGBM LambdaRank predictions and keep the same output contract.
    """
    df = features.copy()
    raw = df["rank_score_raw"].astype(float).fillna(0.0)
    # Saturating probability, avoids overconfidence from many duplicate articles.
    df["transaction_probability"] = (1 - np.exp(-alpha * raw * 10)).clip(0, 0.97)
    # Confidence reflects evidence breadth + source quality.
    breadth = np.log1p(df["event_count"].astype(float)) / np.log(10)
    reliability = (df["reliable_event_count"].astype(float) / df["event_count"].replace(0, np.nan)).fillna(0.0)
    df["confidence"] = (0.35 + 0.35 * breadth + 0.30 * reliability).clip(0.2, 0.95)
    df["rank_score"] = raw.rank(method="first", ascending=True) + raw
    df = df.sort_values(["transaction_probability", "confidence", "rank_score_raw"], ascending=False).reset_index(drop=True)
    df.insert(0, "rank", range(1, len(df) + 1))
    df["predicted_window"] = np.where(df["transaction_probability"] >= 0.75, "3-6 months", np.where(df["transaction_probability"] >= 0.45, "6-12 months", "watchlist"))
    return df


def train_lightgbm_ranker(feature_frame: pd.DataFrame, labels: pd.DataFrame):
    """Production training stub.

    Expected labels schema:
    - company_id
    - as_of_date
    - transacted_next_365d
    - group_id, e.g., quarter or industry-country cohort

    This function is intentionally optional because the take-home does not provide labels.
    """
    try:
        import lightgbm as lgb
    except Exception as exc:  # pragma: no cover
        raise RuntimeError("Install lightgbm to train the production ranker") from exc

    train = feature_frame.merge(labels, on="company_id", how="inner")
    feature_cols = [c for c in train.columns if c.endswith(("_30d", "_90d", "_180d", "_weighted")) or c in ["event_count", "reliable_event_count"]]
    train = train.sort_values("group_id")
    group_sizes = train.groupby("group_id").size().tolist()
    model = lgb.LGBMRanker(
        objective="lambdarank",
        metric="ndcg",
        n_estimators=300,
        learning_rate=0.05,
        num_leaves=31,
        random_state=42,
    )
    model.fit(train[feature_cols], train["transacted_next_365d"], group=group_sizes)
    return model, feature_cols
