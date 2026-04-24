import pandas as pd

import streamlit as st

import data.electricity as electricity
import src.util.data_util as data_util
import src.util.plot_util as plot_util

st.set_page_config(
    page_title="Utility Efficiency & Rates",
    page_icon="⚡",
    layout="wide"
)


@st.cache_data
def load_data(state: str) -> pd.DataFrame:
    utility = electricity.get_utility()
    df = pd.json_normalize(utility)
    state_df = data_util.get_state_data(state, df)
    return data_util.prepare_data(state_df), df


with st.sidebar:
    st.title("⚡ Controls")
    state = st.selectbox(
        "Select State",
        options=["NY", "CA", "TX", "FL", "PA", "IL", "OH"],
        index=0
    )
    st.markdown("---")
    st.markdown(
        "This app explores whether operational inefficiencies "
        "— energy losses and poor load factors — correlate with "
        "higher residential electricity rates."
    )
    st.markdown("[View on GitHub](https://github.com/chalseokorom/utilities-equity-efficiency-gap)")

state_df, full_df = load_data(state)

st.title("⚡ Electricity Utility Inefficiency & Residential Rate Analysis")
st.caption(
    f"Exploring {state} utilities — "
    f"{len(state_df)} utilities across "
    f"{state_df['Utility.Type'].nunique()} ownership models"
)
st.divider()

# ── Section 1: Fairness Audit ─────────────────────────────────
st.header("Fairness Audit — Efficiency vs. Residential Price")
st.caption(
    "Do utilities with higher energy losses or lower load factors "
    "charge residential customers more per MWh?"
)

scatter_df = data_util.get_residential_sys_loss(state_df)
scatter_df = data_util.get_residential_load_factor(scatter_df).round(2)

st.plotly_chart(
    plot_util.get_fairness_dual_y_scatter_plot(scatter_df),
    use_container_width=True
)
st.divider()

# ── Section 2: Ownership Models ───────────────────────────────
st.header("Ownership Model — Price Distribution")

sector = st.radio(
    "Customer sector",
    options=["Residential", "Industrial"],
    horizontal=True,
    label_visibility="collapsed"
)

sector_df = data_util.get_customer_utilities(state_df, sector).round(2)
st.plotly_chart(
    plot_util.get_utility_type_box_plot(sector_df, sector),
    use_container_width=True
)
st.divider()

# ── Section 3: Rate Disparity ─────────────────────────────────
st.header("Rate Disparity — Residential vs. Industrial")

n_utilities = st.slider(
    "Number of utilities to show",
    min_value=5, max_value=20, value=10, step=1
)

both_df = data_util.get_customer_utilities(state_df, "Both").round(2)
st.plotly_chart(
    plot_util.get_rate_disparity_dumbbell_plot(both_df, top_n=n_utilities),
    use_container_width=True
)
st.divider()

# ── Section 4: Energy Flow ────────────────────────────────────
st.header("Energy Flow — Sources & Uses")

col1, col2 = st.columns(2)

with col1:
    st.subheader(f"{state} Aggregate")
    state_flow = data_util.get_utility_usage(state_df.sum(), level="State")
    state_flow['Utility.Name'] = state  # label it as state name
    st.plotly_chart(
        plot_util.get_energy_use_sankey_plot(state_flow),
        use_container_width=True
    )

with col2:
    st.subheader("Individual Utility")
    utility_names = sorted(state_df['Utility.Name'].dropna().unique())
    selected_utility = st.selectbox("Select a utility", options=utility_names)
    utility_row = state_df[state_df['Utility.Name']
                           == selected_utility].iloc[0]
    utility_flow = data_util.get_utility_usage(utility_row, level="State")
    st.plotly_chart(
        plot_util.get_energy_use_sankey_plot(utility_flow),
        use_container_width=True
    )
