#!/usr/bin/env python3
"""Options Pricing & Greeks Calculator - command line interface.

Examples
--------
python main.py price  --S 100 --K 105 --T 0.5 --r 0.05 --sigma 0.2 --type call
python main.py greeks --S 100 --K 105 --T 0.5 --r 0.05 --sigma 0.2 --type put --plot
python main.py iv     --price 8.5 --S 100 --K 100 --T 1 --r 0.05 --type call
python main.py compare --S 100 --K 100 --T 1 --r 0.05 --sigma 0.2 --type put
"""
import argparse
import os
from optionlib import bs_price, bs_greeks, implied_volatility, binomial_price, mc_price
from optionlib.plots import plot_greeks, plot_payoff


def add_common(p, need_sigma=True):
    p.add_argument("--S", type=float, required=True, help="spot price")
    p.add_argument("--K", type=float, required=True, help="strike price")
    p.add_argument("--T", type=float, required=True, help="time to expiry (years)")
    p.add_argument("--r", type=float, required=True, help="risk-free rate, e.g. 0.05")
    if need_sigma:
        p.add_argument("--sigma", type=float, required=True, help="volatility, e.g. 0.2")
    p.add_argument("--q", type=float, default=0.0, help="dividend yield (default 0)")
    p.add_argument("--type", choices=["call", "put"], default="call", dest="otype")


def main():
    ap = argparse.ArgumentParser(description="Options Pricing & Greeks Calculator")
    sub = ap.add_subparsers(dest="cmd", required=True)
    add_common(sub.add_parser("price", help="Black-Scholes price"))
    g = sub.add_parser("greeks", help="price + Greeks"); add_common(g)
    g.add_argument("--plot", action="store_true", help="save Greeks & payoff charts to outputs/")
    c = sub.add_parser("compare", help="compare BS / binomial / American / Monte Carlo"); add_common(c)
    iv = sub.add_parser("iv", help="implied volatility from a market price"); add_common(iv, need_sigma=False)
    iv.add_argument("--price", type=float, required=True, help="observed option price")
    a = ap.parse_args()
    os.makedirs("outputs", exist_ok=True)

    if a.cmd == "price":
        print(f"{a.otype.title()} price (Black-Scholes): {bs_price(a.S, a.K, a.T, a.r, a.sigma, a.otype, a.q):.4f}")
    elif a.cmd == "greeks":
        price = bs_price(a.S, a.K, a.T, a.r, a.sigma, a.otype, a.q)
        gr = bs_greeks(a.S, a.K, a.T, a.r, a.sigma, a.otype, a.q)
        print(f"{a.otype.title()} price: {price:.4f}")
        for k, v in gr.as_dict().items():
            print(f"  {k:<6} {v:>10.5f}")
        if a.plot:
            print("Saved:", plot_greeks(a.K, a.T, a.r, a.sigma, a.otype, a.q),
                  plot_payoff(a.S, a.K, a.T, a.r, a.sigma, a.otype, a.q))
    elif a.cmd == "compare":
        bs = bs_price(a.S, a.K, a.T, a.r, a.sigma, a.otype, a.q)
        eu = binomial_price(a.S, a.K, a.T, a.r, a.sigma, a.otype, a.q)
        am = binomial_price(a.S, a.K, a.T, a.r, a.sigma, a.otype, a.q, american=True)
        mc, se = mc_price(a.S, a.K, a.T, a.r, a.sigma, a.otype, a.q)
        print(f"Black-Scholes (European): {bs:.4f}")
        print(f"Binomial     (European): {eu:.4f}")
        print(f"Binomial     (American): {am:.4f}   early-exercise premium {am - eu:.4f}")
        print(f"Monte Carlo  (European): {mc:.4f} ± {1.96 * se:.4f} (95% CI)")
    elif a.cmd == "iv":
        vol = implied_volatility(a.price, a.S, a.K, a.T, a.r, a.otype, a.q)
        print(f"Implied volatility: {vol:.4%}")


if __name__ == "__main__":
    main()
