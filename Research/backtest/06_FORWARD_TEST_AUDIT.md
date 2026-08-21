# 06 — Audit forward-test (evaluarea rezultatelor live)

> Cum auditezi rezultatele unui forward-test (demo/live) și decizi ce config e gata de funding. Modelul V2→V6.

## Inputs

CSV-uri de trade-uri cu coloane tip:
`#`, `Date_UTC`, `Pair`, `Dir`, `Entry_Exp`, `Entry_Real`, `Slip_p`, `SL`, `TP`, `Spread_Real`, `Spread_Conf`, `Result`, `Pips`, `Lot`, `Cumul_Pips`, `Cumul_DDpct`, `Notes`.

- `Result` ∈ OPEN / Win / Loss → contează doar Win/Loss.
- `Notes` conține `SL=..p TP=..p` (adevărul executat, nu config-ul documentat).

## Pași (paralelizează unde poți)

1. **Parse defensiv.** Custom split (nu DictReader naiv) — ascunde câmpul `Lot` lipsă din header, rânduri duplicate, gunoi binar. **Snapshot CSV-urile întâi** (boții scriu live).
2. **Stats per versiune × pereche:** n, W/L, WR, net pips, `$ = Pips × Lot × pip_value` (10 non-JPY / 6.5 JPY — convenția proiectului). MaxDD prin simulare de equity cu risc 0.5%, cronologic.
3. **Verifică execuția vs config.** Calculează `winR = Pips/SL` per pereche — TP_RR documentat poate diferi de ce a executat botul. **Nu ai încredere în config docs, ai încredere în `Notes`.**
4. **Dedup.** Conturile paralele pe ACELEAȘI semnale nu sunt teste independente; îmbinarea conturilor paralele umflă rezultatele (1 cont = 1 poziție la un moment dat).
5. **Audit cu agenți în paralel:** Verifier (recalculează), Skeptic (contestă: p-values, eșantioane mici corelate, ex-post selection), Debugger (integritatea CSV), Researcher (claim-uri externe), Strategist (recomandare).
6. **Funding gate** (FundingPips Phase 2, $10k, +8%, DD 5/10%, fără limită de timp): bootstrap MC 20k pe R-multiples reale (pips/SL). **Regula:** WR ≥ 60% la RR~1 + 0.5% risk → ~100% pass în ~15–18 zile, 0 breach; WR ~48% → ~31% ruină. Fundezi doar după **100+ trade-uri demo cu WR ≥ 60% menținut**.

## Reguli de aur din date

- **WR ≥ 60% la RR~1 + 0.5% risk** → Phase 2 trecut aproape sigur.
- **WR ~48%** → 1/3 șansă de ruină.
- Eșantion mic (N<100) = nu trage concluzii.
- Conturile paralele pe aceleași semnale = un singur test, nu mai multe.

## Output

Salvează raportul + CSV-ul de date + o intrare în jurnal. Dump-ează TOATE numerele în reply-ul final (nu doar rezumatul).
