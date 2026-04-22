"""Key functions to clean and filter data for use in utility data visualizations"""

import pandas as pd


def get_state_variance(df: pd.DataFrame) -> pd.DataFrame:
    """Summarizes key metrics for states to help choose state for analysis"""
    agg_df = df.groupby('Utility.State').agg({
        'ResidentialUnitPrice': ['std', 'mean'],      # High std = High drama
        'Utility.Type': 'nunique',                # High nunique = Better comparisons
        'SystemLossPercentage': 'max',                  # High max = Great outlier stories
        'IndustrialRevenueRatio': 'mean'       # High mean = Interesting industrial dynamics
    })

    agg_df.columns = [f"{col[0]}_{col[1]}" if isinstance(col, tuple) else col
                            for col in agg_df.columns.values]

    return agg_df.reset_index()

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
    df['IndustrialUnitPrice'] = df['Retail.Industrial.Revenue'] / df['Retail.Industrial.Sales']
    df['IndustrialUnitPrice'] = df['IndustrialUnitPrice'].fillna(0)

    # % Dependency on industrial revenue 
    df['IndustrialRevenueRatio'] = df['Retail.Industrial.Revenue'] / df['Revenues.Retail'] * 100
    df['IndustrialRevenueRatio'] = df['IndustrialRevenueRatio'].fillna(0)

    # Equity Metric
    df['PriceSpread'] = df['ResidentialUnitPrice'] - df['IndustrialUnitPrice']

    # Efficiency Metric
    df['SystemLossPercentage'] = (df['Uses.Losses'] / df['Sources.Total']) * 100

    # Operational metric of 'stress' on system
    df['LoadFactor'] = df['Sources.Total'] / (df['Demand.Summer Peak'] * 8760)
    df['LoadFactor'] = df['LoadFactor'].apply(lambda load: 0 if load == float('inf') else load)

    df['FairnessIndex'] = df['ResidentialUnitPrice'] / df['LoadFactor']

    return df

def get_customer_utilities(df: pd.DataFrame, customer: str) -> pd.DataFrame:
    """Filter data by customer type for use in plots"""
    if customer == "Residential":
        return df[df["Retail.Residential.Customers"] > 0]

    elif customer == "Industrial":
        return df[df["Retail.Industrial.Customers"] > 0]

    else:
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

def get_utility_usage(utility: pd.Series) -> pd.DataFrame:
    """Create data with percentages of utilty usage within the sankey plot"""

    # Convert raw values to percentages of the 'Total Sources'
    keys = [
        'Sources.Generation', 'Sources.Purchased', 'Sources.Other',
        'Uses.Retail', 'Uses.Resale', 'Uses.Losses', 
        'Uses.Consumed', 'Uses.No Charge'
    ]

    named_utility = (utility[keys] / utility['Sources.Total']) * 100
    named_utility['Utility.Name'] = utility['Utility.Name']

    return named_utility
