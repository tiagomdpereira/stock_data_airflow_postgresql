from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import pandas as pd

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def load_data(vars_postgres: dict, table_name: str, df: pd.DataFrame):

    user = vars_postgres["USER"]
    password = vars_postgres["PASSWORD"]
    host = vars_postgres["HOST"]
    port = vars_postgres["PORT"]
    database = vars_postgres["DATABASE"]

    engine = create_engine(f'postgresql://{user}:{quote_plus(password)}@{host}:{port}/{database}')
    
    df.to_sql(
        name=table_name,
        con=engine,
        if_exists='append',
        index=False
    )

    logging.info(f"Data loaded!\n") 
    
    df_check = pd.read_sql(f'SELECT * FROM {table_name}', con=engine)
    logging.info(f"Total entries in table: {len(df_check)}\n")

if __name__=="__main__":
    load_data({
        "USER": "user",
        "PASSWORD": "password",
        "HOST": "host",
        "PORT": "port",
        "DATABASE": "database"
    })

