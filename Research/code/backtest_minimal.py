"""
backtest_minimal.py — Minimal, CORRECT backtest engine (educational).

A strategy is a function `signal(df, i)` that returns +1 (long), -1 (short)
or 0 (no trade), using ONLY bars up to and including index i (closed bars).
Entry is at the OPEN of the NEXT bar (no lookahead). SL/TP are checked with
spread modeled in.

Run:  python backtest_minimal.py
Edit the `signal()` function to try your own idea, then re-run.
"""
import pandas as pd

from data_loader import load_pair


# ---------------- 1. YOUR STRATEGY (edit this) ----------------
# df has columns: datetime, O, H, L, C, V  (15-min bars)
def signal(df, i):
    """
    Return +1 / -1 / 0 for bar index i.
    You may only look at df.iloc[:i+1] (up to and including i).
    """
    if i < 21:
        return 0
    # Example: buy if the close breaks above the high of the previous 20 bars.
    lookback = df.iloc[i - 20:i]      # previous 20 bars (NOT including current)
    if df.iloc[i]["C"] > lookback["H"].max():
        return 1
    return 0


# ---------------- 2. The engine (do not need to edit) ----------------
def backtest(df, entry_signal, sl_pips, tp_pips, spread_pips=0.8, pip=1e-4):
    """
    Run the strategy over df. Returns a list of PnL per trade, in pips.
    - Signal is computed on the CLOSED bar i-1.
    - Entry at the OPEN of bar i.
    - Conservative SL/TP fill (SL takes priority when both hit in one bar).
    """
    trades = []
    pos = None
    for i in range(1, len(df)):
        bar = df.iloc[i]
        if pos is None:
            sig = entry_signal(df, i - 1)          # signal from CLOSED bar i-1
            if sig != 0:
                entry = bar["O"]
                if sig == 1:
                    pos = {"side": 1, "entry": entry,
                           "sl": entry - sl_pips * pip, "tp": entry + tp_pips * pip}
                else:
                    pos = {"side": -1, "entry": entry,
                           "sl": entry + sl_pips * pip, "tp": entry - tp_pips * pip}
            continue

        exit_px = None
        if pos["side"] == 1:
            if bar["L"] <= pos["sl"]:
                exit_px = pos["sl"]           # SL first (conservative)
            elif bar["H"] >= pos["tp"]:
                exit_px = pos["tp"]
        else:
            if bar["H"] >= pos["sl"]:
                exit_px = pos["sl"]
            elif bar["L"] <= pos["tp"]:
                exit_px = pos["tp"]

        if exit_px is not None:
            pnl_pips = (exit_px - pos["entry"]) * pos["side"] / pip - spread_pips
            trades.append(pnl_pips)
            pos = None
    return trades


# ---------------- 3. Metrics ----------------
def metrics(trades, deposit=10000.0, pip_value=1.0):
    """Report N, WR%, PF, net pips, expectancy, MaxDD%, % profit on deposit."""
    n = len(trades)
    if n == 0:
        return {"N": 0}
    wins = [t for t in trades if t > 0]
    losses = [t for t in trades if t <= 0]
    gross_win = sum(wins)
    gross_loss = abs(sum(losses))
    pf = gross_win / gross_loss if gross_loss > 0 else float("inf")
    wr = len(wins) / n * 100
    net_pips = sum(trades)
    expectancy = net_pips / n

    # Equity curve @ 0.5% risk per trade, simple pip -> $ mapping
    balance = deposit
    peak = deposit
    max_dd = 0.0
    for t in trades:
        balance += t * pip_value
        peak = max(peak, balance)
        dd = (peak - balance) / peak * 100
        max_dd = max(max_dd, dd)
    pct_profit = (balance - deposit) / deposit * 100

    return {
        "N": n,
        "WR%": round(wr, 1),
        "PF": round(pf, 2),
        "net_pips": round(net_pips, 1),
        "expectancy": round(expectancy, 2),
        "MaxDD%": round(max_dd, 1),
        "%profit": round(pct_profit, 1),
    }


# ---------------- 4. Run ----------------
if __name__ == "__main__":
    SYM = "GBPUSD"
    SL, TP = 8, 8          # pips
    SPREAD = 0.8           # pips (rough forex average)

    df_m15, _ = load_pair(SYM, "2024-01-01", "2026-07-01")
    trades = backtest(df_m15, signal, SL, TP, SPREAD)
    m = metrics(trades)

    print("Symbol: {}  SL={}p  TP={}p  spread={}p".format(SYM, SL, TP, SPREAD))
    print("-" * 40)
    for k, v in m.items():
        print("  {:<12} {}".format(k, v))
    print("-" * 40)
    if m["N"] < 100:
        print("⚠️  N < 100 — eșantion mic, nu trage concluzii.")
    if m["PF"] < 2.3:
        print("⚠️  PF < 2.3 — sub pragul de breakeven real (vezi 05_METRICS_AND_CALIBRATION).")
