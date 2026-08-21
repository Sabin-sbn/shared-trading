# 04 — Lecții învățate (greșeli care au costat bani)

> Fiecare lecție de aici a costat timp și bani reali. Citește-le ca pe o listă de "ce să nu faci".

## Greșeli care costă bani

1. **Dynamic lot sizing fără validare** — lotul dinamic amplifică pierderile pe semnale slabe. Nu activa nicio schimbare de risk fără 2+ săptămâni de forward test.
2. **Config never validated** — o valoare care "arată bine" dar n-a văzut date unseen nu există. Orice config trece prin walk-forward.
3. **Optimizare în 5 dimensiuni simultan** — 8,250 combinații care se overfitează pe granițe. Maxim 1–2 parametri liberi per rundă.
4. **Safety features netestate** — dacă circuit breaker-ul nu e apelat nicăieri, nu ai plasă de siguranță. Testează daily loss limit + consecutive loss limit înainte de live.
5. **Backtest pe mid, nu bid/ask** — gap sistematic. Modelează bid/ask.
6. **Prea multe versiuni de bot simultan** — 4 boți pe 4 conturi, fiecare cu config diferit = greu de identificat cauza. **Consolidează.**
7. **CSV corruption** — la producție folosește SQLite, nu CSV.

## Greșeli de proces

8. **Căutarea "filtrului magic"** — 10 filtre testate pe rând (oră, zi, ADX, ATR, range, sezonalitate, corelație, chop...), toate null sau negative. Nu există filtru magic. Căutarea lui e overfitting mascat.
9. **Optimizare pe pips, nu pe % profit** — pips brut ignoră SL, risc, drawdown. Scorează mereu prin % profit + MaxDD.
10. **Teste pe tot istoricul (fără train/test)** — orice "câștigător" găsești e suspect. Orice optimizare se validează pe date unseen (walk-forward minim 4 ferestre).

## Ce a mers bine

- **Trailing stop** — primul feature adăugat prin workflow complet: semnal în MFE/MAE → simulare bar-cu-bar → walk-forward 4 ferestre → Monte Carlo → verificare mecanism → implementare ca opțiune separată.
- **Walk-forward pe 4 ferestre** — metoda standard. Dacă nu bate baseline-ul pe 3/4, nu intră.
- **Monte Carlo bootstrap** — îți spune dacă profitul e noroc de ordine sau structural.
- **Per-pair independent testing** — ce merge pe GBPJPY nu merge pe AUDUSD.

## Reguli de aur (neschimbate)

1. Nu adaugi parametri noi fără walk-forward pe date unseen.
2. Orice schimbare = cont demo separat, minim 2 săptămâni.
3. Nu crești riscul peste 0.5% până ai 100+ trade-uri live consistente.
4. După 7 pierderi consecutive: oprește-te. Nu forța.
5. Forward test-ul e sfânt. Nu modifica config-ul în timpul lui.
6. Când ai dubii: "Asta a fost validat pe date unseen?"
7. Backtest-ul e orientativ. Live-ul e adevărul.
8. Dacă ceva "arată prea bine ca să fie adevărat", probabil e overfitting.

> **TL;DR:** "Nu schimba strategia. Schimbă doar când și cum intri." — filtrarea (când/cum) a ridicat WR 52% → 72%, nu schimbarea semnalului de bază.
