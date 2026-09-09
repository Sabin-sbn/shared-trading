"""
seed_profile.py
===============
Genereaza seed_profile.json — profilul default pentru gbpusd_full.html:
  - markers:  trade-urile tale reale GBP/USD din Jurnal_Trading.csv (ghost:false),
              cu W/L + tip de intrare (re-liquidation / fvg / mss / liquidity).
  - drawings: structura detectata cu structure_detector.py IN JURUL fiecarui
              trade — MSS/BOS (M1), FVG + Liquidity + OrderBlock (M15) —
              ca sa vezi exact ce era pe chart la fiecare intrare (ca in poze).

Format dates:
  M15/M1: time = epoch sec UTC.   Coloane: time,open,high,low,close,tick_volume.

Iesire: seed_profile.json -> este ingropat de build_chart_html.py in
        window.GBPUSD_DEFAULT_PROFILE la build.
"""
import os
import re
import json
import datetime as dt
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
JOURNAL = r"C:\Users\dragh\OneDrive\Documente\Second Brain\2_Wiki\Trading\Jurnal\Jurnal_Trading.csv"
M15_CSV = os.path.join(HERE, "gbpusd_pro_m15_2025_09_2026_02.csv")
M1_CSV = os.path.join(HERE, "gbpusd_pro_m1_2025_09_2026_02.csv")
OUT = os.path.join(HERE, "seed_profile.json")

from structure_detector import (detect_bos_mss, detect_fvg,
                                detect_liquidity_sweeps, detect_order_blocks)

SWING = 7
MSS_WINDOW_BEFORE_MIN = 120   # pentru MSS pe M1: -120min .. +60min in jurul intrarii
MSS_WINDOW_AFTER_MIN = 60
DISPLAY_M15_BEFORE = 12       # bare M15 afisate inainte de intrare (~ -3h)
DISPLAY_M15_AFTER = 20        # bare M15 afisate dupa intrare (~ +5h)
DETECT_M15_PAD = 40           # margine M15 pentru pivots (left/right swing)

# Culori pentru drawings (extensia d.color din drawDrawing)
C_MSS_BULL = "#26a69a"
C_MSS_BEAR = "#ef5350"
C_FVG_BULL = "#2962ff"
C_FVG_BEAR = "#ff9800"
C_LIQ = "#f1c40f"
C_OB_BULL = "#00e5ff"
C_OB_BEAR = "#e91e63"


# ----------------------------------------------------------------------------
# Util
# ----------------------------------------------------------------------------
def load_epoch_csv(path):
    df = pd.read_csv(path)
    return df, df["time"].tolist()  # list of epoch sec (UTC)


def find_floor(times, t):
    """Cel mai mare index i cu times[i] <= t (timpi crescaatori). -1 daca t<times[0]."""
    lo, hi = 0, len(times) - 1
    ans = -1
    while lo <= hi:
        mid = (lo + hi) // 2
        if times[mid] <= t:
            ans = mid
            lo = mid + 1
        else:
            hi = mid - 1
    return ans


def parse_open_date(val):
    """'17/11/2025 12:48 (GMT+2)' -> epoch UTC."""
    if not isinstance(val, str):
        return None
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})\s+(\d{1,2}):(\d{2})\s*\(GMT\+(\d+)\)", val)
    if not m:
        return None
    d, mo, y, h, mi, off = m.groups()
    try:
        local = dt.datetime(int(y), int(mo), int(d), int(h), int(mi))
    except ValueError:
        return None
    utc = local - dt.timedelta(hours=int(off))
    return int(utc.replace(tzinfo=dt.timezone.utc).timestamp())


def slice_df(df, start_idx, end_idx, colmap=None):
    sub = df.iloc[start_idx:end_idx].reset_index(drop=True)
    return sub


def ohlc_upper(df):
    """Renumeste coloanele la Open/High/Low/Close (as ezteptate de detectori),
    PASTRAND 'time' numeric (epoch int) — ca mapperile find_floor sa ramana corecte."""
    df = df.copy()
    return df.rename(columns={"open": "Open", "high": "High",
                              "low": "Low", "close": "Close"})


def dur_fmt(t):
    return dt.datetime.fromtimestamp(t, tz=dt.timezone.utc).strftime("%d.%m %H:%M")


# ----------------------------------------------------------------------------
# Detectori + conversie la drawings
# ----------------------------------------------------------------------------
def mss_drawings_m1(m1df, m15times, entry_epoch):
    """MSS/BOS pe M1 in jurul intrarii -> linii orizontale scurte pe bare M15."""
    t0 = entry_epoch - MSS_WINDOW_BEFORE_MIN * 60
    t1 = entry_epoch + MSS_WINDOW_AFTER_MIN * 60
    s0 = find_floor(m1df["time"].tolist(), t0)
    s1 = find_floor(m1df["time"].tolist(), t1)
    if s0 < 0 or s1 <= s0:
        return []
    sub = m1df.iloc[s0:s1 + 1].reset_index(drop=True)
    sub = ohlc_upper(sub)
    try:
        evs = detect_bos_mss(sub, swing_length=SWING)
    except Exception:
        return []
    out = []
    seen = set()
    for e in evs:
        bar15 = find_floor(m15times, e.time)
        if bar15 < 0:
            continue
        # dedup: la aceeasi zona (5 bare M15) pastram un singur MSS
        rng = (bar15 // 5) * 5
        if rng in seen:
            continue
        seen.add(rng)
        color = C_MSS_BULL if e.direction == "bullish" else C_MSS_BEAR
        lab = "MSS ↑" if e.direction == "bullish" else "MSS ↓"
        out.append({
            "id": 0, "type": "line",
            "pts": [{"bar": bar15, "price": e.price},
                    {"bar": min(bar15 + 4, len(m15times) - 1), "price": e.price}],
            "color": color, "text": lab,
            "tag": "s",
        })
    return out


def fvg_drawings_m15(m15df, m15times, inbar):
    lo = max(0, inbar - DISPLAY_M15_BEFORE)
    hi = min(len(m15df), inbar + DISPLAY_M15_AFTER + 1)
    sub = m15df.iloc[lo:hi].reset_index(drop=True)
    sub = ohlc_upper(sub)
    try:
        evs = detect_fvg(sub)
    except Exception:
        return []
    out = []
    for e in evs:
        b = lo + e.bar_index
        color = C_FVG_BULL if e.direction == "bullish" else C_FVG_BEAR
        out.append({
            "id": 0, "type": "rect",
            "pts": [{"bar": b, "price": e.bottom},
                    {"bar": min(b + 6, len(m15times) - 1), "price": e.top}],
            "color": color,
            "text": ("FVG bull" if e.direction == "bullish" else "FVG bear"),
            "tag": "z",
        })
    return out


def liq_drawings_m15(m15df, m15times, inbar):
    lo = max(0, inbar - DISPLAY_M15_BEFORE - 6)
    hi = min(len(m15df), inbar + DISPLAY_M15_AFTER + 6)
    sub = m15df.iloc[lo:hi].reset_index(drop=True)
    sub = ohlc_upper(sub)
    try:
        evs = detect_liquidity_sweeps(sub, swing_length=SWING)
    except Exception:
        return []
    out = []
    for e in evs:
        if e.sweep_type != "body_close":
            continue
        out.append({
            "id": 0, "type": "hline",
            "pts": [{"bar": lo + e.bar_index, "price": e.level}],
            "color": C_LIQ,
            "text": ("LIQ swept↑" if e.direction == "buyside_swept" else "LIQ swept↓"),
            "tag": "h",
        })
    return out


def ob_drawings_m15(m15df, m15times, inbar):
    lo = max(0, inbar - DISPLAY_M15_BEFORE)
    hi = min(len(m15df), inbar + DISPLAY_M15_AFTER + 1)
    sub = m15df.iloc[lo:hi].reset_index(drop=True)
    sub = ohlc_upper(sub)
    try:
        evs = detect_order_blocks(sub, periods=5)
    except Exception:
        return []
    out = []
    for e in evs:
        b = lo + e.bar_index
        color = C_OB_BULL if e.direction == "bullish" else C_OB_BEAR
        out.append({
            "id": 0, "type": "rect",
            "pts": [{"bar": b, "price": e.low},
                    {"bar": min(b + 4, len(m15times) - 1), "price": e.high}],
            "color": color,
            "text": ("OB bull" if e.direction == "bullish" else "OB bear"),
            "tag": "z",
        })
    return out


# ----------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------
def main():
    m15df, m15times = load_epoch_csv(M15_CSV)
    m1df, m1times = load_epoch_csv(M1_CSV)

    j = pd.read_csv(JOURNAL, dtype=str)
    j["Pair"] = j["Pair"].str.strip().str.upper()

    markers = []
    drawings = []
    mid = 0
    dr = 0

    for _, r in j[j["Pair"] == "GBP/USD"].iterrows():
        entry_epoch = parse_open_date(str(r["Open Date"]))
        if entry_epoch is None:
            continue
        inbar = find_floor(m15times, entry_epoch)
        if inbar < 0:
            continue

        # --- marker trade real ---
        try:
            nr = int(str(r["Nr. trade"]).strip())
        except ValueError:
            nr = 0
        pos = str(r["Position"]).strip().upper()
        dire = "LONG" if (pos.startswith("LO") or pos == "LONG") else (
            "SHORT" if (pos.startswith("S") or pos == "SHORT") else None)
        if dire is None:
            continue
        win = str(r["Win"]).strip().lower()
        rr = str(r["Realized R"]).strip()
        entry_price = float(m15df.iloc[inbar]["close"])

        types = []
        for k in ("Setup", "Setups", "Liquidity"):
            v = str(r[k]).strip().lower() if isinstance(r[k], str) else ""
            if "reliquid" in v or "re-liquidation" in v:
                types.append("re-liq")
            if "fvg" in v:
                types.append("fvg")
            if "mss" in v:
                types.append("mss")
            if "liq" in v and "re-l" not in v:
                types.append("liq")
        # dedupe, pastrez ordinea
        seen = set()
        types = [x for x in types if not (x in seen or seen.add(x))]
        tystr = "+".join(types) if types else "setup"

        winlab = {"win": "WIN", "loss": "LOSS"}.get(win, "?")
        notetxt = "#%s · %s · R%s · %s · %s" % (
            nr, winlab, rr if rr and rr.lower() != "nan" else "-", tystr,
            dur_fmt(entry_epoch))
        mid += 1
        markers.append({
            "id": mid, "bar": inbar, "price": entry_price, "dir": dire,
            "ghost": False, "sl": 6.5, "tp": 6.5,
            "note": notetxt,
            "created": int(entry_epoch * 1000),
            "ts": entry_epoch,
            "tf": "M15",
        })

        # --- drawings structura in jurul trade ---
        for dd in mss_drawings_m1(m1df, m15times, entry_epoch):
            dr += 1
            dd["id"] = dr
            drawings.append(dd)
        for fd in fvg_drawings_m15(m15df, m15times, inbar):
            dr += 1
            fd["id"] = dr
            drawings.append(fd)
        for ld in liq_drawings_m15(m15df, m15times, inbar):
            dr += 1
            ld["id"] = dr
            drawings.append(ld)
        for od in ob_drawings_m15(m15df, m15times, inbar):
            dr += 1
            od["id"] = dr
            drawings.append(od)

    # elimina duplicate de drawings (acelasi type+bar+price)
    uniq = {}
    for d in drawings:
        key = (d["type"], d["pts"][0]["bar"], round(d["pts"][0]["price"], 5))
        if d["type"] == "line":
            key = (d["type"], d["pts"][0]["bar"], None)  # MSS line dedup loose
        uniq.setdefault(key, d)
    drawings = list(uniq.values())
    # re-id
    for i, d in enumerate(drawings):
        d["id"] = i + 1

    prof = {"markers": markers, "drawings": drawings}
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(prof, f, ensure_ascii=False, separators=(",", ":"))
    print("scris:", OUT)
    print("markers (trade-uri reale):", len(markers))
    print("drawings (structura):", len(drawings))
    # statistica tipuri
    from collections import Counter
    c = Counter(d["type"] for d in drawings)
    print("drawings pe tip:", dict(c))
    c2 = Counter(d["dir"] for d in markers)
    print("markers pe directie:", dict(c2))


if __name__ == "__main__":
    main()
