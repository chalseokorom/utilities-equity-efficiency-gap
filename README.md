---
title: Utility Efficiency & Rates
emoji: ⚡
colorFrom: blue
colorTo: yellow
sdk: streamlit
sdk_version: "1.56.0"
app_file: streamlit_app.py
pinned: false
---


# Electricity Utility Fairness Residential Rate Analysis

> **Research Question:** Are system-level inefficiencies — high energy losses and poor load factors — statistically correlated with higher retail rates for residential consumers?

---

## Overview

This project investigates a fundamental fairness question in the U.S. electricity sector: do residential customers end up paying more when their utility operates inefficiently? Using the [CORGIS Electricity Dataset](https://corgis-edu.github.io/corgis/), this analysis builds a set of derived efficiency and equity metrics, then examines their statistical relationships through a suite of interactive visualizations.

New York State serves as the primary case study. NY was selected through a data-driven ranking process (get_state_variance) that scores all 50 states across five analytical criteria: number of utilities, number of ownership types, residential price standard deviation, maximum system loss percentage, and industrial revenue dependency. New York ranks at or near the top on all five: it has over 100 utilities across 6 distinct ownership models, exhibits high residential price variance, and sits within one of the most actively scrutinized regulatory environments in the U.S.

[![Open in Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)

---

## Key Metrics

| Metric | Description |
|---|---|
| `System Loss Percentage` | Energy lost in transmission/distribution as % of total supply |
| `Load Factor` | Ratio of actual energy delivered to theoretical maximum (demand efficiency) |
| `Residential Unit Price` | Residential rate in $/MWh |
| `Industrial Unit Price` | Industrial rate in $/MWh |
| `Price Spread` | Gap between residential and industrial rates (equity indicator) |
---

## Visualizations

- **State Selection Table** — Ranking of top 10 states by analytical richness; justifies NY case study
- **Price Spread Strip Plot** — Residential premium over industrial rates by ownership model
- **Correlation Heatmap** — Statistical significance matrix across all key metrics
- **Fairness Audit Scatter** — System loss (%) and load factor (dual y-axis) vs. residential price by ownership model, with OLS trendline
- **Rate Disparity Dumbbell** — Top 10 utilities by residential–industrial price gap
- **Energy Flow Sankey Diagram (State)** — Per-state (or utility) breakdown of energy sources and uses as percentages 
- **Energy Flow Sankey Diagram (US)** — National aggregate energy flow

---

## Project Structure

```
.
├── utility_efficiency_fairness.ipynb
├── streamlit_app.py
├── requirements.txt
├── README.md
├── data/
│   └── electricity.py
│   └── app.py
│   └── electricity.data
│   └── electricity.data
├── src/
│   └── util/         
```

The three modules work as a clean pipeline:
- **`electricity`** — CORGIS data loader (unmodified third-party)
- **`data_util`** — all data preparation, filtering, and metric engineering
- **`plot_util`** — all chart construction and SVG expor

### `util.py` — Helper Functions

| Function | Purpose |
|---|---|
| `prepare_data(df)` | Calculates key metrics and other features from raw columns |
| `get_state_data(state, df)` | Filters and subsets data for a given state |
| `get_state_variance(df)` | Ranks states by residential price variance (for state selection) |
| `get_customer_utilities(df, customer)` | Filters utilities by customer type served |
| `get_residential_load_factor(df)` | Subset with valid load factor for residential utilities |
| `get_residential_sys_loss(df)` | Subset with valid loss % for residential utilities |
| `get_utility_usage(utility)` | Converts raw MWh values to % of total supply for Sankey |

---

## Setup & Usage

- The dataset is pre-bundled — no external downloads required for it.
- Run `jupytr notebook utility_efficiency_fairness.ipynb.`
- Run `pip install pandas plotly scipy kaleido streamlit`

---

## Data Source

**[CORGIS Electricity Dataset](https://corgis-edu.github.io/corgis/python/electricity/)** — a cleaned and structured snapshot of U.S. Energy Information Administration (EIA) [Form 861](https://www.eia.gov/electricity/data/eia861/) data, covering utility-level electricity generation, sales, revenues, and customer counts across all U.S. states.

---

## Potential Extensions

- Expand the analysis to all 50 states and compare regional patterns
- Incorporate time-series data to track changes in efficiency and pricing
- Apply regression modeling to control for utility size and customer density
- Explore the role of renewable energy mix on system loss rates
