import numpy as np

def get_state_variance(df):
    scout_df = df.groupby('Utility.State').agg({
        'ResidentialPrice': ['std', 'mean'],      # High std = High drama
        'Utility.Type': 'nunique',         # High nunique = Better comparisons
        'LossPercentage': 'max',                 # High max = Great outlier stories
        'IndustrialPricePercentage': 'mean'          # High mean = Interesting industrial dynamics
    }).reset_index()

    return scout_df.sort_values(('res_price', 'std'), ascending=False)[0:10]

def get_state_data(state, df):
    keep_columns = ["Utility.Name", "Utility.State", "Utility.Type", 
                "Sources.Total", "Sources.Generation", "Sources.Purchased", "Sources.Other",
                "Retail.Residential.Revenue", "Retail.Residential.Sales", "Retail.Residential.Customers", 
                "Retail.Industrial.Revenue", "Retail.Industrial.Sales",
                "Uses.Retail", "Uses.Losses", "Uses.Total", "Demand.Summer Peak", "Revenues.Retail"]
    
    return df[df["Utility.State"] == state][keep_columns]

def prepare_data(df):    
    # Residential $ per MWh
    df['ResidentialUnitPrice'] = (df['Retail.Residential.Revenue'] / df['Retail.Residential.Sales']) * 1000
    df['ResidentialUnitPrice'] = df['ResidentialUnitPrice'].fillna(0)

    # Residential $ per MWh
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
    df['LoadFactor'].apply(lambda load: 0 if load == np.inf else load)

    return df


