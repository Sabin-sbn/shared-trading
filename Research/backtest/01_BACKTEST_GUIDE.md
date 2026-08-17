# 01 — Ghid Backtest în Python (complet)

> Ghidul complet: setup, date, motor, planuri de backtest, validare. Citește-l o dată cap-coadă, apoi folosește celelalte fișiere ca referință.

## Cuprins
1. [Stack + setup](#1-stack--setup)
2. [Datele: M1 → resample](#2-datele-m1--resample)
3. [Motorul de backtest — reguli](#3-motorul-de-backtest--reguli)
4. [Planurile de backtest (0→6)](#4-planurile-de-backtest-06)
5. [Checklist final](#5-checklist-final)

---

## 1. Stack + setup

```bash
pip install pandas numpy matplotlib
```

- `pandas` — totul e DataFrame.
- `numpy` — calcule vectorizate.
- `matplotlib` — equity curve, drawdown.
- Opțional (doar live/forward, **nu** istoric lung): `pip install MetaTrader5`.

Descărcarea datelor: vezi [[02_DATA_DOWNLOAD]].

## 2. Datele: M1 → resample

O singură sursă de adevăr: M1 → resample în sus. Nu descărca M15 separat.

```python
from data_loader import load_pair
df_m15, df_m1 = load_pair('GBPUSD', '2024-07-01', '2026-07-01')
# df_m15: datetime, O, H, L, C, V  (bari de 15 min)
# df_m1 : Datetime, Open, High, Low, Close, Volume  (raw M1)
```

## 3. Motorul de backtest — reguli

Backtest corect = **event loop cronologic**: parcurgi barele în ordine, și la fiecare bară aplici regula folosind **doar** informația disponibilă până la acea bară.

**Reguli nenegociabile:**
1. **Fără lookahead.** Semnalul se calculează la close-ul barei `t`, intrarea se execută la open-ul barei `t+1`.
2. **Modelează spread-ul.** Fără spread, orice TP mic pare magic.
3. **Modelează bid/ask.** SL-ul unui short se atinge pe Ask, al unui long pe Bid. Dacă testezi doar pe High/Low (mid), ai un gap sistematic.
4. **Ordinea SL vs TP în aceeași bară** trebuie decisă conservator (sau rezolvată cu date M1).
5. **Fără parametri din viitor.**

Motorul didactic gata: `Research/code/backtest_minimal.py`.

## 4. Planurile de backtest (0→6)

Fă-le **în ordine**. Nu sări la optimizare (Plan 6) fără 0–5.

### Plan 0 — Smoke test
Rulează motorul corect? Datele valide? Verifică interval, bare, lipsuri. Rulează o strategie trivială și verifică că 0 trade-uri → 0 profit.

### Plan 1 — Baseline in-sample (mecanica pură)
Strategia **fără filtre** pe tot istoricul. Doar măsoară (N, WR%, PF, net pips, % profit, MaxDD). **Nu optimiza.** Adevăr dur: mecanica pură de obicei pierde — edge-ul stă în **când și cum intri** (filtrele).

### Plan 2 — Train / Test split
- **Split în timp, nu aleator** (trecut → viitor). De obicei 70/30 la o dată fixă.
- Reglezi parametrii **doar** pe train, raportezi **doar** pe test.
- Colaps pe test față de train = overfitting.

### Plan 3 — Walk-forward (inima validării)
- **Rolling:** fereastra 1 = train → test pe 2; train pe 2 → test pe 3; etc.
- **Anchored:** train-ul crește, testul rămâne fix pe următoarea fereastră.
- **Regula (Gate 1):** bate baseline-ul pe minim **3/4 ferestre** de test.
- Template: `Research/code/walk_forward.py`.

### Plan 4 — Blind test (oarbă, complet nevăzută)
Rulează config-ul final, înghețat, pe o fereastră **niciodată folosită** în development (ex: 2022–2023 dacă ai optimizat pe 2024–2026). Compară WR cu train-ul. **Delta > 15pp = respins.**

### Plan 5 — Monte Carlo
Resamplează trade-urile finale cu replacement de mii de ori (5,000), recalculează echitatea + MaxDD (0.5%/trade, $10k), numără breach-urile. **Regula (Gate 3): < 5% breach rate.**
Template: `Research/code/monte_carlo.py`.

### Plan 6 — Grid search / optimizare (cu grijă maximă)
1. **Maxim 1–2 parametri liberi per rundă.**
2. **Regula marginii (Gate 5):** optim la margine → extinde grid-ul.
3. Fiecare parametru cu justificare (Gate 7).
4. După optimizare, **obligatoriu** Plan 3 + Plan 4.

## 5. Checklist final

- [ ] Plan 0–6 în ordine
- [ ] Gate 1–7 trecute (vezi [[03_VALIDATION_GATES]])
- [ ] Calibrare: Python PF ≥ 2.3 (vezi [[05_METRICS_AND_CALIBRATION]])
- [ ] Forward test demo 2+ săptămâni
- [ ] Risc ≤ 0.5% per trade

> **TL;DR:** M1 → resample · fără lookahead · cu spread · Python umflă ~2.22× · validezi pe date unseen · live-ul e adevărul.
