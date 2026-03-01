# Stock Data ETL Pipeline

An automated ETL pipeline that collects real-time stock quote data from the [Finnhub](https://finnhub.io/) API, transforms it, and loads it into a PostgreSQL database. The pipeline runs every 30 minutes, orchestrated and scheduled by Apache Airflow, and the entire stack runs inside Docker containers.

## Tech Stack

- **Python 3.12** — pipeline logic
- **Pandas** — data transformation
- **PostgreSQL 16** — data storage
- **Apache Airflow 3.1.7** — orchestration and scheduling
- **Docker / Docker Compose** — containerised environment

---

## Overview

```
Finnhub API  →  Extract  →  Transform  →  Load  →  PostgreSQL
                   ↑
      Airflow schedules every 30 min
```

---

## Project structure

```
stock_data_airflow_postgresql/
├── main.py                   # Entry point to run the pipeline locally (outside Docker)
├── docker-compose.yaml       # Defines the Airflow and PostgreSQL containers
├── pyproject.toml
├── airflow/
│   └── dags/
│       └── orchestrator.py   # Airflow DAG definition (task wiring and schedule)
├── config/                   # Environment variables (.env file lives here)
├── data/                     # Local output files (stock_data.json, temp Parquet)
├── postgres/
│   ├── airflow_init.sql      # SQL run on first PostgreSQL startup (creates Airflow metadata DB)
│   └── data/                 # Persisted PostgreSQL data volume
├── src/
│   ├── extract_stock_data.py # E – Pull extraction from Finnhub API
│   ├── transform_stock_data.py # T – Clean and normalize the raw data
│   ├── load_stock_data.py    # L – Incremental insert into PostgreSQL
│   └── utils.py              # Shared helpers (env variable loading, etc.)
└── notebooks/
    └── data_analysis.ipynb   # Exploratory analysis and validation
```

---

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) and [Docker Compose](https://docs.docker.com/compose/) (for the containerised stack)
- Or [Python 3.12](https://www.python.org/) + [uv](https://docs.astral.sh/uv/) (for running locally)

### 1. Configure environment variables

Create `config/.env` from the template below and fill in your Finnhub API key:

```dotenv
API_KEY="your_finnhub_api_key"
SYMBOL="TSLA"
TIMEZONE="Europe/Lisbon"
RAW_DATA_PATH="data/stock_data.json"
```

### 2. Run with Docker

Start the full stack (PostgreSQL + Airflow):

```bash
docker compose up -d
```

On the very first run PostgreSQL will automatically execute `postgres/airflow_init.sql` to create the Airflow metadata database. Airflow will then run `airflow db migrate` before starting.

Open the Airflow UI at **http://localhost:8000**, log in with the credentials printed in the container logs.

Enable and trigger the `stock_data_pipeline` DAG from the UI, or wait for it to fire automatically on its 30-minute schedule.

To stop the stack:

```bash
docker compose down
```

To stop and delete all stored data (database volumes):

```bash
docker compose down -v
```

## ETL Pipeline

### Extract — Pull Extraction from API Call

Data is extracted via a **pull extraction** from the [Finnhub Quote API](https://finnhub.io/docs/api/quote):

```
GET https://finnhub.io/api/v1/quote?symbol={SYMBOL}&token={API_KEY}
```

Each call returns a JSON snapshot of the current market quote for the configured stock symbol (e.g. `TSLA`). The relevant fields in the response are:

- `c` — current price at the moment of the call
- `t` — Unix timestamp of the quote

This is **not incremental extraction** in the classical sense (i.e., it does not request all records since the last run). Instead, it is a **periodic snapshot pull**: a single data point is captured every 30 minutes, and the values naturally vary across calls as the market moves. The raw JSON response is saved to `data/stock_data.json` before being passed to the transform step.

### Transform

The raw JSON is loaded into a Pandas DataFrame and processed through the following steps:

1. **Parse & normalize** — `pd.json_normalize` converts the flat JSON response into a DataFrame.
2. **Column selection** — only the columns `c` (current price) and `t` (timestamp) are kept; all other Finnhub fields are dropped.
3. **Column renaming** — columns are renamed to descriptive names: `c` → `current_price`, `t` → `timestamp`.
4. **Timestamp conversion** — the Unix epoch timestamp (seconds) is converted to a timezone-aware `datetime` using `pd.to_datetime(..., unit="s", utc=True)`, then localized to the configured timezone (e.g. `Europe/Lisbon`).

The transformed DataFrame is serialized to a temporary Parquet file (`data/temp_data.parquet`) so it can be passed between Airflow tasks without keeping state in memory.

### Load — Incremental Load (INSERT)

The load step reads the Parquet file and inserts the record into PostgreSQL using a plain `INSERT` statement — one row per pipeline run. This is an **incremental load**: each execution appends a new row rather than truncating or overwriting existing data, building up a time series of price snapshots over time.

The target table is `dev.stock_data`, created automatically on first run if it does not exist:

```sql
CREATE SCHEMA IF NOT EXISTS dev;
CREATE TABLE IF NOT EXISTS dev.stock_data (
    id              SERIAL PRIMARY KEY,
    current_price   FLOAT,
    timestamp       TIMESTAMP
);
```

---

## PostgreSQL

The database runs as a Docker container (see [docker-compose.yaml](#docker-compose)). On first startup, `postgres/airflow_init.sql` is executed automatically to create the Airflow metadata database and user.

The stock data is stored in the `db` database, under the `dev` schema, in the `stock_data` table.

**Connection details (Docker):**

| Parameter | Value |
|-----------|-------|
| Host | `postgres` (service name inside Docker network) |
| Port | `5432` (internal) / `5000` (host-mapped) |
| Database | `db` |
| User | `db_user` |
| Password | `db_password` |

---

## Airflow

[Apache Airflow](https://airflow.apache.org/) is used to **orchestrate, schedule, and monitor** the ETL pipeline. The DAG is defined in `airflow/dags/orchestrator.py` using the Airflow 3.x TaskFlow API (`@dag` and `@task` decorators).

**DAG: `stock_data_pipeline`**

- **Schedule**: every 30 minutes (`*/30 * * * *`)
- **Start date**: 2026-02-26
- **Catchup**: disabled — missed runs are not backfilled
- **Tags**: `etl`, `stock_data`

The three tasks run sequentially:

```
extract()  >>  transform()  >>  load()
```

Each task maps directly to one step of the ETL pipeline. The transform task writes a Parquet file that the load task reads, decoupling the tasks while keeping them lightweight.

Airflow's web UI is accessible at `http://localhost:8000` (when running via Docker). It provides a visual graph of the DAG, per-task logs, run history, and the ability to trigger or pause the pipeline manually.

## Docker Compose

The `docker-compose.yaml` defines two services connected via a shared Docker bridge network (`my-network`):

### `postgres` service

- **Image**: `postgres:16`
- **Credentials**: user `db_user`, password `db_password`, database `db`
- **Port mapping**: `5000:5432` — PostgreSQL's internal port 5432 is exposed on host port 5000
- **Volumes**:
  - `./postgres/data` → `/var/lib/postgresql/data` — persists the database across container restarts
  - `./postgres/airflow_init.sql` → `/docker-entrypoint-initdb.d/` — automatically executed on the very first startup to create the `airflow` user and `airflow_db` database (used by Airflow as its metadata store)

### `af` service (Airflow)

- **Image**: `apache/airflow:3.1.7`
- **Port mapping**: `8000:8080` — Airflow's web UI accessible at `http://localhost:8000`
- **Depends on**: `postgres` — ensures the database is up before Airflow starts
- **Environment**:
  - `AIRFLOW__DATABASE_SQL_ALCHEMY_CONN` — points Airflow's internal metadata database to the `airflow_db` database on the Postgres service
- **Volumes**:
  - `./airflow/dags` → `/opt/airflow/dags` — mounts DAG files into the container
  - `./src` → `/opt/airflow/src` — makes pipeline source code available to the DAG
  - `./data` → `/opt/airflow/data` — shared data directory (raw JSON, temp Parquet)
  - `./config` → `/opt/airflow/config` — provides access to the `.env` file
- **Command**: runs `airflow db migrate` (applies schema migrations) followed by `airflow standalone` (starts the scheduler, triggerer, and web server as a single process)