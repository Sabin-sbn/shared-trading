"""
convert_oanda_to_csv.py — Conversie date OANDA API JSON → CSV format standard.

Rulare:
    python convert_oanda_to_csv.py

Asteapta fisiere JSON descarcate de download_oanda_shares.py
si le converteste in CSV-uri gata de folosit in oanda_shares_reviewer.html.
"""
import os
import json
import csv
import glob

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_DIR = os.path.join(HERE, "json_data")
CSV_DIR = os.path.join(HERE, "csv_data")


def convert_json_to_csv(json_path, csv_path):
    """Convertește un fișier JSON OANDA în CSV."""
    with open(json_path, "r") as f:
        data = json.load(f)

    candles = data.get("candles", [])
    if not candles:
        return 0

    rows = []
    for c in candles:
        time_str = c["time"]
        vol = c.get("volume", 0)
        complete = c.get("complete", False)

        # Folosim midpoint (media bid/ask) sau mid direct
        if "mid" in c:
            p = c["mid"]
        elif "bid" in c and "ask" in c:
            bid, ask = c["bid"], c["ask"]
            p = {
                "o": str((float(bid["o"]) + float(ask["o"])) / 2),
                "h": str((float(bid["h"]) + float(ask["h"])) / 2),
                "l": str((float(bid["l"]) + float(ask["l"])) / 2),
                "c": str((float(bid["c"]) + float(ask["c"])) / 2),
            }
        elif "bid" in c:
            p = c["bid"]
        elif "ask" in c:
            p = c["ask"]
        else:
            continue

        rows.append({
            "Datetime": time_str.replace("T", " ").replace("Z", ""),
            "Open": float(p["o"]),
            "High": float(p["h"]),
            "Low": float(p["l"]),
            "Close": float(p["c"]),
            "Volume": vol,
            "Complete": complete,
        })

    if not rows:
        return 0

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Datetime", "Open", "High", "Low", "Close", "Volume", "Complete"])
        writer.writeheader()
        writer.writerows(rows)

    return len(rows)


if __name__ == "__main__":
    json_files = sorted(glob.glob(os.path.join(JSON_DIR, "*.json")))
    if not json_files:
        print(f"Nu am gasit fisiere JSON in {JSON_DIR}/")
        print("Rulează întâi download_oanda_shares.py pentru a descarca datele.")
        exit(1)

    os.makedirs(CSV_DIR, exist_ok=True)
    total = 0
    for jf in json_files:
        base = os.path.basename(jf).replace(".json", "")
        csv_path = os.path.join(CSV_DIR, f"{base}.csv")
        n = convert_json_to_csv(jf, csv_path)
        if n:
            print(f"  {base}: {n:,} candles -> {os.path.basename(csv_path)}")
            total += n
        else:
            print(f"  {base}: gol")

    print(f"\nTotal: {total:,} candles în {CSV_DIR}/")
