from __future__ import annotations

import argparse
import os
from datetime import datetime
from typing import Any

from cheap_stocks.analysis import compute_hindsight_metrics
from cheap_stocks.data_source import MarketDataClient
from cheap_stocks.io_utils import print_rank_table, read_tickers_csv, write_csv, write_tickers_csv

RANK_BY_KEYS = {
    "profit": ("long_profit", "short_profit"),
    "percent": ("long_return_pct", "short_return_pct"),
}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Compute perfect-hindsight monthly filter scores for long and short sides "
            "using unlimited alternating cycles."
        )
    )
    parser.add_argument("--input", default="input/stocks.csv", help="Path to ticker CSV")
    parser.add_argument(
        "--output-dir",
        default=None,
        help="Directory for output CSV files. Defaults to a timestamped subfolder under output/.",
    )
    parser.add_argument("--shares", type=int, default=100, help="Equal shares per ticker")
    parser.add_argument("--top", type=int, default=10, help="Rows to show in console ranking")
    parser.add_argument(
        "--normalize-input",
        action="store_true",
        help="Deduplicate and alphabetize the input ticker CSV, then exit.",
    )
    parser.add_argument(
        "--normalized-output",
        default=None,
        help="Optional output path for normalized ticker CSV. Defaults to rewriting --input in place.",
    )
    parser.add_argument(
        "--rank-by",
        choices=sorted(RANK_BY_KEYS),
        default="profit",
        help="Sort rankings by raw dollar profit or percent return.",
    )
    return parser


def resolve_output_dir(output_dir: str | None, now: datetime | None = None) -> str:
    if output_dir:
        return output_dir

    timestamp = (now or datetime.now()).strftime("%Y%m%d-%H%M%S")
    return os.path.join("output", timestamp)


def get_rank_keys(rank_by: str) -> tuple[str, str]:
    return RANK_BY_KEYS[rank_by]


def normalize_input_file(input_path: str, normalized_output: str | None) -> int:
    tickers, parse_issues = read_tickers_csv(input_path)
    target_path = normalized_output or input_path
    write_tickers_csv(target_path, tickers)

    print(f"Normalized {len(tickers)} unique tickers to: {os.path.abspath(target_path)}")
    if parse_issues:
        print("Normalization notes:")
        for issue in parse_issues:
            print(f"- {issue}")
    return 0


def _base_row(ticker: str, status: str) -> dict[str, Any]:
    return {
        "ticker": ticker,
        "status": status,
        "start_date": "",
        "end_date": "",
        "start_close": 0.0,
        "end_close": 0.0,
        "shares": 0,
        "long_capture_per_share": 0.0,
        "short_capture_per_share": 0.0,
        "long_profit": 0.0,
        "short_profit": 0.0,
        "long_return_pct": 0.0,
        "short_return_pct": 0.0,
        "long_cycles": 0,
        "short_cycles": 0,
        "error": "",
    }


def run(
    input_path: str,
    output_dir: str | None,
    shares: int,
    top_n: int,
    rank_by: str,
) -> int:
    tickers, parse_issues = read_tickers_csv(input_path)
    if parse_issues:
        print("Input notes:")
        for issue in parse_issues:
            print(f"- {issue}")

    if not tickers:
        print("No valid tickers found. Nothing to analyze.")
        return 1

    client = MarketDataClient(period_days=31)
    combined_rows: list[dict[str, Any]] = []

    for ticker in tickers:
        series = client.fetch_monthly_closes(ticker)
        row = _base_row(ticker=ticker, status=series.status)

        if series.status != "ok":
            row["error"] = series.error or ""
            combined_rows.append(row)
            continue

        metrics = compute_hindsight_metrics(series.closes, shares=shares)
        row.update(
            {
                "start_date": series.dates[0].isoformat(),
                "end_date": series.dates[-1].isoformat(),
                "start_close": round(series.closes[0], 4),
                "end_close": round(series.closes[-1], 4),
                "shares": shares,
                "long_capture_per_share": round(metrics.long_capture_per_share, 4),
                "short_capture_per_share": round(metrics.short_capture_per_share, 4),
                "long_profit": round(metrics.long_profit, 2),
                "short_profit": round(metrics.short_profit, 2),
                "long_return_pct": round(metrics.long_return_pct, 2),
                "short_return_pct": round(metrics.short_return_pct, 2),
                "long_cycles": metrics.long_cycles,
                "short_cycles": metrics.short_cycles,
            }
        )
        combined_rows.append(row)

    ok_rows = [row for row in combined_rows if row["status"] == "ok"]
    long_rank_key, short_rank_key = get_rank_keys(rank_by)
    long_ranked = sorted(ok_rows, key=lambda item: float(item[long_rank_key]), reverse=True)
    short_ranked = sorted(ok_rows, key=lambda item: float(item[short_rank_key]), reverse=True)

    title_suffix = "Profit" if rank_by == "profit" else "Percent"
    print_rank_table(
        f"Top Long Filter Scores By {title_suffix}",
        long_ranked,
        top_n=top_n,
        metric_key="long_profit",
    )
    print_rank_table(
        f"Top Short Filter Scores By {title_suffix}",
        short_ranked,
        top_n=top_n,
        metric_key="short_profit",
    )

    fields = [
        "ticker",
        "status",
        "start_date",
        "end_date",
        "start_close",
        "end_close",
        "shares",
        "long_capture_per_share",
        "short_capture_per_share",
        "long_profit",
        "short_profit",
        "long_return_pct",
        "short_return_pct",
        "long_cycles",
        "short_cycles",
        "error",
    ]

    resolved_output_dir = resolve_output_dir(output_dir)
    os.makedirs(resolved_output_dir, exist_ok=True)
    write_csv(os.path.join(resolved_output_dir, "combined_detailed.csv"), combined_rows, fields)
    write_csv(os.path.join(resolved_output_dir, "long_ranked.csv"), long_ranked, fields)
    write_csv(os.path.join(resolved_output_dir, "short_ranked.csv"), short_ranked, fields)

    print(f"\nWrote output files to: {os.path.abspath(resolved_output_dir)}")
    return 0


def main() -> int:
    args = build_parser().parse_args()
    if args.normalize_input:
        return normalize_input_file(args.input, args.normalized_output)
    return run(args.input, args.output_dir, args.shares, args.top, args.rank_by)


if __name__ == "__main__":
    raise SystemExit(main())
