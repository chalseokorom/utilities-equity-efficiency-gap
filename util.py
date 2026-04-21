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
                "Retail.Industrial.Revenue", "Retail.Industrial.Sales", "Retail.Industrial.Customers",
                "Uses.Retail", "Uses.Losses", "Uses.Resale", "Uses.No Charge", "Uses.Consumed", "Uses.Total",
                "Demand.Summer Peak", "Revenues.Retail"]
    
    return df[df["Utility.State"] == state][keep_columns]

def prepare_data(df):    
    # Residential $ per MWh
    df['ResidentialUnitPrice'] = (df['Retail.Residential.Revenue'] / df['Retail.Residential.Sales']) * 1000
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

def get_customer_utilities(df, customer):
    if customer == "Residential":
        return df[df["Retail.Residential.Customers"] > 0]
    elif customer == "Industrial":
        return df[df["Retail.Industrial.Customers"] > 0]
    else:
        return df[(df["Retail.Residential.Customers"] > 0) & (df["Retail.Industrial.Customers"] > 0)]

def get_residential_load_factor(df):
    df = get_customer_utilities(df, "Residential")
    return df[df["LoadFactor"] > 0]

def get_residential_sys_loss(df):
    df = get_customer_utilities(df, "Residential")
    return df[df["SystemLossPercentage"] > 0]

def get_utility_usage(utility):
    # Convert raw values to percentages of the 'Total Sources'
    keys = [
        'Sources.Generation', 'Sources.Purchased', 'Sources.Other',
        'Uses.Retail', 'Uses.Resale', 'Uses.Losses', 
        'Uses.Consumed', 'Uses.No Charge'
    ]

    named_utility = (utility[keys] / utility['Sources.Total']) * 100
    named_utility['Utility.Name'] = utility['Utility.Name']
    
    return named_utility
