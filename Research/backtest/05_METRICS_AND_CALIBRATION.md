# 05 — Metricile corecte + calibrarea critică

> Ce măsori, cum le raportezi împreună, și **cea mai importantă lecție**: Python îți umflă rezultatele.

## Metricile (le raportezi TOATE împreună)

| Metrică | Sens |
|---|---|
| **N** (trade-uri) | câte finalizate (win+loss). **N < 100 = zgomot, nu trage concluzii.** |
| **WR%** | wins / N. 500 trade-uri → ±4.3pp; 100 → ±9.6pp. |
| **PF** (profit factor) | gross profit / gross loss. PF 1.6 cu N=86 e zgomot; PF 1.2 cu N=400 e de încredere. |
| **net pips** | suma pips după costuri. |
| **% profit pe depozit** | net pips × pip value / deposit. **Asta contează cel mai mult**, nu pips brut. |
| **MaxDD** | drawdown maxim ($ sau %). |
| **expectancy** | (WR × avg_win) − ((1−WR) × avg_loss). |

**Regula de raportare:** mereu **N + % profit pe depozit + PF împreună**. PF singur e orb. Pips brut singur e orb (depinde de pereche și de mărimea SL).

## ⚠️ Calibrarea critică — Python îți minte rezultatele

> **Un backtest Python (pe M1, fără spread/commission real) umflă profitul cu un factor de ~2.22× față de MT5 Strategy Tester cu Model=2** (care face fill pe tick real). Adică **PF Python ≈ 2.2 × PF real**.

**Consecințe practice:**
- **Pragul real de breakeven în Python = PF ≥ 2.3**, nu 1.15. Un config cu PF 1.5 în Python e probabil pierdere în real.
- PF 2.0 în Python ≈ breakeven în MT5 Model=2.
- Deflația exactă calibrată: **M15 = 2.22×, M1-fill = 2.09×**.

**Ce înseamnă pentru tine:**
1. Python = **screening rapid** (sortezi sute de config-uri în secunde).
2. **Verdictul final** = MT5 Strategy Tester (Model=2), nu Python.
3. Dacă un filtru nu arată **PF Python ≥ 2.3**, nu merită dus în MT5.

> Verificarea în MT5 e rapidă (~1 min/rulare pe 2 ani) — rulezi același config în Strategy Tester cu **Model=2** (Every tick based on real ticks). Acela e numărul în care poți avea încredere.

## De ce contează (exemplu)

| Sursă | PF | Verdict real |
|---|---|---|
| Python (inflaționat) | 1.5 | ❌ probabil pierdere |
| Python (inflaționat) | 2.3 | ⚠️ breakeven real |
| Python (inflaționat) | 3.0+ | ✅ șanse reale de profit |
| MT5 Model=2 | 1.2 | ✅ (măsurat direct, de încredere) |
