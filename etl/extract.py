import requests
import pandas as pd
import time
import os
from dotenv import load_dotenv
import argparse

load_dotenv()

KEY = os.getenv("ALPHA_VANTAGE_API_KEY")

parser = argparse.ArgumentParser()
parser.add_argument("--equities", nargs="+", required=True)
args = parser.parse_args()

equities = args.equities
failed = []
dfs = []

for equity in equities: 
    url = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={equity}&apikey={KEY}'
    r = requests.get(url)
    data = r.json()
    if "Time Series (Daily)" in data:
        df = pd.DataFrame(data["Time Series (Daily)"]).T
        df['equity'] = equity
        dfs.append(df)
    else:
        print("Error en API:", data)
        failed.append(equity)
    time.sleep(12)
    
if dfs:
    final_df = pd.concat(dfs)
    final_df= final_df.reset_index(names="date")
    final_df.to_csv('stocks_raw.csv',index=False)
if failed:
    print("Failed:",failed)





