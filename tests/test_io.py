from cheap_stocks.io_utils import read_tickers_csv, write_tickers_csv
from cheap_stocks.main import get_rank_keys, resolve_output_dir


def test_resolve_output_dir_uses_timestamp_when_unspecified() -> None:
    resolved = resolve_output_dir(None, now=__import__("datetime").datetime(2026, 5, 1, 9, 30, 45))

    assert resolved == "output\\20260501-093045"


def test_get_rank_keys_supports_percent_sorting() -> None:
    assert get_rank_keys("percent") == ("long_return_pct", "short_return_pct")


def test_read_tickers_csv_dedup_and_validate(tmp_path) -> None:
    sample = tmp_path / "stocks.csv"
    sample.write_text("ticker\nAAPL\naapl\nBAD$\n,\nMSFT\n", encoding="utf-8")

    tickers, issues = read_tickers_csv(str(sample))

    assert tickers == ["AAPL", "MSFT"]
    assert any("invalid ticker" in issue for issue in issues)
    assert any("empty ticker" in issue for issue in issues)


def test_write_tickers_csv_sorts_and_deduplicates(tmp_path) -> None:
    output = tmp_path / "normalized.csv"

    write_tickers_csv(str(output), ["MSFT", "AAPL", "MSFT"])

    assert output.read_text(encoding="utf-8") == "ticker\nAAPL\nMSFT\n"


def test_write_tickers_csv_supports_in_place_directoryless_paths(tmp_path) -> None:
    output = tmp_path / "stocks.csv"

    write_tickers_csv(str(output), ["ZZZ", "AAA"])

    tickers, issues = read_tickers_csv(str(output))
    assert tickers == ["AAA", "ZZZ"]
    assert issues == []
