"""Monte Carlo pricing of European options with antithetic variates."""
from __future__ import annotations
import numpy as np


def mc_price(S, K, T, r, sigma, option_type="call", q=0.0,
             n_paths=200_000, seed=42):
    """Return (price, standard_error)."""
    rng = np.random.default_rng(seed)
    z = rng.standard_normal(n_paths // 2)
    z = np.concatenate([z, -z])  # antithetic variates
    ST = S * np.exp((r - q - 0.5 * sigma**2) * T + sigma * np.sqrt(T) * z)
    payoff = np.maximum(ST - K, 0) if option_type == "call" else np.maximum(K - ST, 0)
    disc = np.exp(-r * T) * payoff
    return float(disc.mean()), float(disc.std(ddof=1) / np.sqrt(len(disc)))
