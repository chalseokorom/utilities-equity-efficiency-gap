""" Functions to create and retrieves interactive plotly charts  """

import os

import pandas as pd
import numpy as np

from scipy.stats import linregress

import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio

from plotly.subplots import make_subplots


def get_state_variance_table(df: pd.DataFrame) -> go.Figure:
    """Retrieve table of states with highest mean residential unit price"""
    target, row_h, header_h = 7, 35, 50

    fig = go.Figure(go.Table(
        header=dict(
            values=list(df.columns),
            fill_color='#f8f9fa',
            font=dict(size=12, family="Arial Black",),
            align='center',
            height=header_h
        ),
        cells=dict(
            values=df.values.T,
            fill_color=[['dodgerblue' if i ==
                         target else 'white' for i in range(10)]],
            font=dict(
                color=[['white' if i == target else 'black' for i in range(10)]], size=12),
            height=row_h, align='center',
            format=[None, None, None, ".2f", ".2f", ".2f"]
        )
    ))

    fig.update_layout(
        margin=dict(l=5, r=5, t=5, b=5),
        height=row_h * (len(df) + 2),
        autosize=False
    )

    return fig


def get_utility_type_box_plot(df: pd.DataFrame, sector: str) -> go.Figure:
    """Compare Price across Utility Types based on sector string"""

    unit_price_col = f"{sector}UnitPrice"
    customer_col = f"Retail.{sector}.Customers"

    fig = px.box(df, x='Utility.Type', y=unit_price_col, color="Utility.Type",
                 points="all", hover_name="Utility.Name",
                 hover_data=[customer_col, "LoadFactor"],
                 color_discrete_sequence=px.colors.qualitative.Prism,
                 title=f"<b>Utility Type:</b> {sector} Price Distribution",
                 labels={"Utility.Type": "Ownership Model",
                         unit_price_col: f"{sector} Rate",
                         customer_col: "Customer Count",
                         "LoadFactor": "Load Factor"},
                 template='plotly_white')

    fig.update_layout(
        xaxis_title="",
        yaxis_title=f"{sector} Rate ($/MWh)")

    return fig


def get_key_metrics_corr_matrix(df: pd.DataFrame) -> go.Figure:
    """Correlation matrix for key analysis metrics"""
    key_metrics = {
        'SystemLossPercentage': 'System Loss %',
        'LoadFactor': 'Load Factor',
        'IndustrialRevenueRatio': 'Industrial Revenue %',
        'PriceSpread': 'Price Spread',
        'FairnessIndex': 'Fairness Index'
    }

    corr_matrix = df[list(key_metrics.keys())].corr()

    return px.imshow(
        corr_matrix.round(2),
        x=list(key_metrics.values()),
        y=list(key_metrics.values()),
        color_continuous_scale='mint',
        text_auto=True,
        aspect="auto",
        title='<b>Statistical Significance:</b> Correlation Heatmap of Key Metrics',
        labels=dict(color="Score"),
        template='plotly_white')


def add_fairness_trendline(fig: go.Figure, x_data: pd.Series,
                           y_data: pd.Series, row: int, col: int) -> None:
    """Calculates OLS and adds centered stats inside the plot to avoid title overlap."""
    mask = ~np.isnan(x_data) & ~np.isnan(y_data)
    x_clean, y_clean = x_data[mask], y_data[mask]

    if len(x_clean) > 1:
        # Get linear regression
        result = linregress(x_clean, y_clean)

        # Trendline coordinates
        x_range = np.array([x_clean.min(), x_clean.max()])
        y_range = result.slope * x_range + result.intercept

        # Add Trendline
        fig.add_trace(
            go.Scatter(
                x=x_range, y=y_range,
                mode='lines',
                line=dict(color='black', width=2, dash='dash'),
                name='Overall Trend',
                legendgroup='trendline',
                showlegend=(row == 1 and col == 1),
                hoverinfo='skip'
            ), row=row, col=col)

        # 2. Annotation stats box
        fig.add_annotation(
            xref=f"x{col if col > 1 else ''} domain",
            yref="y domain",
            x=0.5,              # Horizontal center
            y=0.92,             # Lowered to 92% of height (inside the plot)
            xanchor="center",
            yanchor="top",      # Box hangs downward from the y=0.92 point
            text=f"<b>R²:</b> {result.rvalue**2:.3f}  |  <b>p:</b> {result.pvalue:.4e}",
            showarrow=False,
            align="center",
            # High opacity for readability
            bgcolor="rgba(255, 255, 255, 0.85)",
            bordercolor="rgba(0,0,0,0.3)",
            borderwidth=1,
            font=dict(size=10))


def get_fairness_dual_y_scatter_plot(df: pd.DataFrame) -> go.Figure:
    """Get dual y-axis scatter plot of utility fairness metrics"""
    fig = make_subplots(
        rows=1, cols=2,
        shared_yaxes=True,
        horizontal_spacing=0.05,
        subplot_titles=('<b>System Loss vs Price</b>',
                        '<b>Load Factor vs Price</b>'))

    df['BubbleSize'] = np.log1p(df['Retail.Residential.Customers'])

    colors = px.colors.qualitative.Prism
    types = df['Utility.Type'].unique()
    color_map = {t: colors[i % len(colors)] for i, t in enumerate(types)}

    # Plot 1: System Loss
    for t in types:
        mask = df['Utility.Type'] == t
        fig.add_trace(
            go.Scatter(
                x=df[mask]['SystemLossPercentage'], y=df[mask]['ResidentialUnitPrice'],
                name=t, hovertext=df[mask]['Utility.Name'], mode='markers',
                marker=dict(color=color_map[t],
                            size=df[mask]['BubbleSize']),
                hovertemplate="<b>%{hovertext}</b><br>Loss: %{x}%<br>Price: $%{y}<extra></extra>",
                showlegend=True), row=1, col=1)
    add_fairness_trendline(
        fig, df['SystemLossPercentage'], df['ResidentialUnitPrice'], 1, 1)

    # Plot 2: Load Factor
    for t in types:
        mask = df['Utility.Type'] == t
        fig.add_trace(
            go.Scatter(
                x=df[mask]['LoadFactor'], y=df[mask]['ResidentialUnitPrice'], name=t,
                mode='markers', marker=dict(color=color_map[t], size=df[mask]['BubbleSize']),
                hovertext=df[mask]['Utility.Name'],
                hovertemplate="<b>%{hovertext}</b><br>Load: %{x}<br>Price: $%{y}<extra></extra>",
                showlegend=False), row=1, col=2)
    add_fairness_trendline(fig, df['LoadFactor'],
                           df['ResidentialUnitPrice'], 1, 2)

    fig.update_layout(
        template='plotly_white',
        title_text='<b>Fairness Audit:</b> Correlation of Utility Metrics to Residential Price',
        legend_title_text="Ownership Model", height=600)

    fig.update_yaxes(title_text='Residential Price ($/MWh)', row=1, col=1)
    fig.update_xaxes(title_text='System Energy Loss (%)', row=1, col=1)
    fig.update_xaxes(title_text='Load Factor', row=1, col=2)

    return fig


def get_rate_disparity_dumbbell_plot(df: pd.DataFrame) -> go.Figure:
    """Get dumbbell plot of highest disparities between industrial/residential rates"""
    # Sort by spread to show the most "unfair" utilities at the top
    df_sorted = df[df.PriceSpread > 0].sort_values(
        'PriceSpread', ascending=True).tail(10)

    fig = go.Figure()

    # Add lines connecting the dots
    for i, row in df_sorted.iterrows():
        fig.add_shape(
            type='line', x0=row['IndustrialUnitPrice'], x1=row['ResidentialUnitPrice'],
            y0=row['Utility.Name'], y1=row['Utility.Name'],
            line=dict(color='lightgrey', width=2))

    # Industrial dumbbells
    fig.add_trace(go.Scatter(
        x=df_sorted['IndustrialUnitPrice'], y=df_sorted['Utility.Name'],
        mode='markers', name='Industrial Rate', marker=dict(color='#1f77b4', size=10)))

    # Residential dumbbells
    fig.add_trace(go.Scatter(
        x=df_sorted['ResidentialUnitPrice'], y=df_sorted['Utility.Name'],
        mode='markers', name='Residential Rate', marker=dict(color='#d62728', size=10)))

    fig.update_layout(title="<b>Top Rate Disparites</b>",
                      xaxis_title="Rate ($/MWh)", yaxis_title="")
    return fig


def add_utility_dropdown(fig: go.Figure, df: pd.DataFrame) -> go.Figure:
    """Post-processing function to add a utility dropdown justified right."""
    buttons = []

    for _, r in df.iterrows():
        buttons.append(dict(
            method="update",
            label=r["Utility.Name"],
            args=[
                {"link.value": [[
                    r["Sources.Generation"], r["Sources.Purchased"], r["Sources.Other"],
                    r["Uses.Retail"], r["Uses.Resale"], r["Uses.Losses"],
                    r["Uses.Consumed"], r["Uses.No Charge"]
                ]]},
                {"title.text": f"<b>Energy Flow: </b>{r['Utility.Name']}"}
            ]
        ))

    first_row = df.iloc[0]
    initial_values = [
        first_row["Sources.Generation"], first_row["Sources.Purchased"], first_row["Sources.Other"],
        first_row["Uses.Retail"], first_row["Uses.Resale"], first_row["Uses.Losses"],
        first_row["Uses.Consumed"], first_row["Uses.No Charge"]
    ]

    # 2. Directly assign the values to the first trace (the Sankey)
    # This ensures the values are injected before the figure is rendered
    fig.data[0].link.value = initial_values

    # 3. Apply the layout and the dropdown menu
    fig.update_layout(
        title_text=f"<b>Energy Flow: </b>{first_row['Utility.Name']}",
        updatemenus=[dict(
            buttons=buttons,
            direction="down",
            showactive=True,
            x=1.0,
            xanchor="right",
            y=2,
            yanchor="top",
            active=0
        )],
    )

    return fig


def get_energy_use_sankey_plot(row: pd.DataFrame) -> go.Figure:
    """Get energy usage sankey plot"""
    labels = ["Generated", "Purchased", "Other", "Uses", "Retail Sales",
              "Resale", "Losses", "Consumed", "No Charge"]

    fig = go.Figure(data=[go.Sankey(
        valueformat=".1f",
        valuesuffix="%",
        node=dict(
            pad=15, thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=px.colors.qualitative.Prism),
        link=dict(
            source=[0, 1, 2, 3, 3, 3, 3, 3],
            target=[3, 3, 3, 4, 5, 6, 7, 8],
            value=[
                row["Sources.Generation"],
                row["Sources.Purchased"],
                row["Sources.Other"],
                row["Uses.Retail"],
                row["Uses.Resale"],
                row["Uses.Losses"],
                row["Uses.Consumed"],
                row["Uses.No Charge"]
            ],
        ))])

    fig.update_layout(
        title_text=f"<b>Energy Flow: </b>{row['Utility.Name']}",
        hovermode='x')

    return fig


def export_plots_as_svg(plots: list[go.Figure]) -> None:
    """Export plots as high-definition SVGs to the 'images' folder"""

    script_dir = os.path.dirname(os.path.abspath(__file__))
    target_dir = os.path.join(script_dir, "..", "..", "images")

    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    pio.write_images(fig=plots,
                     file=["images/top_ten_state_res_variance_table.svg",
                           "images/residential_utility_type_box_plot.svg",
                           "images/industrial_utility_type_box_plot.svg",
                           "images/key_metrics_corr_heatmap.svg",
                           "images/rate_fairness_dual_y_scatter_plot.svg",
                           "images/rate_disparity_dumbbell_plot.svg",
                           "images/energy_usage_ny_sankey_chart.svg",
                           "images/energy_usage_us_sankey_chart.svg"])
