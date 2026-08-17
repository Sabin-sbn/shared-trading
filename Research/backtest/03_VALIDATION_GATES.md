# 03 — Gates de Validare (obligatorii)

> Un config nu intră live dacă nu trece toate gate-urile relevante, indiferent cât de promițător pare. Verifică-le înainte de orice optimizare/testare.

## Gate 1 — Walk-Forward: minim 3/4 ferestre pozitive

Un parametru/config nou trebuie să bată baseline-ul pe **minim 3 din 4 ferestre** walk-forward (6 luni fiecare, train → test). 2/4 = instabil = nu intră.

- **Ferestre standard:** Iul–Dec 2024, Ian–Iun 2025, Iul–Dec 2025, Ian–Iun 2026.
- **"Bate"** = WR și/sau expectancy mai bune decât baseline-ul pe fereastra de TEST.

## Gate 2 — Eșantion minim: 500 trade-uri per config

Minimum **500 trade-uri completate** (win+loss) pe perioada de test. Sub prag, rezultatul nu e statistic suficient.
- 500 trade-uri @ WR 60% → interval de încredere ±4.3pp.
- 100 trade-uri → ±9.6pp (prea larg).
- **N < 100 = zgomot, nu trage concluzii.**

## Gate 3 — Monte Carlo: sub 5% breach rate

La **5,000 simulări** bootstrap (0.5%/trade, $10k), breach-ul limitelor prop-firm (ex: 10% MaxDD) trebuie să fie **sub 5%**. Peste 5% = respins.

## Gate 4 — Blind test: delta WR train/blind sub 15pp

Diferența dintre WR pe TRAIN și WR pe o fereastră complet nevăzută (never used în development) ≤ 15 puncte procentuale.

| Delta WR | Verdict |
|----------|---------|
| 0–5pp | Excelent |
| 5–10pp | Bun |
| 10–15pp | Acceptabil, investighează |
| > 15pp | **RESPINS — overfitting** |

## Gate 5 — Grid boundary: extinde dacă optimul e la margine

Dacă un parametru optim cade exact la marginea grid-ului, **extinde grid-ul** în direcția aia și retestează. Un optim la margine nu e optim — e o limită artificială.

## Gate 6 — Sursa de date: specifică fișierul explicit

Orice rezultat trebuie să spună **exact ce fișier** de trade-uri a folosit. Nu "JSON-urile din folderul X" — nume explicit.

## Gate 7 — Fără factori arbitrari

Nicio constantă fără justificare matematică. `×1.5`, `prag 2.0` fără o propoziție care explică de unde vine = bug potențial.
- **Interzis:** `score = Sharpe * 0.7 + MaxDD * 0.3` (ponderi necalibrate).
- **Permis:** `risk_per_trade = 0.005` (Fractional Kelly, din policy de risc).

## Gate 8 — Maxim 1–2 parametri liberi per rundă

Nu testa mai mult de 1–2 parametri noi per rundă. Restul se fixează din config-ul anterior. Grid search în 3+ dimensiuni produce combinații exponențiale care se overfitează.

## Checklist pre-live

- [ ] Gate 1: 3/4 ferestre walk-forward pozitive
- [ ] Gate 2: ≥ 500 trade-uri per config
- [ ] Gate 3: Monte Carlo sub 5% breach
- [ ] Gate 4: blind test delta WR ≤ 15pp
- [ ] Gate 5: niciun parametru la marginea grid-ului
- [ ] Gate 6: sursa de date specificată explicit
- [ ] Gate 7: nicio constantă arbitrară
- [ ] Forward test pe demo separat, minim 2 săptămâni
- [ ] Risc ≤ 0.5% per trade
