from __future__ import annotations

from dataclasses import dataclass
import pandas as pd


@dataclass(frozen=True)
class PublicSource:
    source_name: str
    signal_area: str
    access_type: str
    used_in_poc: bool
    production_use: str
    quality_notes: str


def load_source_manifest(path: str = "data/public_source_manifest.csv") -> list[PublicSource]:
    """Load the public-source manifest used to explain where data comes from."""
    df = pd.read_csv(path).fillna("")
    sources: list[PublicSource] = []
    for row in df.to_dict("records"):
        sources.append(
            PublicSource(
                source_name=str(row["source_name"]),
                signal_area=str(row["signal_area"]),
                access_type=str(row["access_type"]),
                used_in_poc=str(row["used_in_poc"]).strip().lower() == "yes",
                production_use=str(row["production_use"]),
                quality_notes=str(row["quality_notes"]),
            )
        )
    return sources
