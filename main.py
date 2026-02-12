from src.utils import get_variables
from src.extract_stock_data import extract_data
from src.transform_stock_data import transform_data

vars = get_variables()

url = f"https://finnhub.io/api/v1/quote?symbol={vars['SYMBOL']}&token={vars['API_KEY']}"

extract_data(url=url, vars=vars)
transform_data(vars=vars)

