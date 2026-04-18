
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
                "Uses.Retail", "Uses.Losses", "Uses.Total", "Demand.Summer Peak",
                "Retail.Residential.Revenue", "Retail.Residential.Sales", 
                "Retail.Industrial.Revenue", "Retail.Industrial.Sales"]

    return df[df["Utility.State"] == state][keep_columns]

def prepare_data(df):    
    df['ResidentialRetailRate'] = (df['Retail.Residential.Revenue'] / df['Retail.Residential.Sales']) * 1000
    df['ResidentialRetailRate'] = df['ResidentialRetailRate'].fillna(0)

    df['IndustrialRetailRate'] = df['Retail.Industrial.Revenue'] / df['Retail.Industrial.Sales']
    df['IndustrialRetailRate'] = df['IndustrialRetailRate'].fillna(0)

    df['IndustrialPriceRatio'] = df['Retail.Industrial.Revenue'] / df['RetailRevenue'] * 100
    df['IndustrialPriceRatio'] = df['IndustrialPriceRatio'].fillna(0)

    df['PriceSpread'] = df['ResidentialRetailRate'] - df['IndustrialRetailRate']

    df['LossRatio'] = (df['Uses.Losses'] / df['Sources.Total']) * 100
    
    df['LoadFactor'] = df['Sources.Total'] / (df['Demand.Summer Peak'] * 8760)

    return df


