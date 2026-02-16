from src.utils import get_variables, get_postgres_variables
from src.extract_stock_data import extract_data
from src.transform_stock_data import transform_data
from src.load_stock_data import load_data

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def main():
    
    vars = get_variables()
    vars_postgres = get_postgres_variables()

    url = f"https://finnhub.io/api/v1/quote?symbol={vars['SYMBOL']}&token={vars['API_KEY']}"

    table_name = "stock_price"

    logging.info("PHASE 1: EXTRACT")
    extract_data(url=url, vars=vars)

    logging.info("PHASE 2: TRANSFORM")
    df = transform_data(vars=vars)

    logging.info("PHASE 3: LOAD")
    load_data(vars_postgres=vars_postgres, table_name=table_name, df=df)

if __name__=="__main__":
    main()

