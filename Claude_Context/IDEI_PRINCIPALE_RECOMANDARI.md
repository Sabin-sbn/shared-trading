# IDEI PRINCIPALE — RECOMANDĂRI PENTRU PARAMETRIZAREA BOTULUI

> Fișier separat de repopack. Conține combinarea ideilor din notele din vault:
> `2_Wiki/Inbox/Notari de la Analiza Imagini` + `2_Wiki/Inbox/Ideei noi strategie`.
> Sunt directivele principale ale userului pentru Claude (research + parametri).

---

## 1. Sursele indicatorilor TradingView → extragerea parametrilor de identificare

Trimite lui Claude sursele de cod pentru fiecare indicator din TradingView ca să scoată **parametrul de identificare** la:

- MSS / BOS
- FVG
- Order Block
- Lichiditate (sweep)
- Higher High, Lower High, Lower Low, Higher Low

Indicatorii deja cunoscuți și folosiți:

- **MTF BOS & MSS** — avea `swing_lenght` de 7
- **Order Block Finder (Experimental) by wugamlo** — dacă găsești ceva mai accurat, se poate implementa pe acela

Sursele Pine Script sunt incluse în repopack (`Multi Timeframe Break of Structure(BOS) & Market Structure Shift(MSS)` + `study("Order Block Finder")`).

## 2. rr_ratio — plajă, NU valoare fixă

**Concluzie:** `rr_ratio` nu e o singură valoare fixă (2.0), ci o **plajă 2.0–2.5**, cu 2.0–2.01 și 2.44 confirmate exact. Nu codifica "2R" literal — folosește un interval.

La primele tradeuri de backtest era 2RR fix, dar apoi jurnalul a primit coloane suplimentare:

- **Max RR possible** — prețul maximal ce putea fi atins la trade înainte să scadă la BE sau SL, în ziua aceea, după entry
- **Max Pips Drawdown / Drawdown pips max before SL** — căderea prețului în drawdown în pips; exemplu: SL pips = 20, dar max pips în drawdown = 8

## 3. Semnificația coloanei "Pips" din jurnal

Pips ca și coloană de la jurnal = **stop loss în pips**.

## 4. Deep research cerut expres (Claude face research-ul)

Userul dă sursele codului pentru parametri, dar Claude trebuie să facă și **deep research propriu**, cel mai accurat, pentru TOȚI parametrii: FVG, OB, lichiditate, MSS, BOS etc. — nu doar ce iese din codul indicatorilor.

## 5. Regula re-liquidation pentru Modelul 1 (Trend Follower)

La modelul de trend follower e bun să fie **nicio re-liquidare în apropiere** ca să iei un trade de trend follower. Dacă este o re-liquidare apropiată, piața va veni împotriva ta — exemplu: iei un trade bearish și vine o re-liquidare apropiată, prețul vine împotriva ta și pierzi trade-ul. Dar dacă se face încă un MSS când vine ea, se vor forma **3 MSS-uri** și trendul se va schimba — și atunci intri în alt trade (Model 2).

---

## Ce are Claude de făcut cu aceste recomandări

1. Extrage din sursele Pine (în repopack) definițiile matematice exacte + parametrii de detectare per concept.
2. Completează cu deep research extern cel mai accurat pentru fiecare indicator/parametru.
3. Leagă totul de descoperirile din cele 129 imagini (`SINTEZA_FINALA_Toate_Descoperirile.md`, în repopack).
4. Rezultatul așteptat: set obiectiv de parametri per indicator, gata pentru grid/walk-forward pe cele două modele.
