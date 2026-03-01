from datetime import datetime
from airflow.sdk import dag, task
import pandas as pd
import sys

sys.path.append("/opt/airflow/")

# from utils import get_variables
# from extract_stock_data import extract_data
# from transform_stock_data import transform_data
# from load_stock_data import load_data

from src.utils import get_variables
from src.extract_stock_data import extract_data
from src.transform_stock_data import transform_data
from src.load_stock_data import load_data

vars = get_variables()

url = f"https://finnhub.io/api/v1/quote?symbol={vars['SYMBOL']}&token={vars['API_KEY']}"

default_args={
    "description": "A DAG to orchestrate data",
    "start_date": datetime(2026, 2, 27),
    "catchup": False
}

@dag(
    dag_id="stock_data_pipeline",
    default_args=default_args,
    description="ETL Pipeline - Get stock data",
    schedule="*/30 * * * *",
    start_date=datetime(2026, 2, 26),
    catchup=False,
    tags=["etl", "stock_data"]
)

def stock_pipeline():
    

    @task
    def extract():
        extract_data(url=url, vars=vars)
    
    @task
    def transform():
        df = transform_data(vars=vars)
        df.to_parquet("/opt/airflow/data/temp_data.parquet", index=False)

    @task
    def load():
        df = pd.read_parquet("/opt/airflow/data/temp_data.parquet")
        load_data(df=df)
    
    extract() >> transform() >> load()


stock_pipeline()