# Options Pricing & Greeks Calculator

A Python toolkit that prices European and American options with three independent
models, computes all major Greeks analytically, and backs out implied volatility.

## Features
- **Black-Scholes-Merton** pricing with continuous dividend yield
- **Greeks**: Delta, Gamma, Vega (per 1% vol), Theta (per day), Rho (per 1% rate)
- **Implied volatility** solver (Brent root-finding)
- **Cox-Ross-Rubinstein binomial tree** - supports **American** exercise (early-exercise premium)
- **Monte Carlo** pricer with antithetic variates and 95% confidence interval
- Charts: Greeks vs spot, payoff / P&L diagram
- 9 unit tests (reference values, put-call parity, Greeks vs finite differences, model convergence)

## Setup
```bash
pip install -r requirements.txt
python -m unittest discover -s tests -v
```

## Usage
```bash
python main.py price   --S 100 --K 105 --T 0.5 --r 0.05 --sigma 0.2 --type call
python main.py greeks  --S 100 --K 105 --T 0.5 --r 0.05 --sigma 0.2 --type put --plot
python main.py compare --S 100 --K 100 --T 1   --r 0.05 --sigma 0.2 --type put
python main.py iv      --price 8.5 --S 100 --K 100 --T 1 --r 0.05 --type call
```
Add `--q 0.02` for a 2% dividend yield. Charts are saved to `outputs/`.

Example (`compare`, ATM 1-year put): BS 5.5735 | Binomial 5.5695 | American 6.0888 | Monte Carlo 5.5842 ± 0.038

## Use as a library
```python
from optionlib import bs_price, bs_greeks, implied_volatility
bs_price(100, 100, 1, 0.05, 0.2, "call")      # 10.4506
bs_greeks(100, 100, 1, 0.05, 0.2, "call").delta
```

## Math
d1 = [ln(S/K) + (r - q + σ²/2)T] / (σ√T), d2 = d1 - σ√T
Call = S·e^(-qT)·N(d1) - K·e^(-rT)·N(d2)

## Assumptions / limitations
Constant volatility and rates, log-normal prices, no transaction costs.
Black-Scholes and Monte Carlo price European options only; use the binomial tree for American.

## Project structure
```
optionlib/   black_scholes.py  binomial.py  monte_carlo.py  plots.py
tests/       test_options.py
main.py      CLI
```
