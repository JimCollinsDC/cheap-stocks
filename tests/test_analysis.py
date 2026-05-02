from cheap_stocks.analysis import compute_hindsight_metrics


def test_metrics_strictly_rising_series() -> None:
    metrics = compute_hindsight_metrics([1.0, 2.0, 3.5, 4.0], shares=100)
    assert metrics.long_capture_per_share == 3.0
    assert metrics.short_capture_per_share == 0.0
    assert metrics.long_profit == 300.0
    assert metrics.short_profit == 0.0
    assert metrics.long_cycles == 1
    assert metrics.short_cycles == 0


def test_metrics_strictly_falling_series() -> None:
    metrics = compute_hindsight_metrics([5.0, 4.0, 3.0], shares=100)
    assert metrics.long_capture_per_share == 0.0
    assert metrics.short_capture_per_share == 2.0
    assert metrics.long_profit == 0.0
    assert metrics.short_profit == 200.0
    assert metrics.long_cycles == 0
    assert metrics.short_cycles == 1


def test_metrics_zig_zag_series() -> None:
    metrics = compute_hindsight_metrics([10.0, 11.0, 10.5, 12.0, 11.0], shares=100)
    assert metrics.long_capture_per_share == 2.5
    assert metrics.short_capture_per_share == 1.5
    assert metrics.long_profit == 250.0
    assert metrics.short_profit == 150.0
    assert metrics.long_cycles == 2
    assert metrics.short_cycles == 2
