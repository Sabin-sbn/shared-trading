# 📊 GBPUSD — Visual Approval Chart + Pipeline (TEMPLATE)

> Instrument vizual de **aprobare a strategiilor** NO-Wick pe GBPUSD, perechea noastră principală.
> Acesta e un **template funcțional, fără date** — fiecare membru (Stefan / Sabin / Nicolas) își pune
> **datele lui** de chart și își vizualizează **tranzacțiile lui custom** direct pe chart.

> ℹ️ **Template neutru (actualizat 01 Sep 2026):** am scos toate datele reale (OHLC, CSV, profile, tranzacții).
> A rămas doar codul funcțional + pipeline-ul. Fiecare își completează cu propria sursă de date.

## 🔧 Cum îți pui DATELE TALE (pași, o singură dată)

Chart-ul e generat din datele tale. Rulezi `build_chart_html.py` pe fișierul tău CSV și îți apare
propriul chart încărcat cu datele tale.

### 1. Pregătește datele tale (CSV, format OHLC)
Creează un CSV `gbpusd_pro_m15_<perioada>.csv` cu coloanele:
`time,open,high,low,close,tick_volume` (time = timestamp Unix secunde).
Poți avea și `gbpusd_pro_m1_<perioada>.csv` (M1) — dacă lipsește, chart-ul merge doar pe M15.

### 2. Editează `build_chart_html.py` (2 linii)
Deschide scriptul și schimbă aceste două căi cu numele fișierelor tale:
```python
SRC = os.path.join(HERE, "gbpusd_pro_m15_2016-05_07.csv")   # ← fișierul tău M15
SRC_M1 = os.path.join(HERE, "gbpusd_pro_m1_2016-05_07.csv") # ← fișierul tău M1 (opțional)
```

### 3. Rulează generatorul
```powershell
cd Stefan_Logs/chart_approval_gbpusd
python build_chart_html.py
```
→ generează în același folder: `gbpusd_draw.html` + `gbpusd_ohlc.json` + `gbpusd_ohlc.js`.

### 4. Deschide chart-ul
Deschide `gbpusd_draw.html` **direct în browser** (dublu-clic). Merge pe `file://` din Chrome/Edge.
Chart-ul încarcă singur datele tale din `gbpusd_ohlc.json` (sau `.js` ca fallback pentru `file://`).

---

## 🎯 Vizualizează-ți TRANZACȚIILE CUSTOM pe chart

După ce ai chart-ul cu datele tale, poți desena și marca orice:
- `V` select / `B` LONG / `S` SHORT / `L` linie / `P` pen / `R` zonă / `H` h-linie / `N` notă
- Shift+drag = măsură în pips · Scroll = zoom la cursor · `+1/+10/+60` dezvăluie viitorul (Lookahead OFF)
- Butonul „👻 Ghost" pune LONG/SHORT pe semnalele No-Wick din zona vizibilă (referință AI)
- Butonul „🤖 Bot" = backtest cu config-ul botului pe tot istoricul
- Butonul „Raport" = finalizează sesiunea (TAKE vs SKIP, WIN/LOSS, filtre)
- **Export JSON** / **Import JSON** — îți salvezi/încarci desenele și tranzacțiile tale în protocol propriu.

**Tranzacțiile tale custom** (PASS/SKIP + motiv) se salvează în JSON și pot fi analizate.

---

## 📈 Analiza desenelor și tranzacțiilor tale

După ce desenezi, exportă JSON-ul și rulezi:
```powershell
python analyze_markers.py gbpusd_markers_<numele_tau>.json
```
→ scrie `marker_analysis.csv` + raport pe stdout (No-Wick match, sesiune, outcome RR1).
Fiecare membru exportă JSON-ul lui; îi analizăm separat ca să comparăm **acordul inter-rater**
(fiecare își vizualizează și își pune propriile date/decizii).

---

## 📁 Conținutul folderului (stare template)

| Fișier | Ce e | Necesar? |
|---|---|---|
| `build_chart_html.py` | generatorul chart-ului + datelor OHLC din CSV | da (îți faci propriul chart) |
| `analyze_markers.py` | analiza markerilor/tranzacțiilor desenați | da (după export) |
| `README.md` | acest ghid | da |
| `gbpusd_draw.html` | chart-ul final — **generat de tine cu datele tale** | da (după rulare build) |
| `gbpusd_ohlc.json` / `.js` | datele tale compilate — generate de build | da (după rulare build) |
| `profiles/` | aici îți pui profilul tău (JSON cu desene/tranzacții) | opțional |

> ⚠️ Charter-ul `.html`, OHLC-ul și CSV-urile **NU sunt incluse** (sunt datele fiecăruia).
> Pe GitHub rămâne doar codul — fiecare își completează local.

---

## ⚠️ Reguli de echipă

1. **Nu suprascrie datele/profilul altuia** — fiecare are propriul CSV/OHLC/profil, în propriul folder.
2. **Nu edita `gbpusd_draw.html` / `gbpusd_ohlc.json` direct** — regenerează din propriul CSV cu `build_chart_html.py`.
3. Commit pe repo doar **cod + README**, NU datele reale de piață (CSV-uri mari, OHLC, tranzacții).
4. Dacă vrei să-ți împărtășești o analiză, salvezi ca `Stefan_Logs/` sau `Nicolas_Logs/` (rezumat), nu datele brute.

---

*Template funcțional. Parte din `shared-trading` — fiecare membru își vizualizează propriile date de chart și tranzacții.*
