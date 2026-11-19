"""Cox-Ross-Rubinstein binomial tree supporting American exercise."""
from __future__ import annotations
import numpy as np


def binomial_price(S, K, T, r, sigma, option_type="call", q=0.0,
                   steps=500, american=False) -> float:
    if option_type not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'")
    dt = T / steps
    u = np.exp(sigma * np.sqrt(dt))
    d = 1 / u
    p = (np.exp((r - q) * dt) - d) / (u - d)
    disc = np.exp(-r * dt)
    sign = 1 if option_type == "call" else -1

    j = np.arange(steps + 1)
    prices = S * u ** (steps - j) * d ** j          # terminal prices
    values = np.maximum(sign * (prices - K), 0.0)

    for i in range(steps - 1, -1, -1):              # backward induction
        values = disc * (p * values[:-1] + (1 - p) * values[1:])
        if american:
            j = np.arange(i + 1)
            prices = S * u ** (i - j) * d ** j
            values = np.maximum(values, sign * (prices - K))
    return float(values[0])
