"""
walk_forward.py — Rolling walk-forward template.

Idea: split history into windows. For each adjacent pair (train, test):
  1. Grid-search a small parameter set ON TRAIN ONLY.
  2. Freeze the best parameters, evaluate ON TEST (unseen).
Collect per-window results and apply the gate: config must beat baseline on
>= 3 of 4 test windows.

Run:  python walk_forward.py
"""
import pandas as pd

from data_loader import load_pair
from backtest_minimal import backtest, signal, metrics


def score(df, sl, tp, spread=0.8):
    """Return PF (profit factor) on df — the thing we optimize."""
    t = backtest(df, signal, sl, tp, spread)
    m = metrics(t)
    return m.get("PF", 0.0)


def windows(df, n=4):
    """Split df into n equal, non-overlapping time windows."""
    idx = list(range(0, len(df), len(df) // n)) + [len(df)]
    return [(idx[k], idx[k + 1]) for k in range(n)]


if __name__ == "__main__":
    SYM = "GBPUSD"
    df_m15, _ = load_pair(SYM, "2024-01-01", "2026-07-01")

    # Small grid (keep it small — Gate 8: max 1-2 params per round)
    SL_GRID = [6, 8, 10]
    TP_GRID = [8, 12, 16]
    BASELINE = (8, 8)   # fixed baseline config to beat

    wins = df_m15
    ws = windows(wins, n=4)

    print("Walk-forward: {}  |  windows = 4  |  grid SL{} x TP{}".format(
        SYM, SL_GRID, TP_GRID))
    print("=" * 60)

    beats = 0
    total_test_windows = 0
    for k in range(len(ws) - 1):
        train_a, train_b = ws[k]
        test_a, test_b = ws[k + 1]

        train = wins.iloc[train_a:train_b]
        test = wins.iloc[test_a:test_b]

        # 1. optimize on TRAIN only
        best = None
        for sl in SL_GRID:
            for tp in TP_GRID:
                pf = score(train, sl, tp)
                if best is None or pf > best[0]:
                    best = (pf, sl, tp)

        # 2. evaluate frozen on TEST
        pf_train, bsl, btp = best
        t_test = backtest(test, signal, bsl, btp)
        m_test = metrics(t_test)
        t_base = backtest(test, signal, BASELINE[0], BASELINE[1])
        m_base = metrics(t_base)

        beat = m_test.get("PF", 0) > m_base.get("PF", 0)
        beats += 1 if beat else 0
        total_test_windows += 1

        print("W{} (train {}-{}) -> best SL={} TP={}  trainPF={:.2f}".format(
            k + 1, train_a, train_b, bsl, btp, pf_train))
        print("   TEST: N={}  WR={}%  PF={}  net={}p  |  baseline PF={}  ->  {}".format(
            m_test.get("N"), m_test.get("WR%"), m_test.get("PF"),
            m_test.get("net_pips"), m_base.get("PF"),
            "BEAT ✓" if beat else "lose ✗"))

    print("=" * 60)
    print("Result: {} / {} test windows beat baseline".format(beats, total_test_windows))
    print("Gate 1: PASS" if beats >= 3 else "Gate 1: FAIL (need >= 3/4)")
