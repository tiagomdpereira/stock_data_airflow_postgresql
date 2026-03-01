from sqlalchemy import create_engine, text
from urllib.parse import quote_plus
import pandas as pd
import psycopg2

import logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

def connect_to_db():
    logging.info(f"Connecting to PostgreSQL database...\n")
    try:
        conn = psycopg2.connect(
            host="postgres", # service name in docker-compose.yaml; set "localhost" for this pc instead docker
            port=5432,       # set 5000 for this computer instead docker
            dbname="db",
            user="db_user",
            password="db_password"
        )
        return conn
    except psycopg2.Error as e:
        print(f"Database connection failed: {e}")
        raise

def create_table(conn):
    logging.info(f"Creating table if not exists...\n") 
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE SCHEMA IF NOT EXISTS dev;
            CREATE TABLE IF NOT EXISTS dev.stock_data (
                id SERIAL PRIMARY KEY,
                current_price FLOAT,
                timestamp TIMESTAMP
            )
        """)
        conn.commit()
        print("Table was created.")
    except psycopg2.Error as e:
        print(f"Error creating the table: {e}")
        raise
    
def load_data(df):
    conn = connect_to_db()
    create_table(conn)
    logging.info(f"Inserting stock data into the database...\n")
    try:
        cursor = conn.cursor()
        cursor.execute(f"""
            INSERT INTO dev.stock_data (
                current_price,
                timestamp
            ) VALUES ('{df.loc[0, "current_price"]}', '{df.loc[0, "timestamp"]}')
        """)
        conn.commit()
        print("Data successfully inserted")
    except psycopg2.Error as e:
        print(f"Error inserting the data into the database: {e}")
        raise
    finally:
        conn.close()

if __name__=="__main__":
    from utils import get_variables
    from transform_stock_data import transform_data
    vars = get_variables()
    df = transform_data(vars)

    load_data(df)
    print("Database connection closed.")

    # load_data({
    #     "USER": "user",
    #     "PASSWORD": "password",
    #     "HOST": "host",
    #     "PORT": "port",
    #     "DATABASE": "database"
    # })

