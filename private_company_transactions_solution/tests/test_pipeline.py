from private_tx_predictor.config import load_config
from private_tx_predictor.ingestion.companies import load_companies
from private_tx_predictor.ingestion.demo import load_demo_documents
from private_tx_predictor.extraction.rules import extract_events
from private_tx_predictor.features.build_features import build_feature_frame
from private_tx_predictor.models.ranker import score_features


def test_offline_pipeline_runs():
    config = load_config("configs/signals.yaml")
    companies = load_companies("data/companies_sample.csv")
    docs = load_demo_documents("data/demo_articles.csv", companies)
    events = extract_events(docs, config)
    features = build_feature_frame(companies, events, config)
    scored = score_features(features)
    assert len(scored) == len(companies)
    assert scored["transaction_probability"].max() > 0
    assert scored.iloc[0]["rank"] == 1
