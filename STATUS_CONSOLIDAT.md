# Status Consolidat — Trading Project

> Ultima actualizare: 2026-08-20
> Sinteza TOT ce s-a făcut, tot ce lipsește, și ce urmează.

---

## 1. Infrastructură (FINALIZAT)

| Componentă | Status | Detalii |
|---|---|---|
| Repository Git | ✅ Final | `github.com/Sabin-sbn/shared-trading` — 3 colaboratori |
| Structură Obsidian | ✅ Final | Logs per persoană, Research comun, Chat async, sync.bat |
| AGENTS.md | ✅ Final | Reguli AI, audit trail, permisiuni |
| Project Board | 🟡 Parțial | 5 taskuri planificate, 1 finalizat (setup repo) |
| Data M1 (7 perechi) | ✅ Final | 2024-01 → 2026-06, ~917k bare/pereche |
| Data M1 (15+ perechi) | ✅ Final | Exporturi suplimentare RF/FP |
| Cod backtest | ✅ Final | `backtest_minimal.py`, `data_loader.py`, `walk_forward.py`, `monte_carlo.py` |
| Ghid backtest | ✅ Final | 6 documente: START_HERE → FORWARD_TEST_AUDIT |
| Calibrare Python | ✅ Final | Python PF × 2.22 = real; prag breakeven = PF ≥ 2.3 |

---

## 2. Date Disponibile

| Pereche | M1 (2024-2026) | M1 (suplimentar) | Dimensiune |
|---|---|---|---|
| EURUSD | ✅ 916,676 bare | ✅ RF/FP | ~50MB |
| GBPUSD | ✅ 917,216 bare | ✅ RF/FP | ~50MB |
| USDJPY | ✅ 917,081 bare | ✅ RF/FP | ~50MB |
| USDCHF | ✅ 916,189 bare | ✅ | ~50MB |
| AUDUSD | ✅ 916,852 bare | ✅ | ~50MB |
| GBPJPY | ✅ 919,934 bare | ✅ | ~50MB |
| AUDJPY | ✅ 918,455 bare | ✅ | ~50MB |
| USDCAD | — | ✅ RF/FP | ~50MB |
| NZDUSD | — | ✅ RF/FP | ~50MB |
| EURGBP | — | ✅ RF/FP | ~50MB |
| EURJPY | — | ✅ RF/FP | ~50MB |
| + altele | — | ✅ | ~50MB fiecare |

**Notă:** Spread = 0 în exporturile M1_2Y. Pentru spread real, folosește exporturile RF/FP.

---

## 3. Strategie — Stadiul Curent

### Strategia aleasă: SMC/ICT pe M1
- **Concepte:** MSS (Market Structure Shift) + FVG (Fair Value Gap) + Order Block + Lichiditate
- **Timeframe:** M1 → entry pe LTF, bias pe HTF
- **Sesiuni:** London (8-17 GMT+2), NY Open (13-15 GMT+2)

### Evoluția Backtest-ului

| Versiune | N | WR% | PF | MC% | Verdict |
|---|---|---|---|---|---|
| SMC Complet (sintetic) | 54 | 100% | 2244 | — | ❌ Overfitting |
| SMC M1 (real) | 528 | 29% | 0.75 | 100% | ❌ Eșec total |
| SMC Real (resample) | 90 | 30% | 0.79 | 94.5% | ❌ Eșec |
| STRICT (MSS+FVG+OB) | 815 | 38% | 1.14 | 100% | ⚠️ PF>1 dar MC mare |
| STRICT v2 (+session) | 313 | 42.5% | 1.37 | 84.8% | ⚠️ Session ajută |
| STRICT v3 (sell only) | 176 | 46.6% | 1.62 | 38.2% | ⚠️ SELL mai bun |
| **v4 (best pairs)** | **115** | **50.4%** | **1.89** | **12.9%** | ⚅**Cel mai bun** |
| **SL Opt (DYNAMIC+filtre)** | **202** | **67%** | **3.16** | **0.2%** | ✅ **PROMISING** |

### Configurația Cea Mai Promițătoare
```
Filtre: consec≥3 + DYNAMIC SL (1.5×ATR) + R:R=1.5
WR: 67% | PF: 3.16 | MC: 0.2% breach
Sursa: backtest_sl_opt.py pe 7 perechi M1
```

### Validări Trecute
- ✅ Monte Carlo: 0.2% breach (sub 5%)
- ⚠️ Walk-forward: 2/4 ferestre (necesită 3/4)
- ⚠️ Eșantion: N=202 (sub 500 — necesită mai multe date)
- ❌ Blind test: nu a fost rulat
- ❌ Forward test demo: nu a fost făcut

---

## 4. Analiza Trade-urilor (Nicolas)

### Trades 1-10 (documentate complet)
- **WR:** 8/9 = 88.9% (fără #6 — fără imagine)
- **Setup:** MSS + FVG + (opțional) Re-liquidare
- **Lecții cheie:**
  1. Lichiditatea schimbă totul — trade 8 a pierdut din cauza lichidității ignorate
  2. FVG + MSS = entry puternic
  3. Re-liquidarea + MSS = cel mai puternic setup
  4. NU lua tradeuri când sunt știri
  5. SL = cel mai apropiat swing

### Trades 60-64 (note rough)
- Documentare informală, need polish
- Pattern: MSS after MSS, re-liquidity → MSS → FVG entry

### Backtest images (99+)
- 99+ imagini de backtest analizate
- Prompot de analiză vizuală: `trade_analysis_prompt.txt`

---

## 5. Indicatoare Custom (MT5)

| Categorie | Număr | Exemple |
|---|---|---|
| Entry | 12 | MACD Cross, RSI Extreme, StochRSI, CCI, Keltner, Bollinger, VWAP, Pivot, EMA Ribbon, ADX, Ichimoku |
| TP | 8 | Fibonacci, ATR Multiples, S/R, Pivot PP, CCI, Bollinger, Session H/L, Fixed Pips |
| Multi-TF | 10 | M1-M15-1H Align, HTF Trend, Triple MA, Ichimoku Multi |
| Filter | 12 | Session, News, Spread, Trend, Volatility, Range, Pullout, Breakout, London/NY, ATR, Volume, Day |

**Indicator principal:** `Catalin_entry+TP` — RSI + EMA + BB + Ichimoku

---

## 6. Ce LIPSEȘTE (Critical Path)

### 🔴 Blochează progresul
1. **Walk-forward 3/4 ferestre** — configurația optimă are doar 2/4. Necesită re-testare cu N mai mare.
2. **Eșantion minim 500 trades** — avem 202, necesităm 500+. Datele M1 există (7 perechi × 2.5 ani = ~6.4M bare).
3. **Forward test pe demo** — niciun test live/demo făcut. Minimum 2 săptămâni înainte de funding.

### 🟡 Important dar nu blochează
4. **Consolidare date** — 15+ perechi exportate dar nu toate în formatul potrivit pentru `data_loader.py`.
5. **Documentare trades 60-129** — notes rough, necesită curățare și structurare.
6. **Integrare indicatori MT5** — indicatorii custom nu sunt testați în backtest Python (doar în MT5).
7. **Risk management formal** — regulile sunt documentate dar nu implementate în cod.

### 🟢 Nice to have
8. **Dashboard live** — monitorizare performanță în timp real.
9. **Alerte TradingView** — notificări pentru setup-uri.
10. **Taxe și legislație România** — cercetare neterminată.

---

## 7. PAȘII URMĂTORI (Plan de Acțiune)

### Faza 1: Consolidare Date (1-2 zile)
- [ ] **S1.1** — Copiază toate CSV-urile M1 în `Research/code/history_export/` cu format standard
- [ ] **S1.2** — Verifică integritatea datelor (lipsuri, formatare, spread)
- [ ] **S1.3** — Adaugă perechi suplimentare (USDCAD, NZDUSD, EURGBP, EURJPY) în `data_loader.py`
- [ ] **S1.4** — Testează `load_pair()` pe toate perechile noi

### Faza 2: Backtest Riguros (3-5 zile)
- [ ] **S2.1** — Rulează `backtest_sl_opt.py` pe toate perechile (nu doar 7)
- [ ] **S2.2** — Walk-forward 4 ferestre pe N mare (500+ trades per fereastră)
- [ ] **S2.3** — Grid search: testează SL 5-25p, TP 10-50p, R:R 1.0-3.0
- [ ] **S2.4** — Validare Gate 1-8 pe configurația optimă
- [ ] **S2.5** — Documentează REZULTATE în `Nicolas_Logs/implementari.md`

### Faza 3: Forward Test Demo (2-4 săptămâni)
- [ ] **S3.1** — Configurează cont demo (RoboForex / FundingPips)
- [ ] **S3.2** — Implementează strategia ca EA MT5 sau rulează manual
- [ ] **S3.3** — Colectează trade-uri în CSV (formatul din `06_FORWARD_TEST_AUDIT.md`)
- [ ] **S3.4** — Audit săptămânal: WR, PF, MaxDD, execuție vs config
- [ ] **S3.5** — Nu modifica config-ul în timpul testului (sfânt!)

### Faza 4: Live (doar după Faza 3 trece)
- [ ] **S4.1** — FundingPips Phase 2: $10k, +8%, DD 5/10%
- [ ] **S4.2** — Risc 0.5% per trade, max 2-3 tradeuri/zi
- [ ] **S4.3** — Jurnal de trade-uri zilnic
- [ ] **S4.4** — Review săptămânal cu echipa

---

## 8. ALOCARE SARCINI (Propunere)

| Responsabil | Sarcini | Prioritate |
|---|---|---|
| **Nicolas** | Consolidare date, Backtest, Documentare trades | 🔴 |
| **Stefan** | Cod backtest optimizat, Walk-forward, Monte Carlo | 🔴 |
| **Sabin** | Forward test demo, Trading journal, Coordonare | 🟡 |

---

## 9. RISCURI IDENTIFICATE

| Risc | Impact | Probabilitate | Mitigare |
|---|---|---|---|
| Overfitting | Pierderi financiare | Medie | Walk-forward 3/4 + blind test |
| Date insuficiente | Rezultate nevalide | Mică | 15+ perechi × 2.5 ani |
| Spread real ≠ spread modelat | PF umflat | Mare | Verifică cu date RF/FP spread real |
| Emoții în live trading | Decizii proaste | Mare | EA automat sau jurnal strict |
| FundingPips failure | $10k pierdut | Mică | Phase 2 = testare, nu funding imediat |

---

## 10. CHESTIUNI DESCHISE (de discutat cu echipa)

1. **Ce platformă pentru forward test?** RoboForex demo? FundingPips demo?
2. **EA sau manual?** EA = automatizare dar mai mult cod; Manual = control dar necesită timp
3. **Perechi prioritare?** EURUSD (best historical) sau diversificare?
4. **Program de trading?** Câte ore/zi? Doar London/NY?
5. **Capital real când?** După câte luni de demo consistent?
6. **Taxe România?** Impozit profit trading — cercetare necesară

---

> **TL;DR:** Infrastructura e gata. Datele există. Strategia e identificată (SMC/ICT MSS+FVG+OB). Config optim: WR 67%, PF 3.16, MC 0.2%. Ce lipsește: walk-forward pe N mare (500+ trades) și forward test demo 2+ săptămâni. Următorul pas: consolidare date + backtest pe toate perechile.
