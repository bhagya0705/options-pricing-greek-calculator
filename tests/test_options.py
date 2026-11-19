import math, os, sys, unittest
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from optionlib import bs_price, bs_greeks, implied_volatility, binomial_price, mc_price


class TestOptions(unittest.TestCase):
    P = dict(S=100, K=100, T=1.0, r=0.05, sigma=0.2)

    def test_reference_values(self):
        self.assertAlmostEqual(bs_price(**self.P, option_type="call"), 10.4506, places=3)
        self.assertAlmostEqual(bs_price(**self.P, option_type="put"), 5.5735, places=3)

    def test_put_call_parity(self):
        q = 0.02
        c = bs_price(**self.P, option_type="call", q=q)
        p = bs_price(**self.P, option_type="put", q=q)
        self.assertAlmostEqual(c - p, 100 * math.exp(-q) - 100 * math.exp(-0.05), places=8)

    def test_greeks_match_finite_difference(self):
        h = 1e-3
        g = bs_greeks(**self.P)
        up = bs_price(**{**self.P, "S": 100 + h}); dn = bs_price(**{**self.P, "S": 100 - h})
        mid = bs_price(**self.P)
        self.assertAlmostEqual(g.delta, (up - dn) / (2 * h), places=5)
        self.assertAlmostEqual(g.gamma, (up - 2 * mid + dn) / h**2, places=4)
        v_up = bs_price(**{**self.P, "sigma": 0.2 + h}); v_dn = bs_price(**{**self.P, "sigma": 0.2 - h})
        self.assertAlmostEqual(g.vega, (v_up - v_dn) / (2 * h) / 100, places=5)

    def test_implied_vol_roundtrip(self):
        price = bs_price(S=100, K=110, T=0.5, r=0.03, sigma=0.35, option_type="put")
        self.assertAlmostEqual(implied_volatility(price, 100, 110, 0.5, 0.03, "put"), 0.35, places=6)

    def test_binomial_converges_to_bs(self):
        bs = bs_price(**self.P, option_type="call")
        self.assertAlmostEqual(binomial_price(**self.P, option_type="call", steps=1000), bs, places=2)

    def test_american_put_geq_european(self):
        self.assertGreater(binomial_price(**self.P, option_type="put", american=True),
                           binomial_price(**self.P, option_type="put"))

    def test_american_call_no_dividend_equals_european(self):
        self.assertAlmostEqual(binomial_price(**self.P, option_type="call"),
                               binomial_price(**self.P, option_type="call", american=True), places=6)

    def test_monte_carlo_within_ci(self):
        bs = bs_price(**self.P, option_type="call")
        mc, se = mc_price(**self.P, option_type="call")
        self.assertLess(abs(mc - bs), 4 * se)

    def test_invalid_inputs(self):
        with self.assertRaises(ValueError):
            bs_price(-1, 100, 1, 0.05, 0.2)
        with self.assertRaises(ValueError):
            bs_price(100, 100, 1, 0.05, 0.2, "straddle")


if __name__ == "__main__":
    unittest.main()
