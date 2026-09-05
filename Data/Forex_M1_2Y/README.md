# Forex M1 — 2 ani de date OHLC (2024-01 → 2026-06)

Date M1 (1 minut) pentru 7 perechi forex majore, exportate din MetaTrader 5 (pipeline ExportM1History EA). Acoperire: **2024-01-02 → 2026-06-30** (~2.5 ani, ~917k bare per pereche).

## Fișiere

| Fișier | Bare (linii) | Start | Sfârșit |
| --- | --- | --- | --- |
| `AUDJPY_M1_2024_2026.csv` | 918,455 | 2024-01-02 09:59 | 2026-06-30 23:55 |
| `AUDUSD_M1_2024_2026.csv` | 916,852 | 2024-01-02 09:59 | 2026-06-30 23:55 |
| `EURUSD_M1_2024_2026.csv` | 916,676 | 2024-01-02 09:59 | 2026-06-30 23:55 |
| `GBPJPY_M1_2024_2026.csv` | 919,934 | 2024-01-02 09:59 | 2026-06-30 23:55 |
| `GBPUSD_M1_2024_2026.csv` | 917,216 | 2024-01-02 09:59 | 2026-06-30 23:55 |
| `USDCHF_M1_2024_2026.csv` | 916,189 | 2024-01-02 09:59 | 2026-06-30 23:55 |
| `USDJPY_M1_2024_2026.csv` | 917,081 | 2024-01-02 09:59 | 2026-06-30 23:55 |

> **GBPUSD OANDA `.pro` (feed alternativ):** `GBPUSD_M1_OANDApro_2024_2026.csv` — 981,958 bare, **2024-01-01 → 2026-08-24**. Același format, dar prețurile vin din brokerul **OANDA** (simbolul `GBPUSD.pro`), nu RoboForex. E feed-ul canonic pentru strategia No-Wick (determinarea `no-wick` depinde de prețurile exacte OANDA). Spread = 0 și aici.

## Format coloane

`Datetime,Open,High,Low,Close,Volume,Spread,RealVolume`

- `Datetime` — timp server (fără conversie de timezone)
- `Open/High/Low/Close` — prețuri
- `Volume` — volumul barei
- `Spread` — **0 în aceste exporturi** (nu conține spread real pe bară)

## Notă importantă pentru backtest

- Spread = 0 în toate fișierele de aici. Pentru simulări care au nevoie de spread real, folosiți datele `.pro` (OANDA, spread real, dar acoperă doar May–Jul 2026) sau exporturile FundingPips/RoboForex cu spread pe bară.
- Pentru acoperire 2026-07 → 2026-08 (după sfârșitul acestor fișiere), există exporturi FP/RF separate (`*_M1_FP_20260506_20260812_noWE.csv`, `*_M1_RF_...`, `*_M1_FP_2Y_...`).
