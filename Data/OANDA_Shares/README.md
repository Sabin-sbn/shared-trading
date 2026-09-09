# OANDA Share CFDs — Data & Review Tool

> ⚠️ **IMPORTANT: deschide-l ÎN BROWSER, nu în Obsidian!**
> Obsidian NU execută JavaScript în viewer-ul lui pentru `.html` → pagina pare o „poză",
> butoanele nu reacționează, candelele nu se mișcă.
> **Dublu-clic pe `Deschide_Reviewer.bat`** (deschide automat browser-ul),
> sau dublu-clic pe `oanda_shares_reviewer.html` din Explorer.

## Setup minim (tot ce trebuie)

1. Dublu-clic pe `Deschide_Reviewer.bat` (sau pe `oanda_shares_reviewer.html`).
2. Gata — chart-ul de **GBPUSD M1 2024–2026** (917.216 bare) se încarcă automat
   din `gbpusd_m1_2024_2026.js` (datele vin din `Data/Forex_M1_2Y/GBPUSD_M1_2024_2026.csv`).

## Fișiere

| Fișier | Rol |
| --- | --- |
| `Deschide_Reviewer.bat` | **Deschide reviewer-ul în browser (dublu-clic)** |
| `oanda_shares_reviewer.html` | Chart interactiv + verdict Pass/Skip/Maybe |
| `gbpusd_m1_2024_2026.js` | Datele chart (41 MB) — încărcate automat de HTML |
| `build_gbpusd_data.py` | Reconstruiește JS-ul din CSV (`python build_gbpusd_data.py`) |
| `download_oanda_shares.py` | (opțional) Descarcă alte acțiuni/share CFDs de la OANDA |
| `csv_data/` | (opțional) CSV-urile descărcate de scriptul OANDA |

## Cum folosești reviewer-ul

- **Playback (mecanică Bar Replay):** la încărcare, lookahead e **ON** —
  viitorul e complet ascuns, o linie portocalie „🔒 cutoff" marchează ultima candelă dezvăluită
- **Play:** butonul `▶ Replay`, `Space` sau `Ctrl+Space` (cu mouse-ul pe chart) —
  dezvăluie candelele în continuare (180ms/candelă), oprește automat la sfârșit
- **Restart automat:** dacă apeși Play când s-a ajuns la final, replay-ul reia de la început
- **Accelerare:** ține `Space` apăsat = viteza crește (×2, ×4, … până la ×60)
- **Dezvăluire manuală:** butoanele `+1` / `+10` / `+60` din bara de jos
- **Reset:** butonul `⟲ Reset` — oprește play-ul și arată tot chart-ul de la început
- **Lookahead OFF/ON:** butonul 🔒/🔓 sau tasta `L`
- **Navigare:** taste `←` `→`, slider, sau butoanele din dreapta
- **Verdict:** `P` = PASS · `S` = SKIP · `M` = MAYBE
- **Salvare:** buton „Salvează verdictul" sau `Ctrl+Enter` (salvează + treci mai departe)
- Verdicturile se salvează în browser (localStorage, per instrument) și se pot **exporta JSON**
- Drag & drop un alt CSV peste pagină = schimbi instrumentul

### Scurtături taste (playback)

| Tastă | Acțiune |
| --- | --- |
| `Ctrl+Space` / `Space` | Play/Pause — dezvăluie candele. Funcționează DOAR cu mouse-ul pe chart (evită conflicte cu alte ferestre/aplicații) |
| `Space`/`Ctrl+Space` ținut | Accelerează playback-ul (până la ×60) |
| `L` | Lookahead ON/OFF (ascunde/dezvăluie tot) |
| `+1`/`+10`/`+60` | Butoane dezvăluire manuală (bara de jos) |
| `←` `→` | Navigare fereastră |

Fluxul recomandat: te uiți la fereastra dezvăluită → dai verdict (P/S/M) → `Space` ca să vezi
ce urmează fără lookahead → verdict nou pe fereastra următoare.

Fluxul recomandat: te uiți la fereastra dezvăluită → dai verdict (P/S/M) → `Space` ca să vezi
ce urmează fără lookahead → verdict nou pe fereastra următoare.

## Dacă vrei alt instrument

Fie tragi CSV-ul în browser, fie:

```bash
python download_oanda_shares.py   # (după ce setezi OANDA_TOKEN)
```

## Formate

CSV sursă: `Datetime,Open,High,Low,Close,Volume,Spread,RealVolume`
JS chart: `window.GBPUSD_M1_2024_2026 = [[epoch,o,h,l,c,v], ...]`