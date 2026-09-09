"""
build_gbpusd_data.py — Convertește GBPUSD_M1_2024_2026.csv (din shared-trading/Data/Forex_M1_2Y)
în fișier JS compact pentru oanda_shares_reviewer.html.

Output: gbpusd_m1_2024_2026.js  →  window.GBPUSD_M1_2024_2026 = [[ts,o,h,l,c,v], ...]
"""
import os
import csv
import json

HERE = os.path.dirname(os.path.abspath(__file__))

# Sursa: CSV-ul din shared-trading (Data/Forex_M1_2Y)
SRC = os.path.join(HERE, "..", "Forex_M1_2Y", "GBPUSD_M1_2024_2026.csv")
SRC = os.path.normpath(SRC)

# Output: fișier JS langă HTML
OUT = os.path.join(HERE, "gbpusd_m1_2024_2026.js")

def main():
    if not os.path.exists(SRC):
        print(f"[ERROR] Nu exista: {SRC}")
        print("Cauta manual fisierul GBPUSD_M1_2024_2026.csv in shared-trading/Data/Forex_M1_2Y/")
        return 1

    # datele: doar timp(epoch) + OHLC + volum (in formatul gbpusd_ohlc.js)
    rows = []
    with open(SRC, newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            try:
                import datetime
                dt = datetime.datetime.strptime(r["Datetime"], "%Y-%m-%d %H:%M:%S")
                ts = int(dt.replace(tzinfo=datetime.timezone.utc).timestamp())
            except Exception:
                continue
            rows.append([
                ts,
                float(r["Open"]),
                float(r["High"]),
                float(r["Low"]),
                float(r["Close"]),
                int(r["Volume"]),
            ])

    print(f"Bare: {len(rows):,}  |  {rows[0][0]} -> {rows[-1][0]}")

    # Scrie ca JS compact (o singura linie, ca gbpusd_ohlc.js)
    with open(OUT, "w", encoding="utf-8") as f:
        f.write("window.GBPUSD_M1_2024_2026=")
        f.write(json.dumps(rows, separators=(",", ":")))
        f.write(";\n")

    sz = os.path.getsize(OUT) / (1024 * 1024)
    print(f"[OK] {OUT}")
    print(f"     Dimensiune: {sz:.1f} MB")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())