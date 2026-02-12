### Project structure

- `main.py`: entry point to run the main flow (pipeline orchestration).
- `src/`: pipeline source code.
	- `extract_stock_data.py`: data extraction step (fetch/collect stock data).
	- `transform_stock_data.py`: data transformation step (clean/normalize data).
	- `utils.py`: shared helpers (common utilities and small reusable functions).
- `config/`: project configuration (e.g., environment variables in `.env`).
- `data/`: local output data files (e.g., `stock_data.json`).
- `notebooks/`: notebooks for exploration/validation (analysis and quick tests).
