"""
Genereaza gbpusd_m1_verifier.html cu CELE 3 PERECHI inghetate (GBPUSD/EURUSD/USDJPY, 2024 -> 2026).

Datele = CSV OANDA .pro M1 din Data/Forex_M1_2Y/, comprimate gzip + base64 si decodate in browser
(DecompressionStream) la incarcare. Asa fisierul rămâne ~46 MB in loc de ~175 MB necomprimat,
ramanand un SINGUR fisier autonom (se deschide cu dublu-click) si urcabil pe GitHub.

Inlocuieste blocul `const PAIR_META = ...; const PAIRS_GZ = {...};` din HTML.
Rulare: python build_all_pairs_verifier.py
"""
import base64, gzip, json, os, sys

BASE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(BASE, '..', '..'))
HTML = os.path.join(BASE, 'gbpusd_m1_verifier.html')
DATA = os.path.join(REPO, 'Data', 'Forex_M1_2Y')
PAIRS = ['GBPUSD', 'EURUSD', 'USDJPY']

html = open(HTML, encoding='utf-8', newline='').read()
if 'const PAIRS_GZ = {' not in html:
    print('EROARE: nu gasesc "const PAIRS_GZ = {" in HTML'); sys.exit(1)

meta, parts = {}, []
for p in PAIRS:
    f = os.path.join(DATA, '%s_M1_OANDApro_2024_2026.csv' % p)
    if not os.path.exists(f):
        print('LIPSA: %s' % f); sys.exit(1)
    raw = open(f, 'rb').read().replace(b'\r\n', b'\n')
    txt = raw.decode('utf-8')
    b64 = base64.b64encode(gzip.compress(raw, 9, mtime=0)).decode('ascii')
    chunks = [b64[i:i + 200000] for i in range(0, len(b64), 200000)]
    parts.append('"%s": [\n%s\n]' % (p, ',\n'.join('    "%s"' % c for c in chunks)))
    lines = txt.rstrip('\n').split('\n')
    meta[p] = {'de': lines[1][:19], 'pana': lines[-1][:19], 'bare': len(lines) - 1}
    print('%s: csv %.1f MB -> gzip+base64 %.1f MB | %s -> %s (%d bare)'
          % (p, len(raw) / 1048576, len(b64) / 1048576,
             meta[p]['de'], meta[p]['pana'], meta[p]['bare']))

i = html.index('const PAIR_META = ')
j = html.index('};', html.index('const PAIRS_GZ = {')) + 2
block = ('const PAIR_META = %s;\nconst PAIRS_GZ = {\n%s\n};'
         % (json.dumps(meta, ensure_ascii=False).replace('\n', ' '), ',\n'.join(parts)))
open(HTML, 'w', encoding='utf-8', newline='').write(html[:i] + block + html[j:])
print('GATA: %s (%.1f MB)' % (HTML, os.path.getsize(HTML) / 1048576))
