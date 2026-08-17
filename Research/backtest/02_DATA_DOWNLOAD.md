# 02 — Descărcarea datelor OHLC din MT5

> Cum obții **2.5 ani de date M1** reale (OHLC + spread) pentru backtest, direct din MT5 RoboForex.

## ⚠️ Regula #1: NU folosi API-ul MT5 pentru istoric M1

`MetaTrader5.copy_rates_range()` expune **doar ~66 de zile de M1** (~95k bare), indiferent de intervalul cerut. Pentru backtest serios ai nevoie de **2+ ani**. Soluția reală: **Strategy Tester + un EA de export**.

## Ce ai nevoie

1. **MT5 instalat + logat** pe contul RoboForex (orice terminal MT5 merge).
2. **EA-ul de export** `ExportM1History_EA.ex5` — compilezi sursa `Research/code/ExportM1History_EA.mq5` în MetaEditor (F7).
3. **Python + pandas** (`pip install pandas`).

## Cum funcționează (mecanica)

1. Strategy Tester, cu **Period=M1**, sincronizează ~2.5 ani de istoric M1 de la broker (Period=M1 e esențial — M15 sincronizează mai puțin).
2. EA-ul citește toate barele M1 din cache (`Bars(sym, PERIOD_M1)`) și le scrie într-un CSV în `Common/Files/`.
3. Scriptul Python rulează două treceri per pereche (două `FromDate`) ca să acopere tot intervalul, apoi face merge + dedup + conversie UTF-8.

## Pași concreți

### 1. Compilează EA-ul

- Deschide MT5 → MetaEditor (F4).
- Deschide `Research/code/ExportM1History_EA.mq5`.
- Apasă **F7** (compile). Rezultatul `ExportM1History_EA.ex5` apare în `MQL5/Experts/Advisors/`.

### 2. Editează config-ul din `download_m1.py`

În `Research/code/download_m1.py`, sus, setează:

```python
TERMINAL_EXE = r"C:\Program Files\MetaTrader 5\terminal64.exe"   # path-ul tău
TERMINAL_DIR = r"C:\Program Files\MetaTrader 5"                  # același folder
PAIRS = ["EURUSD", "USDCHF", "AUDUSD", "GBPUSD", "AUDJPY", "GBPJPY", "USDJPY"]
```

### 3. Rulează

```bash
python download_m1.py
```

~3–5 minute pentru 7 perechi. Output: `history_export/{SYM}_M1_full.csv` (~917K bare, ~52 MB per pereche).

## Ce primești în fiecare CSV

| Coloană | Semnificație |
|---|---|
| `Datetime` | timestamp UTC (`2024-01-02 09:59:00`) |
| `Open`, `High`, `Low`, `Close` | OHLC-ul barei M1 |
| `Volume` | tick volume |
| `Spread` | spread-ul la acel moment (0 dacă brokerul nu-l exportă) |
| `RealVolume` | volum real (0 dacă indisponibil) |

**Notă:** gap-urile de weekend (48h) sunt normale — CSV-ul le păstrează. Nu le șterge, motorul le tratează ca "fără bari noi".

## Troubleshooting

- **0 bare pentru o pereche:** simbolul nu e în Market Watch → adaugă-l manual în terminal înainte de export.
- **Fișierele export lipsesc:** verifică `%APPDATA%\MetaQuotes\Terminal\Common\Files\`.
- **GBPUSD iese mai mic (~26 MB):** re-fă merge-ul din fișierele Common — exporturile brute sunt intacte, doar merge-ul s-a întrerupt.
- **Niciodată** `copy_rates_range` pentru M1 — hard-limited la ~66 zile.

## De ce M1 și nu M15 direct

Rulezi pe M15 (sau orice TF mai mare) **întotdeauna prin resampling din M1** (vezi `data_loader.py`). Dacă descarci M15 separat, vine de la alt broker și e inconsistent. **O singură sursă de date (M1) → resample în sus.**
