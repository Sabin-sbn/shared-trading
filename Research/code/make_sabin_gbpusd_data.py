"""
make_sabin_gbpusd_data.py
=========================
Genereaza datele M15 + M1 pentru GBP/USD sept 2025 - feb 2026, in formatul
pe care build_chart_html.py (motorul lui Stefan) il citeste:
    time(sec epoch), open, high, low, close, tick_volume

Sursa: history_export/GBPUSD_M1_full.csv (UTC, coloane Datetime/Open/High/Low/Close/Volume)
Iesire: gbpusd_pro_m15_2025_09_2026_02.csv + gbpusd_pro_m1_2025_09_2026_02.csv
"""
import os
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "history_export", "GBPUSD_M1_full.csv")
OUT15 = os.path.join(HERE, "gbpusd_pro_m15_2025_09_2026_02.csv")
OUTM1 = os.path.join(HERE, "gbpusd_pro_m1_2025_09_2026_02.csv")

START = "2025-09-01"
END = "2026-02-28 23:59:59"


def to_csv(df15, out):
    out_cols = {"time": "Datetime", "open": "Open", "high": "High", "low": "Low",
                "close": "Close", "tick_volume": "Volume"}
    w = df15[list(out_cols.values())].copy()
    # time = epoch SECONDS (UTC). Conversie robusta la secunde (unitatea nu conteaza).
    w["time"] = w["Datetime"].astype("datetime64[s]").astype("int64")
    w = w.rename(columns={"Open": "open", "High": "high", "Low": "low",
                          "Close": "close", "Volume": "tick_volume"})
    w[["time", "open", "high", "low", "close", "tick_volume"]].to_csv(
        out, index=False, float_format=lambda x: f"{x:.5f}")
    print("scris:", out, "bare:", len(w))


def main():
    df = pd.read_csv(SRC)
    df["Datetime"] = pd.to_datetime(df["Datetime"], utc=True)
    w1 = df[(df["Datetime"] >= pd.Timestamp(START, tz="UTC")) &
            (df["Datetime"] <= pd.Timestamp(END, tz="UTC"))].copy()
    print("M1 in fereastra:", len(w1))
    # M1 output (drop tz so int64 conversion to epoch works as naive-UTC)
    w1_out = w1.copy()
    w1_out["Datetime"] = w1_out["Datetime"].dt.tz_localize(None)
    to_csv(w1_out, OUTM1)

    # M15 aggregate
    w15 = w1.set_index("Datetime").resample("15min").agg({
        "Open": "first", "High": "max", "Low": "min", "Close": "last",
        "Volume": "sum"}).dropna().reset_index()
    w15["Datetime"] = w15["Datetime"].dt.tz_localize(None)
    to_csv(w15, OUT15)


if __name__ == "__main__":
    main()
