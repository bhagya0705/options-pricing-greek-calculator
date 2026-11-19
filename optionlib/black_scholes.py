"""Black-Scholes-Merton model (European options, continuous dividend yield q)."""
from __future__ import annotations
import math
from dataclasses import dataclass
from scipy.stats import norm
from scipy.optimize import brentq


def _validate(S, K, T, sigma, option_type):
    if option_type not in ("call", "put"):
        raise ValueError("option_type must be 'call' or 'put'")
    if S <= 0 or K <= 0:
        raise ValueError("S and K must be positive")
    if T < 0 or sigma < 0:
        raise ValueError("T and sigma must be non-negative")


def _d1_d2(S, K, T, r, sigma, q):
    sqrt_t = math.sqrt(T)
    d1 = (math.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * sqrt_t)
    return d1, d1 - sigma * sqrt_t


def bs_price(S, K, T, r, sigma, option_type="call", q=0.0) -> float:
    """Black-Scholes-Merton price.

    S spot, K strike, T years to expiry, r risk-free rate (cont.),
    sigma volatility, q continuous dividend yield.
    """
    _validate(S, K, T, sigma, option_type)
    if T == 0 or sigma == 0:  # intrinsic / discounted-forward value
        fwd = S * math.exp(-q * T) - K * math.exp(-r * T)
        return max(fwd, 0.0) if option_type == "call" else max(-fwd, 0.0)
    d1, d2 = _d1_d2(S, K, T, r, sigma, q)
    if option_type == "call":
        return S * math.exp(-q * T) * norm.cdf(d1) - K * math.exp(-r * T) * norm.cdf(d2)
    return K * math.exp(-r * T) * norm.cdf(-d2) - S * math.exp(-q * T) * norm.cdf(-d1)


@dataclass
class Greeks:
    delta: float
    gamma: float
    vega: float   # per 1 percentage-point change in volatility
    theta: float  # per calendar day
    rho: float    # per 1 percentage-point change in rate

    def as_dict(self):
        return self.__dict__.copy()


def bs_greeks(S, K, T, r, sigma, option_type="call", q=0.0) -> Greeks:
    """Analytical Greeks. Vega/rho are scaled per 1%, theta per day."""
    _validate(S, K, T, sigma, option_type)
    if T == 0 or sigma == 0:
        raise ValueError("Greeks require T > 0 and sigma > 0")
    d1, d2 = _d1_d2(S, K, T, r, sigma, q)
    pdf = norm.pdf(d1)
    disc_q, disc_r = math.exp(-q * T), math.exp(-r * T)
    gamma = disc_q * pdf / (S * sigma * math.sqrt(T))
    vega = S * disc_q * pdf * math.sqrt(T) / 100
    common_theta = -S * disc_q * pdf * sigma / (2 * math.sqrt(T))
    if option_type == "call":
        delta = disc_q * norm.cdf(d1)
        theta = common_theta - r * K * disc_r * norm.cdf(d2) + q * S * disc_q * norm.cdf(d1)
        rho = K * T * disc_r * norm.cdf(d2) / 100
    else:
        delta = -disc_q * norm.cdf(-d1)
        theta = common_theta + r * K * disc_r * norm.cdf(-d2) - q * S * disc_q * norm.cdf(-d1)
        rho = -K * T * disc_r * norm.cdf(-d2) / 100
    return Greeks(delta, gamma, vega, theta / 365, rho)


def implied_volatility(market_price, S, K, T, r, option_type="call", q=0.0,
                       low=1e-6, high=5.0) -> float:
    """Solve for sigma such that model price == market price (Brent's method)."""
    _validate(S, K, T, 0.2, option_type)
    if T <= 0:
        raise ValueError("T must be > 0")
    f = lambda s: bs_price(S, K, T, r, s, option_type, q) - market_price
    if f(low) * f(high) > 0:
        raise ValueError("No implied volatility in [%g, %g]; price violates no-arbitrage bounds" % (low, high))
    return brentq(f, low, high, xtol=1e-10)
