from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Company:
    company_id: str
    company_name: str
    domain: str
    country: str
    industry: str
    aliases: tuple[str, ...]


@dataclass(frozen=True)
class PublicDocument:
    company_id: str
    company_name: str
    source: str
    publication_date: date
    title: str
    url: str
    snippet: str


@dataclass(frozen=True)
class ExtractedEvent:
    company_id: str
    company_name: str
    event_type: str
    event_date: date
    confidence: float
    source: str
    source_reliability: float
    title: str
    url: str
    evidence: str
