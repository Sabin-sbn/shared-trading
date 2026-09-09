"""
structure_detector.py
======================
Traducere fidelă (nu aproximare) a celor două indicatoare Pine Script pe care
le rulezi tu în TradingView, plus FVG standard și un modul de lichiditate
bazat pe research (fără sursă Pine dată — vezi caveat la finalul fișierului).

Surse:
  - MSS/BOS: "Multi Timeframe Break of Structure(BOS) & Market Structure
    Shift(MSS)" by Lenny_Kiruthu — logica Prev_Breakout_Type.
  - Order Block: "Order Block Finder (Experimental)" by wugamlo.

IMPORTANT — ce NU face acest fișier:
  - Nu rulează pe 900k bare eficient (loop-uri Python simple, nu vectorizat).
    E gândit pentru VERIFICARE pe ferestre mici (o fereastră = un trade / un
    interval de câteva sute de bare), nu pentru backtest pe tot istoricul.
    Pentru backtest pe volum, folosește motorul deja existent
    (Research/code/backtest_minimal.py) cu o versiune vectorizată separată.
  - Nu reproduce cei 6 parametri ai indicatorului "Myaccount" (necunoscuți —
    nu avem sursa). Aici ai DOAR ce ai dat tu explicit (Lenny_Kiruthu + wugamlo).
"""

from dataclasses import dataclass, field
import pandas as pd
import numpy as np


# --------------------------------------------------------------------------
# 1. Pivoturi (swing high / swing low) — bază pentru MSS/BOS
# --------------------------------------------------------------------------

def find_pivots(series: pd.Series, left: int, right: int, mode: str) -> pd.Series:
    """
    Replică ta.pivothigh / ta.pivotlow din Pine.
    O bară j e pivot HIGH dacă high[j] e strict mai mare decât toate barele
    din fereastra [j-left, j+right] (excluzând j). Similar pentru LOW.
    Pivotul e "confirmat" abia la bara j+right (non-repainting) — dar aici
    returnăm valoarea la indexul j (momentul real al pivotului), lăsând
    caller-ul să știe că informația devine disponibilă abia right bare mai
    târziu.
    """
    n = len(series)
    out = pd.Series(np.nan, index=series.index)
    vals = series.values
    for j in range(left, n - right):
        window = vals[j - left: j + right + 1]
        center = vals[j]
        if mode == "high":
            if center == window.max() and (window == center).sum() == 1:
                out.iloc[j] = center
        else:
            if center == window.min() and (window == center).sum() == 1:
                out.iloc[j] = center
    return out


# --------------------------------------------------------------------------
# 2. MSS / BOS — fidel Prev_Breakout_Type din Lenny_Kiruthu
# --------------------------------------------------------------------------

@dataclass
class StructureEvent:
    bar_index: int
    time: object
    price: float
    kind: str          # "BOS" sau "MSS"
    direction: str      # "bullish" sau "bearish"
    swing_length: int


def detect_bos_mss(df: pd.DataFrame, swing_length: int = 7,
                    use_high_low: bool = False) -> list[StructureEvent]:
    """
    df trebuie să aibă coloane: time/Datetime, Open, High, Low, Close
    (nume flexibile — vezi normalize_ohlc mai jos).

    use_high_low=False (default-ul din Pine-ul tău) => se compară cu CLOSE,
    adică breakout valid = body-close dincolo de nivel (regula ta de
    "sweep body-close obligatoriu" din Lichiditate.md se aplică IDENTIC aici).
    use_high_low=True => se compară cu High/Low (wick-only breakout, mai slab).
    """
    highs = df["High"].values
    lows = df["Low"].values
    closes = df["Close"].values
    times = df["time"].values if "time" in df.columns else df.index

    piv_high = find_pivots(df["High"], swing_length, swing_length, "high")
    piv_low = find_pivots(df["Low"], swing_length, swing_length, "low")

    price_ref = closes if not use_high_low else highs
    price_ref_low = closes if not use_high_low else lows

    prev_high = None
    prev_low = None
    high_present = False
    low_present = False
    prev_breakout_type = 0   # 0 = niciunul încă, 1 = ultimul breakout a fost sus, -1 = jos

    events: list[StructureEvent] = []
    n = len(df)

    for i in range(n):
        # actualizare pivot high nou confirmat la bara i (dacă există)
        if not np.isnan(piv_high.iloc[i]):
            new_high = piv_high.iloc[i]
            prev_high = new_high
            high_present = True
        if not np.isnan(piv_low.iloc[i]):
            new_low = piv_low.iloc[i]
            prev_low = new_low
            low_present = True

        # verificare breakout în sus
        if high_present and prev_high is not None and price_ref[i] > prev_high:
            kind = "BOS" if prev_breakout_type == 1 else (
                "MSS" if prev_breakout_type == -1 else None)
            if kind is not None:
                events.append(StructureEvent(
                    bar_index=i, time=times[i], price=prev_high,
                    kind=kind, direction="bullish", swing_length=swing_length))
            prev_breakout_type = 1
            high_present = False

        # verificare breakout în jos
        if low_present and prev_low is not None and price_ref_low[i] < prev_low:
            kind = "BOS" if prev_breakout_type == -1 else (
                "MSS" if prev_breakout_type == 1 else None)
            if kind is not None:
                events.append(StructureEvent(
                    bar_index=i, time=times[i], price=prev_low,
                    kind=kind, direction="bearish", swing_length=swing_length))
            prev_breakout_type = -1
            low_present = False

    return events


# --------------------------------------------------------------------------
# 3. Order Block — fidel wugamlo (study("Order Block Finder"))
# --------------------------------------------------------------------------

@dataclass
class OrderBlockEvent:
    bar_index: int          # indexul candelei OB (ob_period bare în urmă)
    time: object
    direction: str           # "bullish" / "bearish"
    high: float
    low: float
    avg: float


def detect_order_blocks(df: pd.DataFrame, periods: int = 5,
                         threshold_pct: float = 0.0,
                         use_wicks: bool = False) -> list[OrderBlockEvent]:
    """
    Replică exact logica din Script_ob.txt:
      ob_period = periods + 1
      absmove   = |close[ob_period] - close[1]| / close[ob_period] * 100
      relmove   = absmove >= threshold
      bullishOB = close[ob_period] < open[ob_period]     (candelă roșie)
      upcandles = nr. candele verzi în ultimele `periods` bare (index 1..periods)
      OB_bull   = bullishOB and upcandles==periods and relmove
    (simetric pentru bearish)
    """
    ob_period = periods + 1
    opens = df["Open"].values
    closes = df["Close"].values
    highs = df["High"].values
    lows = df["Low"].values
    times = df["time"].values if "time" in df.columns else df.index

    n = len(df)
    events: list[OrderBlockEvent] = []

    for i in range(ob_period, n):
        # index curent = i ; [1] = i-1 ; [ob_period] = i-ob_period
        close_ob = closes[i - ob_period]
        open_ob = opens[i - ob_period]
        close_1 = closes[i - 1]

        if close_ob == 0:
            continue
        absmove = abs(close_ob - close_1) / close_ob * 100
        relmove = absmove >= threshold_pct

        # candelele dintre [i-periods .. i-1] => offsets 1..periods
        window_open = opens[i - periods:i]
        window_close = closes[i - periods:i]

        bullish_ob_candle = close_ob < open_ob
        upcandles = int((window_close > window_open).sum())
        if bullish_ob_candle and upcandles == periods and relmove:
            ob_high = highs[i - ob_period] if use_wicks else open_ob
            ob_low = lows[i - ob_period]
            events.append(OrderBlockEvent(
                bar_index=i - ob_period, time=times[i - ob_period],
                direction="bullish", high=ob_high, low=ob_low,
                avg=(ob_high + ob_low) / 2))

        bearish_ob_candle = close_ob > open_ob
        downcandles = int((window_close < window_open).sum())
        if bearish_ob_candle and downcandles == periods and relmove:
            ob_high = highs[i - ob_period]
            ob_low = lows[i - ob_period] if use_wicks else open_ob
            events.append(OrderBlockEvent(
                bar_index=i - ob_period, time=times[i - ob_period],
                direction="bearish", high=ob_high, low=ob_low,
                avg=(ob_high + ob_low) / 2))

    return events


# --------------------------------------------------------------------------
# 4. FVG — Fair Value Gap standard (3 candele)
# --------------------------------------------------------------------------

@dataclass
class FVGEvent:
    bar_index: int       # bara de mijloc (candela 2 din cele 3)
    time: object
    direction: str
    top: float
    bottom: float
    filled: bool
    filled_at_index: int = None


def detect_fvg(df: pd.DataFrame) -> list[FVGEvent]:
    highs = df["High"].values
    lows = df["Low"].values
    times = df["time"].values if "time" in df.columns else df.index
    n = len(df)
    events: list[FVGEvent] = []

    for i in range(2, n):
        # candela 1 = i-2, candela 2 = i-1, candela 3 = i
        c1_high, c1_low = highs[i - 2], lows[i - 2]
        c3_high, c3_low = highs[i], lows[i]

        if c1_high < c3_low:  # bullish FVG
            top, bottom = c3_low, c1_high
            filled = False
            filled_at = None
            for j in range(i + 1, n):
                if lows[j] <= bottom:
                    filled, filled_at = True, j
                    break
            events.append(FVGEvent(i - 1, times[i - 1], "bullish", top, bottom,
                                    filled, filled_at))

        if c1_low > c3_high:  # bearish FVG
            top, bottom = c1_low, c3_high
            filled = False
            filled_at = None
            for j in range(i + 1, n):
                if highs[j] >= top:
                    filled, filled_at = True, j
                    break
            events.append(FVGEvent(i - 1, times[i - 1], "bearish", top, bottom,
                                    filled, filled_at))

    return events


# --------------------------------------------------------------------------
# 5. Lichiditate — NU avem sursă Pine, construit din research ICT/SMC
#    (vezi caveat jos). E componenta cu cea mai mică încredere.
# --------------------------------------------------------------------------

@dataclass
class LiquidityEvent:
    bar_index: int
    time: object
    level: float
    direction: str        # "buyside_swept" (peste high) / "sellside_swept" (sub low)
    sweep_type: str        # "body_close" sau "wick_only"
    is_reliquidation: bool


def detect_liquidity_sweeps(df: pd.DataFrame, swing_length: int = 7,
                             equal_level_tol_pct: float = 0.02,
                             reliq_lookback_bars: int = 300) -> list[LiquidityEvent]:
    """
    Definiție folosită (din research ICT/SMC, filtre F2 deja confirmate în
    jurnalul tău — sweep valid = body-close dincolo de nivel):
      1. Nivelurile de lichiditate = pivot highs/lows (swing points) SAU
         grupuri de 2+ swing-uri apropiate ca preț (equal highs/lows).
      2. Sweep = o bară a cărei BODY (nu doar fitil) închide dincolo de nivel.
      3. Re-liquidation = un nivel deja măturat o dată, măturat a doua oară
         după o pauză (>reliq_lookback_bars între cele 2 sweep-uri).
    """
    highs = df["High"].values
    lows = df["Low"].values
    closes = df["Close"].values
    times = df["time"].values if "time" in df.columns else df.index
    n = len(df)

    piv_high = find_pivots(df["High"], swing_length, swing_length, "high")
    piv_low = find_pivots(df["Low"], swing_length, swing_length, "low")

    # grupăm pivoturi apropiate ca "nivel de lichiditate"
    high_levels = []   # listă de (bar_index_creat, preț, ultimul_index_folosit_sweep)
    low_levels = []

    events: list[LiquidityEvent] = []

    for i in range(n):
        if not np.isnan(piv_high.iloc[i]):
            high_levels.append({"created_at": i, "price": piv_high.iloc[i], "swept_at": []})
        if not np.isnan(piv_low.iloc[i]):
            low_levels.append({"created_at": i, "price": piv_low.iloc[i], "swept_at": []})

        for lvl in high_levels:
            if lvl["created_at"] >= i:
                continue
            tol = lvl["price"] * equal_level_tol_pct / 100
            if highs[i] > lvl["price"] + tol and not lvl["swept_at"]:
                sweep_type = "body_close" if closes[i] > lvl["price"] else "wick_only"
                if sweep_type == "body_close":
                    is_reliq = any(
                        (i - prev_sweep) > reliq_lookback_bars
                        for prev_sweep in lvl["swept_at"]
                    ) if lvl["swept_at"] else False
                    events.append(LiquidityEvent(
                        i, times[i], lvl["price"], "buyside_swept",
                        sweep_type, is_reliq))
                    lvl["swept_at"].append(i)

        for lvl in low_levels:
            if lvl["created_at"] >= i:
                continue
            tol = lvl["price"] * equal_level_tol_pct / 100
            if lows[i] < lvl["price"] - tol and not lvl["swept_at"]:
                sweep_type = "body_close" if closes[i] < lvl["price"] else "wick_only"
                if sweep_type == "body_close":
                    is_reliq = any(
                        (i - prev_sweep) > reliq_lookback_bars
                        for prev_sweep in lvl["swept_at"]
                    ) if lvl["swept_at"] else False
                    events.append(LiquidityEvent(
                        i, times[i], lvl["price"], "sellside_swept",
                        sweep_type, is_reliq))
                    lvl["swept_at"].append(i)

    return events


# --------------------------------------------------------------------------
# Utilitar: normalizează un DataFrame OHLC din formate diferite
# --------------------------------------------------------------------------

def normalize_ohlc(df: pd.DataFrame) -> pd.DataFrame:
    """Acceptă coloane cu variații de nume (Datetime/time/datetime,
    Open/O, etc.) și le aduce la formatul standard folosit mai sus."""
    colmap = {}
    for c in df.columns:
        cl = c.lower()
        if cl in ("datetime", "time", "date"):
            colmap[c] = "time"
        elif cl in ("open", "o"):
            colmap[c] = "Open"
        elif cl in ("high", "h"):
            colmap[c] = "High"
        elif cl in ("low", "l"):
            colmap[c] = "Low"
        elif cl in ("close", "c"):
            colmap[c] = "Close"
        elif cl in ("volume", "v"):
            colmap[c] = "Volume"
    out = df.rename(columns=colmap).copy()
    if "time" in out.columns:
        out["time"] = pd.to_datetime(out["time"], utc=True, errors="coerce")
        out = out.sort_values("time").reset_index(drop=True)
    return out


# CAVEAT explicit, ca să nu se piardă în cod:
# - MSS/BOS și Order Block sunt traduceri FIDELE ale surselor Pine date de tine.
#   Diferența față de ce vezi pe TradingView poate veni DOAR din: (a) valoarea
#   reală de swing_length pe care o folosești (aici default 7, dar tu rulezi
#   probabil 2 instanțe cu valori diferite — configurabile la apel), sau
#   (b) faptul că indicatorul "Myaccount" NU e nici Lenny_Kiruthu nici wugamlo,
#   ci un al treilea script cu logică proprie (necunoscută, nesursă).
# - Lichiditatea NU are sursă Pine — e cea mai slabă verigă, de validat primul.
