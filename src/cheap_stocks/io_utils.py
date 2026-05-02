from __future__ import annotations

import csv
import os
import re
from collections.abc import Iterable

TICKER_PATTERN = re.compile(r"^[A-Z0-9.\-]+$")


def read_tickers_csv(path: str) -> tuple[list[str], list[str]]:
    if not os.path.exists(path):
        raise FileNotFoundError(f"Ticker file not found: {path}")

    tickers: list[str] = []
    issues: list[str] = []
    seen: set[str] = set()

    with open(path, "r", newline="", encoding="utf-8") as handle:
        reader = csv.reader(handle)
        rows = list(reader)

    if not rows:
        return [], ["input CSV is empty"]

    header = [cell.strip().lower() for cell in rows[0]]
    ticker_col = 0
    if "ticker" in header:
        ticker_col = header.index("ticker")

    body_rows = rows[1:] if "ticker" in header else rows

    for index, row in enumerate(body_rows, start=2 if "ticker" in header else 1):
        if not row or ticker_col >= len(row):
            issues.append(f"row {index}: missing ticker")
            continue

        raw = row[ticker_col].strip().upper()
        if not raw:
            issues.append(f"row {index}: empty ticker")
            continue
        if not TICKER_PATTERN.match(raw):
            issues.append(f"row {index}: invalid ticker '{raw}'")
            continue
        if raw in seen:
            continue

        seen.add(raw)
        tickers.append(raw)

    return tickers, issues


def write_tickers_csv(path: str, tickers: list[str]) -> None:
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)

    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["ticker"])
        for ticker in sorted(set(tickers)):
            writer.writerow([ticker])


def write_csv(path: str, rows: Iterable[dict[str, object]], fieldnames: list[str]) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def print_rank_table(title: str, rows: list[dict[str, object]], top_n: int, metric_key: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))

    if not rows:
        print("No rows to display.")
        return

    selected = rows[:top_n]
    header = f"{'Rank':<5} {'Ticker':<8} {'Profit':>12} {'Return %':>10} {'Cycles':>8} {'Status':<16}"
    print(header)
    print("-" * len(header))

    for idx, row in enumerate(selected, start=1):
        profit = float(row.get(metric_key, 0.0))
        pct_key = "long_return_pct" if metric_key == "long_profit" else "short_return_pct"
        cyc_key = "long_cycles" if metric_key == "long_profit" else "short_cycles"
        print(
            f"{idx:<5} {str(row.get('ticker', '')):<8} {profit:>12.2f} "
            f"{float(row.get(pct_key, 0.0)):>10.2f} {int(row.get(cyc_key, 0)):>8} {str(row.get('status', '')):<16}"
        )
