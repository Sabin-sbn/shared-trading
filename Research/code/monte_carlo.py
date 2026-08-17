"""
monte_carlo.py — Bootstrap Monte Carlo on a list of trade R-multiples.

Answers: is this profit structural, or just lucky ordering?
Resamples trades with replacement thousands of times and measures how often
the equity curve breaches a prop-firm drawdown limit.

Gate 3: breach rate must be < 5%.

Run:  python monte_carlo.py
"""
import random

import pandas as pd

from data_loader import load_pair
from backtest_minimal import backtest, signal


def run_mc(trades_pips, n_sims=5000, deposit=10000.0, risk_pct=0.005,
           sl_pips=8.0, pip_value=1.0, max_dd_pct=10.0):
    """
    Bootstrap the trade list (in pips). Each trade risks `risk_pct` of current
    equity; pip value = risk / sl_pips * pip_value (per-unit). Count breaches.
    """
    n = len(trades_pips)
    if n == 0:
        return 0, 0

    breaches = 0
    rng = random.Random(42)
    for _ in range(n_sims):
        balance = deposit
        peak = deposit
        breached = False
        for _ in range(n):
            p = rng.choice(trades_pips)                    # resample with replacement
            # $ per pip at current equity, 0.5% risk, SL = sl_pips
            per_pip = (balance * risk_pct) / sl_pips
            balance += p * per_pip
            peak = max(peak, balance)
            dd = (peak - balance) / peak * 100
            if dd >= max_dd_pct:
                breached = True
                break
        breaches += 1 if breached else 0

    return breaches, n_sims


if __name__ == "__main__":
    SYM = "GBPUSD"
    SL, TP = 8, 8
    df_m15, _ = load_pair(SYM, "2024-01-01", "2026-07-01")
    trades = backtest(df_m15, signal, SL, TP)

    breaches, n_sims = run_mc(trades, sl_pips=SL)
    rate = breaches / n_sims * 100

    print("Monte Carlo: {}  N={}  {} sims  (risk 0.5%/trade, $10k, maxDD 10%)".format(
        SYM, len(trades), n_sims))
    print("-" * 50)
    print("Breaches: {} / {}  ->  {:.2f}%".format(breaches, n_sims, rate))
    print("-" * 50)
    print("Gate 3: PASS (breach < 5%)" if rate < 5 else "Gate 3: FAIL (breach >= 5%)")
