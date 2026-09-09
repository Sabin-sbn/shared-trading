"""
download_oanda_shares.py — Download share CFD data from OANDA REST API v20.

Rulare:
    python download_oanda_shares.py

Cerinte:
    - Cont OANDA (demo sau live) cu API token
    - Python 3 + requests (pip install requests)

Configurare:
    - Seteaza OANDA_TOKEN mai jos (sau ca variabila de mediu)
    - Alege perechile dorite din SHARE_CFDs
    - Alege timeframe-ul (granularity) si perioada
"""
import os
import sys
import json
import time
import requests
from datetime import datetime, timedelta

# ============ CONFIGURARE ============
# Token API OANDA — il gasesti in: OANDA Portal → Manage API Access → Generate Token
# Sau seteaza variabila de mediu: OANDA_TOKEN
OANDA_TOKEN = os.environ.get("OANDA_TOKEN", "ASTEAPTA_API_KEY_AICI")

# Cont OANDA (demo sau live)
# Practice: https://api-fxpractice.oanda.com
# Live:     https://api-fxtrade.oanda.com
OANDA_BASE = "https://api-fxpractice.oanda.com"

# Perechi share CFDs disponibile pe OANDA (format: SYMBOL_CFD.US)
# Lista extinsa — poti comenta/decomenta ce vrei
SHARE_CFDs = [
    # Tech
    "AAPL_CFD.US",   # Apple
    "MSFT_CFD.US",   # Microsoft
    "GOOGL_CFD.US",  # Alphabet (Google)
    "AMZN_CFD.US",   # Amazon
    "NVDA_CFD.US",   # NVIDIA
    "META_CFD.US",   # Meta (Facebook)
    "TSLA_CFD.US",   # Tesla
    "NFLX_CFD.US",   # Netflix
    "AMD_CFD.US",    # AMD
    "INTC_CFD.US",   # Intel
    # Finance
    "JPM_CFD.US",    # JPMorgan
    "V_CFD.US",      # Visa
    "MA_CFD.US",     # Mastercard
    "BAC_CFD.US",    # Bank of America
    "GS_CFD.US",     # Goldman Sachs
    # Healthcare
    "JNJ_CFD.US",    # Johnson & Johnson
    "UNH_CFD.US",    # UnitedHealth
    "PFE_CFD.US",    # Pfizer
    # Energy
    "XOM_CFD.US",    # ExxonMobil
    "CVX_CFD.US",    # Chevron
    # Retail
    "WMT_CFD.US",    # Walmart
    "COST_CFD.US",   # Costco
    "NKE_CFD.US",    # Nike
    # Other
    "DIS_CFD.US",    # Disney
    "BA_CFD.US",     # Boeing
    "CRM_CFD.US",    # Salesforce
    "ADBE_CFD.US",   # Adobe
    "PYPL_CFD.US",   # PayPal
    "SQ_CFD.US",     # Block (Square)
    "UBER_CFD.US",   # Uber
]

# Timeframe: S5, S10, S15, S30, M1, M2, M4, M5, M10, M15, M30, H1, H2, H3, H4, H6, H8, H12, D, W, M
GRANULARITY = "M15"  # 15-minute candles

# Perioada de descarcat (max 5000 candles per request)
# Pentru M15: 5000 candles = ~52 zile
FROM_DATE = "2026-01-01T00:00:00Z"
TO_DATE = "2026-09-01T00:00:00Z"

# Output folder
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "csv_data")

# ============ ENDPOINT ============
CANDLES_URL = f"{OANDA_BASE}/v3/instruments/{{instrument}}/candles"

# ============ FUNCTII ============

def fetch_candles(instrument, from_dt, to_dt, granularity="M15", price="MBA"):
    """
    Descarca candlesticks de la OANDA API.
    price: "M" (midpoint), "B" (bid), "A" (ask), "BA" (bid+ask), "MBA" (all)
    """
    params = {
        "from": from_dt,
        "to": to_dt,
        "granularity": granularity,
        "price": price,
        "includeFirst": "true",
    }
    headers = {
        "Authorization": f"Bearer {OANDA_TOKEN}",
        "Accept-Datetime-Format": "RFC3339",
    }
    url = CANDLES_URL.format(instrument=instrument)
    resp = requests.get(url, headers=headers, params=params, timeout=30)
    resp.raise_for_status()
    return resp.json()


def parse_candles(data, price="MBA"):
    """
    Parseaza raspunsul OANDA intr-o lista de dict-uri plan.
    """
    rows = []
    for c in data.get("candles", []):
        time_str = c["time"]
        complete = c.get("complete", False)
        vol = c.get("volume", 0)

        # Alege componenta de pret
        if price == "M" and "mid" in c:
            p = c["mid"]
        elif price == "B" and "bid" in c:
            p = c["bid"]
        elif price == "A" and "ask" in c:
            p = c["ask"]
        elif "bid" in c and "ask" in c:
            # Media bid/ask pentru midpoint
            bid = c["bid"]
            ask = c["ask"]
            p = {
                "o": str((float(bid["o"]) + float(ask["o"])) / 2),
                "h": str((float(bid["h"]) + float(ask["h"])) / 2),
                "l": str((float(bid["l"]) + float(ask["l"])) / 2),
                "c": str((float(bid["c"]) + float(ask["c"])) / 2),
            }
        elif "mid" in c:
            p = c["mid"]
        elif "bid" in c:
            p = c["bid"]
        elif "ask" in c:
            p = c["ask"]
        else:
            continue

        rows.append({
            "Datetime": time_str,
            "Open": float(p["o"]),
            "High": float(p["h"]),
            "Low": float(p["l"]),
            "Close": float(p["c"]),
            "Volume": vol,
            "Complete": complete,
        })
    return rows


def save_csv(rows, filepath):
    """Salveaza datele in CSV."""
    import csv
    with open(filepath, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["Datetime", "Open", "High", "Low", "Close", "Volume", "Complete"])
        writer.writeheader()
        writer.writerows(rows)


def download_pair(instrument, from_dt, to_dt, granularity, out_dir):
    """
    Descarca toate datele pentru un instrument, imparte in chunk-uri de 5000.
    """
    print(f"\n{'='*50}")
    print(f"  {instrument}")
    print(f"{'='*50}")

    all_rows = []
    current_from = from_dt

    while current_from < to_dt:
        try:
            data = fetch_candles(instrument, current_from, to_dt, granularity)
        except requests.exceptions.HTTPError as e:
            print(f"  [ERROR] {e}")
            if e.response.status_code == 401:
                print("  -> Verifica OANDA_TOKEN!")
            break
        except Exception as e:
            print(f"  [ERROR] {e}")
            break

        candles = data.get("candles", [])
        if not candles:
            break

        rows = parse_candles(data)
        all_rows.extend(rows)
        print(f"  +{len(rows)} candles (total: {len(all_rows)})")

        # Avanseaza: ultimul timp + 1 granularitate
        last_time = candles[-1]["time"]
        # Parse RFC3339
        if "T" in last_time:
            dt = datetime.fromisoformat(last_time.replace("Z", "+00:00"))
        else:
            dt = datetime.fromisoformat(last_time)

        # Adauga o granularitate
        gap_map = {
            "M1": timedelta(minutes=1), "M5": timedelta(minutes=5),
            "M15": timedelta(minutes=15), "M30": timedelta(minutes=30),
            "H1": timedelta(hours=1), "H4": timedelta(hours=4),
            "D": timedelta(days=1), "W": timedelta(weeks=1),
        }
        gap = gap_map.get(granularity, timedelta(minutes=15))
        current_from = (dt + gap).isoformat().replace("+00:00", "Z")

        if len(candles) < 5000:
            break  # Am ajuns la final

        time.sleep(0.5)  # Rate limit politeness

    if not all_rows:
        print(f"  [FAIL] Nu am gasit date pentru {instrument}")
        return 0

    # Salveaza CSV
    safe_name = instrument.replace(".", "_").replace("/", "_")
    csv_path = os.path.join(out_dir, f"{safe_name}_{granularity}.csv")
    save_csv(all_rows, csv_path)
    sz = os.path.getsize(csv_path) / 1024
    print(f"  [OK] {len(all_rows):,} candles -> {os.path.basename(csv_path)} ({sz:.1f} KB)")
    print(f"  Range: {all_rows[0]['Datetime']} -> {all_rows[-1]['Datetime']}")
    return len(all_rows)


# ============ MAIN ============

if __name__ == "__main__":
    print("=" * 60)
    print("OANDA SHARE CFDs DOWNLOADER")
    print(f"Granularity: {GRANULARITY}")
    print(f"Period: {FROM_DATE} -> {TO_DATE}")
    print(f"Pairs: {len(SHARE_CFDs)}")
    print(f"Output: {OUT_DIR}/")
    print("=" * 60)

    if "ASTEAPTA_API_KEY_AICI" in OANDA_TOKEN:
        print("\n[ERRORE] Nu ai setat OANDA_TOKEN!")
        print("Seteaza variabila de mediu sau editeaza OANDA_TOKEN in script.")
        print("Cum obtii token:")
        print("  1. Login pe https://www.oanda.com/")
        print("  2. My Services → Manage API Access → Generate Token")
        sys.exit(1)

    os.makedirs(OUT_DIR, exist_ok=True)

    total_start = time.time()
    results = {}

    for sym in SHARE_CFDs:
        results[sym] = download_pair(sym, FROM_DATE, TO_DATE, GRANULARITY, OUT_DIR)

    total = time.time() - total_start

    print(f"\n{'='*60}")
    print(f"REZUMAT ({total/60:.1f} min total)")
    print(f"{'='*60}")
    ok = 0
    fail = 0
    for sym, n in results.items():
        if n > 0:
            status = f"{n:,} candles"
            ok += 1
        else:
            status = "FAILED"
            fail += 1
        print(f"  {sym:<18} {status}")
    print(f"\n  OK: {ok}  |  FAILED: {fail}  |  Total: {len(SHARE_CFDs)}")
    print(f"  Fisiere in: {OUT_DIR}/")
