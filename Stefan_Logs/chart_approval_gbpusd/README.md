# 📊 GBPUSD — Visual Approval Chart + Pipeline

> Instrument vizual de **aprobare a strategiilor** NO-Wick pe GBPUSD, perechea noastră principală.
> Tot echipa (Stefan / Sabin / Nicolas) poate deschide chart-ul, desena setup-uri și da verdict
> TAKE/SKIP — apoi analizăm obiectiv markerii. Pune aici **aprobarea ta vizuală la strategii diferite**.

> ℹ️ **Actualizat 01 Sep 2026:** am înlocuit varianta „GBPUSD 2026" cu chart-ul **normal** `gbpusd_draw.html`
> (cel mai actual, fără datele 2025-2026 complete care dădeau probleme). Pipeline-ul folosește acum
> doar fereastra **Mai – Iul 2026**, exact perioada reală de forward-test.

## ⚡ Cum deschizi chart-ul (2 secunde)

Deschide `gbpusd_draw.html` **direct în browser** (dublu-clic). Merge pe `file://` din Chrome/Edge.
Dacă stocarea locală e blocată (Firefox pe file://), folosește „Export JSON" când termini și încarcă-l după.

Chart-ul încarcă datele singur din `gbpusd_ohlc.json` (M15 + M1).
**Nicio instalare, doar browser.**

### Comenzi de bază
- `V` select / `B` LONG / `S` SHORT / `L` linie / `P` pen / `R` zonă / `H` h-linie / `N` notă
- Shift+drag = măsură în pips · Scroll = zoom la cursor · tastele `+1/+10/+60` dezvăluie viitorul (Lookahead OFF by default)
- Butonul „👻 Ghost" pune LONG/SHORT pe semnalele No-Wick din zona vizibilă (referință AI)
- Butonul „🤖 Bot" = backtest cu config-ul botului pe tot istoricul
- Butonul „Raport" = finalizează sesiunea (TAKE vs SKIP, WIN/LOSS, filtre)

### Perioada
GBPUSD.pro · M15 · **01 Mai – 31 Iul 2026** (perioada în care avem date reale de forward-test).

---

## 🎯 Cum folosești pentru VISUAL APPROVAL (hibrid uman-bot)

Asta e **calea de fund a proiectului** (singura cu PF real dovedit). Ideea:

1. **Desenezi un setup** (LONG/SHORT) când *tu* ai vedea o intrare No-Wick validă, cu SL/TP.
2. În panoul adnotării (v7.57) alegi **PASS / SKIP + motiv** — fix, nu liber:
   - **PASS** = aș intra pe setup-ul ăsta (edge vizual clar)
   - **SKIP** = aș sări, dar e aproape / ex. filtru de zi/oră (zi/lună/weekend, sesiune slabă, news)
3. La final apeși **Export JSON** → salvezi fișierul.
4. Rulezi `analyze_markers.py` pe JSON → primești features + outcome (win/loss la RR1 în 12h).

**Țintă: 100+ adnotări** înainte să tragem concluzii statistice (la <30 = zgomot).

### Ce fac datele pe care le aduni
- `analyze_markers.py` extrage per-marker: tip candelă/body, potrivire No-Wick, sesiune UTC (bucket), zi, distanța la swing 50, break de structură, trend EMA, + outcome (MFE/MAE, win/loss/ambiguous la RR1 în 12h).
- Le combinăm cu filtrele cunoscute (zi/oră/sesiune) → ipoteze de nivel fin per-trade → **biblioteca de filtre** (Goal 1 din plan).

> Notă (onest): desenele sunt **outcome-visible** (desenezi și vezi ce a urmat). Analyze_markers.py e pentru
> **feedback și feature-mining**, NU pentru validare pură. Test/retest blind se face separat (Partea B).

---

## 🔧 Pipeline de rulare (pentru dev / regenerare)

Toate scripturile folosesc căi relative la folderul propriu (`os.path.dirname(__file__)`), deci merg din
orice loc, cât timp fișierele stau împreună.

### 1. Regenerare chart HTML (după ce editezi cod/date)
```powershell
cd Stefan_Logs/chart_approval_gbpusd
python build_chart_html.py
```
→ rescrie `gbpusd_draw.html` din `gbpusd_pro_m15_2026-05_07.csv` (M15) + `gbpusd_pro_m1_2026-05_07.csv` (M1).
Apoi regenerează `gbpusd_ohlc.json` / `gbpusd_ohlc.js` (datele separate încărcate de chart).

### 2. Analiza markerilor desenați (după ce toți au exportat JSON)
```powershell
python analyze_markers.py gbpusd_markers_stefan.json
python analyze_markers.py gbpusd_markers_sabin.json
...
```
→ scrie `marker_analysis.csv` + raport pe stdout (No-Wick match, sesiune v2 OK %, outcome RR1).
Fiecare membru exportă JSON-ul lui; îi analizăm separat ca să comparăm **acordul inter-rater**.

---

## 📁 Conținutul folderului

| Fișier | Ce e | Necesar la deschidere? |
|---|---|---|
| `gbpusd_draw.html` | chart-ul interactiv | da (deschizi ăsta) |
| `gbpusd_ohlc.json` | datele M15+M1, self-contained | da (încărcat automat) |
| `gbpusd_ohlc.js` | aceleași date (fallback pentru `file://`) | da (fallback) |
| `build_chart_html.py` | generatorul HTML + datele OHLC | nu (doar regenerare) |
| `analyze_markers.py` | analiza markerilor desenați | nu (rulezi după export) |
| `gbpusd_pro_m15_2026-05_07.csv` | datele M15 Mai–Iul 2026 (sursa build + analyze) | nu (doar regenerare) |
| `gbpusd_pro_m1_2026-05_07.csv` | datele M1 Mai–Iul 2026 (sursa build) | nu (doar regenerare) |
| `profiles/gbpusd_draw.profile.json` | profilul default (markeri goi, settings) | nu (fallback) |

---

## ⚠️ Reguli de echipă (ca să nu stricăm treaba)

1. **Fiecare adnotează doar pe profilul lui** (export/import JSON la nevoie) — nu suprascrie fișierele altora.
2. **Nu edita `gbpusd_ohlc.json`** (e datele brute) — dacă vrei altă perioadă, regenerează.
3. **Nu regenerezi `build_chart_html.py` decât dacă schimbi cod/date** — chart-ul funcțional e deja compilat.
4. Când aduni adnotări: **outcome-visible e ok pentru feature-mining**, validatezi separat blind.
5. Commit doar `*.json` exportați + eventual profile/date noi, NU suprascrie HTML-ul altuia.

---

*Parte din `shared-trading`. Chart + pipeline exportate din SecondBrain (vault), folder `nowick-strat-clean/_charts/`.*
