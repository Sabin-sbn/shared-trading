# Cum descarci singur datele M1 (2 ani) de la broker

Datele din `../` (acest folder) au fost descărcate din **MetaTrader 5** printr-un EA mic
numit `ExportM1History`. Brokerul folosit la descărcare: **RoboForex** (cont demo e de ajuns,
nu costă nimic). Merge și cu orice alt broker MT5 care are istoric M1 (ex: FundingPips, IC Markets).

Nu trebuie să plătești nimic — cont demo la RoboForex îți dă acces la același istoric de piață.

---

## De unde sunt datele exact

| Fișier | Sursă | Acoperire |
| --- | --- | --- |
| `*_M1_2024_2026.csv` (7 perechi) | MT5 + ExportM1History EA | 2024-01-02 → 2026-06-30 |

Datele vin din **cache-ul M1 al MT5** (bare de 1 minut, OHLC + volum). MT5-ul sincronizează
istoricul de la broker, iar EA-ul exportă barele în CSV. Spread-ul nu e inclus (0).

---

## Pași (o singură dată)

### 1. Instalează MetaTrader 5 de la RoboForex

1. Mergi pe https://www.roboforex.com/ → descarcă MetaTrader 5 (platformă Windows).
2. Instalează-l (calea default: `C:\Program Files\MetaTrader 5\`).
3. Deschide MT5, creează un **cont demo** (File → Open an Account → demo) — nu trebuie bani.
4. Asigură-te că vezi prețuri live (Market Watch) pentru perechile dorite:
   EURUSD, USDCHF, AUDUSD, GBPUSD, AUDJPY, GBPJPY, USDJPY.
   Dacă vreo pereche nu apare: click dreapta în Market Watch → Symbols → caută-o → Add.

### 2. Copiază EA-ul în MT5

1. Copiază `ExportM1History_EA.ex5` în:
   `C:\Program Files\MetaTrader 5\MQL5\Experts\Advisors\`
   (sau folosește MetaEditor-ul MT5: File → Open Data Folder → MQL5\Experts\Advisors).
2. (Opțional) Sursa `ExportM1History_EA.mq5` e inclusă — dacă vrei să o compilezi singur,
   deschide-o în MetaEditor și apasă F7.

### 3. Instalează Python + pandas

1. Descarcă Python de la https://www.python.org/downloads/ (Windows installer).
2. La instalare bifează **„Add Python to PATH"**.
3. Deschide Command Prompt (Win+R → `cmd`) și rulează:
   ```
   pip install pandas
   ```

### 4. Rulează scriptul de download

1. Deschide Command Prompt în folderul `download_tools` (sau orice folder cu `download_m1.py`).
2. Rulează:
   ```
   python download_m1.py
   ```
3. Așteaptă: ~3-5 minute pentru toate cele 7 perechi (2 treceri per pereche).
4. Rezultatul: fișiere `{PERECHE}_M1_full.csv` în folderul `history_export\` (~52 MB fiecare,
   ~917.000 bare).

> **Notă:** MT5-ul trebuie să fie **închis** când rulezi scriptul (îl oprește el automat).
> Dacă ai MT5 instalat în altă locație, schimbă `TERMINAL` și `DIR` la începutul lui `download_m1.py`.

---

## Format fișier

```
Datetime,Open,High,Low,Close,Volume,Spread,RealVolume
2024-01-02 09:59:00,1.27353,1.27355,1.27323,1.27323,98,0,0
```

- `Datetime` = timpul serverului (fără conversie de timezone)
- `Open/High/Low/Close` = prețurile barei de 1 minut
- `Volume` = volumul
- `Spread` = 0 (nu e inclus în acest export)

---

## Dacă vrei și spread real / alte perioade

- Datele cu **spread real** vin din brokeri diferiți (ex: OANDA `.pro`) — întreabă-l pe
  Stefan, el are scripturi pentru asta.
- Pentru perioada 2026-07 → 2026-08 există exporturi separate FundingPips/RoboForex
  (vezi `3_System/history_export/` din vault-ul lui Stefan).
