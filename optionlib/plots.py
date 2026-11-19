"""Visualisations: Greeks curves and payoff / P&L diagram."""
from __future__ import annotations
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from .black_scholes import bs_price, bs_greeks


def plot_greeks(K, T, r, sigma, option_type="call", q=0.0, path="outputs/greeks.png"):
    spots = np.linspace(0.5 * K, 1.5 * K, 200)
    names = ["delta", "gamma", "vega", "theta", "rho"]
    data = {n: [] for n in names}
    for s in spots:
        g = bs_greeks(s, K, T, r, sigma, option_type, q)
        for n in names:
            data[n].append(getattr(g, n))
    fig, axes = plt.subplots(2, 3, figsize=(14, 7))
    axes = axes.ravel()
    axes[0].plot(spots, [bs_price(s, K, T, r, sigma, option_type, q) for s in spots])
    axes[0].set_title("Option price")
    for ax, n in zip(axes[1:], names):
        ax.plot(spots, data[n], color="tab:orange")
        ax.set_title(n.capitalize())
    for ax in axes:
        ax.axvline(K, color="grey", ls="--", lw=0.8)
        ax.set_xlabel("Spot price"); ax.grid(alpha=0.3)
    fig.suptitle(f"{option_type.title()} Greeks (K={K}, T={T}y, r={r:.1%}, sigma={sigma:.0%})")
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)
    return path


def plot_payoff(S, K, T, r, sigma, option_type="call", q=0.0, path="outputs/payoff.png"):
    spots = np.linspace(0.5 * K, 1.5 * K, 200)
    premium = bs_price(S, K, T, r, sigma, option_type, q)
    intrinsic = np.maximum(spots - K, 0) if option_type == "call" else np.maximum(K - spots, 0)
    fig, ax = plt.subplots(figsize=(8, 5))
    ax.plot(spots, intrinsic - premium, label="P&L at expiry (long)")
    ax.plot(spots, [bs_price(s, K, T, r, sigma, option_type, q) - premium for s in spots],
            label="P&L today (model)", ls="--")
    ax.axhline(0, color="black", lw=0.8)
    ax.set_xlabel("Spot price"); ax.set_ylabel("Profit / loss"); ax.legend(); ax.grid(alpha=0.3)
    ax.set_title(f"Long {option_type} payoff (premium {premium:.2f})")
    fig.tight_layout(); fig.savefig(path, dpi=130); plt.close(fig)
    return path
