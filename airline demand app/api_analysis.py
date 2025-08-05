import pandas as pd

def generate_summary(df):
    """
    Process airline data and generate summary insights.
    """
    if df.empty:
        return {
            "Most Popular Route": "N/A",
            "Highest Price Route": "N/A",
            "Average Price": 0,
            "Average Demand": 0
        }

    popular_route = df.groupby('route')['demand'].sum().idxmax()
    highest_price_route = df.loc[df['price'].idxmax()]['route']
    average_price = round(df['price'].mean(), 2)
    average_demand = round(df['demand'].mean(), 2)

    return {
        "Most Popular Route": popular_route,
        "Highest Price Route": highest_price_route,
        "Average Price": average_price,
        "Average Demand": average_demand
    }
