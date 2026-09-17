# Indicatori & Lichiditate — ce folosim

Setul de indicatori pe care îi folosește strategia (și tool-ul de verificare). Toți sunt
**No-Wick / SMC-ICT**: structură (MSS/BOS), FVG, Order Block și lichiditate.

## 1. MSS / BOS — `MSS_BOS_TradingView.txt`

Indicatorul TradingView de structură (sursă). Regula, așa cum e implementată și în tool:

- se iau **pivoturi** (high/low locale) cu lungimea „swing" setată din slider (implicit 7 bare);
- când prețul **închide** peste ultimul pivot high → spargere în sus; sub ultimul pivot low → în jos;
- dacă spargerea e **în aceeași direcție** cu cea anterioară = **BOS** (continuare);
  dacă e **în direcția opusă** = **MSS** (schimbare de structură / reversare);
- linia se desenează de la bara swing-ului până la bara de rupere, la prețul pivotului.
- Culori în tool: verde = bullish, roșu = bearish.

## 2. Order Block — `OrderBlock_TradingView.txt`

Indicator de tip *wugamlo* (aceeași logică în `Research/code/structure_detector.py`):

- pentru fiecare bară se verifică candela de acum `periods+1` bare;
- **OB bullish**: candela de referință e roșie (close < open) și toate cele `periods` candele
  dintre ea și bara curentă sunt verzi → zona = [low-ul candelei, open-ul ei];
- **OB bearish**: candela de referință e verde și toate cele `periods` de după sunt roșii →
  zona = [open-ul candelei, high-ul ei];
- `periods` se setează din slider (implicit 5). Zona se extinde la dreapta, ca la TradingView.

## 3. FVG — Fair Value Gap

Model pe 3 candele:

- **bullish**: `high` din candela 1 < `low` din candela 3 → gap-ul = [high₁ , low₃];
- **bearish**: `low` din candela 1 > `high` din candela 3 → gap-ul = [high₃ , low₁];
- **completat (filled)** când o candelă ulterioară intră în gap (low ≤ bottom la bullish, high ≥ top la bearish);
- în tool: violet, iar **FVG-ul de la entry** e evidențiat mai tare și rămâne extins până la fill.
  Butonul „extins / doar candela" schimbă geometria (toate extinse vs. doar candela de formare).

## 4. Lichiditate — 4 tipuri (`Concepte_Lichiditate.md`)

Niveluri de lichiditate detectate pe M1, grupate pe tipuri (fiecare cu bifa lui în tool):

| Tip | Cum se detectează | De ce contează |
|---|---|---|
| **HOD / LOD** | High/Low of the Day, per zi calendaristică **UTC**, marcate pe M1 | nivelurile zilei — magnetul cel mai apropiat |
| **Major** | pivoturi pe **M15** (swing 3) | „cel mai bun tip" — niveluri de perioadă lungă |
| **Local** | pivoturi pe **M5** (swing adaptat din slider) | exact ca HOD/LOD, dar de la orice oră |
| **Minor** | zile de trend: low-ul zilei < low-ul zilei precedente cu >0,03% (sau high-ul peste) | trend-following — lichiditatea din zilele care sparg |

Reguli comune:

- **Culoare după parte:** buyside (deasupra, lichiditate de luat în sus) = galben; sellside = violet.
  Stiluri diferite pe tip (HOD/LOD linie continuă, Major dashed lung, Local dashed scurt, Minor dashed mediu).
- **Sweep = închidere (body-close), nu fitil.** Nivelul e considerat luat când o candelă **închide**
  dincolo de el. „Sweep pe fitil = slab" — regula validată în jurnal.
- **Re-liquidation:** a **doua** spargere a aceluiași nivel → se marchează cu ▴ pe chart
  (în jurnal apare ca `ind_lichiditate = "re-liquidation"`).
- Un nivel „local" care coincide cu unul „major" nu se dublează — rămâne cel major.
- Fără lookahead: fiecare nivel apare abia la confirmarea pivotului.

## 5. Cum arată în jurnal

Jurnalul corectat (`../jurnal_backtest_corectat.csv`) are coloanele de indicatori notate manual:

- `ind_MSS` — calitatea MSS-ului („Great", „First Mss good, Seco…")
- `ind_FVG` — calitatea FVG-ului („Good", „Mini fvg", „fvg entry…")
- `ind_lichiditate` — lichiditate (ex. „re-liquidation")
- `entry_model` (`em`) — cum a intrat („Great", „Good")
- plus `strategie` (`st`, ex. „Mss After Mss"), `setup` (`su`), `market` (`mc`).

## 6. Unde e implementarea

- **Python / backtest:** `../code/structure_detector.py` (pivoturi, BOS/MSS, lichiditate multi-timeframe).
- **În tool (JS):** funcțiile `detectBosMss`, `detectFvg`, `detectOrderBlocks`, `detectLiquidity`
  din `../code/gbpusd_m1_verifier.html`.
- Bifele din header-ul tool-ului pornesc/opresc fiecare strat: MSS/BOS, FVG, OB, Liq, HOD/LOD, Major, Local, Minor.
