from __future__ import annotations

from pathlib import Path
import pandas as pd
import streamlit as st
import plotly.express as px

st.set_page_config(page_title="Private Company Transaction Predictor", layout="wide")
st.title("Predicting Private-Company Transactions from Public Data")
st.caption("Early-warning ranking view for analysts: public signals, confidence and evidence trail.")

path = Path("outputs/predictions.csv")
if not path.exists():
    st.warning("Run the scoring pipeline first: python -m private_tx_predictor.cli score --companies data/companies_sample.csv --out outputs/predictions.csv --offline-demo")
    st.stop()

df = pd.read_csv(path)

left, right = st.columns([2, 1])
with left:
    st.subheader("Top ranked companies")
    st.dataframe(df[["rank", "company_name", "transaction_probability", "confidence", "predicted_window", "evidence"]], use_container_width=True)
with right:
    st.subheader("Probability distribution")
    fig = px.bar(df.head(10), x="company_name", y="transaction_probability", title="Top 10")
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Company evidence")
selected = st.selectbox("Select company", df["company_name"].tolist())
row = df[df["company_name"] == selected].iloc[0]
st.metric("Transaction probability", f"{row['transaction_probability']:.1%}")
st.metric("Confidence", f"{row['confidence']:.1%}")
st.write(row["evidence"] if isinstance(row["evidence"], str) and row["evidence"] else "No evidence found")
