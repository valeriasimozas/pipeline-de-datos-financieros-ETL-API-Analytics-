from fastapi import FastAPI
from fastapi import HTTPException
from sqlalchemy import create_engine #engine para conectarse con la database de Postgre
import pandas as pd
import os 
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

DATABASE_URL = os.getenv("DATABASE_URL")

engine = create_engine(DATABASE_URL)

def read_query(query,parameters=None): #refactor
    with engine.connect() as conn:
        return pd.read_sql(query,conn,params=parameters)

def get_equities(): 
    df = read_query("SELECT DISTINCT equity from stocks")
    return df["equity"].tolist()

def validate_equity(equity): 
    query = "SELECT 1 FROM stocks WHERE equity = %(equity)s limit 1"
    df = read_query(query, {"equity": equity.upper()})
    if df.empty:
        raise HTTPException(status_code=404, detail="Equity not available")

@app.get("/") #pagina principal
def root():
   return {
        "message": "Stock API running",
        "description": "Historical stock data API. Each equity contains up to 100 historical daily records (data sourced from Alpha Vantage limitation)",
        "available_equities":get_equities(),
        "endpoints": {
            "all_stocks": 
            {"path": "/stocks",
             "query_params": "limit"},
            "by_equity": 
            {"path":"/stocks/{equity}",
             "query_params": "limit"},
            "summary_by_equity": "/stocks/{equity}/summary",
            "by_date (format=YYYY-MM-DD)": "/stocks/{equity}/date/{date}",
            "SMA": 
            {"path": "/stocks/{equity}/moving_average",
             "query_params": "window"},
            "daily_return_by_equity": "/stocks/{equity}/daily_return"
        }
    }


@app.get("/stocks") #pagina stocks, muestra todo
def get_stocks(limit: int=1000): 
    limit = max(1, min(limit, 5000))
    query = "SELECT DATE(date) as date, open,high, low, close, volume, equity FROM stocks LIMIT %(limit)s"
    df= read_query(query,{"limit":limit})
    return df.to_dict(orient="records")

@app.get("/stocks/{equity}") #filtro por equity
def get_stock(equity,limit:int=100):
    limit = max(1, min(limit, 100))
    validate_equity(equity)
    query = "SELECT DATE(date) as date, open,high, low, close, volume, equity FROM stocks WHERE equity = %(equity)s LIMIT %(limit)s"
    df = read_query(query,{"equity":equity.upper(),"limit":limit})
    return df.to_dict(orient="records")

@app.get("/stocks/{equity}/summary") #resumen por equity
def get_summary(equity):
    validate_equity(equity)
    query = "SELECT MAX(open) as max_open, MIN(open) as min_open,AVG(open) as avg_open,MAX(close) as max_close, MIN(close) as min_close," \
    "AVG(close) as avg_close, MAX(volume) as max_volume, MIN(volume) as min_volume,AVG(volume) as avg_volume from stocks WHERE equity = %(equity)s"
    df = read_query(query,{"equity":equity.upper()})
    return df.iloc[0].to_dict()

@app.get("/stocks/{equity}/date/{date}") #datos de equity en date especifica
def get_date_stocks(equity,date):
    validate_equity(equity)
    query = "SELECT DATE(date) as date, open, high, low, close, volume FROM stocks WHERE equity = %(equity)s and date = %(date)s"
    df = read_query(query,{"equity":equity.upper(),"date":date})
    if df.empty:
        raise HTTPException(status_code=404, detail="No data for this date")
    return df.iloc[0].to_dict()

@app.get("/stocks/{equity}/moving_average") #calculo de SMA con window configurable
def get_moving_average(equity,window=2):
    validate_equity(equity)
    query = "SELECT AVG(close) as avg_close from (select close from stocks where equity = %(equity)s order by date desc limit %(window)s) t"
    df = read_query(query,{"equity": equity.upper(),"window":window})
    return df.iloc[0].to_dict()

@app.get("/stocks/{equity}/daily_return") #retorno diario por acción
def get_daily_return(equity):
    validate_equity(equity)
    query = "SELECT *, round(daily_return*100,2) as pct from(SELECT DATE(date), ((close- LAG(close) over(order by date)) / LAG(close) over(order by date))::numeric as daily_return from stocks where equity = %(equity)s) where daily_return is not null order by DATE(date) desc"
    df = read_query(query,{"equity":equity.upper()})
    return df.to_dict(orient="records")