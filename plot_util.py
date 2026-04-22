""" Retrieves plotly charts  """

import numpy as np
from scipy.stats import linregress

import plotly_express as px
import plotly.graph_objects as go
import plotly.io as pio

from plotly.subplots import make_subplots


def get_utility_type_box_plot(df):
    """Compare Residential Price across Utility Types"""
    fig = px.box(df, x='Utility.Type', y='ResidentialUnitPrice', color="Utility.Type",
                 points="all", hover_name="Utility.Name",
                 hover_data=["Retail.Residential.Customers", "LoadFactor"],
                 color_discrete_sequence=px.colors.qualitative.Prism,
                 title="<b>Utility Type:</b> Residential Price Distribution",
                 labels={"Utility.Type": "Ownership Model",
                         "ResidentialUnitPrice": "Residential Rate",
                         "Retail.Residential.Customers": "Customer Count",
                         "LoadFactor": "Load Factor"},
                 template='plotly_white')

    fig.update_layout(
        xaxis_title="",
        yaxis_title="Residential Rate ($/MWh)"
    )

    return fig


def get_key_metrics_corr_matrix(corr_matrix):
    """Correlation matrix for key analysis metrics"""
    return px.imshow(
        corr_matrix,
        text_auto='.2f',
        color_continuous_scale='BluYl',
        aspect="auto",
        title='<b>Statistical Significance:</b> Correlation Heatmap of Key Metrics',
        labels=dict(color="Correlation Score"),
        template='plotly_white'
    )


def add_fairness_trendline(fig, x_data, y_data, row, col):
    """Calculates OLS and adds centered stats inside the plot to avoid title overlap."""
    mask = ~np.isnan(x_data) & ~np.isnan(y_data)
    x_clean, y_clean = x_data[mask], y_data[mask]

    if len(x_clean) > 1:
        # Get Linear Regression
        slope, intercept, r_val, p_val, std_err = linregress(x_clean, y_clean)

        # Trendline coordinates
        x_range = np.array([x_clean.min(), x_clean.max()])
        y_range = slope * x_range + intercept

        # 1. Add the Trendline
        fig.add_trace(
            go.Scatter(
                x=x_range, y=y_range,
                mode='lines',
                line=dict(color='black', width=2, dash='dash'),
                name='Overall Trend',
                legendgroup='trendline',
                showlegend=(row == 1 and col == 1),
                hoverinfo='skip'
            ),
            row=row, col=col
        )

        # 2. Add Stats Annotation Box (Centered and Lowered)
        stats_text = f"<b>R²:</b> {r_val**2:.3f}  |  <b>p:</b> {p_val:.4e}"

        fig.add_annotation(
            xref=f"x{col if col > 1 else ''} domain",
            yref=f"y{row if row > 1 else ''} domain",
            x=0.5,              # Horizontal center
            y=0.92,             # Lowered to 92% of height (inside the plot)
            xanchor="center",
            yanchor="top",      # Box hangs downward from the y=0.92 point
            text=stats_text,
            showarrow=False,
            align="center",
            # High opacity for readability
            bgcolor="rgba(255, 255, 255, 0.85)",
            bordercolor="rgba(0,0,0,0.3)",
            borderwidth=1,
            font=dict(size=10)
        )


def get_fairness_dual_y_scatter_plot(df):
    fig = make_subplots(
        rows=1, cols=2,
        shared_yaxes=True,
        horizontal_spacing=0.05,
        subplot_titles=('<b>System Loss vs Price</b>',
                        '<b>Load Factor vs Price</b>')
    )

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
                mode='markers', name=t, marker=dict(color=color_map[t], size=df[mask]['BubbleSize']),
                hovertext=df[mask]['Utility.Name'],
                hovertemplate="<b>%{hovertext}</b><br>Loss: %{x}%<br>Price: $%{y}<extra></extra>",
                showlegend=True,
            ), row=1, col=1
        )
    add_fairness_trendline(
        fig, df['SystemLossPercentage'], df['ResidentialUnitPrice'], 1, 1)

    # Plot 2: Load Factors
    for t in types:
        mask = df['Utility.Type'] == t
        fig.add_trace(
            go.Scatter(
                x=df[mask]['LoadFactor'], y=df[mask]['ResidentialUnitPrice'],
                mode='markers', marker=dict(color=color_map[t], size=df[mask]['BubbleSize']),
                hovertext=df[mask]['Utility.Name'],
                hovertemplate="<b>%{hovertext}</b><br>Load: %{x}<br>Price: $%{y}<extra></extra>",
                showlegend=False
            ), row=1, col=2
        )
    add_fairness_trendline(fig, df['LoadFactor'],
                           df['ResidentialUnitPrice'], 1, 2)

    # Formatting
    fig.update_layout(
        template='plotly_white',
        title_text='<b>Fairness Audit:</b> Correlation of Utility Metrics to Residential Price',
        legend_title_text="Ownership Model",
        height=600
    )

    fig.update_yaxes(title_text='Residential Price ($/MWh)', row=1, col=1)
    fig.update_xaxes(title_text='System Energy Loss (%)', row=1, col=1)
    fig.update_xaxes(title_text='Load Factor', row=1, col=2)

    return fig


def get_rate_disparity_dumbbell_plot(df):
    """Get dumbbell plot of highest disparities between industrial/residential rates"""
    # Sort by spread to show the most "unfair" utilities at the top
    df_sorted = df[df.PriceSpread > 0].sort_values(
        'PriceSpread', ascending=True).tail(10)

    fig = go.Figure()

    # 1. Add the lines connecting the dots
    for i, row in df_sorted.iterrows():
        fig.add_shape(
            type='line', x0=row['IndustrialUnitPrice'], x1=row['ResidentialUnitPrice'],
            y0=row['Utility.Name'], y1=row['Utility.Name'],
            line=dict(color='lightgrey', width=2)
        )

    # 2. Add Industrial dots
    fig.add_trace(go.Scatter(
        x=df_sorted['IndustrialUnitPrice'], y=df_sorted['Utility.Name'],
        mode='markers', name='Industrial Rate', marker=dict(color='#1f77b4', size=10)
    ))

    # 3. Add Residential dots
    fig.add_trace(go.Scatter(
        x=df_sorted['ResidentialUnitPrice'], y=df_sorted['Utility.Name'],
        mode='markers', name='Residential Rate', marker=dict(color='#d62728', size=10)
    ))

    fig.update_layout(title="<b>Top Rate Disparites</b>",
                      xaxis_title="Rate ($/MWh)", yaxis_title="")
    return fig


def get_energy_use_sankey_plot(row):
    """Get utility-level energy usage sankey plot"""
    labels = ["Generated", "Purchased", "Other", "Uses", "Retail Sales",
              "Resale", "Losses", "Consumed", "No Charge"]

    fig = go.Figure(data=[go.Sankey(
        valueformat=".1f",
        valuesuffix="%",
        node=dict(
            pad=15, thickness=20,
            line=dict(color="black", width=0.5),
            label=labels,
            color=px.colors.qualitative.Prism[2]
        ),
        link=dict(
            source=[0, 1, 2, 3, 3, 3, 3, 3, 3],
            target=[3, 3, 3, 4, 5, 6, 7, 8, 9],
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
        hovermode='x'
    )

    return fig


def export_plots_as_svg(plots: list) -> None:
    """Export all plots as high-definition SVGs"""
    return pio.write_images(fig=plots,
                            file=["images/utility_type_box_plot.svg",
                                  "images/key_metrics_corr_heatmap.svg",
                                  "images/rate_fairness_dual_y_scatter_plot.svg",
                                  "images/rate_disparity_dumbbell_plot.svg",
                                  "images/energy_usage_utility_sankey_chart.svg",
                                  "images/energy_usage_us_sankey_chart.svg"])
