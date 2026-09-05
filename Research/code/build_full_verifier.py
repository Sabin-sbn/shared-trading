"""
Genereaza gbpusd_m1_verifier.html cu datele GBPUSD 2024-2026 embedded.
Butonul "📂 Tot CSV-ul…" incarca automat datele GBPUSD, fara file picker.
Rulare: python build_full_verifier.py
"""
import os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(BASE, '..', '..'))
HTML_SRC = os.path.join(BASE, 'gbpusd_m1_verifier.html')
CSV_PATH = os.path.join(REPO, 'Data', 'Forex_M1_2Y', 'GBPUSD_M1_OANDApro_2024_2026.csv')

if not os.path.exists(CSV_PATH):
    print(f'CSV nu a fost gasit: {CSV_PATH}'); sys.exit(1)

print(f'Citesc HTML: {HTML_SRC}')
with open(HTML_SRC, 'r', encoding='utf-8') as f:
    html = f.read()

print(f'Citesc CSV: {CSV_PATH} ({os.path.getsize(CSV_PATH)/1024/1024:.1f} MB)')
with open(CSV_PATH, 'r', encoding='utf-8') as f:
    csv_data = f.read()

# Injectam constanta GBPUSD_EMBEDDED imediat dupa linia WINDOWS (inainte de chart_math.js)
embed_js = f'\nconst GBPUSD_EMBEDDED = `{csv_data}`;\n'
MARKER = '// ================= chart_math.js'
if MARKER in html:
    html = html.replace(MARKER, embed_js + '\n' + MARKER)
    print(f'Injectat GBPUSD_EMBEDDED ({len(csv_data)} caractere)')
else:
    print('EROARE: marker chart_math.js negasit in HTML'); sys.exit(1)

# Modificam handler-ul csvBtn: auto-load din GBPUSD_EMBEDDED daca exista
OLD = "document.getElementById('csvBtn').addEventListener('click', ()=>{ document.getElementById('csvFile').click(); });"
NEW = """document.getElementById('csvBtn').addEventListener('click', function(){
  // auto-load GBPUSD embedded (build_full_verifier.py) — fallback la file picker
  if (typeof GBPUSD_EMBEDDED !== 'undefined' && GBPUSD_EMBEDDED){
    try {
      const bars = parseOandaCsv(GBPUSD_EMBEDDED);
      if (!bars.length){ document.getElementById('csvFile').click(); return; }
      setCustom({symbol: 'GBPUSD '+bars[0].t.slice(0,10)+' → '+bars[bars.length-1].t.slice(0,10)+' ('+bars.length.toLocaleString('en-US')+' bare · date OANDA 2024-2026)', bars: bars}, false);
    } catch(err){ document.getElementById('csvFile').click(); }
  } else {
    document.getElementById('csvFile').click();
  }
});"""
if OLD in html:
    html = html.replace(OLD, NEW)
    print('Handler csvBtn actualizat (auto-load GBPUSD)')
else:
    print('WARNING: handler csvBtn vechi negasit — probabil deja actualizat')

# Scriem outputul (suprascriem fisierul)
with open(HTML_SRC, 'w', encoding='utf-8') as f:
    f.write(html)

sz = os.path.getsize(HTML_SRC) / 1024 / 1024
print(f'GATA! Output: {HTML_SRC} ({sz:.1f} MB)')
print('Acum copieaza peste celelalte 2 locatii (cold-context, Desktop).')
