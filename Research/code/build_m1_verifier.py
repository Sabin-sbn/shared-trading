"""
build_m1_verifier.py
=====================
Construieste un chart HTML INTERACTIV self-contained pe date M1 (1 minut) reale
pentru verificarea vizuala a detectorilor de structura (MSS/BOS/FVG), cu butoane
PASS/SKIP + comentariu + export de verdicte — fluxul Claude din SETUP_COPILOT.md,
dar standalone in browser (fara streamlit), la cererea utilizatorului.

Date M1 luate din history_export/{SYM}_M1_full.csv (UTC, coloane Datetime,OHLC).
Ferestrele vin din windows_to_verify.csv. Perechile fara date M1 (ex. NAS100) sunt
sarit, deoarece nu exista istoric M1 in folderul de date.

Rulare:
    python build_m1_verifier.py
-> scrie gbpusd_m1_verifier.html (self-contained, deschide-l in browser).

Detectorii MSS/BOS/FVG sunt reimplementati in JS in interiorul HTML-ului, identici
cu logica din structure_detector.py (find_pivots + Prev_Breakout_Type + FVG 3 candele),
astfel incat poti schimba swing_length/vizibilitatea chiar in browser.
"""

import json
import os
import re
from datetime import datetime

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
QUEUE_CSV = os.path.join(HERE, "windows_to_verify.csv")
DATA_FOLDER = os.path.join(HERE, "history_export")
OUT_HTML = os.path.join(HERE, "gbpusd_m1_verifier.html")

CONTEXT_MIN = 90          # bare M1 de context (inainte/dupa) ca detectorul sa aiba destule
MAX_BARS_PER_WINDOW = 2000  # plafon de siguranta


def load_m1(sym):
    p = os.path.join(DATA_FOLDER, "{}_M1_full.csv".format(sym))
    if not os.path.exists(p):
        return None
    df = pd.read_csv(p)
    df["Datetime"] = pd.to_datetime(df["Datetime"], utc=True)
    return df


def parse_trade_from_note(note):
    """Extrage din nota CSV: side (BUY/SELL), result (WIN/LOSS/—) si,
    daca apar, RR/SL/TP in puncte. Valorile de pret (entry/sl/tp) nu sunt
    cunoscute din CSV — le marchezi manual in comentariu. Returneaza dict."""
    note = note or ""
    n = note.upper()
    side = "BUY" if re.search(r"\bBUY\b", n) else ("SELL" if re.search(r"\bSELL\b", n) else None)
    result = "WIN" if re.search(r"\bWIN\b", n) else ("LOSS" if re.search(r"LOSS", n) else None)
    label = None
    m = re.search(r"(?:SL|STOP)\s*=\s*([\d.]+)\s*p", note, re.I)
    if m: label = "SL " + m.group(1) + "p"
    m2 = re.search(r"(?:TP|TAKE)\s*=\s*([\d.]+)\s*p", note, re.I)
    if m2: label = (label + " / " if label else "") + "TP " + m2.group(1) + "p"
    if not label:
        m3 = re.search(r"RR\s*=\s*([\d.]+)", n)
        if m3: label = "RR " + m3.group(1)
    return {"side": side, "result": result, "label": label,
            "entry": None, "sl": None, "tp": None}


def build_windows():
    if not os.path.exists(QUEUE_CSV):
        raise SystemExit("Lipseste {}".format(QUEUE_CSV))
    q = pd.read_csv(QUEUE_CSV, dtype={"date": str})
    windows = []
    missing = []
    for _, r in q.iterrows():
        sym = str(r["symbol"]).upper()
        date = str(r["date"]).strip()
        st = str(r["start_time"]).strip()
        en = str(r["end_time"]).strip()
        if not date or not st or not en:
            continue
        df = load_m1(sym)
        if df is None:
            missing.append((r["trade_id"], sym))
            continue
        s_dt = pd.Timestamp("{} {}:00".format(date, st), tz="UTC")
        e_dt = pd.Timestamp("{} {}:00".format(date, en), tz="UTC")
        ctx_s = s_dt - pd.Timedelta(minutes=CONTEXT_MIN)
        ctx_e = e_dt + pd.Timedelta(minutes=CONTEXT_MIN)
        w = df[(df["Datetime"] >= ctx_s) & (df["Datetime"] <= ctx_e)]
        if len(w) == 0:
            missing.append((r["trade_id"], sym))
            continue
        w = w.tail(MAX_BARS_PER_WINDOW)
        bars = [
            {
                "t": str(ts),
                "o": float(round(o, 5)), "h": float(round(h, 5)),
                "l": float(round(l, 5)), "c": float(round(c, 5)),
            }
            for ts, o, h, l, c in zip(w["Datetime"], w["Open"], w["High"], w["Low"], w["Close"])
        ]
        start_txt = w["Datetime"].iloc[0]
        end_txt = w["Datetime"].iloc[-1]
        windows.append({
            "id": str(r["trade_id"]),
            "symbol": sym,
            "window_start": "{} {}".format(date, st),
            "window_end": "{} {}".format(date, en),
            "note": str(r["note"]),
            "trade": parse_trade_from_note(str(r["note"])),
            "data_start": str(start_txt),
            "data_end": str(end_txt),
            "bars": bars,
        })
    return windows, missing


# --- Transpunere JS a detectorilor (aceeasi logica ca structure_detector.py) ----
# find_pivots + Prev_Breakout_Type (MSS/BOS) + FVG (3 candele).
JS_DETECT = r"""
// --- pivots (pivothigh/pivotlow) similar ta.pivothigh/pivotlow ---
function findPivots(vals, left, right, mode){
  const n = vals.length;
  const out = new Array(n).fill(null);
  for (let j=left; j<n-right; j++){
    const win = vals.slice(j-left, j+right+1);
    const center = vals[j];
    if (mode==='high'){
      if (center===Math.max(...win) && win.filter(x=>x===center).length===1) out[j]=center;
    } else {
      if (center===Math.min(...win) && win.filter(x=>x===center).length===1) out[j]=center;
    }
  }
  return out;
}

function detectBosMss(bars, swingLength){
  const n = bars.length;
  const highs = bars.map(b=>b.h), lows = bars.map(b=>b.l), closes=bars.map(b=>b.c);
  const ph = findPivots(highs, swingLength, swingLength, 'high');
  const pl = findPivots(lows, swingLength, swingLength, 'low');
  // structura: ultimul pivot high si low confirmat (index + pret) pentru nivelul rupt
  let phIdx=null, phPrice=null, plIdx=null, plPrice=null;
  let prevHigh=null, prevLow=null, highPresent=false, lowPresent=false, prevType=0;
  const events=[];
  for (let i=0;i<n;i++){
    if (ph[i]!=null){ prevHigh=ph[i]; highPresent=true; phIdx=i; phPrice=ph[i]; }
    if (pl[i]!=null){ prevLow=pl[i]; lowPresent=true; plIdx=i; plPrice=pl[i]; }
    if (highPresent && prevHigh!=null && closes[i]>prevHigh){
      const kind = prevType===1 ? 'BOS' : (prevType===-1 ? 'MSS' : null);
      if (kind) events.push({
        kind, direction:'bullish', i, price:prevHigh,
        // linie ORIZONTALA la nivelul rupt: de la bar unde s-a format swing-ul (phIdx)
        // pana la bar de rupere (i) — exact ca in TradingView (line.new x1=time[count], x2=End_High_Time)
        sx: phIdx, ex: i, sy: prevHigh, ey: prevHigh
      });
      prevType=1; highPresent=false;
    }
    if (lowPresent && prevLow!=null && closes[i]<prevLow){
      const kind = prevType===-1 ? 'BOS' : (prevType===1 ? 'MSS' : null);
      if (kind) events.push({
        kind, direction:'bearish', i, price:prevLow,
        // linie ORIZONTALA la nivelul rupt: de la bar unde s-a format swing-ul (plIdx)
        // pana la bar de rupere (i)
        sx: plIdx, ex: i, sy: prevLow, ey: prevLow
      });
      prevType=-1; lowPresent=false;
    }
  }
  return events;
}

function detectFvg(bars){
  const n = bars.length;
  const events=[];
  for (let i=2;i<n;i++){
    const c1h=bars[i-2].h, c1l=bars[i-2].l, c3h=bars[i].h, c3l=bars[i].l;
    if (c1h < c3l){ // bullish
      const top=c3l, bottom=c1h; let filled=false, fi=null;
      for (let j=i+1;j<n;j++){ if (bars[j].l<=bottom){filled=true;fi=j;break;} }
      events.push({kind:'FVG',direction:'bullish',i:i-1,top,bottom,filled,filledAt:fi});
    }
    if (c1l > c3h){ // bearish
      const top=c1l, bottom=c3h; let filled=false, fi=null;
      for (let j=i+1;j<n;j++){ if (bars[j].h>=top){filled=true;fi=j;break;} }
      events.push({kind:'FVG',direction:'bearish',i:i-1,top,bottom,filled,filledAt:fi});
    }
  }
  return events;
}

// --- Order Block (fidel wugamlo, Script_ob.txt din structure_detector.py) ---
function detectOrderBlocks(bars, periods){
  const n = bars.length;
  const events = [];
  const op = periods + 1;
  for (let i=op;i<n;i++){
    const close_ob = bars[i-op].c, open_ob = bars[i-op].o, close_1 = bars[i-1].c;
    if (close_ob===0) continue;
    const absmove = Math.abs(close_ob - close_1) / close_ob * 100;
    const relmove = absmove >= 0;
    // candelele dintre [i-periods .. i-1] => offsets 1..periods
    let up=0, down=0;
    for (let k=i-periods;k<i;k++){ if (bars[k].c>bars[k].o) up++; else if (bars[k].c<bars[k].o) down++; }
    if (close_ob < open_ob && up===periods && relmove){
      events.push({kind:'OB',direction:'bullish',i:i-op,top:open_ob,bottom:bars[i-op].l,avg:(open_ob+bars[i-op].l)/2});
    }
    if (close_ob > open_ob && down===periods && relmove){
      events.push({kind:'OB',direction:'bearish',i:i-op,top:bars[i-op].h,bottom:open_ob,avg:(bars[i-op].h+open_ob)/2});
    }
  }
  return events;
}

// --- Liquidity: 4 tipuri, teoria lui Rares (Trading Instituțional) ---
//   - HOD/LOD   : High/Low of the Day (marcate pe 1 min, per zi UTC)
//   - major     : puncte extreme pe M15 (perioadă lungă, "cel mai bun tip")
//   - local     : pivoți pe M5/M1 (puncte extreme, "exact ca HOD/LOD doar de la orice oră")
//   - minor     : uz de trend-following (zile de trend: low/high-uri extreme)
// Toate respectă no-lookahead: fiecare nivel apare abia la confirmarea pivotului,
// sweep/re-liquidation se verifică pe barele ulterioare M1.
function detectLiquidity(bars, swingLength){
  const n = bars.length, events = [], tolPct = 0.02;
  const highs = bars.map(b=>b.h), lows = bars.map(b=>b.l), closes = bars.map(b=>b.c);
  const tmin = Date.parse(bars[0].t)/60000;

  // ---- agregare M1 -> bare de `mins` minute (după t UTC) ----
  function agg(mins){
    const gs=[];
    for (let i=0;i<n;i++){
      const mi = Math.floor(Date.parse(bars[i].t)/60000/mins);
      const g = gs[gs.length-1];
      if (g && g.mi===mi){ g.idx1=i; if(highs[i]>g.h)g.h=highs[i]; if(lows[i]<g.l)g.l=lows[i]; g.c=closes[i]; }
      else gs.push({mi, idx0:i, idx1:i, o:bars[i].o, h:highs[i], l:lows[i], c:closes[i]});
    }
    return gs;
  }

  // pivoți pe date agregat -> nivele {price, i(M1), dir}
  function swingsAgg(gs, sw){
    const vh=gs.map(g=>g.h), vl=gs.map(g=>g.l);
    const ph=findPivots(vh,sw,sw,'high'), pl=findPivots(vl,sw,sw,'low');
    const out=[];
    for (let j=0;j<gs.length;j++){
      if (ph[j]!=null) out.push({price:ph[j], i:gs[j].idx0, dir:'buyside'});
      if (pl[j]!=null) out.push({price:pl[j], i:gs[j].idx0, dir:'sellside'});
    }
    return out;
  }

  const m15 = agg(15), m5 = agg(5);

  // candidat niveluri per tip.
  //   major: pivoți M15 cu swing_length=3 (exact ca detect_multi_tf_liquidity din
  //          structure_detector.py / files-3 Claude: `detect_pivots(htf, 3)`)
  //   local: pivoți M5, swing adaptat la slider (puncte extreme, "exact ca HOD/LOD
  //          doar de la orice oră" — teoria lui Rares)
  const cands = [];
  swingsAgg(m15, 3).forEach(c=>cands.push({price:c.price, i:c.i, dir:c.dir, type:'major'}));
  const swLoc = Math.max(2, Math.min(5, Math.round(swingLength/2)));
  swingsAgg(m5, swLoc).forEach(c=>cands.push({price:c.price, i:c.i, dir:c.dir, type:'local'}));

  // dedupe: dacă un nivel local coincide cu unul major același preț/zonă, păstrăm major
  function near(a,b){ return Math.abs(a-b) <= (a*b*tolPct/100) + 1e-9; }
  const candsDedup=[];
  for (const c of cands){
    const dupMajor = c.type==='local' && candsDedup.some(o=>o.type==='major' && o.dir===c.dir && near(o.price,c.price));
    if (!dupMajor) candsDedup.push(c);
  }

  // ---- HOD / LOD (per zi calendaristică UTC) ----
  const byDay={};
  for (let i=0;i<n;i++){
    const d=bars[i].t.slice(0,10);
    if (!byDay[d]) byDay[d]={hi:i,ho:highs[i],lo:i,ll:lows[i]};
    else { const dd=byDay[d]; if(highs[i]>dd.ho){dd.ho=highs[i];dd.hi=i;} if(lows[i]<dd.ll){dd.ll=lows[i];dd.lo=i;} }
  }
  for (const k in byDay){
    const dd=byDay[k];
    candsDedup.push({price:dd.ho, i:dd.hi, dir:'buyside',  type:'hodlod', day:k});
    candsDedup.push({price:dd.ll, i:dd.lo, dir:'sellside', type:'hodlod', day:k});
  }

  // ---- Minor (trend-following): în zile de trend negativ/pozitiv marchează
  //      low-urile / high-urile extreme (extindere față de ziua precedentă). ----
  // low-ul zilei < low-ul zilei precedente cu >0.03% => day low "extins" (trend down)
  {
    const keys=Object.keys(byDay).sort();
    let prevLow=null, prevHigh=null;
    for (const k of keys){
      const dd=byDay[k];
      const gapPct = 0.03;
      const extLow  = prevLow !== null && dd.ll < prevLow*(1-gapPct/100);
      const extHigh = prevHigh!== null && dd.ho > prevHigh*(1+gapPct/100);
      if (extLow)  candsDedup.push({price:dd.ll, i:dd.lo, dir:'sellside', type:'minor', day:k});
      if (extHigh) candsDedup.push({price:dd.ho, i:dd.hi, dir:'buyside',  type:'minor', day:k});
      prevLow = dd.ll; prevHigh = dd.ho;
    }
  }

  // ---- sweep + re-liquidation pe bare M1 ulterioare.
  //   Suficient și fidel: nivelul e spart când o candelă ulterioară ÎNCHIDE
  //   (body-close) dincolo de nivel — definiția validată în jurnalul de 143
  //   tranzacții ("sweep pe fitil = slab, body-close = valid"), aceeași pe care
  //   o folosește și Claude pentru major/local. a doua spargere = re-liquidation.
  for (const lv of candsDedup){
    let swept=null, sweptCount=0;
    for (let i=lv.i+1;i<n;i++){
      const hitB = lv.dir==='buyside' ? closes[i] > lv.price
                                      : closes[i] < lv.price;
      if (hitB){ sweptCount++; swept=i; if (sweptCount>=2) break; }
    }
    events.push({
      kind:'LIQ', type:lv.type, direction:lv.dir, i:lv.i, level:lv.price,
      day:lv.day||null, swept: swept, reSwept: sweptCount>=2
    });
  }

  // sortăm cronologic (după momentul formării nivelului)
  events.sort((a,b)=>a.i-b.i || a.level-b.level);
  return events;
}
"""

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title>Verificare M1 — MSS/BOS/FVG (GBPUSD + perechi forex)</title>
<style>
  :root{--bg:#0e1117;--panel:#161b22;--line:#30363d;--txt:#e6edf3;--muted:#8b949e;}
  *{box-sizing:border-box}
  body{margin:0;font-family:-apple-system,Segoe UI,Roboto,sans-serif;background:var(--bg);color:var(--txt)}
  header{display:flex;align-items:center;gap:12px;padding:10px 16px;background:var(--panel);border-bottom:1px solid var(--line);flex-wrap:wrap}
  header h1{font-size:16px;margin:0}
  header .sp{flex:1}
  select,button,input,textarea{background:#0d1117;color:var(--txt);border:1px solid var(--line);border-radius:6px;padding:6px 10px;font-size:13px}
  button{cursor:pointer}
  button.primary{background:#238636;border-color:#2ea043}
  button.warn{background:#9e6a03;border-color:#d29922}
  button.danger{background:#da3633;border-color:#f85149}
  button:hover{filter:brightness(1.1)}
  .bar{width:34px;height:20px;border-radius:4px;border:none;color:#fff;font-weight:700}
  .main{display:flex;gap:12px;padding:12px 16px}
  .left{flex:1;min-width:0}
  #chart{height:65vh;border:1px solid var(--line);border-radius:8px;background:#000;overflow:hidden;position:relative}
  .right{width:360px;flex-shrink:0}
  .card{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:12px;margin-bottom:12px}
  .card h2{font-size:13px;margin:0 0 8px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
  .events{max-height:220px;overflow:auto;font-size:12px}
  .events div{padding:4px 6px;border-bottom:1px solid var(--line)}
  textarea{width:100%;min-height:70px}
  .muted{color:var(--muted);font-size:12px}
  .badge{display:inline-block;padding:2px 8px;border-radius:10px;font-size:11px;font-weight:600}
  .b-green{background:#238636}.b-red{background:#da3633}.b-gray{background:#30363d}
  .note{font-size:12px;background:#0d1117;border-left:3px solid #58a6ff;padding:8px;border-radius:0 6px 6px 0}
  .legend{font-size:11px;display:flex;gap:12px;flex-wrap:wrap;margin-top:6px}
  .sw{display:inline-block;width:10px;height:10px;border-radius:2px;margin-right:4px;vertical-align:middle}
</style>
</head>
<body>
<header>
  <h1>Verificare vizuală M1 · MSS / BOS / FVG ▼</h1>
  <select id="winSel"></select>
  <span class="sp"></span>
  <label class="muted">MSS/BOS swing <span id="swVal">7</span></label>
  <input type="range" id="swing" min="3" max="15" value="7" style="width:90px">
  <label class="muted">OB <span id="obVal">5</span></label>
  <input type="range" id="ob" min="2" max="10" value="5" style="width:70px">
  <label class="muted"><input type="checkbox" id="showBOS" checked> MSS/BOS</label>
  <label class="muted"><input type="checkbox" id="showFVG" checked> FVG</label>
  <span class="muted" style="white-space:nowrap">
    <input type="radio" name="fvgMode" id="fvgExtend" value="extend" checked title="Opțiunea 1: toate FVG-urile extinse până la fill (ca acum)"><label for="fvgExtend">extins</label>
    <input type="radio" name="fvgMode" id="fvgShort" value="short" title="Opțiunea 2: doar pe candelă; singurul FVG de la entry e extins până la fill"><label for="fvgShort">doar candela</label>
  </span>
  <label class="muted"><input type="checkbox" id="showOB" checked> OB</label>
  <label class="muted"><input type="checkbox" id="showLIQ" checked> Liq</label>
  <label class="muted" title="High/Low of the Day — marcate pe 1 min, per zi UTC"><input type="checkbox" id="showHODLOD" checked> HOD/LOD</label>
  <label class="muted" title="Puncte extreme pe M15 (perioadă lungă)"><input type="checkbox" id="showLiqMajor" checked> Major</label>
  <label class="muted" title="Pivoți pe M5/M1 (puncte extreme)"><input type="checkbox" id="showLiqLocal" checked> Local</label>
  <label class="muted" title="Uz de trend-following (zile de trend)"><input type="checkbox" id="showLiqMinor" checked> Minor</label>
  <label class="muted"><input type="checkbox" id="showTrade" checked> Trade</label>
  <button class="primary" id="detectBtn">Recalculează</button>
</header>

<div class="main">
  <div class="left">
    <div id="chart"></div>
    <div class="legend">
      <span><span class="sw" style="background:#2ecc71"></span>MSS/BOS long</span>
      <span><span class="sw" style="background:#e74c3c"></span>MSS/BOS short</span>
      <span><span class="sw" style="background:#9c27b0;opacity:.35"></span>FVG</span>
      <span><span class="sw" style="background:#9e9e9e;opacity:.55"></span>OB</span>
      <span><span class="sw" style="background:#ffe082"></span>HOD/LOD</span>
      <span><span class="sw" style="background:#f0b90b"></span>Liq·Major↑</span>
      <span><span class="sw" style="background:#9b59b6"></span>Liq·Major↓</span>
      <span><span class="sw" style="background:#4fc3f7"></span>Liq·Local↑</span>
      <span><span class="sw" style="background:#7aa2f7"></span>Liq·Minor</span>
      <span class="muted">Tranzacție: <b id="tradeTag" style="color:#fff"></b></span>
    </div>
  </div>

  <div class="right">
    <div class="card">
      <h2>Fereastra activă</h2>
      <div id="winInfo" class="muted"></div>
      <div class="note" id="winNote"></div>
    </div>

    <div class="card">
      <h2>Evenimente detectate</h2>
      <div class="events" id="evList"></div>
    </div>

    <div class="card">
      <h2>Verdict</h2>
      <div style="display:flex;gap:8px;margin-bottom:8px">
        <button class="primary" data-v="PASS" style="flex:1;padding:10px">PASS ✓</button>
        <button class="danger" data-v="SKIP" style="flex:1;padding:10px">SKIP ✗</button>
        <button class="warn" data-v="NESIGUR" style="flex:1;padding:10px">Nesigur ?</button>
      </div>
      <textarea id="comment" placeholder="Comentariu (optional)"></textarea>
      <div style="display:flex;gap:8px;margin-top:8px">
        <button class="primary" id="saveBtn" style="flex:1">Salvează verdictul</button>
        <button id="exportBtn" style="flex:1">Export JSON</button>
      </div>
    </div>

    <div class="card">
      <h2>Verdicte salvate (acest browser)</h2>
      <div id="savedList" class="muted"></div>
      <button id="clearBtn" style="margin-top:6px;width:100%" class="danger">Șterge toate</button>
    </div>
  </div>
</div>

<script>
__JS_DETECT__
// ================= date (inglobate) =================
const WINDOWS = __WINDOWS_JSON__;

// ================= chart_math.js (funcții pure de calcul, fără DOM) ===========
function computeYRange(c, x0, x1, sl, tp, pf) {
  pf = pf == null ? 0.1 : pf;
  const i0 = Math.max(0, Math.floor(x0)), i1 = Math.min(c.length - 1, Math.ceil(x1));
  let yMin = Infinity, yMax = -Infinity;
  for (let i = i0; i <= i1; i++) { if (!c[i]) continue; yMin = Math.min(yMin, c[i].l); yMax = Math.max(yMax, c[i].h); }
  if (sl != null) { yMin = Math.min(yMin, sl); yMax = Math.max(yMax, sl); }
  if (tp != null) { yMin = Math.min(yMin, tp); yMax = Math.max(yMax, tp); }
  if (!isFinite(yMin) || !isFinite(yMax)) { yMin = 0; yMax = 1; }
  const p = (yMax - yMin) * pf;
  return [yMin - (p || 0.0001), yMax + (p || 0.0001)];
}
function makeXS(v, mL, pW) { return i => mL + ((i - v.x0) / Math.max(v.x1 - v.x0, 1)) * pW; }
function makeYS(yMin, yMax, mT, pH) { return p => mT + (1 - (p - yMin) / Math.max(yMax - yMin, 0.0001)) * pH; }
function fmtP(p, pip) { return p.toFixed(pip >= 0.01 ? 3 : 5); }
function fmtPi(d, pip) { return (d / pip).toFixed(1); }
function rMult(e, sl, dist) { if (sl == null || e == null) return null; var sd = Math.abs(e - sl); return sd > 0 ? dist / sd : null; }
function zAt(v, mf, f, n) { var r = v.x1 - v.x0, nr = Math.max(10, Math.min(n * 3, r * f)), md = v.x0 + mf * r; return { x0: md - mf * nr, x1: md + (1 - mf) * nr }; }
function pBy(v, dx, pW) { var r = v.x1 - v.x0, d = -(dx / pW) * r; return { x0: v.x0 + d, x1: v.x1 + d }; }
function fmtT(t) { if (t == null) return ''; var d = new Date(typeof t === 'number' ? t : t); if (isNaN(d.getTime())) return String(t); return String(d.getUTCHours()).padStart(2, '0') + ':' + String(d.getUTCMinutes()).padStart(2, '0'); }

// ================= Chart interactiv SVG (model Claude — pan/zoom/price tag) ==
const svgNS = 'http://www.w3.org/2000/svg';
let svgR = {}, Lyr = {};
const CW = 1100, CH = 550, mL = 56, mR = 74, mT = 26, mB = 26;
const pW = CW - mL - mR, pH = CH - mT - mB;
const vw = { x0: 0, x1: 1 };
let dragging = false, dX = 0, vx0 = 0, vx1 = 0;

function initChart() {
  var c = document.getElementById('chart'); c.innerHTML = '';
  svgR = document.createElementNS(svgNS, 'svg');
  svgR.setAttribute('viewBox', '0 0 ' + CW + ' ' + CH);
  svgR.setAttribute('width', '100%');
  svgR.style.cssText = 'display:block;background:#131722;user-select:none;cursor:grab;font-family:sans-serif;';
  c.appendChild(svgR);
  ['grid','fvg','ob','candles','breaks','liq','tradeLines','axis','priceTag'].forEach(function(n){
    var g = document.createElementNS(svgNS, 'g'); svgR.appendChild(g); Lyr[n] = g;
  });
  svgR.addEventListener('mousedown', function(e){ dragging=true; dX=e.clientX; vx0=vw.x0; vx1=vw.x1; svgR.style.cursor='grabbing'; });
  window.addEventListener('mousemove', function(e){ if(!dragging)return; var v=pBy({x0:vx0,x1:vx1},e.clientX-dX,pW); vw.x0=v.x0; vw.x1=v.x1; requestAnimationFrame(render); });
  window.addEventListener('mouseup', function(){ dragging=false; if(svgR)svgR.style.cursor='grab'; });
  svgR.addEventListener('wheel', function(e){ e.preventDefault(); var rect=svgR.getBoundingClientRect(); var mf=Math.max(0,Math.min(1,(e.clientX-rect.left-mL)/pW)); var zf=e.deltaY>0?1.12:0.89; var v=zAt(vw,mf,zf,currentBars.length); vw.x0=v.x0; vw.x1=v.x1; requestAnimationFrame(render); }, {passive:false});
}

function sv(tag, at, tx) {
  var e = document.createElementNS(svgNS, tag); for (var k in at) e.setAttribute(k, at[k]); if (tx != null) e.textContent = tx; return e;
}
function clr(g) { while (g.firstChild) g.removeChild(g.firstChild); }

function render() {
  var bars = currentBars, n = bars.length; if (!n) return;
  var yr = computeYRange(bars, vw.x0, vw.x1, tradeSl, tradeTp, 0.1);
  var yMin = yr[0], yMax = yr[1];
  var xs = makeXS(vw, mL, pW), ys = makeYS(yMin, yMax, mT, pH);
  var pip = 0.0001;
  var bw = Math.max((pW / Math.max(vw.x1 - vw.x0, 1)) * 0.62, 1);
  Object.values(Lyr).forEach(clr);

  // grid + axis
  for (var g = 0; g <= 5; g++) {
    var pr = yMin + (g / 5) * (yMax - yMin), y = ys(pr);
    Lyr.grid.appendChild(sv('line', {x1:mL,y1:y,x2:CW-mR,y2:y,stroke:'#ffffff14','stroke-width':1}));
    Lyr.axis.appendChild(sv('text', {x:CW-mR+6,y:y+4,'font-size':10,fill:'#787b86'}, fmtP(pr, pip)));
  }
  var nT = 6;
  for (var t = 0; t <= nT; t++) {
    var xi = vw.x0 + (t / nT) * (vw.x1 - vw.x0), x = xs(xi);
    Lyr.grid.appendChild(sv('line', {x1:x,y1:mT,x2:x,y2:CH-mB,stroke:'#ffffff0a','stroke-width':1}));
    var ci = Math.max(0, Math.min(n-1, Math.round(xi)));
    var cd = bars[ci];
    Lyr.axis.appendChild(sv('text', {x:x,y:CH-mB+15,'font-size':9,fill:'#787b86','text-anchor':'middle'}, fmtT(cd ? cd.t : null)));
  }

  // FVG
  if (document.getElementById('showFVG').checked) {
    svgFvgs.forEach(function(z){
      if (z.i1 < vw.x0-1 || z.i0 > vw.x1+1) return;
      var x0=xs(z.i0), x1=xs(Math.max(z.i1,z.i0+1));
      var op = z.isEntry ? 0.24 : 0.16, sw2 = z.isEntry ? 0.9 : 0.6;
      Lyr.fvg.appendChild(sv('rect',{x:x0,y:ys(z.top),width:Math.max(x1-x0,1),height:Math.max(ys(z.bottom)-ys(z.top),1),fill:'#9c27b0','fill-opacity':op,stroke:'#9c27b0','stroke-width':sw2}));
    });
  }
  // OB
  if (document.getElementById('showOB').checked) {
    svgObs.forEach(function(z){
      var x0=xs(z.i0), x1=xs(Math.max(z.i1,z.i0+1));
      var col = z.quality==='good'?'#ffb300':'#787b86';
      Lyr.ob.appendChild(sv('rect',{x:x0,y:ys(z.top),width:Math.max(x1-x0,1),height:Math.max(ys(z.bottom)-ys(z.top),1),fill:col,'fill-opacity':0.2,stroke:col,'stroke-width':0.8}));
      Lyr.ob.appendChild(sv('text',{x:x0+2,y:ys(z.bottom)+11,'font-size':9,fill:col},z.quality==='good'?'OB (good)':'OB'));
    });
  }
  // candele (only visible range)
  var c0 = Math.max(0, Math.floor(vw.x0)-1), c1 = Math.min(n-1, Math.ceil(vw.x1)+1);
  for (var i = c0; i <= c1; i++) {
    var cd = bars[i]; if (!cd) continue;
    var x = xs(i), up = cd.c >= cd.o;
    var col = up ? '#26a69a' : '#ef5350';
    Lyr.candles.appendChild(sv('line',{x1:x,y1:ys(cd.h),x2:x,y2:ys(cd.l),stroke:col,'stroke-width':1}));
    Lyr.candles.appendChild(sv('rect',{x:x-bw/2,y:Math.min(ys(cd.o),ys(cd.c)),width:bw,height:Math.max(Math.abs(ys(cd.c)-ys(cd.o)),1),fill:col}));
  }

  // MSS/BOS — linie orizontala de la swing la rupere (model Claude)
  // culori: long=verde, short=rosu (dupa cerinta utilizatorului)
  if (document.getElementById('showBOS').checked) {
    svgLines.forEach(function(l){
      if (l.ex < vw.x0-5 || l.sx > vw.x1+5) return;
      var x0=xs(l.sx), x1=xs(l.ex), y=ys(l.price);
      Lyr.breaks.appendChild(sv('line',{x1:x0,y1:y,x2:x1,y2:y,stroke:l.color,'stroke-width':2}));
      Lyr.breaks.appendChild(sv('text',{x:x1+3,y:y-4,'font-size':10,fill:l.color,'font-weight':'bold'},l.label));
    });
  }

  // Liquidity — model Claude: major (M15/M5, gros auriu) vs local (M1, subtire cyan)
  if (document.getElementById('showLIQ').checked) {
    // Culori per DIRECȚIE (buyside/sellside) + stil per TIP, teoria lui Rares:
    //   HOD/LOD: alb-auriu, linie solidă, etichetă 'H/L'
    //   Major  : auriu gros dash 6,3  — 'Liq maj'
    //   Local  : cyan subțire dash 2,2 — 'Liq'
    //   Minor  : albastru dash 4,2 — 'Min' (trend)
    svgLiqs.forEach(function(l){
      if (l.x_start==null || l.x_end==null) return;
      if (l.x_end < vw.x0-2 || l.x_start > vw.x1+2) return;
      var x0=xs(Math.max(l.x_start,vw.x0)), x1=xs(Math.min(l.x_end,vw.x1));
      var y=ys(l.price);
      var t = l.type || 'local';
      var st = {};
      if (t==='hodlod'){ st={w:1.4,dash:'1,0',op:.9,label:'H/L'}; }
      else if (t==='major'){ st={w:1.8,dash:'6,3',op:.9,label:'Liq maj'}; }
      else if (t==='local'){ st={w:1,dash:'2,2',op:.6,label:'Liq'}; }
      else { st={w:1.2,dash:'4,2',op:.7,label:'Min'}; }
      // culoare după DIRECȚIE (consistent cu legenda: buyside↑ auriu, sellside↓ mov),
      // ușor diferențiată pe tip pentru lizibilitate pe chart.
      var col = '#f0b90b';
      if (l.direction==='sellside') col = '#9b59b6';
      if (t==='hodlod') col = l.direction==='buyside' ? '#ffe082' : '#b39ddb';
      if (t==='local' && l.direction==='buyside') col = '#4fc3f7';
      if (t==='minor') col = l.direction==='buyside' ? '#7aa2f7' : '#9b4f96';
      Lyr.liq.appendChild(sv('line',{x1:x0,y1:y,x2:x1,y2:y,stroke:col,'stroke-width':st.w,'stroke-dasharray':st.dash,opacity:st.op}));
      var lab = st.label + (l.reliquidation?' '+String.fromCharCode(8635):'');
      Lyr.liq.appendChild(sv('text',{x:x0+3,y:y-3,'font-size':8.5,fill:col,opacity:st.op},lab));
    });
  }

  // Trade — cutie stil TradingView (Long/Short Position tool)
  //   verde = entry->TP, rosu = entry->SL, latime limitata (NU intinsa pe chart)
  if (document.getElementById('showTrade').checked && tradeLabel) {
    var n2 = Math.floor(n/2);
    var xE = xs(n2);
    // daca nu avem pret de entry (verifier-ul nu stocheaza preturi reale),
    // desenam doar linia verticala + eticheta (fallback vechi)
    if (tradeEntry == null) {
      Lyr.tradeLines.appendChild(sv('line',{x1:xE,y1:mT,x2:xE,y2:CH-mB,stroke:'#f1c40f','stroke-width':1.2,'stroke-dasharray':'4,3'}));
      Lyr.tradeLines.appendChild(sv('text',{x:xE,y:mT-8,'font-size':11,'font-weight':'bold','text-anchor':'middle',fill:'#f1c40f'},tradeLabel));
    } else {
    var boxBars = Math.min(35, Math.max(n - n2 - 1, 1));
    var xBoxEnd = xs(Math.min(n2 + boxBars, n - 1));
    var yEntry = ys(tradeEntry);

    if (tradeTp != null) {
      var yTp = ys(tradeTp);
      var dist = tradeTp - tradeEntry;
      Lyr.tradeLines.appendChild(sv('rect',{x:xE,y:Math.min(yEntry,yTp),width:Math.max(xBoxEnd-xE,1),height:Math.max(Math.abs(yEntry-yTp),1),fill:'#089981','fill-opacity':0.22,stroke:'#089981','stroke-width':1}));
      Lyr.tradeLines.appendChild(sv('text',{x:xE+6,y:(yEntry+yTp)/2-4,'font-size':10.5,fill:'#26a69a','font-weight':'bold'},'TP  +'+fmtPi(Math.abs(dist),pip)+' pips'));
      Lyr.tradeLines.appendChild(sv('rect',{x:CW-mR,y:yTp-8,width:mR-2,height:16,fill:'#089981'}));
      Lyr.tradeLines.appendChild(sv('text',{x:CW-mR+4,y:yTp+4,'font-size':9,fill:'#fff'},fmtP(tradeTp,pip)));
    }
    if (tradeSl != null) {
      var ySl = ys(tradeSl);
      var dist = tradeSl - tradeEntry;
      Lyr.tradeLines.appendChild(sv('rect',{x:xE,y:Math.min(yEntry,ySl),width:Math.max(xBoxEnd-xE,1),height:Math.max(Math.abs(yEntry-ySl),1),fill:'#f23645','fill-opacity':0.22,stroke:'#f23645','stroke-width':1}));
      Lyr.tradeLines.appendChild(sv('text',{x:xE+6,y:(yEntry+ySl)/2-4,'font-size':10.5,fill:'#ef5350','font-weight':'bold'},'SL  '+fmtPi(dist,pip)+' pips'));
      Lyr.tradeLines.appendChild(sv('rect',{x:CW-mR,y:ySl-8,width:mR-2,height:16,fill:'#f23645'}));
      Lyr.tradeLines.appendChild(sv('text',{x:CW-mR+4,y:ySl+4,'font-size':9,fill:'#fff'},fmtP(tradeSl,pip)));
    }
    // linia de entry = marginea cutiei + tag pe axa dreapta + eticheta LONG/SHORT
    Lyr.tradeLines.appendChild(sv('line',{x1:xE,y1:mT,x2:xE,y2:CH-mB,stroke:'#d1d4dc','stroke-width':1.2,'stroke-dasharray':'3,3'}));
    Lyr.tradeLines.appendChild(sv('rect',{x:CW-mR,y:yEntry-8,width:mR-2,height:16,fill:'#d1d4dc'}));
    Lyr.tradeLines.appendChild(sv('text',{x:CW-mR+4,y:yEntry+4,'font-size':9,fill:'#131722','font-weight':'bold'},fmtP(tradeEntry,pip)));
    Lyr.tradeLines.appendChild(sv('text',{x:xE+4,y:mT+12,'font-size':10.5,fill:'#d1d4dc','font-weight':'bold'},(tradeLabel||'').split('  ')[0]+'  @ '+fmtP(tradeEntry,pip)));
    }
  }

  // price tag (ultima candelă vizibilă, ca pe TradingView)
  var li = Math.max(0, Math.min(n-1, Math.floor(vw.x1)));
  var lc = bars[li];
  if (lc) {
    var py = ys(lc.c), pcol = lc.c >= lc.o ? '#26a69a' : '#ef5350';
    Lyr.priceTag.appendChild(sv('line',{x1:mL,y1:py,x2:CW-mR,y2:py,stroke:pcol,'stroke-width':1,'stroke-dasharray':'2,2',opacity:0.55}));
    Lyr.priceTag.appendChild(sv('rect',{x:CW-mR,y:py-9,width:mR-2,height:18,fill:pcol}));
    Lyr.priceTag.appendChild(sv('text',{x:CW-mR+4,y:py+4.5,'font-size':10,fill:'#fff','font-weight':'bold'},fmtP(lc.c, pip)));
  }
}

function applyToggles(){
  // toggles handled inside render() via checked state — no separate hide needed
}

let svgFvgs = [], svgObs = [], svgLines = [], svgLiqs = [];
let currentBars = [];
let tradeLabel = null, tradeSl = null, tradeTp = null, tradeEntry = null;
let verdicts = {}, activeIdx = 0;

function fmtPi(v, pip) { return (v / pip).toFixed(0); }

function renderTrade(active){
  const tag = document.getElementById('tradeTag');
  tradeLabel = null; tradeSl = null; tradeTp = null; tradeEntry = null;
  if (!active.trade){ tag.textContent='—'; return; }
  tag.textContent = (active.trade.side||'')+' '+(active.trade.result||'')+(active.trade.label?(' · '+active.trade.label):'');
  tag.style.color = active.trade.result==='WIN' ? '#2ecc71' : (active.trade.result==='LOSS' ? '#e74c3c' : '#f1c40f');
  tradeLabel = (active.trade.side||'TRADE')+(active.trade.label?('  ·  '+active.trade.label):'');
  tradeSl = active.trade.sl!=null ? active.trade.sl : null;
  tradeTp = active.trade.tp!=null ? active.trade.tp : null;
  tradeEntry = active.trade.entry!=null ? active.trade.entry : null;
}

function detectAndDraw(){
  const active = WINDOWS[activeIdx];
  const bars = active.bars;
  currentBars = bars;
  // range-ul afisat: initial intregul set de candele; se pastreaza daca userul
  // a facut deja pan/zoom (vw.x1 != 1 inseamna ca a interactionat)
  if (vw.x1 <= 1) { vw.x0 = 0; vw.x1 = Math.max(bars.length - 1, 1); }
  const sw = parseInt(document.getElementById('swing').value,10);
  const obp = parseInt(document.getElementById('ob').value,10);
  document.getElementById('swVal').textContent = sw;
  document.getElementById('obVal').textContent = obp;

  const evList = document.getElementById('evList'); evList.innerHTML='';
  svgFvgs = []; svgObs = []; svgLines = []; svgLiqs = [];
  const counts = {MSS:0,BOS:0,FVG:0,OB:0,LIQ:0};
  const showBOS = document.getElementById('showBOS').checked;
  const showFVG = document.getElementById('showFVG').checked;
  const showOB  = document.getElementById('showOB').checked;
  const showLIQ = document.getElementById('showLIQ').checked;

  function addCount(k){ counts[k]=(counts[k]||0)+1; }

  if (showBOS){
    const bos = detectBosMss(bars, sw);
    bos.forEach(e=>{
      if (e.sx==null || e.ex==null || e.ex<=e.sx) return;
      addCount(e.kind);
      // model Claude: MSS = mov/magenta, BOS = albastru, linie de la sx la ex
      // culori: long=verde, short=rosu (dupa cerinta utilizatorului)
      svgLines.push({
        sx: e.sx, ex: e.ex, price: e.price,
        color: e.direction==='bullish' ? '#2ecc71' : '#e74c3c',
        label: e.kind+' '+e.direction.slice(0,4)
      });
      const d=document.createElement('div');
      d.innerHTML = '<span class="badge '+(e.direction==='bullish'?'b-green':'b-red')+'">'+e.kind+'</span> <b>'+e.direction+'</b> @ '+bars[e.ex].t.slice(11,19)+'UTC · '+e.price.toFixed(5)+' (swing '+e.sx+'→'+e.ex+')';
      evList.appendChild(d);
    });
  }

  if (showFVG){
    const fvgs = detectFvg(bars);
    // punctul de entry: dacă avem preț de entry, folosim bara cu close-ul cel mai
    // apropiat; altfel mijlocul ferestrei ca proxy (trade-ul e plasat pe centru).
    let entryIdx = Math.floor(bars.length/2);
    if (tradeEntry != null){
      let best=0, bd=Infinity;
      for (let i=0;i<bars.length;i++){ const dd=Math.abs(bars[i].c-tradeEntry); if(dd<bd){bd=dd;best=i;} }
      entryIdx = best;
    }
    // FVG-ul "de la entry" = cel mai recent format la/înaintea punctului de entry
    let entryFvg = null, entryFvgI = -1;
    fvgs.forEach(f=>{ if (f.i<=entryIdx && f.i>entryFvgI){ entryFvg=f; entryFvgI=f.i; } });
    const shortMode = document.getElementById('fvgShort') ? document.getElementById('fvgShort').checked : false;
    fvgs.forEach(f=>{
      addCount('FVG');
      const isEntry = (f===entryFvg);
      let i0, i1;
      if (shortMode && !isEntry){
        // opțiunea 2: doar candela de formare a FVG-ului, toate în afară de entry
        i0 = f.i; i1 = f.i + 1;
      } else {
        // opțiunea 1 (implicit) + FVG-ul de entry rămâne extins până la fill
        i0 = Math.max(0, f.i - 1);
        i1 = (f.filledAt!=null ? f.filledAt : bars.length - 1);
      }
      svgFvgs.push({i0: i0, i1: i1, top:f.top, bottom:f.bottom, isEntry: isEntry});
      const d=document.createElement('div');
      d.innerHTML = '<span class="badge b-gray">FVG</span> <b>'+f.direction+'</b> @ '+bars[f.i].t.slice(11,19)+'UTC · '+(f.filled?'completat':'necompletat')+(isEntry?' · <b>entry</b>':'');
      evList.appendChild(d);
    });
  }

  if (showOB){
    const obs = detectOrderBlocks(bars, obp);
    obs.forEach(o=>{
      addCount('OB');
      svgObs.push({i0:o.i, i1:o.i, top:o.top, bottom:o.bottom, quality:''});
      const d=document.createElement('div');
      d.innerHTML = '<span class="badge b-gray">OB</span> <b>'+o.direction+'</b> @ '+bars[o.i].t.slice(11,19)+'UTC';
      evList.appendChild(d);
    });
  }

  if (showLIQ){
    const showHL  = document.getElementById('showHODLOD').checked;
    const showMaj = document.getElementById('showLiqMajor').checked;
    const showLoc = document.getElementById('showLiqLocal').checked;
    const showMin = document.getElementById('showLiqMinor').checked;
    const liqs = detectLiquidity(bars, sw);
    liqs.forEach(l=>{
      if (l.type==='hodlod' && !showHL) return;
      if (l.type==='major'  && !showMaj) return;
      if (l.type==='local'  && !showLoc) return;
      if (l.type==='minor'  && !showMin) return;
      addCount('LIQ');
      // format uniform (model Claude + tipuri Rares): {x_start,x_end,price,type,reliquidation,direction}
      //   major: linia de la formarea pivotului M15 până la sweep (exact ca Claude:
      //          x_start=formed_at, x_end=swept_at)
      //   celelalte tipuri: segment vizibil în jurul nivelului
      let xs0=0, xs1=bars.length-1;
      if (l.type==='major' && l.swept!=null){ xs0 = Math.max(0, l.i); xs1 = Math.min(bars.length-1, l.swept); }
      else {
        const swBars = Math.max(8, sw*2);
        xs0 = Math.max(0, l.i - Math.floor(swBars/2));
        xs1 = Math.min(bars.length - 1, l.i + Math.floor(swBars/2));
      }
      svgLiqs.push({
        x_start: xs0,
        x_end: (l.type==='major' && l.swept!=null ? xs1 : Math.max(xs1, xs0+1)),
        price: l.level,
        type: l.type,
        reliquidation: l.reSwept,
        direction: l.direction,
        day: l.day||null
      });
      const typeLabel = (l.type==='hodlod'?'HOD/LOD':l.type==='major'?'Major':l.type==='minor'?'Minor':'Local');
      const d=document.createElement('div');
      d.innerHTML = '<span class="badge b-gray">'+(l.dir==='buyside'?'Liq↑':'Liq↓')+'</span> <b>'+typeLabel+'</b> '+(l.reSwept?'(re-liq) ':'')+'@ '+(l.day||bars[l.i].t.slice(11,19))+'UTC · '+l.level.toFixed(5);
      evList.appendChild(d);
    });
  }

  const total = counts.MSS+counts.BOS+counts.FVG+counts.OB+counts.LIQ;
  if (!total){ const d=document.createElement('div'); d.className='muted'; d.textContent='Niciun eveniment detectat in aceasta fereastra.'; evList.appendChild(d); }
  else {
    const s = document.createElement('div'); s.className='muted';
    s.innerHTML = 'Rezumat: MSS '+counts.MSS+' · BOS '+counts.BOS+' · FVG '+counts.FVG+' · OB '+counts.OB+' · Liq '+counts.LIQ;
    evList.appendChild(s);
  }

  renderTrade(active);
  render();
  fillSidebar(active);
}

function fillSidebar(active){
  document.getElementById('winInfo').innerHTML =
    '<b>#'+active.id+'</b> · '+active.symbol+'<br>'+
    active.window_start+' → '+active.window_end+' UTC<br>'+
    (active.data_start.slice(0,19))+' … '+(active.data_end.slice(0,19))+' UTC';
  document.getElementById('winNote').textContent = active.note;
  // prefill comment if saved
  const v = verdicts[active.id];
  if (v){ document.getElementById('comment').value = v.comment||''; } else { document.getElementById('comment').value=''; }
}

function fillSelector(){
  const sel = document.getElementById('winSel');
  sel.innerHTML='';
  WINDOWS.forEach((w,i)=>{
    const o=document.createElement('option'); o.value=i; o.textContent='#'+w.id+' — '+w.symbol+' '+w.window_start;
    sel.appendChild(o);
  });
  sel.onchange = ()=>{ activeIdx=parseInt(sel.value,10); vw.x0=0; vw.x1=1; detectAndDraw(); };
}

// verdict buttons
document.querySelectorAll('[data-v]').forEach(b=>{
  b.onclick = ()=>{
    const active=WINDOWS[activeIdx];
    verdicts[active.id]={verdict:b.dataset.v, comment:document.getElementById('comment').value, savedAt:new Date().toISOString(), symbol:active.symbol, window_start:active.window_start, window_end:active.window_end};
    persist(); renderSaved();
  };
});
document.getElementById('saveBtn').onclick = ()=>{
  const active=WINDOWS[activeIdx];
  if (!verdicts[active.id]){ alert('Alege intai PASS/SKIP/Nesigur.'); return; }
  verdicts[active.id].comment = document.getElementById('comment').value;
  persist(); renderSaved();
};
document.getElementById('exportBtn').onclick = ()=>{ exportJson(); };
document.getElementById('clearBtn').onclick = ()=>{
  if (confirm('Stergi toate verdicturile salvate in acest browser?')){ verdicts={}; localStorage.removeItem('m1verdicts'); renderSaved(); }
};
document.getElementById('detectBtn').onclick = ()=>{ detectAndDraw(); };

function persist(){ try{ localStorage.setItem('m1verdicts', JSON.stringify(verdicts)); }catch(e){} }
function loadPersist(){ try{ const s=localStorage.getItem('m1verdicts'); if (s) verdicts=JSON.parse(s); }catch(e){} }
function renderSaved(){
  const box=document.getElementById('savedList'); box.innerHTML='';
  const ids=Object.keys(verdicts);
  if (!ids.length){ box.innerHTML='Niciun verdict inca.'; return; }
  ids.forEach(id=>{
    const v=verdicts[id];
    const d=document.createElement('div');
    d.innerHTML = '#'+id+' · <b>'+v.verdict+'</b>'+(v.comment?' — '+v.comment:'')+' <span class="muted">'+ (v.savedAt||'').slice(0,19).replace('T',' ')+'</span>';
    box.appendChild(d);
  });
}
function exportJson(){
  const payload = {exportedAt:new Date().toISOString(), verdicts:verdicts};
  const blob = new Blob([JSON.stringify(payload,null,2)],{type:'application/json'});
  const a=document.createElement('a'); a.href=URL.createObjectURL(blob); a.download='m1_verdicts.json'; a.click();
  // also CSV-friendly text
  alert('Exportat verdicts. Fisierul include PASS/SKIP + comentarii + timestamp. Daca nu s-a descarcat, verifica pop-up-ul.');
}

// init
loadPersist(); fillSelector(); renderSaved();
if (WINDOWS.length) activeIdx=0;
initChart();
detectAndDraw();
window.addEventListener('resize', ()=>{ render(); });
['showBOS','showFVG','showOB','showLIQ','showTrade','showHODLOD','showLiqMajor','showLiqLocal','showLiqMinor','fvgExtend','fvgShort'].forEach(id=>{
  document.getElementById(id).addEventListener('change', ()=>{ detectAndDraw(); });
});
['swing','ob'].forEach(id=>{
  document.getElementById(id).addEventListener('input', ()=>{ detectAndDraw(); });
});
</script>
</body>
</html>
"""


def main():
    windows, missing = build_windows()
    if not windows:
        raise SystemExit("Nicio fereastra valida (cu date M1) de construit.")
    windows_json = json.dumps(windows)
    html = HTML_TEMPLATE.replace("__WINDOWS_JSON__", windows_json).replace("__JS_DETECT__", JS_DETECT)
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(html)
    print("Scris: {}".format(OUT_HTML))
    print("Ferestre incluse (cu date M1): {}".format(len(windows)))
    for w in windows:
        print("  #{} {} {} -> {} ({} bare)".format(
            w["id"], w["symbol"], w["window_start"], w["window_end"], len(w["bars"])))
    if missing:
        print("\nSarit (fara date M1 in history_export): {}".format(missing))


if __name__ == "__main__":
    main()
