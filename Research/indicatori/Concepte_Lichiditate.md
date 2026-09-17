---
tip_nota: concept
status: activa
tags: [trading, concept, lichiditate, sweep, ce functioneaza]
cssclass: color-fill-green
data: 2026-08-16
---

# 💧 Lichiditate

> Lichiditatea = banii de pe masă. Smart Money îi ia înainte să miște prețul.

---

## 📊 Ce spune datele

| Lichiditate | WR | AvgR | Trades |
| --- | --- | --- | --- |
| **Vizibilă** | **66%** | **+1.01** | **54** |
| Nu vizibilă | 48% | +0.46 | 75 |
| **Diferență** | **+18%** | — | — |

## 🔍 Ce e Lichiditatea

**Lichiditatea** = Stop Loss-urile acumulate la un nivel:
- **Egali înalți/josuri** (equal highs/lows) = lichiditate mare
- **Swing points** = lichiditate medie
- **High/Low anterior** = lichiditate

## 📐 Tipuri de Sweep

| Tip | Validitate | Descriere |
| --- | --- | --- |
| **Body-close** | ✅ Valid | Când corpul candelei trece peste nivel |
| **Fitil** | ⚠️ Slab | Doar fitilul trece, corpul rămâne |

## 🎯 Regula în strategie

> **Sweep body-close obligatoriu. Fără sweep = skip.**

- Sweep = prețul a măturat lichiditatea
- **Body-close** = candle a închis beyond nivelul
- **Fitil** = doar a atins, nu a confirmat

## 📈 Combinat cu alte semnale

| Combinatie | WR | Trades |
| --- | --- | --- |
| Lichiditate singură | 66% | 54 |
| **Lichiditate + FVG** | **85%** | 7 |
| **Lichiditate + 2 MSS + FVG** | **100%** | 3 |
| Lichiditate + OB | 70% | 10 |

## 💡 Re-lichidare

**Re-lichidare** = lichiditate care a fost luată acum ceva timp:
- Prețul a măturat egali înalți/josuri
- Apoi s-a consolidat
- Acum revine să ia iar lichiditatea

Datele arată **100% WR** pe re-lichidare + MSS Great (5 trades).

## 🔗 Legături

- [[Rapoarte/Analiza_Obiectiva_129]] — datele complete
- [[Concepte/MSS — Market Structure Shift]] — MSS-ul vine după sweep
- [[Concepte/Setup_Tipuri]] — cum se combină
- [[Trading_Hub]] — punctul central
