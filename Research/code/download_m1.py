"""
download_m1.py — Download ~2.5 years of M1 OHLC for a list of forex pairs
via the Strategy Tester + ExportM1History_EA.

Prerequisites:
  1. MT5 installed + logged into your broker (e.g. RoboForex).
  2. ExportM1History_EA.ex5 compiled and placed in MQL5/Experts/Advisors/.
  3. pip install pandas

Edit the CONFIG section below, then run:  python download_m1.py
"""
import subprocess
import time
import os
import glob

import pandas as pd

# ===================== CONFIG (edit these) =====================
TERMINAL_EXE = r"C:\Program Files\MetaTrader 5\terminal64.exe"   # your MT5 terminal
TERMINAL_DIR = r"C:\Program Files\MetaTrader 5"                  # same folder as above
PAIRS = ["EURUSD", "USDCHF", "AUDUSD", "GBPUSD", "AUDJPY", "GBPJPY", "USDJPY"]
# ===============================================================

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "history_export")
COMMON = os.path.join(os.environ["APPDATA"], "MetaQuotes", "Terminal", "Common", "Files")
os.makedirs(OUT, exist_ok=True)

# Two passes per pair: each FromDate syncs ~1.25yr of M1 history in the tester.
# Together they cover ~2024-01 -> now.
PASSES = [
    ("P1", "2025.07.01", "2025.07.02"),   # syncs ~2024.01 - 2025.07
    ("P2", "2026.07.01", "2026.07.02"),   # syncs ~2025.01 - 2026.07
]


def kill():
    """Close the MT5 terminal (so the next test starts fresh)."""
    subprocess.run(
        ["powershell", "-Command",
         "Get-Process terminal64 -ErrorAction SilentlyContinue | "
         "Where-Object { $_.Path -eq '" + TERMINAL_EXE + "' } | Stop-Process -Force"],
        capture_output=True,
    )
    time.sleep(2)


def run_export(sym, name, frm, to):
    """Run the ExportM1History EA once for (sym, pass)."""
    ini = os.path.join(TERMINAL_DIR, "_m1exp_{}_{}.ini".format(sym, name))
    with open(ini, "w") as f:
        f.write(
            "[Tester]\n"
            "Expert=Advisors\\ExportM1History_EA.ex5\n"
            "Symbol={sym}\n"
            "Period=M1\n"
            "Model=0\n"
            "Optimization=0\n"
            "Visual=0\n"
            "ShutdownTerminal=1\n"
            "FromDate={frm}\n"
            "ToDate={to}\n"
            "ForwardMode=0\n"
            "Deposit=10000\n"
            "Currency=USD\n"
            "Leverage=100\n"
            "ExecutionMode=0\n"
            "\n"
            "[TesterInputs]\n"
            "InpFileName={sym}_M1_{name}.csv\n".format(sym=sym, name=name, frm=frm, to=to)
        )

    kill()
    print("  {name}: running...".format(name=name))
    try:
        subprocess.run(
            [TERMINAL_EXE, "/config:" + ini],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            timeout=240,
        )
    except subprocess.TimeoutExpired:
        print("  {name}: timeout (240s) — check the terminal".format(name=name))
    time.sleep(1)


def process_pair(sym):
    """Run both passes for one symbol, merge + dedup + save."""
    print("\n" + "=" * 50)
    print("  {}".format(sym))
    print("=" * 50)

    # Clear old exports for this symbol
    for old in glob.glob(os.path.join(COMMON, "{}_M1_*.csv".format(sym))):
        try:
            os.remove(old)
        except Exception:
            pass

    for name, frm, to in PASSES:
        run_export(sym, name, frm, to)

    files = sorted(glob.glob(os.path.join(COMMON, "{}_M1_*.csv".format(sym))))
    if not files:
        print("  [FAIL] no export files found for {} (check Common\\Files)".format(sym))
        return None

    frames = []
    for fp in files:
        df = pd.read_csv(fp)
        print("    {}: {:,} rows  {} -> {}".format(
            os.path.basename(fp), len(df), df["Datetime"].iloc[0], df["Datetime"].iloc[-1]))
        frames.append(df)

    full = (pd.concat(frames)
            .drop_duplicates(subset="Datetime")
            .sort_values("Datetime")
            .reset_index(drop=True))

    for c in ["Spread", "RealVolume"]:
        if c not in full.columns:
            full[c] = 0
    full = full[["Datetime", "Open", "High", "Low", "Close", "Volume", "Spread", "RealVolume"]]

    path = os.path.join(OUT, "{}_M1_full.csv".format(sym))
    full.to_csv(path, index=False)
    print("  [OK] {:,} bars -> {} ({:.1f} MB)".format(
        len(full), os.path.basename(path), os.path.getsize(path) / 1e6))
    print("  Range: {} -> {}".format(full["Datetime"].iloc[0], full["Datetime"].iloc[-1]))
    return len(full)


if __name__ == "__main__":
    print("M1 DOWNLOAD — {} pairs (Period=M1)".format(len(PAIRS)))
    print("Terminal: {}".format(TERMINAL_EXE))
    print("Pairs: {}".format(", ".join(PAIRS)))

    t0 = time.time()
    results = {}
    for sym in PAIRS:
        results[sym] = process_pair(sym)
    kill()

    print("\n" + "=" * 50)
    print("SUMMARY ({:.1f} min)".format((time.time() - t0) / 60))
    print("=" * 50)
    for sym, n in results.items():
        print("  {:<8} {}".format(sym, "{:,} bars".format(n) if n else "FAILED"))
    print("\nFiles in: {}".format(OUT))
