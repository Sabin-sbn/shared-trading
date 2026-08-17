# Backtest în Python — Hub de cunoștințe

> **Pentru Sabin & Nicolas.** Cum să-ți construiești o strategie de trading și s-o testezi corect în Python, cu date OHLC reale din MT5 (RoboForex).
>
> **Regula de bază a întregului ghid:** *backtest-ul e orientativ, live-ul e adevărul.* Orice rezultat care n-a trecut prin date **nevăzute** (unseen) nu există.

## Citește în ordine

| # | Fișier | Ce înveți |
|---|--------|-----------|
| 1 | [[01_BACKTEST_GUIDE]] | Ghidul complet: setup, date, motor, planuri de backtest, gates |
| 2 | [[02_DATA_DOWNLOAD]] | Cum descarci 2.5 ani de date M1 din MT5 (pipeline-ul real) |
| 3 | [[05_METRICS_AND_CALIBRATION]] | Ce măsori + **calibrarea critică** (Python umflă rezultatele ~2.22×) |
| 4 | [[03_VALIDATION_GATES]] | Cele 8 gate-uri obligatorii înainte de live |
| 5 | [[04_LESSONS_LEARNED]] | Greșelile care au costat bani — ca să nu le repeți |
| 6 | [[06_FORWARD_TEST_AUDIT]] | Cum auditezi un forward-test live (V2→V6 style) |

## Codul (în `Research/code/`)

| Fișier | Ce face |
|--------|---------|
| `ExportM1History_EA.mq5` | EA-ul de export M1 (compilezi în MetaEditor) |
| `download_m1.py` | Descarcă M1 pentru 7 perechi prin Strategy Tester |
| `data_loader.py` | Încarcă M1 + resample M1 → M15 (sursă unică de date) |
| `backtest_minimal.py` | Motor de backtest corect, didactic — **începe de aici** |
| `walk_forward.py` | Template walk-forward (train → test, rolling) |
| `monte_carlo.py` | Monte Carlo bootstrap + breach rate |

## Fluxul recomandat

```
1. Compilezi EA + rulezi download_m1.py   → ai date M1
2. Editezi strategia în backtest_minimal.py → măsori metricile
3. Walk-forward + blind test + Monte Carlo  → validezi pe date unseen
4. Doar dacă trece toate gate-urile        → forward test pe demo 2+ săptămâni
5. Abia apoi → live (risc ≤ 0.5% per trade)
```

> ⚠️ **TL;DR:** M1 → resample în sus · fără lookahead · cu spread · Python PF ≥ 2.3 = breakeven real · validezi pe date unseen · live-ul e adevărul.
