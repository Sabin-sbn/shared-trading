#!/usr/bin/env python3
"""Analiza marker-elor desenate de Stefan pe gbpusd_draw.html.

Input:
  - _charts/gbpusd_pro_m15_2026-05_07.csv   (datele chart-ului)
  - JSON exportat din unealta (time/ts, price, dir, note)

Output:
  - _charts/marker_analysis.csv  (un rand per marker: features + outcome)
  - raport pe stdout

Features per marker (la bara semnalului, FARA lookahead):
  - candle: body pips, bull/bear, No-Wick match (O==L pt BUY / O==H pt SELL, tol 0.5p)
  - sesiune UTC (bucket), zi a saptamanii
  - distanta la swing low/high 50 bare
  - break-uri de structura in ultimele 50 bare (numar de BOS/CHoCH aproximat pe pivot)
  - trend estimat (close > EMA? panta EMA 20)
Outcome (pentru feedback, NU pentru validare — desenele sunt deja outcome-visible):
  - MFE/MAE maxim in urmatoarele 48 bare M15 (~12h) in pips fata de entry
  - daca ar fi atins TP=SL=~6.5p (RR 1) in 48 bare: win/loss/ambiguous/pending
Nota: kappa/test-retest se fac separat (Partea B blind), nu pe aceste desene.
"""
import csv, json, os, sys, argparse
from datetime import datetime, timezone

HERE = os.path.dirname(os.path.abspath(__file__))
CSV = os.path.join(HERE, "gbpusd_pro_m15_2026-05_07.csv")
PIP = 0.0001  # GBPUSD 5 digits

def load_bars(path):
    bars = []
    with open(path, newline="") as f:
        for r in csv.DictReader(f):
            bars.append([int(r["time"]), float(r["open"]), float(r["high"]),
                         float(r["low"]), float(r["close"]), int(r["tick_volume"])])
    return bars

def bar_index(bars, ts):
    lo, hi = 0, len(bars) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if bars[mid][0] == ts: return mid
        if bars[mid][0] < ts: lo = mid + 1
        else: hi = mid - 1
    return None

def swing_extreme(bars, i, back, which):
    """which: 'high'/'low' — extremul in ultimele `back` bare (exclusiv i)."""
    lo = max(0, i - back)
    if which == "high":
        return max(b[2] for b in bars[lo:i]) if i > lo else None
    return min(b[3] for b in bars[lo:i]) if i > lo else None

def structure_breaks(bars, i, back=50):
    """Aproximare BOS/CHoCH: de cate ori close a depasit high-ul (sus) sau a
    cazut sub low-ul (jos) pivotului din ultimele 20 bare, in ultimele `back` bare."""
    up = dn = 0
    for k in range(max(1, i - back), i):
        hi20 = max(b[2] for b in bars[max(0, k-20):k])
        lo20 = min(b[3] for b in bars[max(0, k-20):k])
        if bars[k][4] > hi20: up += 1
        if bars[k][4] < lo20: dn += 1
    return up, dn

def ema(series, n):
    if len(series) < n:
        return None
    k = 2.0 / (n + 1)
    e = series[0]
    for v in series[1:]:
        e = v * k + e * (1 - k)
    return e

def features(bars, idx, dir_str, nw_tol):
    _, o, h, l, c, _ = bars[idx]
    body = abs(c - o) / PIP
    is_bull = c > o
    # No-Wick cu DIRECTIE (fix Verifier 6b): BUY cere lumanare bull cu open==low,
    # SELL cere lumanare bear cu open==high; toleranta = tolerancea strategiei (default 8p)
    nw_match = (is_bull and o - l <= nw_tol) if dir_str == "BUY" else ((not is_bull) and h - o <= nw_tol)
    dt = datetime.fromtimestamp(bars[idx][0], tz=timezone.utc)
    mins = dt.hour * 60 + dt.minute
    # Bucket numit UTC + sesiune frozen (OBIECTIVIZARE: 09-17 UTC, fara NY open+30min, fara 14:30-16:30)
    if mins < 540:      bucket_name = "Pre-London"
    elif mins < 720:    bucket_name = "London"        # 09:00-11:59
    elif mins < 750:    bucket_name = "NY-open+30min"  # interzis
    elif mins < 870:    bucket_name = "NY"             # 12:30-14:29
    elif mins < 990:    bucket_name = "US-news"        # interzis
    else:               bucket_name = "Late"
    session_v2_ok = (540 <= mins <= 1020) and not (720 <= mins < 750) and not (870 <= mins < 990)
    lo50 = swing_extreme(bars, idx, 50, "low")
    hi50 = swing_extreme(bars, idx, 50, "high")
    up, dn = structure_breaks(bars, idx)
    # trend fara lookahead: EMA20 pe inchiderile INAINTE de bara semnalului
    closes = [b[4] for b in bars[max(0, idx-120):idx]]
    ema20 = ema(closes, 20)
    prev_close = bars[idx-1][4] if idx > 0 else c
    trend = 1 if (ema20 is not None and prev_close > ema20) else (-1 if (ema20 is not None and prev_close < ema20) else 0)
    return {"bar_ts": bars[idx][0], "bar_time": dt.strftime("%Y-%m-%d %H:%M"),
            "candle": "BULL" if is_bull else "BEAR", "body_pips": round(body, 1),
            "nw_match": nw_match, "dow": dt.strftime("%A"), "bucket_utc": bucket_name,
            "session_v2_ok": session_v2_ok,
            "dist_low50_pips": round((c - lo50) / PIP, 1) if lo50 else None,
            "dist_high50_pips": round((hi50 - c) / PIP, 1) if hi50 else None,
            "brk_up": up, "brk_dn": dn, "trend_ema": trend}

def outcome(bars, idx, price, dir_str, sl_pips=6.5, tp_pips=None, hours=12):
    """MFE/MAE pe urmatoarele `hours` ore M15; win/loss/ambiguous cu SL/TP per marker."""
    if tp_pips is None:
        tp_pips = sl_pips
    n = int(hours * 4)  # 15 min = 4 bare/ora
    end = min(len(bars), idx + 1 + n)
    mfe = mae = 0.0
    hit_tp = hit_sl = False
    tp_p = price + dir_str * tp_pips * PIP
    sl_p = price - dir_str * sl_pips * PIP
    res = "pending"
    for k in range(idx + 1, end):
        hi, lo = bars[k][2], bars[k][3]
        if dir_str == 1:  # BUY
            mfe = max(mfe, hi - price)
            mae = max(mae, price - lo)
            if hi >= tp_p: hit_tp = True
            if lo <= sl_p: hit_sl = True
        else:
            mfe = max(mfe, price - lo)
            mae = max(mae, hi - price)
            if lo <= tp_p: hit_tp = True
            if hi >= sl_p: hit_sl = True
        if hit_tp and hit_sl:
            res = "ambiguous"; break   # ambele niveluri in aceeasi bara — ordine necunoscuta
        if hit_tp:
            res = "win"
        elif hit_sl:
            res = "loss"
    return {"mfe_pips": round(mfe / PIP, 1), "mae_pips": round(mae / PIP, 1),
            "result_rr1": res}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("json", nargs="?", help="JSON exportat din unealta")
    ap.add_argument("--data", default=CSV)
    ap.add_argument("--out", default=os.path.join(HERE, "marker_analysis.csv"))
    ap.add_argument("--nw-tol", type=float, default=8.0, help="toleranta No-Wick in pips (strategie GBPUSD ~8-12p)")
    a = ap.parse_args()
    if not a.json:
        print("Usage: python analyze_markers.py markers.json")
        sys.exit(1)
    bars = load_bars(a.data)
    obj = json.load(open(a.json, encoding="utf-8"))
    markers = obj["markers"] if (isinstance(obj, dict) and "markers" in obj) else (obj if isinstance(obj, list) else [])
    tol = a.nw_tol * PIP
    rows = []
    for m in markers:
        ts = m.get("ts") or int(datetime.strptime(m["time"], "%Y-%m-%d %H:%M").replace(tzinfo=timezone.utc).timestamp())
        idx = bar_index(bars, ts)
        if idx is None:
            print(f"!! marker fara bara: {m}"); continue
        d = 1 if m["dir"] in ("BUY","LONG") else -1
        f = features(bars, idx, "BUY" if m["dir"] in ("BUY","LONG") else "SELL", tol)
        o = outcome(bars, idx, m["price"], d, sl_pips=m.get("sl") or 6.5, tp_pips=m.get("tp") or 6.5)
        rows.append({**m, **f, **o})
    if not rows:
        print("Niciun marker procesat (JSON gol sau timpuri fara bara).")
        return
    with open(a.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    n = len(rows)
    buy = sum(1 for r in rows if r["dir"] in ("BUY","LONG"))
    nw = sum(1 for r in rows if r["nw_match"])
    win = sum(1 for r in rows if r["result_rr1"] == "win")
    loss = sum(1 for r in rows if r["result_rr1"] == "loss")
    amb = sum(1 for r in rows if r["result_rr1"] == "ambiguous")
    pend = sum(1 for r in rows if r["result_rr1"] == "pending")
    s2 = sum(1 for r in rows if r["session_v2_ok"])
    avg_body = sum(r["body_pips"] for r in rows) / n if n else 0
    print(f"Markere: {n} | BUY {buy} / SELL {n-buy}")
    print(f"No-Wick match (tol {a.nw_tol}p, cu directie): {nw}/{n} ({100*nw/n:.0f}%)")
    print(f"Sesiune v2 OK (09-17 fara US): {s2}/{n} ({100*s2/n:.0f}%)")
    print(f"Body mediu: {avg_body:.1f}p | Outcome RR1 (12h): win {win} / loss {loss} / ambiguous {amb} / pending {pend}")
    print(f"Salvat: {a.out}")

if __name__ == "__main__":
    main()
