from __future__ import annotations

from datetime import date
import math
import pandas as pd
from private_tx_predictor.schemas import Company, ExtractedEvent


def recency_weight(event_date: date, as_of: date, half_life_days: int = 120) -> float:
    age = max(0, (as_of - event_date).days)
    return math.exp(-math.log(2) * age / half_life_days)


def build_feature_frame(companies: list[Company], events: list[ExtractedEvent], config: dict, as_of: date | None = None) -> pd.DataFrame:
    as_of = as_of or date.today()
    event_cfg = config.get("transaction_events", {})
    half_life = int(config.get("model", {}).get("half_life_days", 120))

    rows = []
    for company in companies:
        company_events = [e for e in events if e.company_id == company.company_id]
        row = {
            "company_id": company.company_id,
            "company_name": company.company_name,
            "country": company.country,
            "industry": company.industry,
            "event_count": len(company_events),
            "reliable_event_count": sum(1 for e in company_events if e.source_reliability >= 0.75),
        }
        total_signal = 0.0
        evidence = []
        for event_type, spec in event_cfg.items():
            typed = [e for e in company_events if e.event_type == event_type]
            base_weight = float(spec.get("weight", 1.0))
            val_30 = sum(1 for e in typed if (as_of - e.event_date).days <= 30)
            val_90 = sum(1 for e in typed if (as_of - e.event_date).days <= 90)
            val_180 = sum(1 for e in typed if (as_of - e.event_date).days <= 180)
            weighted = sum(base_weight * e.confidence * e.source_reliability * recency_weight(e.event_date, as_of, half_life) for e in typed)
            row[f"{event_type}_30d"] = val_30
            row[f"{event_type}_90d"] = val_90
            row[f"{event_type}_180d"] = val_180
            row[f"{event_type}_weighted"] = round(weighted, 4)
            total_signal += weighted
            for e in typed[:2]:
                evidence.append(f"{event_type}: {e.title} ({e.source})")
        row["rank_score_raw"] = round(total_signal, 4)
        row["evidence"] = " | ".join(evidence[:5])
        rows.append(row)
    return pd.DataFrame(rows)
