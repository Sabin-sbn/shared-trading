"""
validate_data.py
==================
Rulează O SINGURĂ DATĂ (sau după fiecare export nou de date) ÎNAINTE de a
folosi verifier_app.py. Scanează toate CSV-urile M1 dintr-un folder și
verifică integritatea lor, ca să nu descoperi probleme abia în mijlocul
unei sesiuni de verificare vizuală.

Rulare:
    python validate_data.py --folder history_export

Ce verifică pentru fiecare fișier *_M1_full.csv:
  1. Coloanele obligatorii există (Datetime/Open/High/Low/Close)
  2. Datetime e parsabil și STRICT crescător (sortat)
  3. Nu există duplicate de Datetime
  4. High >= Low, High >= Open/Close, Low <= Open/Close (bare valide)
  5. Găuri mari în serie (weekend-urile sunt normale, dar o gaură de
     >6 ore într-o zi lucrătoare = suspect, de investigat)
  6. Intervalul de date acoperit (prima -> ultima bară)
"""

import argparse
import glob
import os
import pandas as pd


REQUIRED_COLS = {"Datetime", "Open", "High", "Low", "Close"}


def validate_file(path: str) -> dict:
    report = {"file": os.path.basename(path), "ok": True, "issues": []}

    try:
        df = pd.read_csv(path)
    except Exception as e:
        report["ok"] = False
        report["issues"].append(f"Nu pot citi fișierul: {e}")
        return report

    cols_present = set(df.columns)
    missing = REQUIRED_COLS - cols_present
    if missing:
        report["ok"] = False
        report["issues"].append(f"Lipsesc coloane: {missing}")
        return report

    try:
        df["Datetime"] = pd.to_datetime(df["Datetime"], utc=True)
    except Exception as e:
        report["ok"] = False
        report["issues"].append(f"Datetime neparsabil: {e}")
        return report

    n_dupes = df["Datetime"].duplicated().sum()
    if n_dupes > 0:
        report["issues"].append(f"{n_dupes} rânduri cu Datetime duplicat")

    if not df["Datetime"].is_monotonic_increasing:
        report["issues"].append("Datetime NU e sortat crescător (verifică ordinea)")

    bad_bars = df[(df["High"] < df["Low"]) |
                  (df["High"] < df["Open"]) | (df["High"] < df["Close"]) |
                  (df["Low"] > df["Open"]) | (df["Low"] > df["Close"])]
    if len(bad_bars) > 0:
        report["issues"].append(f"{len(bad_bars)} bare invalide (High/Low inconsistent cu Open/Close)")

    diffs = df["Datetime"].sort_values().diff().dt.total_seconds() / 60
    big_gaps = diffs[(diffs > 360) & (diffs < 60 * 24 * 2)]  # >6h dar nu weekend întreg
    if len(big_gaps) > 0:
        report["issues"].append(f"{len(big_gaps)} găuri suspecte (>6h, non-weekend) în serie")

    report["rows"] = len(df)
    report["start"] = str(df["Datetime"].min())
    report["end"] = str(df["Datetime"].max())
    if report["issues"]:
        report["ok"] = False if any("Nu pot" in i or "Lipsesc" in i for i in report["issues"]) else report["ok"]

    return report


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folder", default="history_export")
    ap.add_argument("--pattern", default="*_M1_full.csv")
    args = ap.parse_args()

    files = sorted(glob.glob(os.path.join(args.folder, args.pattern)))
    if not files:
        print(f"Nu am găsit niciun fișier care să se potrivească cu "
              f"'{args.pattern}' în '{args.folder}'.")
        print("Verifică calea sau ajustează --folder / --pattern.")
        return

    print(f"Găsite {len(files)} fișiere în '{args.folder}':\n")
    all_ok = True
    for f in files:
        r = validate_file(f)
        status = "OK  " if r["ok"] and not r.get("issues") else ("ATENȚIE" if r["ok"] else "EROARE")
        all_ok = all_ok and r["ok"]
        print(f"[{status}] {r['file']}")
        if "rows" in r:
            print(f"         {r['rows']:,} bare | {r['start']} -> {r['end']}")
        for issue in r.get("issues", []):
            print(f"         - {issue}")
        print()

    print("=" * 60)
    print("Toate fișierele OK — sigur poți continua la verifier_app.py" if all_ok
          else "ATENȚIE: unele fișiere au probleme — vezi detaliile de mai sus "
               "înainte să le folosești în verificarea vizuală (rezultatele "
               "detectorului pot fi greșite pe date corupte).")


if __name__ == "__main__":
    main()
