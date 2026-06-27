from __future__ import annotations

EVENT_SCHEMA = {
    "event_type": "IPO_PREP | BANK_HIRED | BOARD_CHANGE | CFO_HIRE | STRATEGIC_REVIEW | DEBT_REFINANCING | SECONDARY_SALE | GROWTH_INVESTMENT | ACQUISITION_SIGNAL | NONE",
    "company_name": "string",
    "confidence": "float 0-1",
    "evidence": "short quote or paraphrase",
    "transaction_window_hint": "0-3m | 3-6m | 6-12m | unknown",
}


def build_event_extraction_prompt(company_name: str, title: str, text: str) -> str:
    return f"""
You are extracting early warning signals that a private company may enter a transaction in the next 12 months.

Company: {company_name}
Title: {title}
Text: {text}

Allowed event types:
- IPO_PREP
- BANK_HIRED
- BOARD_CHANGE
- CFO_HIRE
- STRATEGIC_REVIEW
- DEBT_REFINANCING
- SECONDARY_SALE
- GROWTH_INVESTMENT
- ACQUISITION_SIGNAL
- NONE

Return JSON only with this schema:
{EVENT_SCHEMA}

Rules:
- Do not infer beyond the text.
- If the article is only generic growth news, use NONE or low confidence.
- Include evidence that supports the event.
""".strip()
