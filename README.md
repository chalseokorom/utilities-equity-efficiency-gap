# ⚡ Electricity Utility Inefficiency & Residential Rate Analysis

> **Research Question:** Are system-level inefficiencies — high energy losses and poor load factors — statistically correlated with higher retail rates for residential consumers?

---

## Overview

This project investigates a fundamental fairness question in the U.S. electricity sector: do residential customers end up paying more when their utility operates inefficiently? Using the [CORGIS Electricity Dataset](https://corgis-edu.github.io/corgis/), this analysis builds a set of derived efficiency and equity metrics, then examines their statistical relationships through a suite of interactive visualizations.

The analysis focuses on **New York State** utilities as a case study, comparing investor-owned, municipal, cooperative, and other utility ownership models. New York was chosen BECAUSE 

---

## Key Metrics

| Metric | Description |
|---|---|
| `SystemLossPercentage` | Energy lost in transmission/distribution as % of total supply |
| `LoadFactor` | Ratio of actual energy delivered to theoretical maximum (demand efficiency) |
| `ResidentialUnitPrice` | Residential rate in $/MWh |
| `IndustrialUnitPrice` | Industrial rate in $/MWh |
| `PriceSpread` | Gap between residential and industrial rates (equity indicator) |
| `FairnessIndex` | Residential price normalized by load factor (equity/burden metric) |

---

## Visualizations

- **State Selection Table** — Ranking of top 10 states by analytical richness; justifies NY case study
- **Residential Price Box Plot** — Distribution of residential rates across ownership models
- **Industrial Price Box Plot** — Distribution of industrial rates across ownership models
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
├── data/
│   └── electricity.py
│   └── electricity.data
├── src/
│   └── util/
│       ├── data_util.py
│       └── plot_util.py
└── images/            
```

The three modules work as a clean pipeline:
- **`electricity`** — CORGIS data loader (unmodified third-party)
- **`data_util`** — all data preparation, filtering, and metric engineering
- **`plot_util`** — all chart construction and SVG expor

### `util.py` — Helper Functions

| Function | Purpose |
|---|---|
| `prepare_data(df)` | Engineers all derived metrics from raw columns |
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
- Run pip install pandas plotly scipy kaleido

---

## Data Source

**[CORGIS Electricity Dataset](https://corgis-edu.github.io/corgis/python/electricity/)** — a cleaned and structured snapshot of U.S. Energy Information Administration (EIA) [Form 861](https://www.eia.gov/electricity/data/eia861/) data, covering utility-level electricity generation, sales, revenues, and customer counts across all U.S. states.

---

## Potential Extensions

- Expand the analysis to all 50 states and compare regional patterns
- Incorporate time-series data to track changes in efficiency and pricing
- Apply regression modeling to control for utility size and customer density
- Explore the role of renewable energy mix on system loss rates