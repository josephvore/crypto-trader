from __future__ import annotations


def kelly_fraction(
    hit_rate: float, avg_win: float, avg_loss: float, cap_fraction: float = 0.25
) -> float:
    if avg_loss <= 0 or avg_win <= 0:
        return 0.0
    b = avg_win / avg_loss
    f = (hit_rate * (b + 1) - 1) / b
    return max(0.0, min(f, cap_fraction))
