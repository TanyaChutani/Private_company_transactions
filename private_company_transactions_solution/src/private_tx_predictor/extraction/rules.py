from __future__ import annotations

import re
from datetime import date
from private_tx_predictor.schemas import PublicDocument, ExtractedEvent


def source_reliability(source: str, config: dict) -> float:
    domain = source.lower().replace("www.", "")
    mapping = config.get("source_reliability", {})
    for key, val in mapping.items():
        if key != "default" and key in domain:
            return float(val)
    return float(mapping.get("default", 0.55))


def extract_events(docs: list[PublicDocument], config: dict) -> list[ExtractedEvent]:
    """Hybrid extraction POC.

    In production, this is Stage 1 keyword filtering + Stage 2 NER + Stage 3 LLM JSON extraction.
    This runnable version implements deterministic extraction for repeatability and an evidence trail.
    """
    events: list[ExtractedEvent] = []
    event_cfg = config.get("transaction_events", {})

    for doc in docs:
        text = f"{doc.title}. {doc.snippet}".lower()
        for event_type, spec in event_cfg.items():
            matched_terms = [kw for kw in spec.get("keywords", []) if re.search(r"\b" + re.escape(kw.lower()) + r"\b", text)]
            if not matched_terms:
                continue
            rel = source_reliability(doc.source, config)
            confidence = min(0.98, 0.55 + 0.1 * len(matched_terms) + 0.25 * rel)
            events.append(
                ExtractedEvent(
                    company_id=doc.company_id,
                    company_name=doc.company_name,
                    event_type=event_type,
                    event_date=doc.publication_date or date.today(),
                    confidence=round(confidence, 3),
                    source=doc.source,
                    source_reliability=rel,
                    title=doc.title,
                    url=doc.url,
                    evidence="; ".join(matched_terms[:3]),
                )
            )
    return events
