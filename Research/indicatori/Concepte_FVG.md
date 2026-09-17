---
tip_nota: concept
status: activa
tags: [trading, concept, fvg, ce functioneaza]
cssclass: color-fill-green
data: 2026-08-16
---

# 📐 FVG — Fair Value Gap

> **CEL MAI PUTERNIC semnal obiectiv din strategie.**

---

## 📊 Ce spune datele

| Metrică | Valoare |
| --- | --- |
| **Win Rate cu FVG** | **93%** (14W / 1L) |
| **Win Rate fără FVG** | 50% (58W / 56L) |
| **Diferență** | **+43%** |
| **AvgR cu FVG** | +1.80 |
| **AvgR fără FVG** | +0.54 |

## 🔍 Ce e FVG

Un **Fair Value Gap** e un spațiu gol între 3 candele consecutive:
- **Bullish FVG**: Candela 1 high < Candela 3 low (gap în sus)
- **Bearish FVG**: Candela 1 low > Candela 3 high (gap în jos)

## 📐 Cum îl identifici

1. Caută 3 candele consecutive în care corpul lor nu se suprapune complet
2. Spațiul dintre candela 1 și candela 3 = FVG
3. Marchează zona (low-high a gap-ului)
4. **Necompletat** = prețul nu s-a întors încă în zona FVG

## 🎯 Regula în strategie

> **Fără FVG = SKIP automat.**

- FVG e **obligatoriu** pentru intrare
- FVG **necompletat** = cel mai bun (prețul nu a umplut gap-ul încă)
- FVG **suprapus cu OB** = confluență maximă

## 📈 Combinat cu alte semnale

| Combinatie | WR | Trades |
| --- | --- | --- |
| FVG singur | 93% | 15 |
| **FVG + 2 MSS** | **100%** | 5 |
| **FVG + Lichiditate** | **85%** | 7 |
| FVG + OB | 80% | 6 |
| FVG + London/NY | 92% | 14 |

## 🔗 Legături

- [[Rapoarte/Analiza_Obiectiva_129]] — datele complete
- [[Concepte/Setup_Tipuri]] — cum se încadrează în setup-uri
- [[Trading_Hub]] — punctul central
