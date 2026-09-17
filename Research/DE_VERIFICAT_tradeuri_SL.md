# DE VERIFICAT — trade-uri cu SL pe partea greșită

> Generat automat la 2026-09-17 din `Research/code/gbpusd_m1_verifier.html`.
> La aceste trade-uri SL-ul din jurnal nu e de partea corectă a entry-ului
> (LONG → SL sub entry; SHORT → SL deasupra). **Nu le-am modificat** — valorile
> corecte se citesc din pozele trade-urilor.

| # | Pereche | Direcție | Entry | SL în jurnal | SL pips | R | Rezultat | Problema |
|---|---|---|---|---|---|---|---|---|
| 40 | EURUSD | SHORT | 1.16082 | 1.16011 | 7.1 | -1.0 | LOSS | SL sub entry la SHORT |
| 49 | EURUSD | SHORT | 1.18224 | 1.18173 | 5.1 | -1.0 | LOSS | SL sub entry la SHORT |
| 108 | GBPUSD | SHORT | 1.23224 | 1.23224 | 0.0 | 2.0 | WIN | SL = entry (distanță 0) — imposibil pentru un trade real, dar e marcat WIN R=2 |
| 114 | GBPUSD | SHORT | 1.24142 | 1.24044 | 9.8 | -1.0 | LOSS | SL sub entry la SHORT |

## Impact

- **#108 (GBPUSD)**: SL = entry → trade-ul nu putea funcționa; e marcat totuși WIN cu R=2.
- **#114 (GBPUSD)**, **#40 + #49 (EURUSD)**: la SHORT SL-ul e sub entry — probabil entry și SL
  inversate la citirea din poză.
- Generatorul de setup-uri ignoră trade-urile cu SL = entry (filtrul de pips le exclude),
  deci **modelul antrenat din backtest nu e afectat**; pe chart însă poziția lor se desenează cu SL greșit.

## Cum se repară

1. Corectează entry/SL în `JOURNAL` din `Research/code/gbpusd_m1_verifier.html` (sau în tool).
2. Re-exportă cu butonul **Export CSV / Export JSON** din tool, sau cere o re-exportare,
   ca acest fișier și `jurnal_backtest_corectat.*` să rămână sincrone.
3. Șterge rândul corespunzător din tabelul de mai sus.
