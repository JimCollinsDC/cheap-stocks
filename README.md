# Cheap Stocks Filter

This project ranks a user-provided stock list by **perfect-hindsight filter scores** over the past month.

It is a filter, not a trading system.

## What the score means

For each ticker, using daily close-to-close moves in the trailing 1 calendar month:

- Long filter score assumes unlimited `buy/sell/buy/sell` cycles with perfect hindsight.
- Short filter score assumes unlimited `sell/buy/sell/buy` cycles with perfect hindsight.
- Both scores are scaled by the same share count (default: 100 shares).
- No fees, slippage, or borrow costs are applied.

These are upper-bound screening metrics meant to help prioritize names for deeper review.

## Setup

```powershell
# from project root, with your .venv activated
pip install -r requirements.txt
```

## Input

Provide tickers in any CSV file you want to analyze. The default path is `input/stocks.csv`, but you can point `--input` at a larger universe file anywhere on disk.

CSV schema:

- Header row with `ticker` preferred
- One ticker per row

Example:

```csv
ticker
AAPL
MSFT
SOFI
```

## Run

```powershell
cheap-stocks --input input/stocks.csv --shares 100 --top 10
```

Alternative:

```powershell
python -m cheap_stocks --input input/stocks.csv --shares 100 --top 10
```

Useful options:

- `--rank-by profit`: rank by raw dollar capture using the configured share count
- `--rank-by percent`: rank by percent capture relative to the first close in the window
- `--output-dir path/to/folder`: override the default timestamped output folder
- `--normalize-input`: deduplicate and alphabetize the ticker CSV, then exit
- `--normalized-output path/to/file.csv`: write the normalized list to a separate file instead of overwriting `--input`

Examples:

```powershell
cheap-stocks --input input/stocks.csv --rank-by percent --top 25
cheap-stocks --input C:/data/full_universe.csv --rank-by profit --shares 100
cheap-stocks --input C:/data/full_universe.csv --output-dir output/full-universe-run
cheap-stocks --input input/stocks.csv --normalize-input
cheap-stocks --input C:/data/raw_universe.csv --normalize-input --normalized-output C:/data/clean_universe.csv
```

## Output files

Written to a timestamped folder under `output/` by default, for example `output/20260501-093045/`:

- `combined_detailed.csv`: all tickers with status and metrics
- `long_ranked.csv`: successful tickers sorted by long score
- `short_ranked.csv`: successful tickers sorted by short score

Key columns:

- `long_capture_per_share`, `short_capture_per_share`
- `long_profit`, `short_profit`
- `long_return_pct`, `short_return_pct`
- `long_cycles`, `short_cycles`
- `status`, `error`

## Testing

```powershell
pytest
```
