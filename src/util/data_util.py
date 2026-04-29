"""Functions to clean and filter data for use in utility data visualizations"""

import pandas as pd

HOURS_PER_YEAR = 8760


def get_state_variance(df: pd.DataFrame) -> pd.DataFrame:
    """Summarizes key metrics for states to help choose state for analysis"""

    agg_df = df.groupby('Utility.State').agg({
        'Utility.Name': 'nunique',                # Want = More utilites to analyze
        'Utility.Type': 'nunique',                # Want = More utility types to compare
        'ResidentialUnitPrice': 'std',            # Want = High std for varied utilities
        'SystemLossPercentage': 'max',            # Want = Great outlier stories
        'IndustrialRevenueRatio': 'mean'          # Want = High for industrial bias
    })

    agg_df.rename(columns={
        'Utility.Name': '# Utilities',
        'Utility.Type': '# Utility Types',
        'Utility.State': 'State',
        'ResidentialUnitPrice': 'Residential Price Std. Dev.',
        'SystemLossPercentage': 'System Loss %',
        'IndustrialRevenueRatio': 'Industrial Revenue %'
    }, inplace=True)

    agg_df.columns = [f"{col[0]}_{col[1]}" if isinstance(col, tuple) else col
                      for col in agg_df.columns.values]
    agg_df.sort_values('Residential Price Std. Dev.',
                       ascending=False, inplace=True)

    return agg_df.reset_index().head(10)


def get_state_data(state: str, df: pd.DataFrame) -> pd.DataFrame:
    """Select and filter out relevant columns for analysis"""
    keep_columns = ["Utility.Name", "Utility.State", "Utility.Type",
                    "Sources.Total", "Sources.Generation", "Sources.Purchased",
                    "Sources.Other", "Retail.Residential.Revenue", "Retail.Residential.Sales",
                    "Retail.Residential.Customers", "Retail.Industrial.Revenue",
                    "Retail.Industrial.Sales", "Retail.Industrial.Customers",
                    "Uses.Retail", "Uses.Losses", "Uses.Resale",
                    "Uses.No Charge", "Uses.Consumed", "Uses.Total",
                    "Demand.Summer Peak", "Revenues.Retail"]

    return df[df["Utility.State"] == state][keep_columns]


def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """Perform calculations for key metrics and add them to the data"""
    # Residential $ per MWh
    df['ResidentialUnitPrice'] = (df['Retail.Residential.Revenue']
                                  / df['Retail.Residential.Sales']) * 1000
    df['ResidentialUnitPrice'] = df['ResidentialUnitPrice'].fillna(0)

    # Industrial $ per MWh
    df['IndustrialUnitPrice'] = df['Retail.Industrial.Revenue'] / \
        df['Retail.Industrial.Sales']
    df['IndustrialUnitPrice'] = df['IndustrialUnitPrice'].fillna(0)

    # % Dependency on industrial revenue
    df['IndustrialRevenueRatio'] = df['Retail.Industrial.Revenue'] / \
        df['Revenues.Retail'] * 100
    df['IndustrialRevenueRatio'] = df['IndustrialRevenueRatio'].fillna(0)

    # Equity Metric
    df['PriceSpread'] = df['ResidentialUnitPrice'] - df['IndustrialUnitPrice']

    # Efficiency Metric
    df['SystemLossPercentage'] = (
        df['Uses.Losses'] / df['Sources.Total']) * 100

    # Operational metric of 'stress' on system
    df['LoadFactor'] = df['Sources.Total'] / \
        (df['Demand.Summer Peak'] * HOURS_PER_YEAR)
    df['LoadFactor'] = df['LoadFactor'].apply(
        lambda load: 0 if load == float('inf') else load)

    return df


def get_customer_utilities(df: pd.DataFrame, sector="Residential") -> pd.DataFrame:
    """Filter data by customer type for use in plots"""
    if sector == "Residential":
        return df[df["Retail.Residential.Customers"] > 0]

    elif sector == "Industrial":
        return df[df["Retail.Industrial.Customers"] > 0]

    return df[(df["Retail.Residential.Customers"] > 0)
              & (df["Retail.Industrial.Customers"] > 0)]


def get_residential_load_factor(df: pd.DataFrame) -> pd.DataFrame:
    """Filter data by customer type and utilities with a load factor"""
    df = get_customer_utilities(df, "Residential")

    return df[df["LoadFactor"] > 0]


def get_residential_sys_loss(df: pd.DataFrame) -> pd.DataFrame:
    """Filter data by customer type and utilities with system loss"""
    df = get_customer_utilities(df, "Residential")

    return df[df["SystemLossPercentage"] > 0]


def get_utility_usage(utility: pd.Series, level: str = "State") -> pd.DataFrame:
    """Create data with percentages of utilty usage within the sankey plot"""

    # Convert raw values to percentages of the 'Total Sources'
    keys = [
        'Sources.Generation', 'Sources.Purchased', 'Sources.Other',
        'Uses.Retail', 'Uses.Resale', 'Uses.Losses',
        'Uses.Consumed', 'Uses.No Charge'
    ]

    named_utility = (utility[keys] / utility['Sources.Total']) * 100

    if level == "State":
        named_utility['Utility.Name'] = "State of " + \
            utility['Utility.State'][0:2]
    elif level == "US":
        named_utility['Utility.Name'] = "United States"
    else:
        named_utility['Utility.Name'] = utility['Utility.Name']

    return named_utility
