import pandas as pd
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

load_dotenv()

if not os.path.exists("stocks_raw.csv"):
    raise Exception("No raw data file. Run ingestion first.")

df = pd.read_csv('stocks_raw.csv',header=0)
df = df.rename(columns={
    '1. open': 'open',
    '2. high': 'high',
    '3. low': 'low',
    '4. close': 'close',
    '5. volume': 'volume'
})
df[['open','high','low','close','volume']] = df[['open','high','low','close','volume']].astype(float)
df['date'] = pd.to_datetime(df['date'])
df = df.sort_values('date',ascending=False).reset_index(drop=True)

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

df.to_sql('stocks',engine,if_exists='replace',index=False)
