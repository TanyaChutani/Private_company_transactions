from __future__ import annotations

import argparse
from pathlib import Path

from private_tx_predictor.config import load_config
from private_tx_predictor.ingestion.companies import load_companies
from private_tx_predictor.ingestion.demo import load_demo_documents
from private_tx_predictor.ingestion.gdelt import fetch_gdelt_documents
from private_tx_predictor.extraction.rules import extract_events
from private_tx_predictor.features.build_features import build_feature_frame
from private_tx_predictor.models.ranker import score_features
from private_tx_predictor.product.reporting import analyst_columns


def score_command(args: argparse.Namespace) -> None:
    config = load_config(args.config)
    companies = load_companies(args.companies)

    if args.offline_demo:
        docs = load_demo_documents(args.demo_articles, companies)
    else:
        docs = fetch_gdelt_documents(companies, days=args.days, max_per_company=args.max_per_company)

    events = extract_events(docs, config)
    features = build_feature_frame(companies, events, config)
    scored = score_features(features, alpha=float(config.get("model", {}).get("calibration_alpha", 0.018)))

    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    scored.to_csv(out_path, index=False)

    analyst = analyst_columns(scored)
    print("\nTop transaction candidates\n")
    print(analyst.head(args.top).to_string(index=False))
    print(f"\nSaved full predictions to {out_path}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Predict private-company transactions from public data")
    sub = parser.add_subparsers(dest="command", required=True)
    p = sub.add_parser("score", help="Score private companies")
    p.add_argument("--companies", required=True)
    p.add_argument("--out", default="outputs/predictions.csv")
    p.add_argument("--config", default="configs/signals.yaml")
    p.add_argument("--offline-demo", action="store_true")
    p.add_argument("--demo-articles", default="data/demo_articles.csv")
    p.add_argument("--days", type=int, default=365)
    p.add_argument("--max-per-company", type=int, default=10)
    p.add_argument("--top", type=int, default=10)
    p.set_defaults(func=score_command)
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
