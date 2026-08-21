"""
data_loader.py — Single source of truth: M1 only.
Resamples M15 OHLC from M1 data. No separate M15 CSVs (those come from
different brokers and are inconsistent).

Provides:
  load_pair(sym, start=None, end=None) -> (df_m15, df_m1)
    df_m1  : raw M1 with columns [Datetime, Open, High, Low, Close, Volume, Spread, RealVolume]
    df_m15 : resampled 15-min bars with columns [datetime, O, H, L, C, V]
"""
import os

import pandas as pd

BASE = os.path.dirname(os.path.abspath(__file__))


def load_m1(sym):
    """Load raw M1 data for a symbol, parse to UTC datetime."""
    path = os.path.join(BASE, "history_export", "{}_M1_full.csv".format(sym))
    if not os.path.exists(path):
        raise FileNotFoundError("Missing M1 data: {} (run download_m1.py first)".format(path))
    df = pd.read_csv(path)
    df["Datetime"] = pd.to_datetime(df["Datetime"], utc=True)
    df = df.drop_duplicates(subset="Datetime").sort_values("Datetime").reset_index(drop=True)
    return df


def resample_m15(df_m1):
    """Resample M1 -> M15 OHLC."""
    d = df_m1.copy().set_index("Datetime")
    m15 = d.resample("15min").agg({
        "Open": "first",
        "High": "max",
        "Low": "min",
        "Close": "last",
        "Volume": "sum",
    }).dropna(subset=["Open"]).reset_index()
    m15 = m15.rename(columns={"Datetime": "datetime", "Open": "O", "High": "H",
                              "Low": "L", "Close": "C", "Volume": "V"})
    return m15


def load_pair(sym, start=None, end=None):
    """Return (df_m15, df_m1) sliced to [start, end) if given."""
    df_m1 = load_m1(sym)
    if start is not None:
        df_m1 = df_m1[df_m1["Datetime"] >= pd.Timestamp(start, tz="UTC")].reset_index(drop=True)
    if end is not None:
        df_m1 = df_m1[df_m1["Datetime"] < pd.Timestamp(end, tz="UTC")].reset_index(drop=True)
    df_m15 = resample_m15(df_m1)
    return df_m15, df_m1


if __name__ == "__main__":
    for sym in ["GBPUSD", "USDJPY"]:
        df_m15, df_m1 = load_pair(sym, "2024-07-01", "2026-07-01")
        print("{}: M1={:,} bars, M15={:,} bars  {} -> {}".format(
            sym, len(df_m1), len(df_m15),
            str(df_m15["datetime"].iloc[0]), str(df_m15["datetime"].iloc[-1])))
