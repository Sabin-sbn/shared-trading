"""
verifier_app.py
================
Instrument de VERIFICARE VIZUALĂ, nu de backtest.

Scop: închide bucla dintre "ce zice codul" și "ce desenezi tu manual pe
TradingView", cu un verdict Pass/Skip logat, ca să acumulezi în timp un
set de date etichetat corect (nu circular) — util mai târziu la calibrarea
swing_length și la modelul de confidence.

Rulare locală (unde ai deja pip):
    pip install streamlit plotly --break-system-packages
    streamlit run verifier_app.py

Aștept CSV-uri M1 în formatul deja folosit de data_loader.py:
    Datetime, Open, High, Low, Close, Volume
(exact ce produce ExportM1History_EA.mq5 / download_m1.py din proiect)

Flux de lucru recomandat:
    1. Alegi fișierul CSV (perechea) și fereastra orară a unui trade pe care
       îl cunoști deja bine (ex. orele aproximative dintr-un batch vechi de
       analiză, sau un trade nou din jurnal).
    2. Setezi swing_length — implicit 7 (Lenny_Kiruthu), dar poți rula și cu
       3, ca să compari cele două "sensibilități" pe care le vezi simultan
       în TradingView (Myaccount + BOS+MSS).
    3. Te uiți la chart-ul interactiv de aici ALĂTURI de TradingView (nu în
       locul lui — asta rămâne sursa de adevăr vizuală).
    4. Pentru fiecare eveniment din lista de jos, apeși Pass (codul a nimerit
       exact ce ai desenat tu) sau Skip (nu se potrivește / lipsă / greșit).
    5. Apeși "Salvează verdictele" — se adaugă în verification_log.csv.
       Rulezi asta pe 20-30 de ferestre diferite și abia atunci ai un număr
       de acuratețe real, nu o impresie.
"""

import glob
import json
import os
from datetime import datetime

import pandas as pd
import streamlit as st
import plotly.graph_objects as go

from structure_detector import (
    normalize_ohlc, detect_bos_mss, detect_order_blocks,
    detect_fvg, detect_liquidity_sweeps,
)

LOG_PATH = "verification_log.csv"
LOG_COLUMNS = [
    "logged_at", "symbol", "window_start", "window_end",
    "event_type", "direction", "bar_time", "price_level",
    "params_json", "verdict", "note",
]
QUEUE_PATH = "windows_to_verify.csv"
QUEUE_COLUMNS = ["trade_id", "symbol", "date", "start_time", "end_time", "note", "done"]
DATA_FOLDER = "history_export"


def load_log() -> pd.DataFrame:
    if os.path.exists(LOG_PATH):
        return pd.read_csv(LOG_PATH)
    return pd.DataFrame(columns=LOG_COLUMNS)


def append_log(rows: list[dict]):
    df_new = pd.DataFrame(rows)
    if os.path.exists(LOG_PATH):
        df_new.to_csv(LOG_PATH, mode="a", header=False, index=False)
    else:
        df_new.to_csv(LOG_PATH, index=False)


def load_queue() -> pd.DataFrame:
    if os.path.exists(QUEUE_PATH):
        df = pd.read_csv(QUEUE_PATH)
        if "done" not in df.columns:
            df["done"] = False
        return df
    return pd.DataFrame(columns=QUEUE_COLUMNS)


def mark_queue_done(trade_id):
    df = load_queue()
    if len(df) == 0:
        return
    df.loc[df["trade_id"].astype(str) == str(trade_id), "done"] = True
    df.to_csv(QUEUE_PATH, index=False)


def discover_csv_files(folder: str) -> dict:
    """Returnează {simbol_ghicit: cale_fisier} pentru toate CSV-urile găsite."""
    files = sorted(glob.glob(os.path.join(folder, "*.csv")))
    result = {}
    for f in files:
        base = os.path.basename(f)
        symbol_guess = base.split("_")[0] if "_" in base else base.replace(".csv", "")
        result[f"{symbol_guess}  ({base})"] = f
    return result


st.set_page_config(layout="wide", page_title="Verificator MSS/BOS/FVG/OB/Liq")
st.title("Verificator vizual — cod vs chart manual")

with st.sidebar:
    st.header("0. Coadă de ferestre (opțional)")
    queue_df = load_queue()
    pending = queue_df[queue_df["done"] != True] if len(queue_df) else queue_df
    st.caption(f"{len(pending)} ferestre nefăcute din {len(queue_df)} în {QUEUE_PATH}")
    queue_choice = None
    if len(pending) > 0:
        queue_labels = [f"#{r.trade_id} — {r.symbol} {r.date} {r.start_time}-{r.end_time}"
                         for r in pending.itertuples()]
        queue_pick = st.selectbox("Alege din coadă", ["— manual —"] + queue_labels)
        if queue_pick != "— manual —":
            queue_choice = pending.iloc[queue_labels.index(queue_pick)]

    st.header("1. Date")
    available = discover_csv_files(DATA_FOLDER)
    if available:
        default_label = None
        if queue_choice is not None:
            for label, path in available.items():
                if queue_choice["symbol"].upper() in label.upper():
                    default_label = label
                    break
        csv_label = st.selectbox(
            "Fișier CSV (descoperit automat în history_export/)",
            list(available.keys()),
            index=list(available.keys()).index(default_label) if default_label else 0,
        )
        csv_path = available[csv_label]
        symbol = csv_label.split(" ")[0]
    else:
        st.warning(f"Niciun CSV găsit în '{DATA_FOLDER}/'. Introdu calea manual mai jos.")
        csv_path = st.text_input("Cale CSV (M1)", value="history_export/GBPUSD_M1_full.csv")
        symbol = st.text_input("Simbol (pentru log)", value="GBPUSD")

    st.header("2. Fereastră de timp")
    date_str = st.text_input("Data (YYYY-MM-DD)",
                              value=str(queue_choice["date"]) if queue_choice is not None else "2026-01-08")
    start_time = st.text_input("Ora start (UTC, HH:MM)",
                                value=str(queue_choice["start_time"]) if queue_choice is not None else "12:00")
    end_time = st.text_input("Ora end (UTC, HH:MM)",
                              value=str(queue_choice["end_time"]) if queue_choice is not None else "16:00")

    st.header("3. Parametri detecție")
    swing_length = st.number_input("swing_length (BOS/MSS)", min_value=1, value=7)
    use_high_low = st.checkbox("Folosește High/Low în loc de Close (wick, nu body-close)", value=False)

    ob_periods = st.number_input("Order Block: periods", min_value=1, value=5)
    ob_threshold = st.number_input("Order Block: threshold %", min_value=0.0, value=0.0, step=0.05)
    ob_usewicks = st.checkbox("Order Block: folosește High/Low complet", value=False)

    show_fvg = st.checkbox("Arată FVG", value=True)
    show_liq = st.checkbox("Arată lichiditate (sweep)", value=True)
    liq_tol = st.number_input("Lichiditate: toleranță nivel egal (%)", min_value=0.0, value=0.02, step=0.01)

    load_btn = st.button("Încarcă și detectează", type="primary")

if "events_cache" not in st.session_state:
    st.session_state.events_cache = None

if load_btn:
    if not os.path.exists(csv_path):
        st.error(f"Nu găsesc fișierul: {csv_path}")
    else:
        df_full = pd.read_csv(csv_path)
        df_full = normalize_ohlc(df_full)
        start_dt = pd.Timestamp(f"{date_str} {start_time}:00", tz="UTC")
        end_dt = pd.Timestamp(f"{date_str} {end_time}:00", tz="UTC")
        window = df_full[(df_full["time"] >= start_dt) & (df_full["time"] <= end_dt)].reset_index(drop=True)

        if len(window) < swing_length * 2 + 5:
            st.warning(f"Doar {len(window)} bare în fereastră — prea puțin pentru swing_length={swing_length}. Lărgește fereastra.")
        else:
            bos_mss = detect_bos_mss(window, swing_length=swing_length, use_high_low=use_high_low)
            obs = detect_order_blocks(window, periods=ob_periods, threshold_pct=ob_threshold, use_wicks=ob_usewicks)
            fvgs = detect_fvg(window) if show_fvg else []
            liqs = detect_liquidity_sweeps(window, swing_length=swing_length, equal_level_tol_pct=liq_tol) if show_liq else []

            st.session_state.events_cache = {
                "window": window, "bos_mss": bos_mss, "obs": obs,
                "fvgs": fvgs, "liqs": liqs,
                "symbol": symbol, "window_start": str(start_dt), "window_end": str(end_dt),
                "params": {
                    "swing_length": swing_length, "use_high_low": use_high_low,
                    "ob_periods": ob_periods, "ob_threshold": ob_threshold,
                    "ob_usewicks": ob_usewicks, "liq_tol": liq_tol,
                },
            }

cache = st.session_state.events_cache

if cache is not None:
    window = cache["window"]
    fig = go.Figure(data=[go.Candlestick(
        x=window["time"], open=window["Open"], high=window["High"],
        low=window["Low"], close=window["Close"], name=cache["symbol"])])

    for ev in cache["bos_mss"]:
        color = "#2ecc71" if ev.direction == "bullish" else "#e74c3c"
        dash = "solid" if ev.kind == "MSS" else "dot"
        fig.add_hline(y=ev.price, line_color=color, line_dash=dash, line_width=2,
                      annotation_text=f"{ev.kind} ({ev.direction})",
                      annotation_position="top left")

    for ob in cache["obs"]:
        color = "rgba(46,204,113,0.18)" if ob.direction == "bullish" else "rgba(231,76,60,0.18)"
        fig.add_shape(type="rect", x0=window["time"].iloc[ob.bar_index], x1=window["time"].iloc[-1],
                      y0=ob.low, y1=ob.high, fillcolor=color, line_width=0)

    for fvg in cache["fvgs"]:
        color = "rgba(52,152,219,0.15)" if fvg.direction == "bullish" else "rgba(230,126,34,0.15)"
        x1 = window["time"].iloc[fvg.filled_at_index] if fvg.filled and fvg.filled_at_index else window["time"].iloc[-1]
        fig.add_shape(type="rect", x0=window["time"].iloc[fvg.bar_index], x1=x1,
                      y0=fvg.bottom, y1=fvg.top, fillcolor=color, line_width=0)

    for liq in cache["liqs"]:
        color = "#9b59b6" if liq.is_reliquidation else "#95a5a6"
        fig.add_hline(y=liq.level, line_color=color, line_dash="dashdot", line_width=1,
                      annotation_text=("Re-liq" if liq.is_reliquidation else "Liq"),
                      annotation_position="bottom right")

    fig.update_layout(height=700, xaxis_rangeslider_visible=False,
                       margin=dict(l=10, r=10, t=30, b=10))
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("Evenimente detectate — verifică vs chart-ul tău din TradingView")

    all_events = []
    for ev in cache["bos_mss"]:
        all_events.append({
            "type": ev.kind, "direction": ev.direction,
            "time": str(ev.time), "price": round(float(ev.price), 5),
            "extra": f"swing_length={ev.swing_length}",
        })
    for ob in cache["obs"]:
        all_events.append({
            "type": "Order Block", "direction": ob.direction,
            "time": str(ob.time), "price": f"{ob.low:.5f} - {ob.high:.5f}",
            "extra": f"avg={ob.avg:.5f}",
        })
    for fvg in cache["fvgs"]:
        all_events.append({
            "type": "FVG", "direction": fvg.direction,
            "time": str(fvg.time), "price": f"{fvg.bottom:.5f} - {fvg.top:.5f}",
            "extra": "filled" if fvg.filled else "necompletat",
        })
    for liq in cache["liqs"]:
        all_events.append({
            "type": "Liquidity", "direction": liq.direction,
            "time": str(liq.time), "price": round(float(liq.level), 5),
            "extra": "RE-LIQUIDATION" if liq.is_reliquidation else liq.sweep_type,
        })

    if not all_events:
        st.info("Niciun eveniment detectat în fereastra asta cu parametrii curenți.")
    else:
        verdicts = {}
        notes = {}
        for idx, ev in enumerate(all_events):
            cols = st.columns([2, 2, 2, 3, 2, 3])
            cols[0].write(f"**{ev['type']}**")
            cols[1].write(ev["direction"])
            cols[2].write(ev["time"][11:19] if len(ev["time"]) > 11 else ev["time"])
            cols[3].write(str(ev["price"]))
            cols[4].write(ev["extra"])
            verdicts[idx] = cols[5].radio(
                "verdict", ["—", "Pass", "Skip", "Nesigur"],
                key=f"verdict_{idx}", horizontal=True, label_visibility="collapsed")

        note_text = st.text_input("Notă generală pentru această fereastră (opțional)", value="")

        if st.button("Salvează verdictele în verification_log.csv", type="primary"):
            rows = []
            now = datetime.utcnow().isoformat()
            for idx, ev in enumerate(all_events):
                v = verdicts[idx]
                if v == "—":
                    continue
                rows.append({
                    "logged_at": now, "symbol": cache["symbol"],
                    "window_start": cache["window_start"], "window_end": cache["window_end"],
                    "event_type": ev["type"], "direction": ev["direction"],
                    "bar_time": ev["time"], "price_level": ev["price"],
                    "params_json": json.dumps(cache["params"]),
                    "verdict": v, "note": note_text,
                })
            if rows:
                append_log(rows)
                if queue_choice is not None:
                    mark_queue_done(queue_choice["trade_id"])
                st.success(f"Salvat {len(rows)} verdicte." +
                           (f" Fereastra #{queue_choice['trade_id']} marcată ca făcută în coadă."
                            if queue_choice is not None else ""))
            else:
                st.warning("Nu ai marcat niciun verdict (toate erau pe '—').")

st.markdown("---")
st.subheader("Rată de acuratețe acumulată (din verification_log.csv)")
log_df = load_log()
if len(log_df) == 0:
    st.info("Încă nu ai verdicte salvate. Rulează câteva ferestre mai sus.")
else:
    summary = (log_df[log_df["verdict"].isin(["Pass", "Skip"])]
               .groupby(["event_type"])["verdict"]
               .value_counts(normalize=True)
               .unstack(fill_value=0) * 100)
    st.dataframe(summary.round(1))
    st.caption(f"Total verdicte logate: {len(log_df)}")
