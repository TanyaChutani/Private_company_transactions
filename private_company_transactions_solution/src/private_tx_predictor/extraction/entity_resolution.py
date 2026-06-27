from __future__ import annotations

from difflib import SequenceMatcher
from private_tx_predictor.schemas import Company, PublicDocument


def match_company(doc: PublicDocument, companies: list[Company]) -> tuple[str, float]:
    """Resolve company mention to known universe.

    Production version should use embeddings + domain/country/industry constraints.
    This POC uses deterministic name/alias fuzzy matching so it runs locally.
    """
    text = f"{doc.company_name} {doc.title} {doc.snippet}".lower()
    best_id = doc.company_id
    best_score = 0.0
    for c in companies:
        candidates = [c.company_name, *c.aliases, c.domain]
        score = max(SequenceMatcher(None, cand.lower(), text[: max(40, len(cand))]).ratio() for cand in candidates if cand)
        if c.company_name.lower() in text or any(a.lower() in text for a in c.aliases):
            score = max(score, 0.98)
        if score > best_score:
            best_id, best_score = c.company_id, score
    return best_id, round(best_score, 3)
