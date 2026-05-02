from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class HindsightMetrics:
    long_capture_per_share: float
    short_capture_per_share: float
    long_profit: float
    short_profit: float
    long_return_pct: float
    short_return_pct: float
    long_cycles: int
    short_cycles: int


def _count_cycles(deltas: Sequence[float], positive: bool) -> int:
    cycles = 0
    in_run = False

    for delta in deltas:
        matches = delta > 0 if positive else delta < 0
        if matches and not in_run:
            cycles += 1
            in_run = True
        elif not matches:
            in_run = False

    return cycles


def compute_hindsight_metrics(closes: Sequence[float], shares: int) -> HindsightMetrics:
    if shares <= 0:
        raise ValueError("shares must be positive")
    if len(closes) < 2:
        raise ValueError("at least 2 close prices are required")

    deltas = [float(closes[i] - closes[i - 1]) for i in range(1, len(closes))]

    long_capture = sum(delta for delta in deltas if delta > 0)
    short_capture = sum(-delta for delta in deltas if delta < 0)

    baseline = float(closes[0]) if float(closes[0]) != 0 else 1.0

    return HindsightMetrics(
        long_capture_per_share=long_capture,
        short_capture_per_share=short_capture,
        long_profit=long_capture * shares,
        short_profit=short_capture * shares,
        long_return_pct=(long_capture / baseline) * 100.0,
        short_return_pct=(short_capture / baseline) * 100.0,
        long_cycles=_count_cycles(deltas, positive=True),
        short_cycles=_count_cycles(deltas, positive=False),
    )
