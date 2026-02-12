### Project structure

- `main.py`: entry point to run the main flow (pipeline orchestration).
- `src/`: pipeline source code.
	- `extract_stock_data.py`: data extraction step (fetch/collect stock data).
	- `transform_stock_data.py`: data transformation step (clean/normalize data).
	- `utils.py`: shared helpers (common utilities and small reusable functions).
- `config/`: project configuration (environment variables live in `config/.env`).
- `data/`: local output data files (e.g., `stock_data.json`).
- `notebooks/`: notebooks for exploration/validation (analysis and quick tests).

### Environment variables (.env)

All runtime configuration variables must be defined in `config/.env`.

Current keys used by the project:

- `API_KEY`: `""` (fill with your provider key)
- `SYMBOL`: `"TSLA"`
- `TIMEZONE`: `"Europe/Lisbon"`
- `RAW_DATA_PATH`: `"data/stock_data.json"`

Example `config/.env`:

```dotenv
API_KEY=""
SYMBOL="TSLA"
TIMEZONE="Europe/Lisbon"
RAW_DATA_PATH="data/stock_data.json"
```
