"""
download_m1.py — Download ~2.5 ani de M1 OHLC din MT5 (RoboForex sau orice broker).
Rulare simpla: python download_m1.py

Cum functioneaza:
  1. Ruleaza ExportM1History_EA.ex5 in Strategy Tester (headless) cu Period=M1
     -> testerul sincronizeaza istoricul M1 de la broker (~2.5 ani)
  2. EA-ul exporta barele M1 din cache intr-un CSV in folderul Common\\Files
  3. Scriptul ia fisierele, le combina, deduplica si salveaza ca {SYM}_M1_full.csv

De ce 2 treceri (passes): testerul sincronizeaza doar ~1.5-2 ani de M1 la o singura
rulare. Cu 2 treceri (FromDate=2025.07 + FromDate=2026.07) acoperi 2024 -> 2026.

Cerinte:
  - MT5 instalat (ex: RoboForex) — cont demo e de ajuns, nu trebuie bani
  - ExportM1History_EA.ex5 copiat in: <MT5_DIR>\\MQL5\\Experts\\Advisors\\
  - Python 3 + pandas (pip install pandas)
"""
import subprocess, time, os, sys, re, glob
import pandas as pd

# ============ CONFIGURARE ============
# Calea catre terminal64.exe al MT5-ului tau (schimba daca e altundeva):
TERMINAL = r"C:\Program Files\MetaTrader 5\terminal64.exe"
# Directorul MT5 (unde se afla terminal64.exe):
DIR = r"C:\Program Files\MetaTrader 5"
# Folderul Common al MT5 (unde pune EA-ul fisierele) — de obicei automat:
COMMON = os.path.join(os.environ.get("APPDATA", ""), "MetaQuotes", "Terminal", "Common", "Files")
# Perechile de descarcat:
PAIRS = ["EURUSD", "USDCHF", "AUDUSD", "GBPUSD", "AUDJPY", "GBPJPY", "USDJPY"]
# Output folder (implicit: folderul curent):
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "history_export")
# =====================================

# Doua treceri ca sa acoperi 2024-01 -> 2026-07 (2.5 ani de M1)
PASSES = [
    ("P1", "2025.07.01", "2025.07.02"),  # sincronizeaza ~2024.01 -> 2025.07
    ("P2", "2026.07.01", "2026.07.02"),  # sincronizeaza ~2025.01 -> 2026.07
]

os.makedirs(OUT, exist_ok=True)


def kill():
    """Opreste MT5 daca e deschis (trebuie sa fie inchis inainte de tester)."""
    subprocess.run(
        [
            "powershell",
            "-Command",
            "Get-Process terminal64 -ErrorAction SilentlyContinue | "
            "Where-Object { $_.Path -eq '" + TERMINAL + "' } | "
            "Stop-Process -Force",
        ],
        capture_output=True,
    )
    time.sleep(2)


def run_export(sym, name, frm, to):
    """Ruleaza EA-ul ExportM1History in Strategy Tester pentru un simbol."""
    ini = os.path.join(DIR, f"_m1exp_{sym}_{name}.ini")
    with open(ini, "w") as f:
        f.write(
            f"""[Tester]
Expert=Advisors\\ExportM1History_EA.ex5
Symbol={sym}
Period=M1
Model=0
Optimization=0
Visual=0
ShutdownTerminal=1
FromDate={frm}
ToDate={to}
ForwardMode=0
Deposit=10000
Currency=USD
ProfitInPips=0
Leverage=100
ExecutionMode=0
OptimizationCriterion=5

[TesterInputs]
"""
        )

    kill()
    t0 = time.time()
    proc = subprocess.Popen(
        [TERMINAL, "/config:" + ini],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        proc.wait(timeout=180)
    except subprocess.TimeoutExpired:
        print(f"    {name}: timeout -> opresc procesul")
        proc.kill()
        kill()
    return time.time() - t0


def process_pair(sym):
    """Ruleaza ambele treceri pentru un simbol, combina si salveaza."""
    print(f"\n{'=' * 50}")
    print(f"  {sym}")
    print(f"{'=' * 50}")

    # Sterge exporturile vechi ale acestui simbol
    for old in glob.glob(os.path.join(COMMON, f"{sym}_M1_*csv")):
        try:
            os.remove(old)
        except Exception:
            pass

    # Ruleaza trecerile
    for pname, frm, to in PASSES:
        elapsed = run_export(sym, pname, frm, to)
        print(f"  {pname}: {elapsed:.0f}s")

    # Colecteaza fisierele exportate
    files = sorted(glob.glob(os.path.join(COMMON, f"{sym}_M1_*csv")))
    if not files:
        print(f"  [FAIL] Nu am gasit niciun fisier exportat pentru {sym}")
        print(f"         (caut in: {COMMON})")
        return None

    frames = []
    for fp in files:
        df = pd.read_csv(fp, encoding="utf-16")
        print(f"    {os.path.basename(fp)}: {len(df):,} rows, "
              f"{df['Datetime'].iloc[0]} -> {df['Datetime'].iloc[-1]}")
        frames.append(df)

    full = (
        pd.concat(frames)
        .drop_duplicates(subset="Datetime")
        .sort_values("Datetime")
        .reset_index(drop=True)
    )

    # Formateaza data (puncte -> liniute) + coloanele lipsa
    full["Datetime"] = full["Datetime"].str.replace(".", "-", regex=False)
    full["Spread"] = 0
    full["RealVolume"] = 0
    full = full[["Datetime", "Open", "High", "Low", "Close", "Volume", "Spread", "RealVolume"]]

    path = os.path.join(OUT, f"{sym}_M1_full.csv")
    full.to_csv(path, index=False)
    sz = os.path.getsize(path) / (1024 * 1024)

    print(f"  [OK] {len(full):,} bare -> {os.path.basename(path)} ({sz:.1f} MB)")
    print(f"  Range: {full['Datetime'].iloc[0]} -> {full['Datetime'].iloc[-1]}")
    return len(full)


if __name__ == "__main__":
    print("=" * 60)
    print("DOWNLOAD M1 — 7 PERECHI (Period=M1)")
    print(f"Perechi: {', '.join(PAIRS)}")
    print("=" * 60)

    total_start = time.time()
    results = {}

    for sym in PAIRS:
        results[sym] = process_pair(sym)

    kill()
    total = time.time() - total_start

    print(f"\n{'=' * 60}")
    print(f"REZUMAT ({total / 60:.1f} min total)")
    print(f"{'=' * 60}")
    for sym, n in results.items():
        status = f"{n:,} bare" if n else "FAILED"
        print(f"  {sym:<8} {status}")
    print(f"\nFisiere in: {OUT}/")
