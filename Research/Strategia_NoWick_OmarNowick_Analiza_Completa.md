---
tags:
  - trading
  - strategie
  - no-wick
  - forex
  - research
sursa: YouTube @omarnowick (66 clipuri analizate) + Playbook oficial PDF + indicator TradingView
data-analiza: 2026-08-21
---

# Strategia No Wick — Omar Nowick (Analiză Completă)

> **Ce e asta:** Analiza completă a strategiei "No Wick Candles" de la **omarnowick** (Omar Abouradi), bazată pe transcrierile integrale a **66 de clipuri YouTube** (~386.000 cuvinte curățate), inclusiv cursul complet de 5 ore, playbook-ul oficial PDF și codul indicatorului lui de TradingView.

---

## 1. Cine e Omar Nowick

- Trader forex full-time, originar din Suedia (a trăit într-un subsol, acum trăiește din trading în Dubai/Asia)
- Canal YouTube: [@omarnowick](https://www.youtube.com/@omarnowick) — ~174 videoclipuri, ~5K abonați
- Instagram/TikTok: @omarnowick
- Site mentorship: nowicktrading.com (No Wick Lab) + The Nowick Edge (cu Bardhi Shala)
- Indicator open-source pe TradingView: ["omarnowick"](https://www.tradingview.com/script/yTrRQHtf-omarnowick/) (4.400+ likes)
- Playbook gratuit (PDF, 25 pagini): "90% No Wick Strategy"
- Revendică: $20-40K/lună dintr-un singur cont live, folosind DOAR această strategie

---

## 2. Ce este un No Wick Candle (definiția lui EXACTĂ)

Din propriul lui indicator TradingView și din curs:

| Tip | Condiție |
| --- | --- |
| **Bullish No Wick** | Lumânare verde care are **fără fitil JOS** (open = low) |
| **Bearish No Wick** | Lumânare roșie care are **fără fitil SUS** (open = high) |

**Reguli critice de definiție:**
- ⚠️ Chiar și un fitil MIC descalifică lumânarea (trebuie zoom ca să vezi — de aceea folosește indicator)
- ⚠️ NU contează fitilul de pe partea opusă (o lumânare bullish poate avea fitil sus mare și tot e validă dacă nu are deloc jos)
- 📊 Statistica lui (USDJPY, 15min): doar **6,9%** din lumânările bullish se închid fără fitil jos, doar **6,3%** din cele bearish fără fitil sus → strategia se bazează pe ~13% din toate lumânările

### Indicatorul folosit
- **"X Ghost wickless candles"** pe TradingView — marchează automat cu săgeți lumânările valide
- El zice că e "un must" — imposibil de verificat manual cu zoom

---

## 3. Cele 5 Reguli de Bază (din clipul "Rules, Entries & Examples")

1. **Cu trendul:** Buys doar în uptrend, sells doar în downtrend. Lumânarea trebuie să fie în direcția trendului.
2. **Timeframe:** Doar **15 minute și peste**. Pe 5min funcționează dar win rate mai mic + prea zgomotos. El tradează EXCLUSIV pe 15min, fără top-down analysis, fără daily bias.
3. **Perechi valide:** USDJPY, GBPUSD, AUDUSD (+ gold istoric). Clasament actualizat după backtest 2026: **USDCHF > GBPUSD > USDJPY**
4. **Regula celor 10 lumânări:** Prețul TREBUIE să revină la lumânarea no-wick în maximum **10 lumânări**. După aia, setup-ul e invalid.
5. **SL + TP:** Stop loss la schimbarea de caracter (CHOCH) = ultimul **higher low confirmat** (uptrend) / ultimul **lower high confirmat** (downtrend). Take profit **exact 1:1**.

---

## 4. Mecanica Intrării (pas cu pas)

```
1. Confirmă trendul (structură de piață: HH+HL = uptrend, LH+LL = downtrend)
2. Apare lumânare No Wick în direcția trendului
3. AȘTEAPTĂ retragerea prețului ÎNAPOI la lumânarea no-wick ("tap")
4. INTRĂ când prețul atinge lumânarea (buy limit sau manual — el preferă buy limit)
5. SL la ultimul higher low confirmat (buys) / lower high confirmat (sells)
6. TP exact 1:1 RR
7. Dacă 10 lumânări trec fără tap → anulezi ordinul, setup invalid
```

**Detalii execuție:**
- Buy limit SAU intrare manuală — "nu face diferență mare", el pune de obicei limit
- Analizează pe TradingView → execută pe telefon (MT5/broker)
- **⚠️ REGULA DE DATE CRITICĂ:** Pe TradingView alege feed-ul **OANDA** ("Wanda" în transcriere)! Feed-uri diferite arată fitiluri diferite — o lumânare poate fi no-wick pe un feed și cu fitil pe altul. El tradează pe MT5 dar analizează DOAR pe date OANDA.

---

## 5. Trend & Structură de Piață (fundamentul)

### External vs Internal trend
- **External trend** = structura mare (swing highs/lows vizibile) → pentru trades în direcția trendului principal, SL bazat pe external
- **Internal trend** = structura mică din interior → permite trades contra trendului extern (ex: sell în uptrend extern bazat pe internal downtrend), SL bazat pe internal

### Verificarea în 3 pași (când se schimbă trendul)
1. **Închidere** sub ultimul higher low = **CHOCH** (Change of Character) — atenție: ÎNCHIDERE, nu fitil!
2. Respectarea highs-urilor (prețul nu face HH nou)
3. Închidere sub lows = **BOS** (Break of Structure) → downtrend confirmat

⚠️ După CHOCH există riscul de **fake out** (market makers împing prețul contra direcției) — trade-urile post-CHOCH au win rate mai mic decât trendurile clare.

---

## 6. Setup Ranking: A / B / C

| Setup | Win Rate | Descriere |
| --- | --- | --- |
| **A setup** | ~90% | Trend clar confirmat (toți cei 3 pași), lumânare perfectă |
| **B setup** | ~80% | Condiții bune dar nu perfecte |
| **C setup** | ~70%+ | Trade-uri mai slabe (ex: după CHOCH, fake-out zone) — după backtest 2026 win rate-ul lor a crescut |

El ia TOATE tipurile, dar mizează diferențiat. Secretul lui: "A setups" dau 90%.

---

## 7. Omar Entry (Early Entry / Pre-Entry)

**Problema:** în ~40% din cazuri, prețul vine spre lumânarea no-wick dar SE REJECTEAZĂ chiar înainte s-o atingă, apoi merge direct la TP — fără tine.

**Soluția lui:** intră CU UN PAS ÎNAINTE de atingerea lumânării (limit order plasat înainte).
- Se întâmplă cel mai mult pe USDJPY > GBPUSD > AUDUSD
- Aceleași reguli: SL la ultimul HL, TP 1:1
- ⚠️ **STATUS APRILIE 2026:** Omar entry e **PAUZAT** — "backtesting it more, want to make it crystal perfect". Nu-l folosi până anunță el.

---

## 8. Filtre & Invalidări

### Știri (red folder news)
- ❌ Fără trade-uri NOI cu 1 oră înainte de știri roșii
- ✅ Dacă EȘTI deja într-un trade: închide cu 15 minute înainte de știre
- ✅ Fără trade-uri noi până la 15 minute DUPĂ știre
- (Avansații pot evalua cazual: SL mic < 15 min până la știre = poți lăsa)

### Sesiuni
- Strategia funcționează în TOATE sesiunile
- Clasament actualizat (2026): **Asia #1, London #2**, NY cea mai slabă pe UJ/GU dar excelentă pe USDCHF
- Evită primele 1-2 ore după deschiderea Asiei (spread-uri mari)

### Imbalances (Fair Value Gaps)
- Concept BONUS/confluencă, NU obligatoriu
- Folosit ca filtru de calitate a trade-ului

### Minimum Stop Loss
- **Minimum 5 pips** (înainte de breathing room) — sub atât, sari trade-ul
- Motiv: comisioanele prop firm-urilor mănâncă profitul la SL-uri minuscule

### Alte invalidări
- Lumânarea nu e no-wick conform indicatorului (fitil mic ascuns)
- Trendul nu e clar (structură confuză, range)
- Setup la swing high/low structural major

---

## 9. Risk Management (Lecția 3 din Playbook — "non-negociabilă")

1. **Risc fix per trade: 1%** din cont. Niciodată mai mult după o pierdere, niciodată revenge trading. "Risk-ul trebuie să fie plictisitor."
2. **Un trade nu înseamnă nimic.** E despre repetarea aceluiași proces pe sute de trade-uri. Maraton, nu sprint.
3. **RR fix 1:1.** "Oamenilor le place RR mare; instituțiile iubesc probabilitatea." Nu ai nevoie de 1:5 dacă câștigi majoritatea trade-urilor.
4. **NU miști stopurile.** SL rămâne unde e, TP rămâne unde e. Mișcat stopul = frică deghizată.
5. **Protejează-ți mintea, nu doar contul.** Emoții calme = structură clară = aștepți închiderea lumânării = nu forțezi trade-uri.

---

## 10. Instrumentele lui complete

Din indicatorul lui TradingView (open-source):
1. No Wick Momentum Candles (detectare automată)
2. Market Structure labels (HH/HL/LH/LL)
3. BOS & CHOCH lines
4. Trading Sessions (Asia/London/NY backgrounds)
5. Session Break Zone (No Trading Zone)
6. Risk Dashboard (lot size calculator: balance, risk %, SL size → lot)
7. Manual Backtest Dashboard (track W/L, win rate automat)

Alte tooluri: alerte TradingView pentru no-wick candles (nu stă pe chart, primește notificări).

---

## 11. Rezultate revendicate vs. Realitate

| Claim | Context |
| --- | --- |
| 90% win rate | DOAR pe A-setups (trend clar confirmat); media reală e mai mică |
| $40K/lună | Cont live personal; media lui ~$20K/lună |
| 30 conturi funded trecute într-o lună | De la comunitatea lui/studenți |
| "90% dar am pierdut $4.500 într-o săptămână" | Titlu propriu al unui clip — chiar el arată pierderile |

**⚠️ Notă critică:** Win rate-ul de 90% NU e garantat. El însuși spune: "if you can't manage your risk, even my 90% win-rate strategy will not help you." Cifrele lui sunt din backtest-urile proprii, neverificate independent. **Backtest-ează singur înainte să riști bani reali.**

---

## 12. Plan de Acțiune pentru Noi (Sabin, Stefan, Nicolas)

- [ ] Instalează pe TradingView: indicatorul "omarnowick" (open-source) + X Ghost wickless candles
- [ ] Setează feed-ul pe **OANDA** pentru toate perechile analizate
- [ ] Backtest manual: minimum 100 de trade-uri pe USDCHF + GBPUSD, 15min, jurnal în `Research/`
- [ ] Cont demo/prop firm simulator 30 de zile înainte de bani reali
- [ ] Decideți împreună: ce % riscăm, ce perechi tradeăm fiecare
- [ ] Discutați în [[Chat]] deciziile de echipă

## Surse

- Curs complet 5 ore: https://www.youtube.com/watch?v=RslG-JI61M8
- Reguli actualizate + backtest (apr 2026): https://www.youtube.com/watch?v=vlk8CermPfQ
- Rules, Entries & Examples: https://www.youtube.com/watch?v=2LpRJTbrdF4
- Market Structure: https://www.youtube.com/watch?v=c_E-uMWszL4
- Indicator TradingView: https://www.tradingview.com/script/yTrRQHtf-omarnowick/
- Playbook PDF: caută "Playbook by Omarnowick" pe Scribd
- FX Replay documentare: https://fxreplay.com/strategies/bard-fx-compensation-play-nowick-strategy
