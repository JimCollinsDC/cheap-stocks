from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta

import yfinance as yf


@dataclass(frozen=True)
class PriceSeriesResult:
    ticker: str
    status: str
    dates: list[date]
    closes: list[float]
    error: str | None = None


class MarketDataClient:
    def __init__(self, period_days: int = 31) -> None:
        self.period_days = period_days

    def fetch_monthly_closes(self, ticker: str) -> PriceSeriesResult:
        end_date = datetime.utcnow().date() + timedelta(days=1)
        start_date = end_date - timedelta(days=self.period_days)

        try:
            frame = yf.download(
                tickers=ticker,
                start=start_date.isoformat(),
                end=end_date.isoformat(),
                interval="1d",
                progress=False,
                auto_adjust=False,
                threads=False,
            )
        except Exception as exc:
            return PriceSeriesResult(
                ticker=ticker,
                status="error",
                dates=[],
                closes=[],
                error=str(exc),
            )

        if frame is None or frame.empty:
            return PriceSeriesResult(ticker=ticker, status="no_data", dates=[], closes=[])

        if "Close" not in frame.columns:
            return PriceSeriesResult(ticker=ticker, status="missing_close", dates=[], closes=[])

        close_data = frame["Close"]
        # yfinance may return Close as either a Series or a DataFrame.
        if hasattr(close_data, "columns"):
            if ticker in close_data.columns:
                close_series = close_data[ticker].dropna()
            else:
                close_series = close_data.iloc[:, 0].dropna()
        else:
            close_series = close_data.dropna()

        if close_series.empty:
            return PriceSeriesResult(ticker=ticker, status="no_data", dates=[], closes=[])

        dates = [stamp.date() for stamp in close_series.index.to_pydatetime()]
        closes = [float(value) for value in close_series.tolist()]

        if len(closes) < 2:
            return PriceSeriesResult(ticker=ticker, status="insufficient_data", dates=dates, closes=closes)

        return PriceSeriesResult(ticker=ticker, status="ok", dates=dates, closes=closes)
