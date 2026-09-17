# Jurnal de backtest CORECTAT (GBPUSD și celelalte perechi)

Export automat din tool-ul de verificare: **`Research/code/gbpusd_m1_verifier.html`**.
Generat la **2026-09-17**. Autor: Nicolas (Tioping).

## Fișiere

| Fișier | Ce e |
|---|---|
| `jurnal_backtest_corectat.csv` | toate trade-urile, un rând per trade — se deschide în Excel / LibreOffice |
| `jurnal_backtest_corectat.json` | același lucru + metadate (total, pe perechi, coloane) pentru scripturi |
| `DE_VERIFICAT_tradeuri_SL.md` | 4 trade-uri cu SL pe partea greșită — de corectat din poze |

## Ce e corectat față de jurnalul brut

1. **Entry și SL** — validate manual de Nicolas, prin potrivirea prețurilor și citirea din pozele
   trade-urilor (Stop Loss-ul e nivelul structural, nu valoarea din notițe).
2. **Ora** — jurnalul nu era pe un singur fus orar; coloana `fix_ore` conține corecția aplicată
   pentru fiecare trade, iar `intrare_utc` = ora corectată (UTC). Sunt 49 de corecții.
3. **Rezultatul real** — `rezultat` = WIN / LOSS, plus `R_realizat` (2.0 = +2R, -1.0 = -1R).

## Coloane (CSV)

`nr` · `pereche` · `directie` · `intrare_jurnal` · `fix_ore` · `intrare_utc` · `durata_min` ·
`entry` · `sl` · `sl_pips` · `R_realizat` · `rezultat` · `sesiune` ·
**`ind_MSS`** · **`ind_FVG`** · **`ind_lichiditate`** · `market` · `strategie` · `setup` · `entry_model` · `nota`

Coloanele `ind_*` sunt **indicatorii notați de Nicolas la fiecare trade** (calitatea MSS, calitatea FVG,
lichiditate — ex. „re-liquidation"). Vezi `indicatori/README_INDICATORI.md` pentru ce înseamnă fiecare.

## Cifre

- **127 trade-uri** reale (jurnalul are 132 rânduri, 5 goale).
- Pe perechi: GBPUSD 48 · NAS100 33 · USDJPY 25 · EURUSD 18 · AUDUSD 1 · EURAUD 1 · GER40 1.
- Rezultate: **74 WIN / 52 LOSS**.

## Cum se regenerează

Din tool: **`Export dataset (JSON)`** și **`Export CSV`** (cardul „Setups din jurnal — antrenare AI").
Sursa de adevăr e constanta `JOURNAL` din `Research/code/gbpusd_m1_verifier.html` — dacă se corectează
un trade acolo, re-exportă și înlocuiește fișierele de aici ca să rămână sincronizate.

## Vezi și

- `indicatori/` — indicatorii folosiți (MSS/BOS, Order Block, FVG, Lichiditate) + notele de concepte.
- `Research/code/structure_detector.py` — același model de structură, implementat în Python.
- `Nicolas_Logs/60-130ish_trades_Nicholas_analiza.md` — analiza trade-urilor 60-130.
