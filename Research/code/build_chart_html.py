#!/usr/bin/env python3
"""Construieste _charts/gbpusd_draw.html â€” Mini-TradingView local cu date GBPUSD.pro M15.
v4 (06 Aug 2026): fix blank-chart (ResizeObserver), SL/TP in dialog, DRAWING SYSTEM
(linie / zona / h-line) exportat cu axe X(bar/ts)+Y(price), tools toolbar."""
import csv, os, json

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "gbpusd_pro_m15_2025_09_2026_02.csv")
SRC_M1 = os.path.join(HERE, "gbpusd_pro_m1_2025_09_2026_02.csv")
OUT = os.path.join(HERE, "gbpusd_full.html")

rows = []
with open(SRC, newline="") as f:
    for r in csv.DictReader(f):
        rows.append([int(r["time"]), float(r["open"]), float(r["high"]),
                     float(r["low"]), float(r["close"]), int(r["tick_volume"])])

rows_m1 = []
if os.path.exists(SRC_M1):
    with open(SRC_M1, newline="") as f:
        for r in csv.DictReader(f):
            rows_m1.append([int(r["time"]), float(r["open"]), float(r["high"]),
                            float(r["low"]), float(r["close"]), int(r["tick_volume"])])

data_js = json.dumps(rows, separators=(",", ":"))
data_m1_js = json.dumps(rows_m1, separators=(",", ":")) if rows_m1 else "[]"

HTML = r"""<!DOCTYPE html>
<html lang="ro">
<head>
<meta charset="UTF-8">
<title>Mini-TradingView â€” GBPUSD.pro M15 (Sept 2025 - Feb 2026)</title>
<style>
  :root { --bg:#131722; --grid:#232833; --panel:#1e222d; --text:#d1d4dc;
          --up:#26a69a; --down:#ef5350; --accent:#2962ff; --line:#2a2e39; }
  * { margin:0; padding:0; box-sizing:border-box; }
  html,body { height:100%; background:var(--bg); color:var(--text);
              font-family:'Segoe UI',Roboto,'Helvetica Neue',Arial,sans-serif; overflow:hidden; }
  #wrap { display:flex; height:100%; }
  #chartBox { flex:1; position:relative; min-width:0; border-left:1px solid var(--line); }
  #strip { position:absolute; top:0; left:0; right:0; height:6px; background:#e53935; z-index:6; }
  canvas { display:block; width:100%; height:100%; cursor:crosshair; user-select:none; }
  #pricebar { position:absolute; top:0; right:0; bottom:0; width:52px; z-index:6;
              background:rgba(19,23,34,0.4); border-left:1px solid var(--line); cursor:ns-resize; }
  #pricebar:hover { background:rgba(30,34,45,0.65); }
  #pbtag { position:absolute; top:8px; right:2px; left:2px; text-align:center;
           font-size:11px; font-weight:700; color:#fff; background:var(--accent);
           border-radius:5px; padding:2px 0; pointer-events:none; z-index:8;
           transition:top .08s ease-out; }
  .pblabel { position:absolute; right:3px; left:3px; text-align:center;
             font:bold 9px Segoe UI, Arial, sans-serif; padding:1px 2px; border-radius:3px;
             pointer-events:none; white-space:nowrap; z-index:7;
             transform:translateY(-50%); }
  .pblabel.entry { color:#ffa726; background:rgba(255,167,38,0.18); border:1px solid rgba(255,167,38,0.35); }
  .pblabel.sl    { color:#ff5252; background:rgba(255,82,82,0.18);   border:1px solid rgba(255,82,82,0.35); }
  .pblabel.tp    { color:#4caf50; background:rgba(76,175,80,0.18);   border:1px solid rgba(76,175,80,0.35); }
  #status { position:absolute; top:8px; right:62px; background:rgba(30,34,45,0.85);
            border:1px solid var(--line); border-radius:6px; padding:4px 10px;
            font-size:11px; color:#9aa0ab; pointer-events:none; z-index:5;
            max-width:calc(100% - 130px); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
  #status b { color:#fff; font-weight:600; }
  #sidebar { width:330px; background:var(--panel); border-left:1px solid var(--line);
             display:flex; flex-direction:column; transition:width .18s ease;   /* FIX P4: slide smooth la collapse */
             user-select:none; -webkit-user-select:none; }   /* FIX: click+drag accidental pe bara din dreapta nu mai selecteaza text (lista desene/indicatori) */
  #sidebar.collapsed { width:0; border-left:none; overflow:hidden; }   /* FIX P4: colapsat â€” continutul nu â€žsare" afara vizual */
  #sidebar input, #sidebar textarea, #sidebar select { user-select:text; -webkit-user-select:text; }   /* campurile editabile raman normale */
  #shead { padding:10px 12px; border-bottom:1px solid var(--line); font-size:13px; }
  #shead b { color:#fff; }
  #shead .hint { font-size:11px; color:#787b86; margin-top:4px; line-height:1.5; }
  #banner { display:none; margin-top:6px; background:#3d2626; border:1px solid #8a4a4a;
            color:#ffb4b4; border-radius:6px; padding:6px 8px; font-size:11px; line-height:1.4; }
  #toolbar { padding:8px 10px; border-bottom:1px solid var(--line); display:flex; gap:5px; flex-wrap:wrap; }
  #toolbar button { background:#363a45; border:none; color:var(--text); border-radius:6px;
        padding:5px 8px; font-size:11px; cursor:pointer; transition:background .12s; }
  #toolbar button:hover { background:#4c525e; }
  #toolbar button.on { background:var(--accent); color:#fff; }
  #list { flex:1; overflow-y:auto; padding:6px; }
  #list::-webkit-scrollbar { width:8px; } #list::-webkit-scrollbar-thumb { background:#3a3e49; border-radius:4px; }
  .sechead { display:flex; align-items:center; gap:6px; font-size:11px; font-weight:700; letter-spacing:0.4px;
    color:#d1d4dc; background:rgba(255,255,255,0.04); border-top:1px solid var(--line); border-radius:4px;
    padding:6px 8px; margin:8px 0 6px; text-transform:uppercase; }
  .sechead:first-of-type { margin-top:0; }
  .sechead .cnt { margin-left:auto; font-weight:600; color:#787b86; background:rgba(255,255,255,0.06);
    border-radius:8px; padding:0 6px; font-size:10px; line-height:16px; }
  .mk { background:#262a35; border-radius:8px; padding:8px; margin-bottom:6px;
        border-left:3px solid var(--up); font-size:12px; transition:background .15s; }
  .mk:hover { background:#2d3240; }
  .mk.sel { outline:2px solid #4fc3f7; box-shadow:0 0 0 1px #4fc3f7, 0 4px 14px rgba(79,195,247,0.25); background:#1d2b3a; }   /* selectat pe chart => evidenÈ›iat È™i Ã®n listÄƒ (nu-l mai cauÈ›i dupÄƒ ID) */
  .mk.ghost { background:rgba(245,197,66,0.06); border-left:3px solid #f5c542; box-shadow:inset 0 0 0 1px rgba(245,197,66,0.25); }
  .mk.ghost:hover { background:rgba(245,197,66,0.10); }
  .mk.sell { border-left-color:var(--down); }
  .mk .inote { width:100%; box-sizing:border-box; background:#131722; color:var(--text); border:1px solid var(--line);
               border-radius:5px; padding:4px 6px; font-size:11px; margin-top:4px; resize:vertical; font-family:inherit; }
  .mk .igrp { background:#131722; color:var(--text); border:1px solid var(--line); border-radius:4px; font-size:11px; padding:1px 4px; }
  .mk .top { display:flex; justify-content:space-between; align-items:center; gap:6px; }
  .mk .tag { font-weight:700; }
  .mk .tag.buy { color:var(--up); } .mk .tag.sell { color:var(--down); }
  .mk .time { color:#787b86; }
  .mk .resbadge { font-size:9px; font-weight:700; border:1px solid; border-radius:4px; padding:1px 4px; margin-left:auto; white-space:nowrap; }
  .mk .note { margin-top:4px; white-space:pre-wrap; color:#d1d4dc; word-break:break-word; }
  .mk .meta { margin-top:3px; font-size:10px; color:#6a6d78; }
  .mk .acts { margin-top:6px; display:flex; gap:6px; }
  .drw { background:#1e2a38; border-radius:8px; padding:7px; margin-bottom:6px; font-size:11px;
         border-left:3px solid #4fc3f7; cursor:pointer; }
  .drw.sel { outline:1px solid #4fc3f7; }
  .mk button, #sfoot button, #revealbar button, .drw button { background:#363a45; border:none; color:var(--text);
        border-radius:5px; padding:4px 8px; font-size:11px; cursor:pointer; transition:background .12s; }
  .mk button:hover, #sfoot button:hover, #revealbar button:hover, .drw button:hover { background:#4c525e; }
  #revealbar { padding:8px 10px; border-top:1px solid var(--line); display:flex; flex-direction:column; gap:5px;
               align-items:stretch; font-size:11px; color:#787b86; }
  #revealbar .rglabel { font-size:8px; color:#787b86; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:2px; }
  #revealbar .rg { display:grid; grid-template-columns:repeat(4, minmax(0,1fr)); gap:2px; }
  #revealbar .rg button { aspect-ratio:1.3; min-width:0; padding:1px 0; display:flex; flex-direction:column; align-items:center; justify-content:center; gap:1px;
                          border:none; border-radius:5px; background:#363a45; color:var(--text); cursor:pointer; }
  #revealbar .rg button svg { width:12px; height:12px; fill:none; stroke:currentColor; stroke-width:1.5; stroke-linecap:round; stroke-linejoin:round; }
  #revealbar .rg button span { font-size:7px; color:#9aa0ab; line-height:1; }
  #revealbar .rg button.on { background:var(--accent); color:#fff; }
  #revealbar .rg button.on span { color:#fff; }
  #revealbar .rg button[title^="DezvÄƒluie +1"], #revealbar .rg button[title^="DezvÄƒluie +10"], #revealbar .rg button[title^="DezvÄƒluie +60"] { font-size:11px; font-weight:600; }
  #indpanel { border-bottom:1px solid var(--line); max-height:38%; display:flex; flex-direction:column; }
  #indpanel .indhead { display:flex; align-items:center; gap:6px; padding:6px 10px; font-size:11px; color:#9aa0ab; }
  #indpanel .indhead b { flex:1; color:#fff; }
  #indpanel .indhead button { background:#363a45; border:none; color:var(--text); border-radius:5px; padding:3px 8px; font-size:11px; cursor:pointer; }
  #indpanel .indhead button:hover { background:#4c525e; }
  #indlist { overflow-y:auto; padding:0 8px 6px; }
  .ind { display:flex; align-items:center; gap:6px; background:#262a35; border-radius:6px; padding:5px 8px; margin-bottom:4px; font-size:12px; }
  .ind.on { border-left:3px solid var(--accent); }
  .ind .nm { flex:1; color:#d1d4dc; }
  .ind .nm small { display:block; color:#6a6d78; font-size:10px; }
  .ind input[type=checkbox] { accent-color: var(--accent); }
  .ind button { background:#363a45; border:none; color:var(--text); border-radius:4px; padding:2px 7px; font-size:11px; cursor:pointer; }
  .ind button:hover { background:#4c525e; }
  .ind .set { display:none; margin-top:5px; padding-top:5px; border-top:1px solid var(--line); }
  .ind .set.open { display:block; }
  .ind .set label { display:block; font-size:10px; color:#787b86; margin-bottom:3px; }
  .ind .set input[type=text], .ind .set input[type=number] { width:90px; background:#131722; color:var(--text); border:1px solid var(--line); border-radius:4px; padding:2px 5px; font-size:11px; }
  #indpicker { position:absolute; left:10px; top:120px; z-index:15; background:#262a35; border:1px solid #3a3f4d;
               border-radius:8px; padding:8px; width:240px; box-shadow:0 8px 28px #000a; }
  #indpicker button { display:block; width:100%; text-align:left; background:none; border:none; color:var(--text);
                      padding:6px 8px; border-radius:6px; font-size:12px; cursor:pointer; }
  #indpicker button:hover { background:#363a45; }
  #indpicker button small { color:#787b86; }
  #themePicker { position:absolute; right:10px; bottom:56px; z-index:15; background:var(--panel); border:1px solid var(--line);
                 border-radius:8px; padding:10px; width:220px; box-shadow:0 8px 28px #000a; }
  #ctxMenu { position:fixed; z-index:99; background:#1e222d; border:1px solid var(--line); border-radius:8px;
             min-width:190px; padding:5px; box-shadow:0 10px 32px #000c; display:none; font-size:12px; }
  #ctxMenu .ci { display:flex; align-items:center; gap:8px; padding:6px 10px; border-radius:5px; cursor:pointer;
                 color:var(--text); white-space:nowrap; }
  #ctxMenu .ci:hover { background:#363a45; }
  #ctxMenu .ci.on { color:var(--accent); }
  #ctxMenu .csep { height:1px; background:var(--line); margin:4px 6px; }
  #ctxMenu .ci.long { color:var(--up); } #ctxMenu .ci.short { color:var(--down); }
  #ctxMenu .ci .kbd { margin-left:auto; font-size:10px; color:#787b86; }
  #ctxMenu .rrpreset { flex:1; background:#363a45; border:1px solid transparent; color:var(--text); border-radius:5px;
                       padding:4px 0; font-size:11px; cursor:pointer; text-align:center; }
  #ctxMenu .rrpreset:hover { background:#4c525e; border-color:var(--accent); }
  #themePicker .tprow { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:8px; }
  #themePicker .tp { flex:1; min-width:70px; background:#363a45; border:1px solid transparent; color:var(--text);
                     border-radius:6px; padding:5px 4px; font-size:11px; cursor:pointer; }
  #themePicker .tp.on { border-color:var(--accent); }
  #themePicker label { font-size:10px; color:#787b86; display:block; margin-bottom:3px; }
  #themePicker input[type=color] { width:100%; height:26px; border:1px solid var(--line); border-radius:5px; background:var(--bg); cursor:pointer; }
  #btPanel { position:absolute; left:8px; bottom:50px; z-index:14; background:var(--panel); border:1px solid var(--line);
             border-radius:8px; padding:8px 10px; font-size:11px; color:var(--text); min-width:170px;
             box-shadow:0 8px 28px #000a; }
  #btPanel b { color:#fff; }
  #btPanel .r { display:flex; justify-content:space-between; gap:12px; margin:2px 0; }
  #btPanel .win { color:#26a69a; } #btPanel .loss { color:#ef5350; } #btPanel .open { color:#f5c542; }
  #sfoot { padding:10px; border-top:1px solid var(--line); display:flex; gap:8px; }
  #sfoot button { flex:1; padding:7px 4px; font-size:12px; }
  #dlg { position:absolute; background:#262a35; border:1px solid #3a3f4d;
         border-radius:10px; padding:12px; width:290px; z-index:10; box-shadow:0 8px 28px #000a;
         cursor:move; user-select:none; }   /* drag de ORICARE din dialog, mai puÈ›in cÃ¢mpurile editabile */
  #dlg input, #dlg textarea, #dlg select { user-select:text; cursor:default; }   /* aici scrii â†’ cursor normal */
  #dlg h4 { font-size:13px; margin-bottom:8px; color:#fff; }
  #dlg .row { margin-bottom:8px; }
  #dlg label { font-size:11px; color:#787b86; display:block; margin-bottom:3px; }
  #dlg .dirbtns { display:flex; gap:6px; }
  #dlg .dirbtns button { flex:1; padding:6px; border:none; border-radius:6px;
        background:#363a45; color:var(--text); cursor:pointer; font-size:12px; }
  #dlg .dirbtns button.on.buy { background:var(--up); color:#fff; }
  #dlg .dirbtns button.on.sell { background:var(--down); color:#fff; }
  #dlg input[type=number] { width:50%; background:#131722; color:var(--text); border:1px solid var(--line);
        border-radius:6px; padding:5px 6px; font-size:12px; outline:none; }
  #dlg input[type=number]:focus { border-color:#4a6fd4; }
  #dlg textarea { width:100%; height:56px; background:#131722; color:var(--text);
        border:1px solid var(--line); border-radius:6px; padding:6px; font-size:12px;
        resize:vertical; font-family:inherit; outline:none; }
  #dlg textarea:focus { border-color:#4a6fd4; }
  #dlg .acts { display:flex; gap:6px; justify-content:flex-end; margin-top:2px; }
  #dlg .acts button { padding:6px 12px; border:none; border-radius:6px; cursor:pointer; font-size:12px; }
  #dlg .save { background:var(--accent); color:#fff; }
  #dlg .save:hover { background:#3a72ff; }
  #dlg .cancel { background:#363a45; color:var(--text); }
  #toast { position:fixed; bottom:14px; left:50%; transform:translateX(-50%);
        background:#2a2e39; border:1px solid var(--line); border-radius:8px;
        padding:8px 16px; font-size:12px; z-index:20; display:none; box-shadow:0 4px 16px #000a;
        pointer-events:none; }
  #strip { pointer-events:none; }
  #tfbar { position:absolute; top:8px; left:8px; z-index:7; display:flex; gap:2px;
           background:rgba(19,23,34,0.8); border:1px solid var(--line); border-radius:6px; padding:2px; }
  #tfbar button { background:none; border:none; color:#9aa0ab; font-size:11px; font-weight:600;
                  padding:2px 8px; border-radius:4px; cursor:pointer; }
  #tfbar button:hover { background:#363a45; color:#fff; }
  #tfbar button.on { background:var(--accent); color:#fff; }
  #drawbar { position:absolute; top:8px; right:60px; z-index:7; display:flex; gap:4px;
             background:rgba(19,23,34,0.85); border:1px solid var(--line); border-radius:8px; padding:3px; }
  #drawbar button { background:none; border:none; color:#d1d4dc; cursor:pointer;
                    padding:3px 5px; border-radius:6px; display:flex; flex-direction:column; align-items:center; gap:1px; }
  #drawbar button svg { width:15px; height:15px; fill:none; stroke:currentColor; stroke-width:1.5; stroke-linecap:round; stroke-linejoin:round; display:block; }
  #drawbar button span { font-size:7.5px; color:#9aa0ab; line-height:1; white-space:nowrap; }
  #drawbar button:hover { background:#363a45; color:#fff; }
  #drawbar button:disabled { opacity:0.35; cursor:default; background:none; color:#9aa0ab; }
  #drawbar button.on { background:var(--accent); color:#fff; }
  #drawbar button.on span { color:#fff; }
  #drawbar .sep { width:1px; background:var(--line); margin:2px 3px; }
  /* â­ FAVORITES plutitoare (ca TradingView): bara cu TOATE uneltele favorite vizibile â€” tragi de â­ oriunde.
     ATENÈšIE: doar left/top, FÄ‚RÄ‚ right â€” altfel left+right = elementul se Ã®ntinde cÃ¢nd Ã®l muÈ›i Ã®n stÃ¢nga! */
  #favbar { position:absolute; top:64px; left:auto; z-index:9; display:flex; gap:2px; align-items:center;
            background:rgba(19,23,34,0.92); border:1px solid var(--line); border-radius:10px; padding:3px 6px;
            cursor:grab; box-shadow:0 4px 14px #000a; user-select:none; width:auto; }
  #favbar.dragging { cursor:grabbing; }
  #favbar .favlabel { font-size:12px; line-height:1; margin-right:2px; }
  #favbar .favcnt { font-size:9px; color:#9aa0ab; margin-left:2px; font-weight:600; }
  #favbar button { background:none; border:none; color:#d1d4dc; cursor:pointer; padding:4px; border-radius:6px; display:flex; }
  #favbar button svg { width:15px; height:15px; fill:none; stroke:currentColor; stroke-width:1.5; stroke-linecap:round; stroke-linejoin:round; display:block; }
  #favbar button:hover { background:#363a45; color:#fff; }
  #favbar button.on { background:var(--accent); color:#fff; }
  #favbar:hover { border-color:#4fc3f7; }
  /* POPUP cu uneltele favorite â€” deschis la click pe â­, poziÈ›ionat sub pill (clampat Ã®n chart) */
  #favpop { position:absolute; z-index:10; display:none; flex-direction:column; gap:2px;
            background:rgba(19,23,34,0.96); border:1px solid var(--line); border-radius:8px; padding:4px;
            box-shadow:0 8px 24px #000c; min-width:44px; width:auto; }
  #favpop button { background:none; border:none; color:#d1d4dc; cursor:pointer; padding:5px 7px; border-radius:6px;
                   display:flex; align-items:center; gap:7px; font-size:11px; width:100%; text-align:left; }
  #favpop button svg { width:15px; height:15px; fill:none; stroke:currentColor; stroke-width:1.5; stroke-linecap:round; stroke-linejoin:round; display:block; flex:none; }
  #favpop button:hover { background:#363a45; color:#fff; }
  #favpop button.on { background:var(--accent); color:#fff; }
  #favpop .favpop-tip { font-size:9px; color:#787b86; padding:2px 6px 4px; }
  /* replay bar jos pe chart (ca TradingView) â€” play + blind + reveal */
  #replaybar { position:absolute; bottom:10px; left:50%; transform:translateX(-50%); z-index:7; display:flex; gap:3px; align-items:center;
               background:rgba(19,23,34,0.85); border:1px solid var(--line); border-radius:8px; padding:3px 4px; }
  #replaybar button { background:none; border:none; color:#d1d4dc; cursor:pointer; padding:4px 7px; border-radius:6px;
                      font-size:11px; font-weight:600; display:flex; align-items:center; }
  #replaybar button svg { width:14px; height:14px; fill:none; stroke:currentColor; stroke-width:1.5; stroke-linecap:round; stroke-linejoin:round; display:block; }
  #replaybar button:hover { background:#363a45; color:#fff; }
  #replaybar button.on { background:var(--accent); color:#fff; }
  #toolrail { position:absolute; top:70px; left:8px; z-index:7; display:flex; flex-direction:column; gap:2px;
              background:rgba(19,23,34,0.85); border:1px solid var(--line); border-radius:8px; padding:4px; }
  #toolrail button { background:none; border:none; color:#d1d4dc; cursor:pointer; width:52px; text-align:center;
                     padding:5px 2px 4px; border-radius:6px; display:flex; flex-direction:column; align-items:center; gap:2px; }
  #toolrail button svg { width:18px; height:18px; fill:none; stroke:currentColor; stroke-width:1.5; stroke-linecap:round; stroke-linejoin:round; }
  #toolrail button span { font-size:8.5px; color:#9aa0ab; line-height:1; white-space:nowrap; }
  #toolrail button:hover { background:#363a45; }
  #toolrail button.on { background:var(--accent); }
  #toolrail button.on span { color:#fff; }
  #toolrail button.long { color:#26a69a; } #toolrail button.short { color:#ef5350; }
  #toolrail button.long.on, #toolrail button.short.on { color:#fff; }
</style>
</head>
<body>
<div id="wrap">
  <div id="chartBox">
    <div id="strip"></div>
    <div id="tfbar">
      <button data-tf="M1" title="M1 real (94k bare)">M1</button>
      <button data-tf="M15" class="on">M15</button>
      <button data-tf="H1">H1</button>
      <button data-tf="H4">H4</button>
      <button data-tf="D1">D1</button>
    </div>
    <div id="pricebar"><div id="pbtag"></div><div id="pbEntry" class="pblabel entry" style="display:none"></div><div id="pbSL" class="pblabel sl" style="display:none"></div><div id="pbTP" class="pblabel tp" style="display:none"></div></div>
    <canvas id="cv"></canvas>
    <div id="drawbar">
      <button id="undoBtn" title="Undo (Ctrl+Z) â€” anuleazÄƒ ultima modificare"><svg><use href="#i-undo"/></svg></button>
      <button id="redoBtn" title="Redo (Ctrl+Shift+Z) â€” refÄƒ modificarea anulatÄƒ"><svg><use href="#i-redo"/></svg></button>
      <div class="sep"></div>
      <button id="resetViewBtn" title="Reset view (fit content) â€” tasta A"><svg><use href="#i-pin"/></svg></button>
      <button id="blindBtn" title="Lookahead OFF: vezi tot chart-ul â€” apasÄƒ ca sÄƒ ascunzi viitorul"><svg><use href="#i-lock"/></svg><span>Lookahead</span></button>
      <button id="laPlaceBtn" title="ðŸ“ Pune bara de lookahead: click pe chart = linia acolo (o datÄƒ), apoi click-ul revine la normal"><svg><use href="#i-ruler"/></svg><span>Bara</span></button>
      <button id="laDefaultBtn" title="ðŸ’¾ SalveazÄƒ poziÈ›ia ACTUALÄ‚ de lookahead ca default â€” la restart, chart-ul porneÈ™te dezvÄƒluit pÃ¢nÄƒ aici (nu mai dai +10/+60 de fiecare datÄƒ)"><svg><use href="#i-flag"/></svg><span>Lookahead def</span></button>
      <button id="saveBtn" title="ðŸ’¾ SalveazÄƒ profilul (Ctrl+S) â€” tot ce ai pe chart e persistat"><svg><use href="#i-save"/></svg><span>SalveazÄƒ</span></button>
      <button id="themeBtn" title="TemÄƒ culori"><svg><use href="#i-theme"/></svg></button>
      <button id="expProfBtn" title="Export profil (desene+markers) ca JSON">â¤“</button>
      <button id="impProfBtn" title="Import profil din JSON (desene+markers)">â¤’</button>
      <button id="sideBtn" title="AratÄƒ/ascunde panoul din dreapta">â—€</button>
    </div>
    <div id="favbar" style="display:none"><span class="favlabel">â­</span><span class="favcnt"></span></div>
    <div id="favpop"></div>
    <div id="replaybar">
      <button id="playBtn" title="Play â€” dezvÄƒluie candela urmÄƒtoare (Space = toggle, È›ine apÄƒsat = accelerare)"><svg><use href="#i-play"/></svg></button>
      <button id="r1" title="DezvÄƒluie +1 candelÄƒ">+1</button>
      <button id="r10" title="DezvÄƒluie +10 candele">+10</button>
      <button id="r60" title="DezvÄƒluie +60 candele">+60</button>
    </div>
    <div id="status"></div>
    <div id="dlg" style="display:none;"></div>
  </div>
  <div id="sidebar">
    <div id="shead">
      <b>GBPUSD.pro Â· M15 Â· 01 Mai â€“ 31 Iul 2026</b>
      <div class="hint" style="font-size:10px;color:#6a6d78;margin-top:4px;line-height:1.4">Unelte: V=Select Â· B=LONG Â· S=SHORT Â· L=Linie Â· P=Pen Â· R=ZonÄƒ Â· H=H-Linie Â· N=NotÄƒ Â· Shift+drag=mÄƒsurÄƒ Â· Scroll=zoom la cursor Â· ðŸ‘» NW=AI pe chart Â· ðŸ¤– Bot=switch listÄƒ.</div>
      <div id="banner">âš  Stocarea localÄƒ e blocatÄƒ (file:// Ã®n Firefox) â€” datele NU se pÄƒstreazÄƒ la refresh.
      FoloseÈ™te â€žExport JSONâ€ cÃ¢nd termini.</div>
    </div>
    <div id="toolbar" style="display:none">
      <button data-t="pointer" class="on">ðŸ–± Select</button>
      <button data-t="long" class="long">â–² LONG</button>
      <button data-t="short" class="short">â–¼ SHORT</button>
      <button data-t="line">ðŸ“ Linie</button>
      <button data-t="pen">âœï¸ Pen</button>
      <button data-t="rect">ðŸŸ¦ ZonÄƒ</button>
      <button data-t="hline">âž– H-Linie</button>
      <button data-t="arrow">ðŸ’¬ NotÄƒ</button>
    </div>
    <div id="toolrail" title="Unelte (taste: V=Select B=LONG S=SHORT L=Linie P=Pen R=ZonÄƒ H=H-Linie N=NotÄƒ)">
      <button data-t="pointer" class="on" title="Select (V)"><svg><use href="#i-pointer"/></svg><span>Select</span></button>
      <button data-t="long" class="long" title="LONG (B)"><svg><use href="#i-long"/></svg><span>LONG</span></button>
      <button data-t="short" class="short" title="SHORT (S)"><svg><use href="#i-short"/></svg><span>SHORT</span></button>
      <button data-t="line" title="Linie (L)"><svg><use href="#i-line"/></svg><span>Linie</span></button>
      <button data-t="pen" title="Pen (P)"><svg><use href="#i-pen"/></svg><span>Pen</span></button>
      <button data-t="rect" title="ZonÄƒ (R)"><svg><use href="#i-rect"/></svg><span>ZonÄƒ</span></button>
      <button data-t="hline" title="H-Linie (H)"><svg><use href="#i-hline"/></svg><span>H-Linie</span></button>
      <button data-t="arrow" title="NotÄƒ (N)"><svg><use href="#i-note"/></svg><span>NotÄƒ</span></button>
    </div>
    <div id="debug" style="display:none;padding:4px 10px;font-size:10px;color:#6a6d78;background:#1a1d26;border-bottom:1px solid var(--line);font-family:Consolas,monospace;"></div>
    <div id="indpanel">
      <div class="indhead"><b>INDICATORI</b><button id="addInd" title="AdaugÄƒ indicator">ï¼‹ AdaugÄƒ</button></div>
      <div id="indlist"></div>
      <div id="indpicker" style="display:none"></div>
    </div>
    <div id="list"></div>
    <div id="revealbar">
      <div class="rglabel">AnalizÄƒ</div>
      <div class="rg">
        <button id="btBtn" title="Backtest vizual: ruleazÄƒ SL/TP pe barele viitoare"><svg><use href="#i-test"/></svg><span>Backtest</span></button>
        <button id="btEye" title="Ascunde/aratÄƒ liniile de backtest (overlay on/off)"><svg><use href="#i-eye"/></svg><span>Liniile</span></button>
        <button id="nwBtn" title="Ghost markers: pune LONG/SHORT pe semnalele No-Wick din zona vizibilÄƒ"><svg><use href="#i-ai"/></svg><span>Ghost</span></button>
        <button id="botBtn" title="ðŸ¤– Bot: backtest automat cu config-ul bot-ului pe TOT istoricul"><svg><use href="#i-bot"/></svg><span>Bot</span></button>
        <button id="finBtn" title="FinalizeazÄƒ sesiunea: raport complet (TAKE vs SKIP, WIN/LOSS, filtre)"><svg><use href="#i-report"/></svg><span>Raport</span></button>
      </div>
      <div class="rglabel" style="margin-top:6px">SetÄƒri poziÈ›ii</div>
      <div class="rg">
        <button id="lockRRBtn" title="ðŸ”’ R:R fix: cÃ¢nd muÈ›i SL-ul, TP-ul se mutÄƒ proporÈ›ional (acelaÈ™i R:R) È™i invers"><svg><use href="#i-lock"/></svg><span>ðŸ”’ R:R fix</span></button>
        <button id="magBtn" title="ðŸ§² Magnet (ca TradingView): lipeÈ™te preÈ›ul de wick-uri (high/low), open/close, liniile SL/TP È™i desene. Soft = doar cÃ¢nd eÈ™ti aproape, Hard = mereu pe cel mai apropiat. Èšine Ctrl Ã®n timpul drag-ului = Hard temporar."><svg><use href="#i-magnet"/></svg><span>ðŸ§² Magnet</span></button>
      </div>
      <span id="nwCount" style="font-size:10px;color:#f5c542;white-space:nowrap;margin-top:2px"></span>
    </div>
    <div id="btPanel" style="display:none"></div>
    <div id="themePicker" style="display:none"></div>
    <div id="sfoot">
      <button id="delD" title="È˜terge desenul selectat (Delete)">ðŸ—‘ È˜terge desen</button>
      <button id="exp">Export JSON</button>
      <button id="expEA">ðŸ“¤ MT5 EA</button>
      <button id="imp">Import JSON</button>
      <button id="cls">È˜terge tot</button>
      <input type="file" id="impFile" accept="application/json" style="display:none">
    </div>
  </div>
</div>
<div id="ctxMenu">
  <div class="ci" data-cmd="pointer">ðŸ–± Select<span class="kbd">V</span></div>
  <div class="ci long" data-cmd="long">â–² LONG<span class="kbd">B</span></div>
  <div class="ci short" data-cmd="short">â–¼ SHORT<span class="kbd">S</span></div>
  <div class="csep"></div>
  <div class="ci" data-cmd="line">ðŸ“ Linie<span class="kbd">L</span></div>
  <div class="ci" data-cmd="rect">ðŸŸ¦ ZonÄƒ<span class="kbd">R</span></div>
  <div class="ci" data-cmd="hline">âž– H-Linie<span class="kbd">H</span></div>
  <div class="ci" data-cmd="arrow">ðŸ’¬ NotÄƒ<span class="kbd">N</span></div>
  <div class="csep"></div>
  <div class="ci" data-cmd="lockrr" id="ctxLockRR">ðŸ”’ R:R fix</div>
  <div class="ci" data-cmd="isolate" id="ctxIsolate">ðŸ” IzoleazÄƒ la selectare</div>
  <div class="ci" data-cmd="slanchor" id="ctxSlAnchor">ðŸ“Œ SL Anchor</div>
  <div id="ctxPosSet" class="ci" style="cursor:default;flex-wrap:wrap;gap:4px;padding:4px 8px;display:none">
    <span style="color:#787b86;font-size:10px;width:100%">SetÄƒri poziÈ›ie selectatÄƒ:</span>
    <span style="display:flex;gap:4px;width:100%;align-items:center;flex-wrap:wrap">
      <label style="font-size:11px;display:flex;gap:3px;align-items:center"><input id="ctxExpOn" type="checkbox"> Expiry</label>
      <input id="ctxExpN" type="number" min="1" max="500" step="1" style="width:52px;background:#363a45;border:1px solid var(--line);color:var(--text);border-radius:5px;padding:2px 4px"> candele
      <button class="rrpreset" id="ctxEntryNow" style="flex:none">Entry aici</button>
      <button class="rrpreset" id="ctxEntryNext" style="flex:none">Entry urm.</button>
    </span>
  </div>
  <div class="csep"></div>
  <div class="ci" style="cursor:default;flex-wrap:wrap;gap:4px;padding:4px 8px">
    <span style="color:#787b86;font-size:10px;width:100%">AplicÄƒ R:R pe poziÈ›ia selectatÄƒ:</span>
    <span style="display:flex;gap:4px;width:100%">
      <button class="rrpreset" data-rr="1">1</button>
      <button class="rrpreset" data-rr="1.5">1.5</button>
      <button class="rrpreset" data-rr="2">2</button>
      <button class="rrpreset" data-rr="2.5">2.5</button>
      <button class="rrpreset" data-rr="3">3</button>
    </span>
  </div>
  <div class="ci" data-cmd="bt">ðŸ§ª Backtest</div>
  <div class="ci" data-cmd="export">ðŸ“¦ Export JSON</div>
</div>
<div id="toast"></div>
<script>
"use strict";
let DATA = [], DATA_M1 = [];
let DATA_BASE = DATA;              // M15 original â€” sursa pentru agregari
function __setData(o){ if(!o) return; DATA = o.m15 || []; DATA_M1 = o.m1 || []; DATA_BASE = DATA; __boot(); }
window.GBPUSD_DEFAULT_PROFILE={"markers":[{"bar":148,"price":1.35664,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-04 10:15 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1777888800000,"seen_through":null,"id":4},{"bar":207,"price":1.35304,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-05 01:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1777941900000,"seen_through":null,"id":7},{"bar":262,"price":1.35484,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-05 14:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1777991400000,"seen_through":null,"id":9},{"bar":300,"price":1.35416,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-05-06 00:15 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1778025600000,"seen_through":null,"id":10},{"bar":375,"price":1.35908,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-06 19:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1778093100000,"seen_through":null,"id":11},{"bar":492,"price":1.35519,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-08 00:15 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1778198400000,"seen_through":null,"id":12},{"bar":511,"price":1.3553,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-05-08 05:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1778215500000,"seen_through":null,"id":13},{"bar":514,"price":1.35541,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-05-08 05:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1778218200000,"seen_through":null,"id":14},{"bar":621,"price":1.3592,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-11 08:30 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1778487300000,"seen_through":null,"id":15},{"bar":745,"price":1.3529,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-12 15:30 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1778598900000,"seen_through":null,"id":16},{"bar":802,"price":1.35358,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-05-13 05:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1778650200000,"seen_through":null,"id":17},{"bar":811,"price":1.35449,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-05-13 08:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1778658300000,"seen_through":null,"id":18},{"bar":878,"price":1.35301,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-05-14 00:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1778718600000,"seen_through":null,"id":19},{"bar":913,"price":1.35192,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-14 09:30 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1778750100000,"seen_through":null,"id":20},{"bar":1003,"price":1.33532,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-15 08:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1778831100000,"seen_through":null,"id":21},{"bar":1087,"price":1.3312,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-18 05:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1779079500000,"seen_through":null,"id":22},{"bar":1111,"price":1.33716,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-05-18 11:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1779101100000,"seen_through":null,"id":23},{"bar":1180,"price":1.3417,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-19 04:15 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1779163200000,"seen_through":null,"id":24},{"bar":1200,"price":1.33997,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-19 09:15 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1779181200000,"seen_through":null,"id":25},{"bar":1267,"price":1.34018,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-20 02:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1779241500000,"seen_through":null,"id":26},{"bar":1284,"price":1.33997,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-05-20 06:15 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1779256800000,"seen_through":null,"id":27},{"bar":1293,"price":1.33897,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-05-20 08:30 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1779264900000,"seen_through":null,"id":28},{"bar":1316,"price":1.33998,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-05-20 14:15 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1779285600000,"seen_through":null,"id":29},{"bar":1488,"price":1.34246,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-22 09:15 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1779440400000,"seen_through":null,"id":30},{"bar":1571,"price":1.34765,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-25 06:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1779687900000,"seen_through":null,"id":31},{"bar":1606,"price":1.34999,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-05-25 14:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1779719400000,"seen_through":null,"id":32},{"bar":1650,"price":1.35009,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-26 01:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1779759000000,"seen_through":null,"id":33},{"bar":1782,"price":1.34473,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-27 10:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1779877800000,"seen_through":null,"id":34},{"bar":1851,"price":1.34055,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-28 04:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1779939900000,"seen_through":null,"id":35},{"bar":1962,"price":1.34405,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-29 07:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1780039800000,"seen_through":null,"id":36},{"bar":1965,"price":1.34441,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-29 08:30 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1780042500000,"seen_through":null,"id":37},{"bar":1975,"price":1.34166,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-05-29 11:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1780051500000,"seen_through":null,"id":38},{"bar":2060,"price":1.34632,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-06-01 08:15 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1780300800000,"seen_through":null,"id":39},{"bar":2137,"price":1.346,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-06-02 03:30 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1780370100000,"seen_through":null,"id":40},{"bar":2186,"price":1.34732,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-06-02 15:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1780414200000,"seen_through":null,"id":41},{"bar":2227,"price":1.34544,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-06-03 02:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1780451100000,"seen_through":null,"id":42},{"bar":2335,"price":1.34248,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-06-04 05:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1780548300000,"seen_through":null,"id":43},{"bar":2455,"price":1.3454,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-06-05 11:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1780656300000,"seen_through":null,"id":44},{"bar":2542,"price":1.33297,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-06-08 08:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1780907400000,"seen_through":null,"id":45},{"bar":2656,"price":1.33956,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-06-09 13:15 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1781010000000,"seen_through":null,"id":46},{"bar":2747,"price":1.33948,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-06-10 12:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1781091900000,"seen_through":null,"id":47},{"bar":2895,"price":1.34196,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-06-12 01:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1781225100000,"seen_through":null,"id":48},{"bar":3189,"price":1.34297,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-06-17 02:30 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1781662500000,"seen_through":null,"id":49},{"bar":3234,"price":1.3406,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-06-17 13:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1781703000000,"seen_through":null,"id":50},{"bar":3472,"price":1.32099,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-06-22 01:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1782091800000,"seen_through":null,"id":51},{"bar":3480,"price":1.32259,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-06-22 03:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1782099000000,"seen_through":null,"id":52},{"bar":3596,"price":1.32408,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-06-23 08:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1782203400000,"seen_through":null,"id":53},{"bar":3604,"price":1.32216,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-06-23 10:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1782210600000,"seen_through":null,"id":54},{"bar":3759,"price":1.31641,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-06-25 01:30 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1782350100000,"seen_through":null,"id":55},{"bar":3811,"price":1.31587,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-06-25 14:30 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1782396900000,"seen_through":null,"id":56},{"bar":3855,"price":1.31897,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-06-26 01:30 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1782436500000,"seen_through":null,"id":57},{"bar":3947,"price":1.31939,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-06-29 00:30 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1782692100000,"seen_through":null,"id":58},{"bar":3952,"price":1.31956,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-06-29 01:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1782696600000,"seen_through":null,"id":59},{"bar":3966,"price":1.32028,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-06-29 05:15 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1782709200000,"seen_through":null,"id":60},{"bar":4195,"price":1.32401,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-07-01 14:30 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1782915300000,"seen_through":null,"id":61},{"bar":4238,"price":1.328,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-07-02 01:15 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1782954000000,"seen_through":null,"id":62},{"bar":4477,"price":1.3342,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-07-06 13:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1783341900000,"seen_through":null,"id":63},{"bar":4482,"price":1.33444,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-07-06 14:15 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1783346400000,"seen_through":null,"id":64},{"bar":4542,"price":1.33912,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-07-07 05:15 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1783400400000,"seen_through":null,"id":65},{"bar":4781,"price":1.33989,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-07-09 17:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1783615500000,"seen_through":null,"id":66},{"bar":4930,"price":1.33785,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-07-13 06:15 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1783922400000,"seen_through":null,"id":67},{"bar":5027,"price":1.33599,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-07-14 06:30 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1784009700000,"seen_through":null,"id":68},{"bar":5032,"price":1.33657,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-07-14 07:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1784014200000,"seen_through":null,"id":69},{"bar":5107,"price":1.33952,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-07-15 02:30 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1784081700000,"seen_through":null,"id":70},{"bar":5293,"price":1.34745,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-07-17 01:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1784249100000,"seen_through":null,"id":71},{"bar":5359,"price":1.34461,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-07-17 17:30 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1784308500000,"seen_through":null,"id":72},{"bar":5505,"price":1.34365,"dir":"LONG","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bull Â· fill@2026-07-21 06:00 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1784612700000,"seen_through":null,"id":73},{"bar":6010,"price":1.32799,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-07-28 12:15 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1785240000000,"seen_through":null,"id":74},{"bar":6062,"price":1.32849,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-07-29 01:15 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1785286800000,"seen_through":null,"id":75},{"bar":6072,"price":1.32888,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-07-29 03:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1785295800000,"seen_through":null,"id":76},{"bar":6284,"price":1.346,"dir":"SHORT","sl":8,"tp":8,"ghost":true,"fc":2,"note":"ðŸ”¬ RETRACE bear Â· fill@2026-07-31 08:45 Â· SL 8.0p / TP 8.0p Â· EOD 21:30","created":1785486600000,"seen_through":null,"id":77},{"id":1,"bar":47,"price":1.35964,"dir":"LONG","ghost":true,"note":"ðŸ‘» NW bull Â· body 14.5p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786331932524,"seen_through":249},{"id":2,"bar":125,"price":1.35892,"dir":"SHORT","ghost":true,"note":"ðŸ‘» NW bear Â· body -9.0p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786331932524,"seen_through":249},{"id":3,"bar":131,"price":1.35842,"dir":"LONG","ghost":true,"note":"ðŸ‘» NW bull Â· body 13.6p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786331932524,"seen_through":249},{"id":5,"bar":184,"price":1.35188,"dir":"LONG","ghost":true,"note":"ðŸ‘» NW bull Â· body 13.4p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786331932524,"seen_through":249},{"id":6,"bar":196,"price":1.35371,"dir":"SHORT","ghost":true,"note":"ðŸ‘» NW bear Â· body -6.3p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786331932524,"seen_through":249},{"id":8,"bar":231,"price":1.3524,"dir":"SHORT","ghost":true,"note":"ðŸ‘» NW bear Â· body -8.2p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786331932524,"seen_through":249},{"id":78,"bar":12,"price":1.37307,"dir":"LONG","ghost":true,"note":"ðŸ‘» NW bull Â· body 7.2p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":79,"bar":18,"price":1.37398,"dir":"SHORT","ghost":true,"note":"ðŸ‘» NW bear Â· body -7.2p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":80,"bar":23,"price":1.37295,"dir":"LONG","ghost":true,"note":"ðŸ‘» NW bull Â· body 7.2p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":81,"bar":30,"price":1.37449,"dir":"SHORT","ghost":true,"note":"ðŸ‘» NW bear Â· body -6.5p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":82,"bar":48,"price":1.3774,"dir":"SHORT","ghost":true,"note":"ðŸ‘» NW bear Â· body -13.1p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":83,"bar":49,"price":1.3761,"dir":"LONG","ghost":true,"note":"ðŸ‘» NW bull Â· body 10.1p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":84,"bar":75,"price":1.37094,"dir":"LONG","ghost":true,"note":"ðŸ‘» NW bull Â· body 14.9p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":85,"bar":89,"price":1.37419,"dir":"SHORT","ghost":true,"note":"ðŸ‘» NW bear Â· body -5.7p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":86,"bar":136,"price":1.37281,"dir":"SHORT","ghost":true,"note":"ðŸ‘» NW bear Â· body -3.0p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":87,"bar":146,"price":1.36912,"dir":"LONG","ghost":true,"note":"ðŸ‘» NW bull Â· body 6.2p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":88,"bar":158,"price":1.36533,"dir":"SHORT","ghost":true,"note":"ðŸ‘» NW bear Â· body -44.3p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":89,"bar":169,"price":1.36049,"dir":"LONG","ghost":true,"note":"ðŸ‘» NW bull Â· body 8.5p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":90,"bar":188,"price":1.36352,"dir":"SHORT","ghost":true,"note":"ðŸ‘» NW bear Â· body -4.8p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":91,"bar":200,"price":1.36545,"dir":"SHORT","ghost":true,"note":"ðŸ‘» NW bear Â· body -4.6p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":92,"bar":212,"price":1.36488,"dir":"SHORT","ghost":true,"note":"ðŸ‘» NW bear Â· body -11.8p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":93,"bar":225,"price":1.36256,"dir":"LONG","ghost":true,"note":"ðŸ‘» NW bull Â· body 3.2p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":94,"bar":233,"price":1.36629,"dir":"LONG","ghost":true,"note":"ðŸ‘» NW bull Â· body 8.0p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":95,"bar":257,"price":1.36341,"dir":"LONG","ghost":true,"note":"ðŸ‘» NW bull Â· body 15.1p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847},{"id":96,"bar":269,"price":1.36532,"dir":"SHORT","ghost":true,"note":"ðŸ‘» NW bear Â· body -12.9p Â· SL 5p / TP 5p Â· PASS/SKIP? DE CE?","sl":5,"tp":5,"fc":60,"created":1786334704779,"seen_through":20847}],"drawings":[],"indicators":[{"type":"omar","on":true,"params":{"pivotLen":5,"showStruct":true,"showBosChoch":true,"showNoWick":true,"anchorType":"Body"}}],"omarParams":{"pivotLen":5,"showStruct":true,"showBosChoch":true,"showNoWick":true,"anchorType":"Body"},"settings":{"anchored":true,"sidebarCollapsed":false,"lockRR":false,"magnet":"hard","isolate":false,"nwVisible":true,"treeView":"all","botActivated":false,"theme":"dark"}};   // PROFIL DEFAULT (24 drawing lines + 5 trades) â€” din profiles/gbpusd_draw.profile.json, salvat in _charts/
// DATE EXTERNE (separate de cod): gbpusd_ohlc.json (http) sau gbpusd_ohlc.js (file:// â€” fetch blocat de CORS)
(async () => {
  await Promise.resolve();   // asteapta sfarsitul parse-ului scriptului (const cv/ctx etc. in TDZ altfel)
  let o = null;
  if (window.GBPUSD_OHLC && Array.isArray(window.GBPUSD_OHLC.m15)) { o = window.GBPUSD_OHLC; }
  else {
    try { const r = await fetch("gbpusd_ohlc.json"); if (r.ok) o = await r.json(); } catch(e) {}
    if (!o) {
      o = await new Promise((res, rej) => {
        const s = document.createElement("script");
        s.src = "gbpusd_ohlc.js";
        s.onload = () => res(window.GBPUSD_OHLC || null);
        s.onerror = () => rej(new Error("gbpusd_ohlc.js lipseste langa HTML (data file)"));
        document.head.appendChild(s);
      });
    }
  }
  if (o) { DATA = o.m15 || DATA; DATA_M1 = o.m1 || DATA_M1; DATA_BASE = DATA; __boot(); }
})();
const DIG = 5, PIP = 0.0001;   // PIP = pip REAL GBPUSD (5 digiti) â€” NU point 0.00001; analizorul (analyze_markers.py) foloseste tot 0.0001
const COL = { bg:"#131722", grid:"#232833", up:"#26a69a", down:"#ef5350",
              text:"#d1d4dc", cross:"#758696", line:"#2a2e39", dimUp:"#3d6b66", dimDn:"#6b4a48",
              vol:"#3a3f4d", accent:"#2962ff", draw:"#4fc3f7" };
const el = id => document.getElementById(id);
// ---- TEMA CULORI (preset-uri + accent custom, persistata) ----
const THEMES={
  dark:{ name:"Dark",   vars:{bg:"#131722",grid:"#232833",panel:"#1e222d",text:"#d1d4dc",up:"#26a69a",down:"#ef5350",accent:"#2962ff",line:"#2a2e39"} },
  light:{ name:"Light", vars:{bg:"#f5f6f8",grid:"#e2e5ea",panel:"#ffffff",text:"#131722",up:"#0e8a7e",down:"#d64545",accent:"#2962ff",line:"#d8dbe2"} },
  blue:{ name:"Blue",   vars:{bg:"#0d1b2a",grid:"#1b2b3f",panel:"#152238",text:"#d1d4dc",up:"#26a69a",down:"#ef5350",accent:"#42a5f5",line:"#23354d"} },
  green:{ name:"Green", vars:{bg:"#0f1f14",grid:"#1c3623",panel:"#16281b",text:"#d1d4dc",up:"#4caf50",down:"#ef5350",accent:"#66bb6a",line:"#24402a"} },
};
let themeName="dark", themeAccent=null;
function applyTheme(name, accent){
  const t=THEMES[name]||THEMES.dark; themeName=name;
  const v=Object.assign({}, t.vars);
  if(accent) v.accent=accent; else if(themeAccent) v.accent=themeAccent;
  for(const k in v) document.documentElement.style.setProperty("--"+k, v[k]);
  COL.bg=v.bg; COL.grid=v.grid; COL.up=v.up; COL.down=v.down; COL.text=v.text; COL.line=v.line; COL.accent=v.accent;
  try{ localStorage.setItem("gbpusd_theme", JSON.stringify({name:themeName, accent:themeAccent})); }catch(e){}
  requestRender();
}
function renderThemePicker(){
  const pk=el("themePicker");
  pk.innerHTML='<div class="tprow">'+Object.keys(THEMES).map(k=>
    '<button class="tp'+(k===themeName?" on":"")+'" data-t="'+k+'" style="background:'+THEMES[k].vars.bg+';color:'+THEMES[k].vars.text+'">'+THEMES[k].name+'</button>').join("")+'</div>'+
    '<label>Accent custom</label><input type="color" id="tpAccent" value="'+((themeAccent||COL.accent))+'" style="display:block">';
  pk.querySelectorAll(".tp").forEach(b=>b.onclick=()=>{ applyTheme(b.dataset.t, themeAccent); renderThemePicker(); });
  el("tpAccent").oninput=ev=>{ themeAccent=ev.target.value; applyTheme(themeName, themeAccent); renderThemePicker(); };
}
el("sideBtn").onclick=()=>{ sidebarCollapsed=!sidebarCollapsed; el("sidebar").classList.toggle("collapsed", sidebarCollapsed); el("sideBtn").textContent = sidebarCollapsed ? "â–¶" : "â—€";
  try{ localStorage.setItem("gbpusd_full_settings", JSON.stringify({lockRR, magnet:magnetMode, isolate:isolateSel, sidebarCollapsed, slAnchor:slAnchorMode})); }catch(e){}
  setTimeout(resize, 200);   // FIX P4: dupa transition-ul CSS (.18s) â€” W se recalculeaza pe noul layout
  toast(sidebarCollapsed ? "Panou ascuns â€” â—€ revine" : "Panou afiÈ™at");
  requestRender(); };
el("themeBtn").onclick=()=>{ const pk=el("themePicker");
  if(pk.style.display==="block"){ pk.style.display="none"; return; }
  renderThemePicker(); pk.style.display="block"; };
document.addEventListener("click", ev=>{ const pk=el("themePicker");
  if(pk.style.display==="block" && !pk.contains(ev.target) && ev.target.id!=="themeBtn") pk.style.display="none"; });

const cv = document.getElementById("cv"), ctx = cv.getContext("2d");
let W=0, H=0, DPR=1, drawOps=0;
let view = { start: 0, count: 250 };
let blind = false, cutoff = 0;   // SABIN: pornim cu lookahead OFF -> se vede TOT chart-ul
                                  // (trade-uri + MSS/FVG/liq) de la deschidere. Lookahead e activabil din buton.
let lookaheadPlacing=false;   // v7.47: mod plasare lookahead (butonul Lookahead) â€” click pune linia O DATA, apoi click-ul revine la normal   // LOOKAHEAD OFF by default â€” viitorul e gri, dezvÄƒlui cu +10/+60 (butonul ðŸ”’)
let sessionId = Date.now();
let markers = [], drawings = [];
let hist=[], histIdx=-1;   // UNDO/REDO stack â€” declarat INAINTE de save() (altfel TDZ crash la load)
let mkSeq = 0, drwSeq = 0, xhair=null, drag=null, dlgOpen=false, hoverMk=null, rafPending=false;
// ---- TAG-URI (v7.42): desenele au etichete permanente â€” trade = #NN Â· desene = litera tip + cifre ----
const TAG_LETTER={ line:"L", rect:"Z", hline:"H", note:"N", arrow:"A", pen:"P", omar:"O" };
function tagOf(obj){
  if(!obj) return null;
  if(obj.kind==="m" || (obj.dir && !obj.pts)) return obj.tag || null;      // marker trade
  return obj.tag || null;                                                   // drawing
}
function nextTradeTag(){ let n=0; for(const m of markers) if(m.tag && /^#\d+$/.test(m.tag)) n=Math.max(n,+m.tag.slice(1)); return "#"+String(n+1).padStart(2,"0"); }
function nextDrawTag(type){ const L=TAG_LETTER[type]||"X"; let n=0;
  for(const d of drawings) if(d.tag && d.tag[0]===L && /^[A-Z]\d+$/.test(d.tag)) n=Math.max(n,+d.tag.slice(1));
  return L+String(n+1); }
function hitTagAt(x, y){
  for(const m of [...markers].reverse()){
    if(m.bar<view.start || m.bar>=viewEnd()) continue;
    const ex=xAtBar(m.bar), ey=yAtPrice(m.price);
    if(Math.hypot(x-ex, y-ey)<16 && m.tag) return m.tag;
  }
  for(const d of [...drawings].reverse()){
    if(!d.tag || !Array.isArray(d.pts)||!d.pts.length) continue;
    for(const p of d.pts){
      if(p && Number.isInteger(p.bar) && isFinite(p.price)){
        const hx=xAtBar(p.bar), hy=yAtPrice(p.price);
        if(Math.hypot(x-hx, y-hy)<=10) return d.tag;
      }
    }
    if(d.type==="hline" && d.pts.length){ const hx=xAtBar(d.pts[0].bar), hy=yAtPrice(d.pts[0].price); if(Math.abs(y-hy)<=8 && Math.abs(x-hx)<=W) return d.tag; }
  }
  return null;
}
function insertAtCursor(el, text){
  if(!el) return;
  const s0=el.selectionStart!=null?el.selectionStart:el.value.length, s1=el.selectionEnd!=null?el.selectionEnd:el.value.length;
  el.value=el.value.slice(0,s0)+text+el.value.slice(s1);
  const pos=s0+text.length;
  if(el.setSelectionRange) el.setSelectionRange(pos,pos);
  el.dispatchEvent(new Event("input",{bubbles:true}));
  el.focus();
}
function ensureTags(){   // backfill: desenele vechi fara tag primesc eticheta (ca TV â€” fiecare obiect are ID)
  let tr=0, trMax=0; for(const m of markers) if(m.tag && /^#\d+$/.test(m.tag)) trMax=Math.max(trMax,+m.tag.slice(1));
  for(const m of markers) if(m.dir && !m.pts && !m.tag){ trMax++; m.tag="#"+String(trMax).padStart(2,"0"); }
  const used={}; for(const d of drawings) if(d.tag && /^[A-Z]\d+$/.test(d.tag)){ const L=d.tag[0]; used[L]=Math.max(used[L]||0,+d.tag.slice(1)); }
  for(const d of drawings) if(!d.tag){ const L=TAG_LETTER[d.type]||"X"; used[L]=(used[L]||0)+1; d.tag=L+used[L]; }
  save();
}

let lastSl=6.5, lastTp=6.5, lastFc=60, lastExp=11;   // v7.51: expiry default 11 candele â€” pus cu arrow pe NW candle, expiry-ul se termina bine in dreapta   // "same size": ultimele setari SL/TP/forecast/EXPIRY devin default la urmatorul marker
// lastExp = expiry entry (bare): dacÄƒ entry-ul nu e atins Ã®n N candele de la candela urmÄƒtoare => poziÈ›ia EXPIRED
try{ const s=JSON.parse(localStorage.getItem("gbpusd_last")||"null"); if(s){ if(s.sl>0)lastSl=s.sl; if(s.tp>0)lastTp=s.tp; if(s.fc>=20)lastFc=s.fc; if(s.exp>=1)lastExp=s.exp;
  // LOOKAHEAD DEFAULT: dacÄƒ ai salvat pÃ¢nÄƒ unde ai dezvÄƒluit, pornim fix acolo (nu mai dai +60 de fiecare datÄƒ)
  if(s.lookaheadTs!=null){ const lb=findBar(s.lookaheadTs); if(lb!=null) cutoff=Math.min(DATA.length-1, lb); }
} }catch(e){}
let posDraft=null;                        // pozitie LONG/SHORT in curs de plasare (mutabila pe chart)
let selMk=null;                           // marker selectat (highlight + handles + sageti nudge)
const TOOLS={ POINTER:"pointer", LINE:"line", PEN:"pen", RECT:"rect", HLINE:"hline", ARROW:"arrow", LONG:"long", SHORT:"short" };
let tool=TOOLS.POINTER, draft=null, sel=null, selSet=[];   // selSet = multi-select (desene + marker-e)
let dlgOpenedAt=0;   // anti-close: mouseup-ul care a deschis dialogul e ignorat 300ms
let dlgCtrlInsert=false;   // v7.42c: ultimul mousedown = Ctrl+click pt tag â€” mouseup-ul NU inchide dialogul
let TF = "M15";                      // timeframe curent (M1/M15/H1/H4/D1)
// Agregare M15 -> H1/H4/D1 (grupeaza pe bucket de timp UTC; robust la gap-uri de weekend); M1 = date reale
function buildTF(tf){
  if(tf==="M1") return DATA_M1.length ? DATA_M1 : DATA_BASE;   // M1 real (94k bare) dacÄƒ existÄƒ
  if(tf==="M15") return DATA_BASE;
  const bucket = tf==="H1" ? 3600 : tf==="H4" ? 14400 : 86400;
  const out=[]; let cur=null;
  for(const b of DATA_BASE){
    const bk=Math.floor(b[0]/bucket);
    if(!cur || cur.bk!==bk){ if(cur) out.push([cur.ts,cur.o,cur.h,cur.l,cur.c,cur.v]);
      cur={bk, ts:b[0], o:b[1], h:b[2], l:b[3], c:b[4], v:b[5]}; }
    else { cur.h=Math.max(cur.h,b[2]); cur.l=Math.min(cur.l,b[3]); cur.c=b[4]; cur.v+=b[5]; }
  }
  if(cur) out.push([cur.ts,cur.o,cur.h,cur.l,cur.c,cur.v]);
  return out;
}
function switchTF(tf){
  if(tf===TF) return;
  // salveaza ts-urile marker-elor + desenelor, apoi remapeaza pe noul DATA (bar -> findBar(ts))
  const mkTs = markers.map(m=>DATA[m.bar]?DATA[m.bar][0]:null);
  const drTs = drawings.map(d=>d.pts.map(p=>DATA[p.bar]?DATA[p.bar][0]:null));
  // FIX v7.29: pastram ANCHORA de timp + FEREASTRA vizibila + progresul blind (nu mai sarim la inceputul istoricului)
  const anchorTs = DATA[Math.min(DATA.length-1, view.start + view.count)][0];   // v7.32: right-bar-stays mereu (anchored const true)
  const spanS = Math.max(60, (DATA[Math.min(viewEnd()-1, DATA.length-1)][0] - DATA[view.start][0]));
  const revealedTs = blind ? DATA[Math.min(cutoff, DATA.length-1)][0] : null;
  DATA = buildTF(tf); TF=tf;
  markers.forEach((m,i)=>{ if(mkTs[i]!=null){ const b=findBarFloor(mkTs[i]); if(b>=0) m.bar=b; } });   // v7.54: floor (bara exactÄƒ poate lipsi pe alt TF)
  drawings.forEach((d,di)=>{ d.pts.forEach((p,pi)=>{ if(drTs[di]&&drTs[di][pi]!=null){ const b=findBarFloor(drTs[di][pi]); if(b>=0) p.bar=b; } }); });
  const barS = tf==="M1" ? 60 : tf==="M15" ? 900 : tf==="H1" ? 3600 : tf==="H4" ? 14400 : 86400;
  const anchorB = findBar(anchorTs); if(anchorB==null) { view.start=0; view.count=Math.min(250,DATA.length); }
  else {
    view.count = clampCount(Math.max(30, Math.round(spanS/barS)));
    const frac = 1;   // v7.32: right-bar-stays mereu (anchored const true)
    view.start = Math.max(0, Math.min(Math.max(0,DATA.length-view.count), Math.round(anchorB - frac*view.count)));
  }
  if(revealedTs!=null){ const rc=findBar(revealedTs); if(rc!=null) cutoff=rc; }
  else cutoff = blind ? Math.min(DATA.length-1, view.start+view.count-1) : DATA.length-1;
  yOff=0; computeOmar(); indCache={}; renderIndList(); save();
  yLock=null; zoomAnim=null; yRangeCache=null;   // FIX: DATA s-a schimbat â€” scala veche e stale
  document.querySelectorAll("#tfbar button").forEach(b=>b.classList.toggle("on", b.dataset.tf===tf));
  el("shead").querySelector("b").textContent="GBPUSD.pro Â· "+tf+" Â· 01 Mai â€“ 31 Iul 2026";
  requestRender(); toast("Timeframe: "+tf+" ("+DATA.length+" bare)");
}
document.querySelectorAll("#tfbar button").forEach(b=>b.onclick=()=>switchTF(b.dataset.tf));
let measure=null;    // Shift+drag = dreptunghi de masura (pips + bare/timp)
let dlgPreview=null; // preview LONG/SHORT in spatele dialogului, live
let dlgTarget=null;   // v7.43: obiectul editat in dialog (marker sau drawing) â€” pt auto-save la click-out
let dlgNoteBase="";    // valoarea notei la deschidere â€” salvez doar daca s-a modificat
let zoomAnim=null;   // animatie zoom smooth orizontal (rAF)
let vzoom=1, vzoomAnim=null;   // zoom VERTICAL (inaltimea candelelor, ca price scale TV)
const anchored=true; // right-bar-stays MEREU (ca TradingView) â€” toggle-ul a fost ELIMINAT (v7.32): zoomul orizontal se limiteazÄƒ la ultima candelÄƒ vizibilÄƒ din dreapta, nu â€žfuge" Ã®n dreapta la zoom out Â· Ctrl+scroll = pointer (handled direct in wheel handler)
let yOff=0;          // pan VERTICAL liber (unitati de pret) â€” chart-ul se misca oriunde
let lastPx=null;     // ultima pozitie X a pointerului pe chart (ancla zoom orizontal la mouse)
let priceBarDrag=null, yRangeCache=null, yLock=null;   // yLock = scala verticala inghetata (anchored OFF width-only)
// FIX TDZ CRITIC: indicators/omarParams declarate INAINTE de load â€” altfel accesul din blocul de load
// (indicators=o.indicators) arunca ReferenceError (let e in TDZ pana la linia de declaratie) => persistarea
// normalizarii ghost NU se salva => marker-e vechi fara 'ghost' dispareau de pe chart (ex. #92)
let indicators=[];
let omarParams={};

function storageAvailable(t){ try{ const s=window[t], x="__t__"; s.setItem(x,x); s.removeItem(x); return true; }catch(e){ return false; } }
const storageOK = storageAvailable("localStorage");
function __restoreState(){   // RULEAZA DUPA incarcarea datelor (DATA.length > 0 â€” altfel filtrul sterge tot)
if(storageOK){
  try{
    // PROFIL: gbpusd_profile (nou, dedicat) > gbpusd_profile_bak (backup) > gbpusd_data (vechi) â€” mereu se incarca
    const s=localStorage.getItem("gbpusd_full_profile") || localStorage.getItem("gbpusd_full_profile_bak") || localStorage.getItem("gbpusd_full_data");
    const o = s ? JSON.parse(s) : (window.GBPUSD_DEFAULT_PROFILE || null);   // FALLBACK: profilul default din _charts/profiles/ (ca TV â€” desenele sunt ACOLO la deschidere)
    if(o){
      // v7.53: PROFIL TF-SAFE â€” dacÄƒ e salvat pe alt TF (ex. M1), detectÄƒm + remapÄƒm prin timestamp
      const srcTF=(o.tf==="M1"||o.tf==="M15"||o.tf==="H1"||o.tf==="H4"||o.tf==="D1")?o.tf:detectProfileTF(o);
      const recovered=!!(srcTF && srcTF!=="M15");
      if(recovered){ remapProfileTF(o, srcTF); console.log("[chart] profil recuperat de pe "+srcTF+" â†’ M15"); }
      markers=(Array.isArray(o.markers)?o.markers:[]).filter(m=>m&&Number.isInteger(m.bar)&&m.bar>=0&&m.bar<DATA.length)
        .map(m=>({...m, ghost:!!m.ghost, tf:(m.tf==="M1"||m.tf==="M15"||m.tf==="H1"||m.tf==="H4"||m.tf==="D1")?m.tf:"M15",   // v7.54: ancora de evaluare (TF de plasare + ts)
          ts:(m.ts!=null&&isFinite(m.ts))?m.ts:(DATA[m.bar]?DATA[m.bar][0]:undefined)}));   // FIX CRITIC: marker-ele vechi fara 'ghost' (undefined) -> false â€” altfel drawMarker le ascundea (ex. #92 editata inainte de v7.31.35)
      drawings=(Array.isArray(o.drawings)?o.drawings:[]).filter(d=>d&&Array.isArray(d.pts)&&d.pts.length>=1&&d.pts.every(p=>Number.isInteger(p.bar)&&p.bar>=0&&p.bar<DATA.length&&isFinite(p.price)));
      if(Array.isArray(o.indicators)&&o.indicators.length) indicators=o.indicators
        .filter(x=>IND_TYPES[x.type])
        .map(x=>({type:x.type, on:x.on!==false, params:Object.assign({}, IND_TYPES[x.type].defaults, x.params||{})}));
      if(o.omarParams) omarParams=Object.assign({}, IND_TYPES.omar.defaults, o.omarParams);
      if(recovered && (markers.length||drawings.length)){   // persistÄƒm profilul corectat (M15 + tf) â€” ca sÄƒ nu mai detecteze data viitoare
        try{ const prof=JSON.stringify(normalizeToM15({markers,drawings,indicators,omarParams}));
          localStorage.setItem("gbpusd_full_profile", prof);
          localStorage.setItem("gbpusd_full_profile_bak", prof);
          toast("ðŸ”§ Profil recuperat: era salvat pe "+srcTF+" â†’ remapat pe M15 (marker-e + desene)");
        }catch(e){} }
    }
  }catch(e){}
}
// FIX v7.31: re-numerotez ghost-urile secvential 1..N la load (ID-urile 600k/700k din versiunile vechi dispar â€” raman #1..#N curate)
{ let gseq=1;
  const ghostsAll=markers.filter(m=>m.ghost).sort((a,b)=>a.bar-b.bar);
  for(const g of ghostsAll) g.id=gseq++;
  // persist normalizarea ghost (marker-e vechi fara 'ghost' -> false, altfel dispar de pe chart â€” ex. #92) + re-numerotarea
  if(markers.length){ try{ localStorage.setItem("gbpusd_full_data", JSON.stringify({markers,drawings,indicators,omarParams})); }catch(e){} }
}
mkSeq = markers.reduce((mx,m)=>Math.max(mx, typeof m.id==="number"?m.id:0), 0);
drwSeq = drawings.reduce((mx,d)=>Math.max(mx, typeof d.id==="number"?d.id:0), 0);
if(!storageOK) el("banner").style.display="block";
}
let nwVisible=false;         // ghost markers vizibili? (ðŸ‘» NW = toggle: click 1 aratÄƒ, click 2 ascunde) â€” declarat INAINTE de renderList (TDZ fix)
let treeView="all";          // object tree: 'all' | 'ai' (doar ghost) | 'mine' (doar ale tale) â€” butonul ðŸ¤– Bot comutÄƒ asta
let botActivated=false;      // la load, ghost-urile bot din storage NU se afiÈ™eazÄƒ Ã®n listÄƒ pÃ¢nÄƒ la prima apÄƒsare ðŸ¤– Bot (refresh = start curat)
let lockRR=false;            // settings: cÃ¢nd muÈ›i SL â†’ TP se mutÄƒ proporÈ›ional (acelaÈ™i R:R), È™i invers
let sidebarCollapsed=false;  // FIX P4: panoul din dreapta colapsat? (persistat in gbpusd_settings)
let magnetMode="hard";       // ðŸ§² MAGNET (ca TradingView): "off" | "soft" | "hard" â€” lipeÈ™te preÈ›ul de OHLC/wick/SL/TP/desene. Ctrl È›inut = hard temporar
let isolateSel=true;         // ðŸ” IZOLARE la selectare (default ON): cÃ¢nd selectezi o poziÈ›ie, pe chart se vede DOAR ea (restul dispar â€” fÄƒrÄƒ clutter). Comutabil din click dreapta.
let slAnchorMode=false;      // ðŸ“Œ SL ANCHOR: cÃ¢nd tragi SL-ul pe o lumÃ¢nare cu Ctrl, salveazÄƒ referinÈ›a Ã®n nota poziÈ›iei
try{ const st=JSON.parse(localStorage.getItem("gbpusd_full_settings")||"null"); if(st){ lockRR=!!st.lockRR; if(st.magnet) magnetMode=st.magnet; if(st.isolate!==undefined) isolateSel=!!st.isolate; if(st.sidebarCollapsed!==undefined) sidebarCollapsed=!!st.sidebarCollapsed; if(st.slAnchor!==undefined) slAnchorMode=!!st.slAnchor; } }catch(e){}   // persistat: revine la ultima valoare
if(sidebarCollapsed){ el("sidebar").classList.add("collapsed"); el("sideBtn").textContent="â–¶"; }   // FIX P4: aplica starea persistata la load
renderList();   // afiseaza sidebar-ul imediat (fix: nu aparea dupa refresh)

function resize(){ DPR=window.devicePixelRatio||1;
  const r=cv.getBoundingClientRect();
  W=Math.max(r.width||0, 300);   // FIX P1: doar masurarea REALA (r.width) + minim de siguranta â€” fallback-ul fix (innerWidth-350) facea W artificial mai mare decat canvas-ul afisat
  H=Math.max(r.height||0, 200);   // FIX P1 (aceeasi problema gasita la H): doar masurarea reala + minim
  cv.width=Math.max(1,W*DPR); cv.height=Math.max(1,H*DPR);
  cv.style.width=W+"px"; cv.style.height=H+"px";   // forteaza dimensiunea reala, nu doar CSS
  requestRender(); render(); }
window.addEventListener("resize", resize);
window.addEventListener("focus", resize);
if(window.ResizeObserver) new ResizeObserver(()=>resize()).observe(el("chartBox"));
setTimeout(resize, 300); setTimeout(resize, 1200);   // siguranta: tab deschis in fundal

function requestRender(){ if(rafPending) return; rafPending=true;
  requestAnimationFrame(()=>{ rafPending=false; render(); }); }

function fmtT(ts){ return new Date(ts*1000).toISOString().slice(0,16).replace("T"," "); }   // UTC â€” folosit in EXPORT (analiza pe UTC)
function fmtTRO(ts){ return new Date(ts*1000).toLocaleString("sv-SE",{timeZone:"Europe/Bucharest",
    year:"numeric",month:"2-digit",day:"2-digit",hour:"2-digit",minute:"2-digit"}).replace(" "," "); }  // ora Romaniei (UTC+3 vara / UTC+2 iarna)
// OPTIMIZARE LAG: fmtTRO (toLocaleString) e scump (~2-5us) si e apelat pt FIECARE bara in axa timp la FIECARE
// render (pan/zoom) => cache pe timestamp (barele au timpi unici, cache-ul e mereu valid).
const _fmtTROCache=new Map();
function fmtTROCached(ts){ let s=_fmtTROCache.get(ts); if(s===undefined){ s=fmtTRO(ts); if(_fmtTROCache.size>2000) _fmtTROCache.clear(); _fmtTROCache.set(ts,s); } return s; }
function fmtP(p){ return p.toFixed(DIG); }
function fmtDur(mins){ if(mins<60) return mins+" min";
  const h=Math.floor(mins/60), m=mins%60; return h+"h "+String(m).padStart(2,"0")+"m"; }
function bw(){ return Math.max(1,(W-60)/view.count); }
function candleW(){ return Math.max(1, Math.floor(bw()-1)); }
function barAtX(x){ const b=view.start+Math.floor((x-60)/bw());
  return Math.max(view.start, Math.min(view.start+view.count-1, DATA.length-1, b)); }
function xAtBar(b){ return 60+(b-view.start)*bw()+bw()/2; }
function priceAtY(y){ const r=yRangeCache||yrange(); return r.hi-(y/H)*(r.hi-r.lo); }
function yAtPrice(p){ const r=yRangeCache||yrange(); return (r.hi-p)/(r.hi-r.lo)*H; }
function maxStart(){ return Math.max(0, DATA.length-1-view.count+1); }  // zoom/pan liber peste tot (barele future sunt gri oricum); cutoff ramane doar pt linia de revelare + plasare marker-e
function viewEnd(){ return Math.min(DATA.length, view.start+view.count); }

function baseRange(){
  let lo=Infinity, hi=-Infinity;
  const end=viewEnd();
  for(let i=Math.max(0,view.start);i<end;i++){ const c=DATA[i]; if(c[2]>hi)hi=c[2]; if(c[3]<lo)lo=c[3]; }
  for(const m of markers){ if(m.bar>=view.start && m.bar<end){ if(m.price>hi)hi=m.price; if(m.price<lo)lo=m.price; } }
  for(const d of drawings){ for(const p of d.pts){ if(p.bar>=view.start && p.bar<end){ if(p.price>hi)hi=p.price; if(p.price<lo)lo=p.price; } } }
  if(draft){ for(const p of draft.pts){ if(p.bar>=view.start && p.bar<end){ if(p.price>hi)hi=p.price; if(p.price<lo)lo=p.price; } } }
  if(!isFinite(lo)||!isFinite(hi)){ lo=0; hi=1; }
  return {lo,hi};
}
function yrange(){
  if(drag && drag.mode==="pan" && drag.yr){   // FIX WARP v3: scala INGHETATA la mousedown (inclusiv vzoom), doar SHIFT-ata cu delta yOff â€” fara re-aplicare vzoom (cauza warp la zoom)
    return { lo: drag.yr.lo + (yOff-drag.yOff0), hi: drag.yr.hi + (yOff-drag.yOff0) };
  }
  let b = yLock ? {lo:yLock.lo, hi:yLock.hi} : baseRange();   // scala verticala inghetata la zoom width-only (anchored OFF)
  const mid=(b.lo+b.hi)/2, r=(b.hi-b.lo)/vzoom;
  let lo=mid-r/2+yOff, hi=mid+r/2+yOff;   // vzoom (inaltime candele) + yOff (pan vertical liber)
  const pad=(hi-lo)*0.06||0.001; return {lo:lo-pad, hi:hi+pad};
}

// ðŸ§² MAGNET (ca TradingView): lipeÈ™te preÈ›ul de candela sub cursor (O/H/L/C = open/high/low/close),
// plus liniile SL/TP ale poziÈ›iilor vizibile È™i punctele desenelor. "soft" = doar dacÄƒ eÈ™ti Ã®n raza de
// 8px de È›intÄƒ; "hard" = mereu pe cel mai apropiat (Ctrl È›inut = hard temporar).
const MAGNET_PX=8;   // raza soft-magnet (pixeli pe ecran)
function snapPrice(bar, price, y){
  if(magnetMode==="off" && !ctrlPressedMagnet) return price;   // magnet OFF: nimic de lipit
  // OPTIMIZARE LAG: scala se calculeaza O SINGURA DATA (yrange()/baseRange() e scump â€” loop peste toate
  // barele vizibile). Inainte, fiecare yAtPrice() din bucla de candidati o recalcula la fiecare mousemove
  // (yRangeCache e null in timpul pan-ului) => zeci de mii de iteratii pe eveniment = lag la miscarea chart-ului.
  // FARA ALOCARI: nu construim array de candidati â€” urmarim direct cel mai apropiat (best/bestDy).
  const R = yRangeCache || yrange();
  const span = (R.hi-R.lo) || 1e-9;
  const Hl=H;
  let best=null, bestDy=Infinity;
  const consider = p => { const py=(R.hi-p)/span*Hl; const dy=py>y?py-y:y-py; if(dy<bestDy){ bestDy=dy; best=p; } };
  // 1) candela sub cursor: open/high/low/close (high/low = wick-urile)
  const b=Math.max(0, Math.min(DATA.length-1, bar));
  const c=DATA[b];
  if(c){ consider(c[1]); consider(c[2]); consider(c[3]); consider(c[4]); }
  // 2) liniile SL/TP + entry ale poziÈ›iilor din setul activ (doar cele din viewport, ca TV)
  for(const m of markers){
    if(m.ghost!==nwVisible) continue;
    if(m.bar<view.start || m.bar>=viewEnd()) continue;
    const up=m.dir==="LONG";
    if(m.sl!=null) consider(m.price-(up?1:-1)*m.sl*PIP);
    if(m.tp!=null) consider(m.price+(up?1:-1)*m.tp*PIP);
    consider(m.price);
  }
  // 3) desene: punctele (inclusiv hline) din viewport
  for(const d of drawings){
    for(const p of d.pts){ if(p.bar>=view.start && p.bar<viewEnd()) consider(p.price); }
  }
  if(best==null) return price;                    // nimic de lipit
  const hard = magnetMode==="hard" || ctrlPressedMagnet;
  if(hard) return best;                           // HARD: mereu pe cel mai apropiat È›intÄƒ
  return bestDy<=MAGNET_PX ? best : price;        // SOFT: doar dacÄƒ eÈ™ti aproape de È›intÄƒ
}
let ctrlPressedMagnet=false;   // Ctrl È›inut Ã®n timpul drag-ului = magnet HARD temporar (ca TradingView)

// ============================================================================
// OMAR NOWICK INDICATOR â€” port 1:1 din Pine Script v6 ("omarnowick")
// No-Wick triangles (O==L bull / O==H bear) + pivots HH/HL/LH/LL (5,5)
// + CHoCH/BOS cu Body anchor (max/min body in fereastra pivotului)
// ANTI-LOOKAHEAD: evenimentele apar doar cand sunt CONFIRMATE in barele revelate
//   (pivot la bara i => vizibil doar daca i+PIVOT_LEN <= cutoff).
// ============================================================================
const PIVOT_LEN=5;   // fallback; valoarea reala vine din omarParams.pivotLen (setÄƒri)
let omar={ nowick:[], pivots:[], breaks:[] };
function computeOmar(){
  const n=DATA.length, PL=omarParams.pivotLen||PIVOT_LEN;
  const ph=new Array(n).fill(null), pl=new Array(n).fill(null);
  for(let i=PL;i<n-PL;i++){
    let okH=true, okL=true;
    for(let j=i-PL;j<=i+PL;j++){
      if(DATA[j][2]>DATA[i][2]) okH=false;   // ta.pivothigh(high,5,5)
      if(DATA[j][3]<DATA[i][3]) okL=false;   // ta.pivotlow(low,5,5)
    }
    if(okH) ph[i]=DATA[i][2];
    if(okL) pl[i]=DATA[i][3];
  }
  const pivots=[], breaks=[], nowick=[];
  let trend=0, lastHigh=null, lastLow=null;
  let activeTop=null, activeTopLoc=-1, activeBtm=null, activeBtmLoc=-1;
  let topBroken=true, btmBroken=true;
  for(let i=0;i<n;i++){
    // --- BULLISH PIVOT ---
    if(ph[i]!=null){
      const isHH = lastHigh==null || ph[i]>lastHigh;
      pivots.push({bar:i, price:ph[i], label:isHH?"HH":"LH", bull:true});
      lastHigh=ph[i];
      let anchor;                                // anchorType: "Wick" = high-ul pivotului (ca Pine); "Body" = max body in [i-PL, i+PL] (ca Pine)
      if(omarParams.anchorType==="Wick") anchor=DATA[i][2];
      else { anchor=0;
        for(let j=Math.max(0,i-PL); j<=Math.min(n-1,i+PL); j++) anchor=Math.max(anchor, Math.max(DATA[j][1],DATA[j][4])); }
      activeTop=anchor; activeTopLoc=i; topBroken=false;
    }
    // --- BEARISH PIVOT ---
    if(pl[i]!=null){
      const isHL = lastLow==null || pl[i]>lastLow;
      pivots.push({bar:i, price:pl[i], label:isHL?"HL":"LL", bull:false});
      lastLow=pl[i];
      let anchor;                                // "Wick" = low-ul pivotului; "Body" = min body in [i-PL, i+PL]
      if(omarParams.anchorType==="Wick") anchor=DATA[i][3];
      else { anchor=Infinity;
        for(let j=Math.max(0,i-PL); j<=Math.min(n-1,i+PL); j++) anchor=Math.min(anchor, Math.min(DATA[j][1],DATA[j][4])); }
      activeBtm=anchor; activeBtmLoc=i; btmBroken=false;
    }
    // --- BREAKOUT: close > activeTop (BOS daca trend==1, altfel CHoCH) ---
    if(activeTop!=null && DATA[i][4]>activeTop && !topBroken){
      const isBOS = trend===1;
      breaks.push({from:activeTopLoc, to:i, price:activeTop, label:isBOS?"BOS":"CHoCH", bull:true});
      trend=1; topBroken=true;
    }
    // --- BREAKOUT: close < activeBtm (BOS daca trend==-1, altfel CHoCH) ---
    if(activeBtm!=null && DATA[i][4]<activeBtm && !btmBroken){
      const isBOS = trend===-1;
      breaks.push({from:activeBtmLoc, to:i, price:activeBtm, label:isBOS?"BOS":"CHoCH", bull:false});
      trend=-1; btmBroken=true;
    }
    // --- NO-WICK OPEN (strict, ca Pine: O==L bull / O==H bear) ---
    if(DATA[i][4]>DATA[i][1] && DATA[i][1]===DATA[i][3]) nowick.push({bar:i, bull:true});
    else if(DATA[i][4]<DATA[i][1] && DATA[i][1]===DATA[i][2]) nowick.push({bar:i, bull:false});
  }
  omar={ nowick, pivots, breaks };
}
function drawOmar(){
  const end=viewEnd();
  const colBull="#26a69a", colBear="#ef5350";
  // culorile semnalelor No-Wick (triunghiuri sub/deasupra candelelor): LONG = verde NEON, SHORT = pink BRIGHT
  const nwBull="#39ff14", nwBear="#ff2d95";
  const PL=omarParams.pivotLen||PIVOT_LEN;
  // --- No-Wick triangles (pe TOATE datele â€” candelele sunt istorice; cutoff ascunde doar WIN/LOSS) ---
  if(omarParams.showNoWick) for(const s of omar.nowick){
    if(s.bar<view.start || s.bar>=end) continue;
    if(blind && s.bar>cutoff) continue;   // v7.45: indicatorii NU apar dupa linia de lookahead (ca TV)
    const x=xAtBar(s.bar);
    const y=s.bull ? yAtPrice(DATA[s.bar][3]) : yAtPrice(DATA[s.bar][2]);
    ctx.fillStyle=s.bull?nwBull:nwBear;   // NEON: verde/pink â€” se deosebesc instant de pozitiile tale
    ctx.beginPath();
    if(s.bull){ ctx.moveTo(x-6,y+14); ctx.lineTo(x+6,y+14); ctx.lineTo(x,y+5); }   // 14px sub low â€” NU atinge candela
    else      { ctx.moveTo(x-6,y-14); ctx.lineTo(x+6,y-14); ctx.lineTo(x,y-5); }   // 14px deasupra high â€” NU atinge candela
    ctx.fill();
  }
  // --- Pivots HH/HL/LH/LL (confirmate â€” pe TOATE datele) ---
  if(omarParams.showStruct) for(const p of omar.pivots){
    if(p.bar<view.start || p.bar>=end) continue;
    if(blind && p.bar>cutoff) continue;   // v7.45
    const x=xAtBar(p.bar), y=yAtPrice(p.price);
    ctx.font="bold 10px Segoe UI, Arial"; ctx.textAlign="center";
    ctx.fillStyle=p.bull?colBull:colBear;
    ctx.fillText(p.label, x, p.bull ? y-18 : y+22);   // HH/LH sus, HL/LL jos (like TV label_down/up)
  }
  // --- CHoCH/BOS lines + labels (pe TOATE datele) ---
  if(omarParams.showBosChoch) for(const b of omar.breaks){
    if(b.to<view.start || b.from>end-1) continue;
    if(blind && b.from>cutoff) continue;   // v7.45: BOS/CHoCH nu apar dupa linia de lookahead
    const x1=xAtBar(b.from), x2=xAtBar(b.to), y=yAtPrice(b.price);
    ctx.strokeStyle=b.bull?colBull:colBear; ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(x1,y); ctx.lineTo(x2,y); ctx.stroke();   // solid, ca Pine (line.style_solid width=1)
    ctx.font="bold 10px Segoe UI, Arial"; ctx.textAlign="center";
    ctx.fillStyle=b.bull?colBull:colBear;
    ctx.fillText(b.label, (x1+x2)/2, b.bull ? y-4 : y+12);
  }
}
// ============================================================================
// SISTEM INDICATORI (ca TradingView): catalog + on/off + settings
// ============================================================================
const IND_TYPES={
  omar:{ name:"Omar Nowick", desc:"No-Wick + pivots + CHoCH/BOS",
         defaults:{pivotLen:5, showStruct:true, showBosChoch:true, showNoWick:true, anchorType:"Body"},
         fields:[["pivotLen","Pivot Length","num"],["showStruct","HH/HL/LH/LL","bool"],
                 ["showBosChoch","CHoCH/BOS","bool"],["showNoWick","No-Wick","bool"],
                 ["anchorType","Anchor","sel:B0dy,Wick"]] },
  ema:{ name:"EMA", desc:"Exponential Moving Average", defaults:{periods:"20,50,200"},
        fields:[["periods","Perioade (virgulÄƒ)","text"]] },
  sma:{ name:"SMA", desc:"Simple Moving Average", defaults:{periods:"20,50,200"},
        fields:[["periods","Perioade (virgulÄƒ)","text"]] },
  bb:{ name:"Bollinger", desc:"Bollinger Bands", defaults:{period:20, mult:2},
       fields:[["period","PerioadÄƒ","num"],["mult","DeviaÈ›ii","num"]] },
  vwap:{ name:"VWAP", desc:"Volume Weighted Avg Price (zi)", defaults:{},
         fields:[] },
};
indicators=[{type:"omar", on:true, params:Object.assign({}, IND_TYPES.omar.defaults)}];   // default Omar â€” dacÄƒ localStorage are alÈ›i indicatori, load-ul Ã®i Ã®nlocuieÈ™te
let indCache={};
omarParams=Object.assign({}, IND_TYPES.omar.defaults);   // params-ul activ al lui Omar
function indParams(ind){ return ind.type==="omar" ? omarParams : ind.params; }
function indKey(ind){ return ind.type+":"+JSON.stringify(indParams(ind)); }
function computeMA(type, periodsStr){
  const periods=String(periodsStr).split(",").map(s=>+s.trim()).filter(x=>x>0);
  const n=DATA.length, lines=periods.map(()=>new Array(n).fill(null));
  for(let pi=0;pi<periods.length;pi++){
    const p=periods[pi]; let sum=0;
    for(let i=0;i<n;i++){
      sum+=DATA[i][4];
      if(i>=p) sum-=DATA[i-p][4];
      if(i>=p-1){
        const sma=sum/p;
        if(type==="sma") lines[pi][i]=sma;
        else if(i===p-1) lines[pi][i]=sma;
        else lines[pi][i]=lines[pi][i-1]+(2/(p+1))*(DATA[i][4]-lines[pi][i-1]);
      }
    }
  }
  return {lines, periods};
}
function computeBB(period, mult){
  const n=DATA.length;
  const mid=new Array(n).fill(null), up=new Array(n).fill(null), lo=new Array(n).fill(null);
  for(let i=period-1;i<n;i++){
    let s=0; for(let j=0;j<period;j++) s+=DATA[i-j][4];
    const m=s/period; mid[i]=m;
    let v=0; for(let j=0;j<period;j++) v+=(DATA[i-j][4]-m)**2;
    const sd=Math.sqrt(v/period);
    up[i]=m+mult*sd; lo[i]=m-mult*sd;
  }
  return {mid, up, lo};
}
function computeVWAP(){
  const n=DATA.length, line=new Array(n).fill(null);
  let day="", cumPV=0, cumV=0;
  for(let i=0;i<n;i++){
    const d=new Date(DATA[i][0]*1000).toISOString().slice(0,10);
    if(d!==day){ day=d; cumPV=0; cumV=0; }
    const tp=(DATA[i][2]+DATA[i][3]+DATA[i][4])/3;
    cumPV+=tp*DATA[i][5]; cumV+=DATA[i][5];
    line[i]=cumV>0?cumPV/cumV:null;
  }
  return {line};
}
function computeInd(ind){
  const key=indKey(ind);
  if(indCache[key]) return indCache[key];
  let data;
  if(ind.type==="ema"||ind.type==="sma") data=computeMA(ind.type, indParams(ind).periods);
  else if(ind.type==="bb") data=computeBB(+indParams(ind).period, +indParams(ind).mult);
  else if(ind.type==="vwap") data=computeVWAP();
  if(data) indCache[key]=data;
  return data;
}
function drawLineSeries(series, colors){
  const end=viewEnd();
  for(let si=0;si<series.length;si++){
    const arr=series[si];
    ctx.strokeStyle=colors[si%colors.length]; ctx.lineWidth=1.5;
    ctx.beginPath(); let started=false;
    for(let b=view.start;b<end;b++){
      const v=arr[b]; if(v==null){ started=false; continue; }
      const x=xAtBar(b), y=yAtPrice(v);
      if(!started){ ctx.moveTo(x,y); started=true; } else ctx.lineTo(x,y);
    }
    ctx.stroke();
  }
}
function drawActiveIndicators(){
  for(const ind of indicators){
    if(!ind.on) continue;
    if(ind.type==="omar"){ drawOmar(); continue; }
    const d=computeInd(ind);
    if(ind.type==="ema"||ind.type==="sma") drawLineSeries(d.lines, ["#f5c542","#ff8f00","#ab47bc"]);
    else if(ind.type==="bb") drawLineSeries([d.mid,d.up,d.lo], ["#f5c542","#42a5f5","#42a5f5"]);
    else if(ind.type==="vwap") drawLineSeries([d.line], ["#2962ff"]);
  }
}
function indFieldHtml(ind, i, f, val){
  const [key,label,typ]=f;
  if(typ==="bool") return '<label><input type="checkbox" data-i="'+i+'" data-k="'+key+'"'+(val?" checked":"")+'> '+label+'</label>';
  if(typ.startsWith("sel:")) return '<label>'+label+' <select data-i="'+i+'" data-k="'+key+'">'+
    typ.slice(4).split(",").map(o=>'<option'+(val===o?" selected":"")+'>'+o+'</option>').join("")+'</select></label>';
  return '<label>'+label+' <input type="'+(typ==="num"?"number":"text")+'" data-i="'+i+'" data-k="'+key+'" value="'+val+'"></label>';
}
function renderIndList(){
  const l=el("indlist");
  if(!indicators.length){ l.innerHTML='<div style="font-size:11px;color:#787b86;padding:4px 8px">Niciun indicator. ï¼‹ AdaugÄƒ.</div>'; return; }
  l.innerHTML=indicators.map((ind,i)=>{
    const t=IND_TYPES[ind.type];
    return '<div class="ind'+(ind.on?" on":"")+'">'+
      '<input type="checkbox" data-i="'+i+'"'+(ind.on?" checked":"")+'>'+
      '<span class="nm">'+t.name+'<small>'+t.desc+'</small></span>'+
      '<button data-s="'+i+'" title="SetÄƒri">âš™</button>'+
      '<button data-x="'+i+'" title="È˜terge">âœ•</button></div>'+
      '<div class="set" id="set'+i+'">'+t.fields.map(f=>indFieldHtml(ind,i,f,indParams(ind)[f[0]])).join("")+'</div>';
  }).join("");
  l.querySelectorAll("input[type=checkbox][data-i]").forEach(c=>c.onchange=()=>{
    const ind=indicators[+c.dataset.i]; ind.on=c.checked;
    el("indlist").children[+c.dataset.i].classList.toggle("on", ind.on);
    save(); requestRender(); });
  l.querySelectorAll("button[data-s]").forEach(b=>b.onclick=()=>{
    const s=el("set"+b.dataset.s); s.classList.toggle("open"); });
  l.querySelectorAll("button[data-x]").forEach(b=>b.onclick=()=>{
    indicators.splice(+b.dataset.x,1); indCache={}; renderIndList(); save(); requestRender(); });
  l.querySelectorAll(".set input, .set select").forEach(inp=>inp.onchange=()=>{
    const ind=indicators[+inp.dataset.i], k=inp.dataset.k;
    if(ind.type==="omar"){
      omarParams[k]= inp.type==="checkbox" ? inp.checked : (inp.type==="number"?+inp.value:inp.value);
      computeOmar();
    } else ind.params[k]= inp.type==="checkbox" ? inp.checked : (inp.type==="number"?+inp.value:inp.value);
    indCache={}; save(); requestRender(); });
}
el("addInd").onclick=()=>{
  const pk=el("indpicker");
  if(pk.style.display==="block"){ pk.style.display="none"; return; }
  pk.innerHTML=Object.keys(IND_TYPES).filter(t=>!indicators.some(i=>i.type===t)).map(t=>
    '<button data-t="'+t+'">'+IND_TYPES[t].name+' <small>â€” '+IND_TYPES[t].desc+'</small></button>').join("");
  pk.style.display="block";
  pk.querySelectorAll("button").forEach(b=>b.onclick=()=>{
    const t=b.dataset.t;
    indicators.push({type:t, on:true, params:Object.assign({}, IND_TYPES[t].defaults)});
    if(t==="omar") omarParams=Object.assign({}, IND_TYPES.omar.defaults);
    pk.style.display="none"; indCache={}; renderIndList(); save(); requestRender(); });
};
document.addEventListener("click", ev=>{ const pk=el("indpicker");
  if(pk.style.display==="block" && !pk.contains(ev.target) && ev.target.id!=="addInd") pk.style.display="none"; });
function render(){
  updateNwCount();
  ctx.setTransform(DPR,0,0,DPR,0,0);
  ctx.fillStyle=COL.bg; ctx.fillRect(0,0,W,H);
  yRangeCache=yrange(); const {lo,hi}=yRangeCache; const end=viewEnd();
  const yP=p=>((hi-p)/(hi-lo)*H);           // O(1) local â€” NU yAtPrice (evita re-apele yrange = LAG la zoom mare)
  // grid orizontal
  ctx.strokeStyle=COL.grid; ctx.lineWidth=1;
  for(let i=0;i<=5;i++){ const y=H*i/5; ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W-52,y); ctx.stroke(); }
  // grid vertical
  const barsPer=Math.max(1, Math.round(view.count/8));
  for(let b=view.start;b<end;b+=barsPer){ const x=xAtBar(b);
    ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke(); }
  const cw=candleW();
  // lumanari â€” BATCHED (Path2D per culoare): fara beginPath/stroke per candela = fara LAG la zoom mare
  const wUp=new Path2D(), wDn=new Path2D();
  const bUp=new Path2D(), bDn=new Path2D();
  const lastDraw=blind?Math.min(cutoff, end-1):end-1;   // v7.44: candelele din DREAPTA liniei lookahead DISPAR COMPLET (ca TV â€” viitorul nu se vede deloc, nici cu opacitate)
  for(let b=Math.max(0,view.start);b<=lastDraw;b++){
    const c=DATA[b]; const x=Math.round(xAtBar(b));
    const yO=yP(c[1]), yC=yP(c[4]), yH=yP(c[2]), yL=yP(c[3]);
    const up=c[4]>=c[1];
    const top=Math.min(yO,yC), h=Math.max(1,Math.abs(yC-yO));
    const w= up?wUp:wDn;
    w.moveTo(x,yH); w.lineTo(x,yL);
    const bd= up?bUp:bDn;
    if(cw>=2){ bd.rect(x-cw/2, top, cw, h); } else { bd.rect(x-0.5, top, 1, h); }
    drawOps++;
  }
  ctx.lineWidth=1;
  ctx.strokeStyle=COL.up; ctx.stroke(wUp); ctx.fillStyle=COL.up; ctx.fill(bUp);
  ctx.strokeStyle=COL.down; ctx.stroke(wDn); ctx.fillStyle=COL.down; ctx.fill(bDn);
  // linia de revelare (v7.46: evidenta â€” trage-o cu mouse-ul pe orice candela, schimbari instant)
  if(blind && cutoff>=view.start && cutoff<end){
    const xc=xAtBar(cutoff)+bw()/2;
    ctx.strokeStyle="#ffa726"; ctx.lineWidth=2;
    ctx.setLineDash([6,4]);
    ctx.beginPath(); ctx.moveTo(xc,0); ctx.lineTo(xc,H); ctx.stroke(); ctx.setLineDash([]);
    // maner sus (prindere usoara)
    ctx.fillStyle="#ffa726"; ctx.fillRect(xc-16, 2, 32, 18);
    ctx.fillStyle="#131722"; ctx.font="bold 11px Segoe UI, Arial"; ctx.textAlign="center";
    ctx.fillText("â‡”", xc, 15);
    ctx.fillStyle="#ffa726"; ctx.font="10px Segoe UI, Arial";
    ctx.fillText("Lookahead", xc, 34);
    ctx.lineWidth=1;
  }
  // bara fantoma la hover (v7.46: arata unde pui linia cand treci cu mouse-ul, tool POINTER, lookahead ON)
  if(blind && lookaheadPlacing && xhair && tool===TOOLS.POINTER && xhair.bar>=view.start && xhair.bar<end){
    const xg=xAtBar(xhair.bar)+bw()/2;
    ctx.strokeStyle="rgba(255,167,38,0.5)"; ctx.lineWidth=2; ctx.setLineDash([3,4]);
    ctx.beginPath(); ctx.moveTo(xg,0); ctx.lineTo(xg,H); ctx.stroke(); ctx.setLineDash([]); ctx.lineWidth=1;
  }
  // desene
  for(const d of drawings){ if(d===sel || selSet.some(it=>it.kind==="d" && it.ref===d)) continue; drawDrawing(d, false); }
  // multi-select: highlight pe TOATE desenele din selSet (altele decat sel, care e desenat mai jos cu handles)
  for(const it of selSet){ if(it.kind==="d" && it.ref!==sel) drawDrawing(it.ref, true); }
  if(sel) drawDrawing(sel, true);
  if(draft && draft.pts.length) drawDrawing(draft, true, true);
  // marker-e
  // ðŸ” IZOLARE (default ON): cÃ¢nd o poziÈ›ie e selectatÄƒ, desenÄƒm DOAR ea pe chart â€” restul dispar (fÄƒrÄƒ clutter).
  // drawMarker are deja highlight pe selMk (contur galben + badge R:R), deci izolatul se vede clar.
  // ATENÈšIE: izolarea deseneazÄƒ selMk DOAR dacÄƒ e din setul vizibil (ghost===nwVisible) â€” altfel drawMarker
  // face early-return È™i marker-ul DISPARE complet (fix: Ã®n cazul Äƒsta desenÄƒm tot setul, nu nimic).
  if(isolateSel && selMk && selMk.ghost===nwVisible){ drawMarker(selMk); }
  else for(const m of markers){ if(m.bar>=view.start && m.bar<end) drawMarker(m); }
  // grupuri: conexiuni intre pozitiile din acelasi grup (subiectivitate -> obiectivitate)
  const grp={};
  for(const m of markers) if(m.group) (grp[m.group]=grp[m.group]||[]).push(m);
  const GRP_COLORS=["#ab47bc","#ff7043","#42a5f5","#d4e157","#ec407a"];
  for(const g in grp){
    const arr=grp[g].filter(m=>m.bar>=view.start && m.bar<viewEnd());
    if(arr.length<2) continue;
    const col=GRP_COLORS[(+g-1)%GRP_COLORS.length];
    arr.sort((a,b)=>a.bar-b.bar);
    ctx.strokeStyle=col; ctx.lineWidth=1.5; ctx.setLineDash([5,3]);
    ctx.globalAlpha=0.55;
    ctx.beginPath();
    arr.forEach((m,i)=>{ const px=xAtBar(m.bar), py=yAtPrice(m.price);
      if(i===0) ctx.moveTo(px,py); else ctx.lineTo(px,py); });
    ctx.stroke(); ctx.setLineDash([]); ctx.globalAlpha=1;
    ctx.fillStyle=col; ctx.font="bold 9px Segoe UI, Arial"; ctx.textAlign="center";
    const first=arr[0];
    ctx.fillText("G"+g, xAtBar(first.bar), yAtPrice(first.price)-14);
  }
  // pozitia in curs de plasare (draft box, mutabil pe chart)
  if(posDraft && posDraft.bar>=view.start && posDraft.bar<end) drawMarker(posDraft);
  // indicatori (Omar + orice adÄƒugat din catalog) â€” mereu vizibili, ca TradingView
  drawActiveIndicators();
  // preview pozitie (in spatele dialogului, live) + masura Shift
  if(dlgPreview) drawMarkerPreview(dlgPreview);
  if(measure) drawMeasure(measure);
  // marquee box (Ctrl+drag) â€” selectie multipla ca TradingView
  if(drag && drag.mode==="selbox"){
    const x0=Math.min(drag.x0,drag.x1), x1=Math.max(drag.x0,drag.x1);
    const y0=Math.min(drag.y0,drag.y1), y1=Math.max(drag.y0,drag.y1);
    ctx.fillStyle="rgba(255,213,79,0.10)"; ctx.fillRect(x0,y0,x1-x0,y1-y0);
    ctx.strokeStyle="#ffd54f"; ctx.lineWidth=1; ctx.setLineDash([5,4]);
    ctx.strokeRect(x0,y0,x1-x0,y1-y0); ctx.setLineDash([]);
  }
  // backtest vizual: ruleazÄƒ SL/TP pe barele viitoare pentru fiecare marker
  if(btOn && btOverlay) drawBacktest();
  // axa pret â€” IN price bar (dreapta, full-height, ca TradingView)
  ctx.fillStyle=COL.text; ctx.font="11px Segoe UI, Arial"; ctx.textAlign="right";
  for(let i=0;i<=5;i++){ const p=hi-(hi-lo)*i/5; ctx.fillText(fmtP(p), W-8, H*i/5+4); }
  ctx.textAlign="right"; ctx.fillStyle="#787b86";
  for(let b=Math.max(0,view.start);b<end;b+=barsPer){ const t=fmtTROCached(DATA[b][0]);
    ctx.fillText(t.slice(5,10)+"  "+t.slice(11,16), xAtBar(b), H-4); }
  // crosshair
  if(xhair){
    const bx=Math.max(0, Math.min(end-1, blind?Math.min(cutoff,xhair.bar):xhair.bar));
    const x=xAtBar(bx), y=yP(xhair.price);
    ctx.strokeStyle=COL.cross; ctx.setLineDash([4,4]);
    ctx.beginPath(); ctx.moveTo(x,0); ctx.lineTo(x,H); ctx.stroke();
    ctx.beginPath(); ctx.moveTo(0,y); ctx.lineTo(W-52,y); ctx.stroke();
    ctx.setLineDash([]);
    const c=DATA[bx];
    ctx.fillStyle="#262a35"; ctx.fillRect(8,8,196,58);
    ctx.strokeStyle="#3a3f4d"; ctx.strokeRect(8,8,196,58);
    ctx.fillStyle=COL.text; ctx.textAlign="left";
    ctx.fillText(fmtTROCached(c[0])+"   O "+fmtP(c[1]), 16, 24);   // ora Romaniei (UTC+3 vara)
    ctx.fillText("H "+fmtP(c[2])+"    L "+fmtP(c[3]), 16, 40);
    ctx.fillText("C "+fmtP(c[4])+"    Â· "+fmtP(xhair.price), 16, 56);
    ctx.fillStyle="#787b86"; ctx.fillText("vol "+DATA[bx][5], 16, 70);
    // display mic jos langa axa timp: data + ora exacta a candelei sub cursor (ca TV)
    const dt=fmtTROCached(c[0]);
    const lab=dt.slice(5,10)+"  "+dt.slice(11,16);
    ctx.font="10px Segoe UI, Arial"; ctx.textAlign="center";
    const lw=ctx.measureText(lab).width+10;
    const lx=Math.max(66+lw/2, Math.min(x, W-52-lw/2));
    ctx.fillStyle="#262a35"; ctx.fillRect(lx-lw/2, H-18, lw, 15);
    ctx.strokeStyle="#3a3f4d"; ctx.strokeRect(lx-lw/2, H-18, lw, 15);
    ctx.fillStyle=COL.text; ctx.fillText(lab, lx, H-7);
  }
  // price bar (dreapta): pretul live la cursor + SL/TP/Entry (ca TradingView)
  updatePricebar();
  // status
  const i0=Math.max(0,view.start), i1=Math.min(DATA.length-1,end-1);
  const d0=new Date(DATA[i0][0]*1000), d1=new Date(DATA[i1][0]*1000);
  const rng=d0.toISOString().slice(0,10)+" â†’ "+d1.toISOString().slice(0,10);
  const bd=blind?("blind Â· pÃ¢nÄƒ la "+fmtTRO(DATA[Math.min(cutoff,end-1)][0]).slice(0,10)):"tot chart-ul";
  el("status").innerHTML="<b>"+rng+"</b> Â· "+view.count+" bare Â· "+bd+" Â· "+markers.length+" marker-e Â· "+drawings.length+" desene Â· <span title=\"Datele sunt UTC; afiÈ™at Ã®n ora RomÃ¢niei (UTC+3 varÄƒ / +2 iarnÄƒ). Analiza/export = UTC.\">ðŸ• RO</span>";
  yRangeCache=null;
  el("debug").textContent="canvas "+W+"x"+H+" (backing "+cv.width+"x"+cv.height+") Â· lumanari desenate "+drawOps+" Â· blind "+(blind?"ON":"OFF")+" Â· view "+view.start+".."+(end-1)+" Â· vzoom "+vzoom.toFixed(2)+"x Â· js:ok";
  drawOps=0;
}

function drawMarker(m){
  // switch NW: ON = doar backtest trades (ghost); OFF = doar ale tale
  if(m.ghost !== nwVisible) return;
  const b=m.bar, x=xAtBar(b), y=yAtPrice(m.price);
  const up=m.dir==="LONG"; const hover=m===hoverMk;
  // ghost (AI): CULOARE MONO pe direcÈ›ie â€” LONG = tot verde, SHORT = tot roÈ™u (separare clarÄƒ)
  const gcol = m.ghost ? (up ? "#26a69a" : "#ef5350") : null;   // pastram pt banda (subtila), dar liniile SL/TP sunt STANDARD ca la pozitiile tale
  // exit-ul real (primul SL/TP atins pe barele viitoare) â€” ca TradingView
  const bt=(m.sl!=null && m.tp!=null) ? btMapCur(btRun(m)) : null;   // v7.54: rezultatul (M1) e mapat pe TF-ul afiÈ™at
  // FILL LA TOUCH: trail-ul + liniile SL/TP Ã®ncep de la PRIMA candelÄƒ care atinge entry-ul (fillBar),
  // nu de la bara markerului (care poate fi Ã®nainte ca preÈ›ul sÄƒ ajungÄƒ la entry)
  const filled = bt && bt.fillBar!=null;
  const x0 = filled ? xAtBar(bt.fillBar) : x;
  const noFill = bt && bt.res==="NOFILL";
  const expired = bt && bt.res==="EXPIRED";
  const fcBars = (m.fc>0)?m.fc:60;                              // forecast length (bare) â€” "same size", ca TV
  const fcEnd = Math.min(DATA.length-1, m.bar+fcBars);
  const xEnd = bt && bt.bar!=null ? Math.max(x, xAtBar(bt.bar)) : Math.max(x, xAtBar(fcEnd));  // oprit la SL/TP atins; altfel forecast box (nu infinit)
  // MINIM 2 CANDELE vizual: dacÄƒ intrarea È™i ieÈ™irea sunt pe ACEEAÈ˜I candelÄƒ (39% din bot trades), banda e 1px = invizibilÄƒ.
  // Extindem vizual banda + liniile SL/TP la cel puÈ›in 2 candele (trail-ul/punctul de exit rÄƒmÃ¢n la poziÈ›ia realÄƒ).
  const xEndVis = Math.max(xEnd, x0 + 2*bw());
  const colEx = bt ? (bt.res==="WIN" ? "#26a69a" : bt.res==="LOSS" ? "#ef5350" : "#f5c542") : null;
  // banda pozitiei â€” IDENTICA pentru ghost si ale tale: SL side ROSU, TP side VERDE (ca TV)
  if(m.sl!=null && m.tp!=null && (filled || noFill)){
    const sy=yAtPrice(m.price-(up?1:-1)*m.sl*PIP), ty=yAtPrice(m.price+(up?1:-1)*m.tp*PIP);
    const w=Math.max(1,xEndVis-x0);
    ctx.globalAlpha=0.18;   // 0.10 era aproape invizibil pe fundal inchis (fix vizibilitate overlay)
    ctx.fillStyle="#ef5350"; ctx.fillRect(x0, Math.min(y,sy), w, Math.max(1,Math.abs(y-sy)));        // SL side (rosu)
    ctx.fillStyle="#26a69a"; ctx.fillRect(x0, Math.min(y,ty), w, Math.max(1,Math.abs(y-ty)));        // TP side (verde)
    ctx.globalAlpha=1;
  }
  // SL (rosu) si TP (verde) â€” LINII DRAGGABLE, din prima candelÄƒ care atinge entry pana la exit
  // (si la NOFILL: se deseneaza pana la xEnd, ca pozitia sa fie vizibila chiar daca nu s-a executat)
  if(m.sl!=null && (filled || noFill)){ const sy=yAtPrice(m.price-(up?1:-1)*m.sl*PIP);
    ctx.strokeStyle="#ef5350"; ctx.setLineDash([3,3]); ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(x0,sy); ctx.lineTo(xEndVis,sy); ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle="#ef5350"; ctx.font="10px Segoe UI, Arial"; ctx.textAlign="left";
    ctx.fillText("SL "+m.sl+"p", x0+2, Math.max(10,sy-3)); }
  if(m.tp!=null && (filled || noFill)){ const ty=yAtPrice(m.price+(up?1:-1)*m.tp*PIP);
    ctx.strokeStyle="#26a69a"; ctx.setLineDash([3,3]); ctx.lineWidth=1;
    ctx.beginPath(); ctx.moveTo(x0,ty); ctx.lineTo(xEndVis,ty); ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle="#26a69a"; ctx.font="10px Segoe UI, Arial"; ctx.textAlign="left";
    ctx.fillText("TP "+m.tp+"p", x0+2, Math.max(10,ty-3)); }
  // calea pretului: de la PRIMA candela care atinge entry, bara cu bara (closes), pana la primul SL/TP atins
  if(bt && bt.fillBar!=null && bt.bar!=null && bt.bar>=bt.fillBar){
    const xf=xAtBar(bt.fillBar);
    ctx.strokeStyle=colEx; ctx.lineWidth=1.6; ctx.setLineDash([]);
    ctx.beginPath(); ctx.moveTo(xf,y);
    for(let i=bt.fillBar+1;i<=bt.bar;i++) ctx.lineTo(xAtBar(i), yAtPrice(DATA[i][4]));
    ctx.stroke();
    ctx.fillStyle=colEx;
    ctx.beginPath(); ctx.arc(xAtBar(bt.bar), yAtPrice(bt.price), 4, 0, Math.PI*2); ctx.fill();   // punct exit
    ctx.fillStyle="#131722"; ctx.font="bold 9px Segoe UI, Arial"; ctx.textAlign="center";
    ctx.fillText(bt.res, xAtBar(bt.bar), yAtPrice(bt.price)+(up?-8:14));                        // WIN/LOSS/OPEN
  }
  if(noFill){   // nu s-a atins entry-ul â€” trade-ul nu s-a executat (doar sageata + eticheta, fara bandÄƒ/trail)
    ctx.fillStyle="#787b86"; ctx.font="bold 9px Segoe UI, Arial"; ctx.textAlign="left";
    ctx.fillText("no fill", x+6, y+(up?-10:20));
  }
  if(expired){   // EXPIRY: entry-ul nu a fost atins Ã®n exp candele â€” semnul stÄƒ â€žÃ®n aer" lÃ¢ngÄƒ candela de start
    // (NU atinge prima candelÄƒ ex. 21:45), cu lungime orizontalÄƒ ~4-5 candele + mic emoji = ratat/expired
    const bwp=bw();
    const sx=x+1.5*bwp;                    // decalat la dreapta: nu atinge candela
    const sw=Math.max(34, 4.5*bwp);        // ~4-5 candele lungime orizontalÄƒ
    ctx.strokeStyle="#9aa0ab"; ctx.lineWidth=1.4; ctx.setLineDash([4,3]);
    ctx.beginPath(); ctx.moveTo(sx,y); ctx.lineTo(sx+sw,y); ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle="#9aa0ab"; ctx.font="12px Segoe UI, Arial"; ctx.textAlign="left";
    ctx.fillText("â³", sx+sw+4, y+4);      // mic emoji: poziÈ›ia a expirat
    ctx.font="bold 8px Segoe UI, Arial";
    ctx.fillText("expired", sx+2, y+(up?-7:13));
  }
  // linia de intrare + sageata â€” din PRIMA candela care atinge entry pana la exit (culori standard; neon-ul e doar pe indicatorul Omar)
  // EXPIRED: linia de intrare NU se deseneazÄƒ (semnul plutitor È›ine locul â€” nu vrem linia sÄƒ atingÄƒ candela)
  if(!expired){
    ctx.strokeStyle=up?COL.up:COL.down; ctx.setLineDash([6,4]); ctx.lineWidth=hover?2:1.5;
    if(hover) ctx.shadowColor=(up?COL.up:COL.down); ctx.shadowBlur=hover?8:0;
    ctx.beginPath(); ctx.moveTo(x0,y); ctx.lineTo(xEnd,y); ctx.stroke();
    ctx.setLineDash([]); ctx.lineWidth=1; ctx.shadowBlur=0;
  }
  ctx.fillStyle=up?COL.up:COL.down;
  ctx.beginPath();
  if(up){ ctx.moveTo(x-14,y+16); ctx.lineTo(x+14,y+16); ctx.lineTo(x,y-8); }
  else  { ctx.moveTo(x-14,y-16); ctx.lineTo(x+14,y-16); ctx.lineTo(x,y+8); }
  ctx.fill();
  if(m.id==null) m.id=++mkSeq;   // marker-e vechi fara id â†’ generez (sigur, nu crapa)
  try{  // badge #ID pe chart â€” izolat: daca un marker are date proaste, NU opreste restul chart-ului
    ctx.font="bold 9px Segoe UI"; ctx.textAlign="left";
    const idCol = m.ghost ? (up?"#26a69a":"#ef5350") : "#9aa0ae";
    const idLabel="#"+m.id;
    const idw=ctx.measureText(idLabel).width+8;
    let bx=x+14; if(bx+idw>W-54) bx=W-54-idw;   // clamp: nu intra sub pricebar (dreapta)
    ctx.fillStyle="#131722"; ctx.fillRect(bx, up?y+8:y-16, idw, 13);
    ctx.strokeStyle=idCol; ctx.lineWidth=1; ctx.strokeRect(bx, up?y+8:y-16, idw, 13);
    ctx.fillStyle=idCol; ctx.fillText(idLabel, bx+4, up?y+17:y-7);
  }catch(e){}
  // ghost pe chart = IDENTIC cu pozitiile tale (distinctia e doar in LISTA din dreapta)
  if(m.note){ ctx.fillStyle="rgba(19,23,34,0.88)";
    const w=Math.min(230, m.note.length*6+12);
    let nx=x+10; if(nx+w>W-54) nx=W-54-w;   // clamp: nu intra sub pricebar
    ctx.fillRect(nx, y-26, w, 20);
    ctx.strokeStyle=COL.line; ctx.strokeRect(nx,y-26,w,20);
    ctx.fillStyle=COL.text; ctx.font="10px Segoe UI, Arial";
    ctx.fillText(m.note.length>34?m.note.slice(0,34)+"â€¦":m.note, nx+6, y-12); }
  // handles SL/TP + highlight DOAR pe SELECTAT (hover-ul schimba doar cursorul â€” curat, ca TV)
  if(selSet.length>1 && selSet.some(it=>it.kind==="m" && it.ref===m) && m!==selMk){
    // multi-select: contur galben subtil (fara handles/badge â€” doar semnalizare)
    const sy=m.sl!=null?yAtPrice(m.price-(up?1:-1)*m.sl*PIP):y;
    const ty=m.tp!=null?yAtPrice(m.price+(up?1:-1)*m.tp*PIP):y;
    ctx.globalAlpha=0.45; ctx.strokeStyle="#ffd54f"; ctx.lineWidth=1; ctx.setLineDash([4,3]);
    ctx.strokeRect(x-8, Math.min(sy,ty)-8, 16, Math.max(1,Math.abs(ty-sy))+16);
    ctx.setLineDash([]); ctx.globalAlpha=1;
  }
  if(m===selMk){
    // selectat = simplu highlight la border (ca TV): contur subtil in jurul box-ului vizual, fara cerculete/handles
    const sy=m.sl!=null?yAtPrice(m.price-(up?1:-1)*m.sl*PIP):y;
    const ty=m.tp!=null?yAtPrice(m.price+(up?1:-1)*m.tp*PIP):y;
    ctx.globalAlpha=0.9; ctx.strokeStyle="#ffd54f"; ctx.lineWidth=1.5; ctx.setLineDash([]);
    ctx.strokeRect(x-8, Math.min(sy,ty)-8, Math.max(16,(xEnd-x)+16), Math.max(1,Math.abs(ty-sy))+16);
    ctx.globalAlpha=1;
    // badge R:R + pips (mic, FARA cerculete) â€” LONG: deasupra liniei TP (sus) Â· SHORT: sub linia TP (jos)
    if(m.sl!=null && m.tp!=null){
      const rr=m.sl>0?(m.tp/m.sl):0;
      // WIN/LOSS/OPEN vizibil la selectare â€” culori clare (verde/roÈ™u/galben), ca TradingView
      let resTxt="", resCol="#787b86";
      const rbt=btRun(m);
      if(rbt){ if(rbt.res==="WIN"){ resTxt="WIN"; resCol="#26a69a"; } else if(rbt.res==="LOSS"){ resTxt="LOSS"; resCol="#ef5350"; } else if(rbt.res==="OPEN"){ resTxt="OPEN"; resCol="#f5c542"; } else if(rbt.res==="EXPIRED"){ resTxt="expired"; resCol="#9aa0ab"; } else { resTxt="no fill"; resCol="#787b86"; } }
      const badge="R:R "+rr.toFixed(2)+" Â· SL "+m.sl+"p Â· TP "+m.tp+"p"+(lockRR?" Â· ðŸ”’":"");
      ctx.font="10px Segoe UI, Arial"; const bw=ctx.measureText(badge).width+12;
      const tyLine=yAtPrice(m.price+(up?1:-1)*m.tp*PIP);   // linia TP (sus la LONG, jos la SHORT)
      const by = up ? tyLine-25 : tyLine+6;                 // LONG: deasupra Â· SHORT: sub
      let bx=Math.max(8, x-bw); if(bx+bw>W-54) bx=W-54-bw;  // clamp: nu intra sub pricebar
      ctx.fillStyle="rgba(19,23,34,0.92)"; ctx.fillRect(bx, by, bw, 17);
      ctx.strokeStyle="#ffd54f"; ctx.lineWidth=1; ctx.strokeRect(bx, by, bw, 17);
      ctx.fillStyle="#ffd54f"; ctx.fillText(badge, bx+6, by+13);
      // badge WIN/LOSS (mic, deasupra badge-ului R:R) â€” se vede clar ce a fost trade-ul
      if(resTxt){
        const wb=ctx.measureText(resTxt).width+10;
        let wbx=Math.max(8, bx+bw-wb); if(wbx+wb>W-54) wbx=W-54-wb;
        const wy=by-19;
        ctx.fillStyle="rgba(19,23,34,0.92)"; ctx.fillRect(wbx, wy, wb, 16);
        ctx.strokeStyle=resCol; ctx.lineWidth=1; ctx.strokeRect(wbx, wy, wb, 16);
        ctx.fillStyle=resCol; ctx.fillText(resTxt, wbx+5, wy+12);
      }
    }
  }
}

// care parte a unui marker e sub cursor: SL / TP / intrare (pentru drag)
// preview LONG/SHORT in spatele dialogului â€” live, inainte de Salveaza
function drawMarkerPreview(p){
  const b=p.bar, x=xAtBar(b), y=yAtPrice(p.price);
  if(b<view.start || b>=viewEnd()) return;
  const up=p.dir==="LONG";
  // exit-ul real (primul SL/TP atins) â€” live, ca TradingView
  const bt=(p.sl!=null && p.tp!=null) ? btMapCur(btRun(p)) : null;   // v7.54: mapat pe TF-ul afiÈ™at
  const fcBars = (p.fc>0)?p.fc:60;                              // forecast length (bare) â€” "same size"
  const fcEnd = Math.min(DATA.length-1, b+fcBars);
  const xEnd = bt&&bt.bar!=null ? Math.max(x, xAtBar(bt.bar)) : Math.max(x, xAtBar(fcEnd));
  const colEx = bt ? (bt.res==="WIN" ? "#26a69a" : bt.res==="LOSS" ? "#ef5350" : "#f5c542") : null;
  ctx.save(); ctx.globalAlpha=0.6;
  if(p.sl!=null && p.tp!=null){
    const sy=yAtPrice(p.price-(up?1:-1)*p.sl*PIP), ty=yAtPrice(p.price+(up?1:-1)*p.tp*PIP);
    const w=Math.max(1,xEnd-x);
    ctx.globalAlpha=0.08;
    ctx.fillStyle="#ef5350"; ctx.fillRect(x, Math.min(y,sy), w, Math.max(1,Math.abs(y-sy)));        // SL side (rosu)
    ctx.fillStyle="#26a69a"; ctx.fillRect(x, Math.min(y,ty), w, Math.max(1,Math.abs(y-ty)));        // TP side (verde)
    ctx.globalAlpha=0.6;
  }
  ctx.setLineDash([5,5]); ctx.lineWidth=1.5;
  if(p.sl!=null){ const sy=yAtPrice(p.price-(up?1:-1)*p.sl*PIP);
    ctx.strokeStyle="#ef5350"; ctx.beginPath(); ctx.moveTo(x,sy); ctx.lineTo(xEnd,sy); ctx.stroke(); }
  if(p.tp!=null){ const ty=yAtPrice(p.price+(up?1:-1)*p.tp*PIP);
    ctx.strokeStyle="#26a69a"; ctx.beginPath(); ctx.moveTo(x,ty); ctx.lineTo(xEnd,ty); ctx.stroke(); }
  // EXPIRED preview: semnul plutitor (segment + emoji) ca pe chart â€” se vede Ã®n spatele dialogului
  if(bt && bt.res==="EXPIRED" && p.exp>0){
    const bwp=bw();
    const sx=x+1.5*bwp, sw=Math.max(34, 4.5*bwp);
    ctx.strokeStyle="#9aa0ab"; ctx.setLineDash([4,3]); ctx.lineWidth=1.4;
    ctx.beginPath(); ctx.moveTo(sx,y); ctx.lineTo(sx+sw,y); ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle="#9aa0ab"; ctx.font="12px Segoe UI, Arial"; ctx.textAlign="left";
    ctx.fillText("â³", sx+sw+4, y+4);
  }
  // calea pretului pana la primul SL/TP atins (live in preview)
  if(bt && bt.bar>b){
    ctx.strokeStyle=colEx; ctx.lineWidth=1.6; ctx.setLineDash([]);
    ctx.beginPath(); ctx.moveTo(x,y);
    for(let i=b+1;i<=bt.bar;i++) ctx.lineTo(xAtBar(i), yAtPrice(DATA[i][4]));
    ctx.stroke();
    ctx.fillStyle=colEx;
    ctx.beginPath(); ctx.arc(xAtBar(bt.bar), yAtPrice(bt.price), 4, 0, Math.PI*2); ctx.fill();
  }
  ctx.strokeStyle=up?COL.up:COL.down;
  ctx.beginPath(); ctx.moveTo(x,y); ctx.lineTo(xEnd,y); ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle=up?COL.up:COL.down;
  ctx.beginPath();
  if(up){ ctx.moveTo(x-14,y+16); ctx.lineTo(x+14,y+16); ctx.lineTo(x,y-8); }
  else  { ctx.moveTo(x-14,y-16); ctx.lineTo(x+14,y-16); ctx.lineTo(x,y+8); }
  ctx.fill();
  ctx.restore();
  const lab=(up?"â–² LONG":"â–¼ SHORT")+" â€” SL "+(p.sl!=null?p.sl:"-")+"p Â· TP "+(p.tp!=null?p.tp:"-")+"p";
  ctx.font="10px Segoe UI, Arial"; ctx.textAlign="left";
  const w=ctx.measureText(lab).width+12;
  const lx=Math.max(8, Math.min(x+10, W-52-w-4)), ly=Math.max(8, y-30);
  ctx.fillStyle="rgba(19,23,34,0.9)"; ctx.fillRect(lx,ly,w,17);
  ctx.strokeStyle=COL.line; ctx.strokeRect(lx,ly,w,17);
  ctx.fillStyle=up?COL.up:COL.down; ctx.fillText(lab, lx+6, ly+12);
}

// Shift+drag â€” dreptunghi de masura (ca TradingView): pips + bare + timp
function drawMeasure(m){
  const x1=xAtBar(Math.min(m.b0,m.b1)), x2=xAtBar(Math.max(m.b0,m.b1));
  const y1=Math.min(yAtPrice(m.p0),yAtPrice(m.p1)), y2=Math.max(yAtPrice(m.p0),yAtPrice(m.p1));
  ctx.globalAlpha=0.10; ctx.fillStyle=COL.accent;
  ctx.fillRect(x1,y1,Math.max(1,x2-x1),Math.max(1,y2-y1)); ctx.globalAlpha=1;
  ctx.strokeStyle=COL.accent; ctx.lineWidth=1; ctx.setLineDash([4,3]);
  ctx.strokeRect(x1,y1,x2-x1,y2-y1); ctx.setLineDash([]);
  const pips=Math.abs(m.p1-m.p0)/PIP, bars=Math.abs(m.b1-m.b0);
  const lab=pips.toFixed(1)+" pips Â· "+bars+" bare Â· "+fmtDur(Math.round(bars*15));
  ctx.font="10px Segoe UI, Arial"; ctx.textAlign="left";
  const w=ctx.measureText(lab).width+12;
  const lx=Math.max(8, Math.min(x2-w-2, W-52-w-4)), ly=Math.max(8, Math.min(y2+8, H-26));
  ctx.fillStyle="rgba(19,23,34,0.9)"; ctx.fillRect(lx,ly,w,18);
  ctx.strokeStyle=COL.accent; ctx.strokeRect(lx,ly,w,18);
  ctx.fillStyle="#fff"; ctx.fillText(lab, lx+6, ly+13);
}

// ============================================================================
// BACKTEST VIZUAL â€” ruleazÄƒ SL/TP pe barele viitoare pentru fiecare marker
// Anti-lookahead: Ã®n blind mode, rezultatul apare doar dacÄƒ exit-bar <= cutoff
// ============================================================================
let btOn=false;              // toggle
let btOverlay=true;          // overlay liniilor backtest (eye on/off)
let btCache={ json:"", stats:null };   // panou actualizat doar cÃ¢nd se schimbÄƒ
// cache btRun: fingerprint pe (id,bar,price,sl,tp,cutoff,TF) â€” rezultatul se invalideaza automat la orice modificare
let btCacheMap=new Map();
function btRun(m){
  // v7.56: rezultatul se calculeazÄƒ pe datele de 1 MINUT (adevÄƒrul fin), indiferent de view-ul afiÈ™at.
  // Fereastra de expirare e aliniatÄƒ la candelele TF-ului de plasare: fill-ul Ã®ncepe la urmÄƒtoarea
  // candelÄƒ de plasare (ts + tfMin), fereastra = exp Ã— minutele TF-ului (11 M15 = [ts+15, ts+180)).
  // Deci 11 candele se comportÄƒ ca pe 15m, dar fill/SL/TP sunt calculate pe M1 â€” precizia realÄƒ.
  const ev = DATA_M1.length ? DATA_M1 : DATA_BASE;
  // ancora de timp a poziÈ›iei: m.ts (fix la plasare) â€” fallback pentru marker-e vechi: bara curentÄƒ
  let ts = (m.ts!=null && isFinite(m.ts)) ? m.ts : (DATA[m.bar]?DATA[m.bar][0]:null);
  let eBar = ts!=null ? findBarFloorIn(ev, ts) : -1;
  if(eBar<0) eBar = Math.min(ev.length-1, m.bar);
  const tfMin = m.tf==="M1"?1 : m.tf==="H1"?60 : m.tf==="H4"?240 : m.tf==="D1"?1440 : 15;
  const expBars = m.exp===0 ? 0 : (m.exp>0?m.exp:lastExp);   // 0 explicit = fÄƒrÄƒ expiry; undefined = default salvat (lastExp)
  const expMin = expBars * tfMin;
  // start: urmÄƒtoarea candelÄƒ de plasare (sau chiar ancora cu "Entry aici"); capÄƒt: start + fereastra
  const fillStartTs = (m.entryMode==="now") ? ts : (ts!=null ? ts + tfMin*60 : null);
  const baseTs = (fillStartTs!=null ? fillStartTs : (ts!=null ? ts : ev[0][0]));
  const fillFrom = fillStartTs!=null ? Math.max(0, findBarFloorIn(ev, fillStartTs)) : eBar;
  const searchLim = expMin>0 ? Math.min(ev.length-1, findBarFloorIn(ev, baseTs + expMin*60 - 1)) : ev.length-1;
  const key=(m.id||0)+"|"+(ts!=null?ts:"-")+"|"+fillFrom+"|"+searchLim+"|"+m.price+"|"+m.sl+"|"+m.tp+"|"+expMin+"|"+(DATA_M1.length?"M1":"M15")+"|"+(m.entryMode||"-");
  const cached=btCacheMap.get(key);
  if(cached!==undefined) return cached;
  // limite: pÃ¢nÄƒ la capÄƒtul datelor REALE â€” candelele sunt istorice, deci evaluÄƒm peste tot.
  // cutoff blocheazÄƒ DOAR plasarea marker-elor Ã®n blind, NU rezultatul real al backtest-ului.
  const lim = ev.length-1;
  const dir=m.dir, e=m.price, sl=m.sl*PIP, tp=m.tp*PIP;
  const slP = dir==="LONG" ? e-sl : e+sl;
  const tpP = dir==="LONG" ? e+tp : e-tp;
  // FILL LA TOUCH: prima candelÄƒ (dupÄƒ bara markerului) care atinge efectiv preÈ›ul entry
  // (bar-touch fill â€” ca MT5): candela e atinsÄƒ dacÄƒ entry-ul e Ã®n intervalul [low, high].
  // De acolo Ã®ncepe trail-ul + evaluarea SL/TP. DacÄƒ nicio candelÄƒ nu atinge â†’ NOFILL (nu s-a executat).
  // EXPIRY: marker-ele fÄƒrÄƒ exp folosesc default-ul salvat (lastExp). DacÄƒ entry-ul nu e atins Ã®n
  // fereastra de expirare (ex. 11 candele M15 = 165 min) de la urmÄƒtoarea candelÄƒ => EXPIRED.
  let fillBar=null;
  for(let b=fillFrom;b<=searchLim;b++){
    const c=ev[b];
    if(c[3]<=e && e<=c[2]){ fillBar=b; break; }
  }
  if(fillBar===null){
    const res = expMin>0
      ? {res:"EXPIRED", bar:null, price:null, fillBar:null, expiryBar:searchLim, ev,
         expiryTs:ev[searchLim][0]}
      : {res:"NOFILL", bar:null, price:null, fillBar:null, ev};
    btCacheMap.set(key, res); if(btCacheMap.size>4000) btCacheMap.clear();
    return res;
  }
  let res=null;
  for(let b=fillBar;b<=lim;b++){
    const c=ev[b];
    if(dir==="LONG"){
      if(c[3]<=slP){ res={res:"LOSS", bar:b, price:slP}; break; }
      if(c[2]>=tpP){ res={res:"WIN",  bar:b, price:tpP}; break; }
    } else {
      if(c[2]>=slP){ res={res:"LOSS", bar:b, price:slP}; break; }
      if(c[3]<=tpP){ res={res:"WIN",  bar:b, price:tpP}; break; }
    }
  }
  if(res===null && fillBar<=lim) res={res:"OPEN", bar:lim, price:ev[lim][4]};   // Ã®ncÄƒ Ã®n desfÄƒÈ™urare
  res.fillBar=fillBar; res.fillTs=ev[fillBar][0]; res.ev=ev;
  if(res.bar!=null) res.barTs=ev[res.bar][0];
  btCacheMap.set(key, res);
  if(btCacheMap.size>4000) btCacheMap.clear();   // limita de memorie (drag lung)
  return res;
}
// rezultatul btRun e Ã®n coordonatele datelor de EVALUARE (M1) â€” Ã®l mapÄƒm pe TF-ul afiÈ™at pt desenare
function btMapCur(r){
  if(!r || !r.ev || r.ev===DATA) return r;
  const o={...r};
  if(r.fillBar!=null && r.fillTs!=null){ const b=findBarFloor(r.fillTs); o.fillBar=b>=0?b:r.fillBar; }
  if(r.bar!=null && r.barTs!=null){ const b=findBarFloor(r.barTs); o.bar=b>=0?b:r.bar; }
  if(r.expiryBar!=null && r.expiryTs!=null){ const b=findBarFloor(r.expiryTs); o.expiryBar=b>=0?b:r.expiryBar; }
  return o;
}
let btStatsCache={ fp:-1, json:"", stats:null };   // OPTIMIZARE LAG: btStats e apelat la fiecare render (drawBacktest) â€” cache pe fingerprint (markers+nwVisible), doar marker-ele schimbate invalideaza
function btStats(){
  // fingerprint ieftin: lungime + suma id/bar/sl/tp + starea NW â€” se schimba DOAR cand marker-ele se schimba
  let fp=markers.length*7 + (nwVisible?131:0);
  for(const m of markers) fp = (fp + m.id*13 + m.bar*17 + (m.sl||0)*19 + (m.tp||0)*23 + (m.dir==="SHORT"?29:0) + (m.exp>0?m.exp*31:0)) % 2147483647;
  if(btStatsCache.fp===fp && btStatsCache.stats) return btStatsCache.stats;
  const rows=[];
  for(const m of markers){
    if(m.ghost !== nwVisible) continue;                  // switch NW: doar setul activ Ã®n statistici
    const r=btRun(m); if(!r) continue;
    rows.push({m, r});
  }
  const wins=rows.filter(x=>x.r.res==="WIN"), losses=rows.filter(x=>x.r.res==="LOSS");
  const opens=rows.filter(x=>x.r.res==="OPEN");
  const noFills=rows.filter(x=>x.r.res==="NOFILL");
  const expireds=rows.filter(x=>x.r.res==="EXPIRED");
  const winPips=wins.reduce((s,x)=>s+(x.m.dir==="LONG"?x.m.tp:x.m.tp),0);
  const lossPips=losses.reduce((s,x)=>s+x.m.sl,0);
  const totR=wins.length-losses.length;
  const pf = lossPips>0 ? winPips/lossPips : (wins.length? Infinity : 0);
  const st={ n:rows.length, wins:wins.length, losses:losses.length, opens:opens.length, noFills:noFills.length, expired:expireds.length,
           wr: wins.length+losses.length ? (wins.length/(wins.length+losses.length))*100 : 0,
           totR, pf: (pf===Infinity?"âˆž":pf.toFixed(2)), winPips, lossPips };
  btStatsCache={ fp, json:JSON.stringify(st), stats:st };
  return st;
}
function drawBacktest(){
  // liniile entry â†’ exit pentru fiecare marker rezolvat
  for(const m of markers){
    if(m.ghost !== nwVisible) continue;                  // switch NW: doar setul activ are linii
    if(m.bar<view.start || m.bar>viewEnd()) continue;
    const r=btMapCur(btRun(m)); if(!r || r.res==="NOFILL" || r.res==="EXPIRED") continue;
    const x1=r.fillBar!=null ? xAtBar(r.fillBar) : xAtBar(m.bar), y1=yAtPrice(m.price);
    const x2=xAtBar(r.bar), y2=yAtPrice(r.price);
    const col = r.res==="WIN" ? "#26a69a" : r.res==="LOSS" ? "#ef5350" : "#f5c542";
    ctx.globalAlpha=0.9; ctx.strokeStyle=col; ctx.lineWidth=1.5;
    ctx.beginPath(); ctx.moveTo(x1,y1); ctx.lineTo(x2,y2); ctx.stroke();
    ctx.fillStyle=col;
    ctx.beginPath(); ctx.arc(x2,y2,4,0,Math.PI*2); ctx.fill();
    ctx.globalAlpha=1;
  }
  // panou statistici (doar cÃ¢nd se schimbÄƒ) â€” JSON.stringify e scump, cache-ul il tine deja serializat
  const st=btStats();
  const j=btStatsCache.json;
  if(j!==btCache.json){
    btCache.json=j; btCache.stats=st;
    const p=el("btPanel");
    p.innerHTML='<b>ðŸ§ª Backtest</b>'+
      '<div class="r"><span>Trades</span><span>'+st.n+'</span></div>'+
      '<div class="r"><span class="win">WIN</span><span class="win">'+st.wins+'</span></div>'+
      '<div class="r"><span class="loss">LOSS</span><span class="loss">'+st.losses+'</span></div>'+
      '<div class="r"><span class="open">OPEN</span><span class="open">'+st.opens+'</span></div>'+
      (st.noFills?'<div class="r"><span style="color:#787b86">no fill</span><span style="color:#787b86">'+st.noFills+'</span></div>':'')+
      (st.expired?'<div class="r"><span style="color:#9aa0ab">expired</span><span style="color:#9aa0ab">'+st.expired+'</span></div>':'')+
      '<div class="r"><span>WR %</span><span>'+st.wr.toFixed(0)+'%</span></div>'+
      '<div class="r"><span>Î£ R</span><span>'+(st.totR>0?"+":"")+st.totR+'R</span></div>'+
      '<div class="r"><span>Profit factor</span><span>'+st.pf+'</span></div>';
  }
}
el("btBtn").onclick=()=>{ btOn=!btOn;
  el("btBtn").classList.toggle("on", btOn);
  el("btPanel").style.display = btOn?"block":"none";
  if(btOn){
    // Backtest = vezi direct trade-urile WIN/LOSS (verde/roÈ™u), fÄƒrÄƒ sÄƒ desenezi tu fiecare poziÈ›ie:
    // 1) nimic desenat â†’ generez automat backtest-ul bot (BOT8_SPEC) pe tot istoricul + Ã®l arÄƒt pe chart
    // 2) setul vizibil e gol, dar celÄƒlalt are trade-uri â†’ comut pe el (ghost AI â†” ale tale)
    if(markers.length===0){ autoBotTrades();
      if(!nwVisible){ nwVisible=true; el("nwBtn").classList.add("on");
        el("nwBtn").title = "Ghost ON: vezi DOAR backtest trades â€” apasÄƒ din nou ca sÄƒ revin ale tale"; } }
    else if(!markers.some(m=>m.ghost===nwVisible)){ nwVisible=!nwVisible;
      el("nwBtn").classList.toggle("on", nwVisible);
      el("nwBtn").title = nwVisible ? "Ghost ON: vezi DOAR backtest trades â€” apasÄƒ din nou ca sÄƒ revin ale tale" : "Ghost OFF: vezi doar trade-urile tale â€” apasÄƒ ca sÄƒ vezi backtest trades"; }
    btCache.json=""; btStats();
  }
  requestRender(); };
el("btEye").onclick=()=>{ btOverlay=!btOverlay;
  el("btEye").classList.toggle("off", !btOverlay);
  el("btEye").textContent = btOverlay ? "ðŸ‘" : "ðŸš«";
  requestRender(); toast(btOverlay?"Liniile backtest vizibile":"Liniile backtest ascunse"); };

// Ghost markers â€” semnalele No-Wick din ZONA VIZIBILÄ‚ (nu doar pÃ¢nÄƒ la cutoff!).
// Candelele sunt date istorice (vizibile È™i Ã®n zona gri); cutoff ascunde DOAR WIN/LOSS (btRun se opreÈ™te la el).
function autoNWGhosts(){
  const from = Math.max(0, view.start-60);                       // buffer mic spre stÃ¢nga
  const to   = Math.min(DATA.length-1, blind?cutoff:view.start+view.count-1); // v7.45: semnalele bot NU apar dupa linia de lookahead
  let n=0;
  for(let i=from; i<=to; i++){
    const c=DATA[i]; if(!c) continue;
    const o=c[1], h=c[2], l=c[3], cl=c[4];
    const bodyPips=(cl-o)/PIP;
    if(Math.abs(bodyPips)<3) continue;                      // body minim 3p (relaxat â€” vezi mai multe trade-uri)
    const bull = (o===l) && cl>o;                            // NW bullish: open==low (Pine-pure, tol 0)
    const bear = (o===h) && cl<o;                            // NW bearish: open==high
    if(!bull && !bear) continue;
    // toate sesiunile (fÄƒrÄƒ filtru 09-17) â€” vezi mai multe semnale; filtrezi tu cu PASS/SKIP
    if(markers.some(m=>m.bar===i)) continue;                 // nu dubla marker-ele existente
    const dir = bull?"LONG":"SHORT";
    // SL config realÄƒ: la extremul candelei NW + buffer, DAR minim 5p (sub spread nu se poate â€” NW pur are O==L, deci low==open)
    // pentru NW pur folosim minimul bot-ului (clamp [5,15] din BOT8_SPEC)
    const buf=1.5;
    const rawSl = (dir==="LONG" ? (o-l) : (h-o))/PIP + buf;
    const sl = Math.min(15, Math.max(5, Math.round(rawSl*10)/10));   // clamp [5, 15] ca bot-ul
    const tp = Math.round(sl*10)/10;                         // RR 1.0
    markers.push({ id:++mkSeq, bar:i, price:o, dir, ghost:true, tf:TF, ts:DATA[i][0],   // v7.54: evaluare pe M1, ancorat aici
      note:"ðŸ‘» NW "+(dir==="LONG"?"bull":"bear")+" Â· body "+bodyPips.toFixed(1)+"p Â· SL "+sl+"p / TP "+tp+"p Â· PASS/SKIP? DE CE?",
      sl, tp, fc:60, created:Date.now(),
      seen_through:(blind && i<=cutoff) ? cutoff : null });  // zona gri: rezultatul e necunoscut
    n++;
  }
  if(n>0){ save(); requestRender(); toast("ðŸ‘» "+n+" ghost markers puse â€” click pe fiecare: PASS/SKIP + DE CE + SL/TP real"); }
  else toast("ðŸ‘» Niciun semnal NW Ã®n zona vizibilÄƒ â€” pan/zoom spre altÄƒ zonÄƒ sau dezvÄƒlui mai mult");
}

// ðŸ¤– Bot â€” backtest automat: ruleazÄƒ config-ul bot-ului (BOT8_SPEC) pe TOT istoricul È™i pune trade-urile ca ghost markers
function autoBotTrades(){
  computeOmar();   // asigurÄƒ nowick + pivots actualizate
  // IDEMPOTENT: È™tergem ghost-urile bot generate anterior (nota Ã®ncepe cu "ðŸ¤– Bot") â€” re-apÄƒsarea NU dubleazÄƒ trade-urile
  for(let i=markers.length-1;i>=0;i--){
    if(markers[i].ghost && markers[i].note && markers[i].note.startsWith("ðŸ¤– Bot")) markers.splice(i,1);
  }
  const MIN_BODY=5, SESS0=240, SESS1=1170, BREATH=1.10, MIN_SL=5, MAX_SL=15, RR=1.0, EXPIRY_BARS=10;
  const made=[];
  let activeUntil=-1;   // o singurÄƒ poziÈ›ie pe rÃ¢nd (decizia #11)
  for(const s of omar.nowick){
    const i=s.bar;
    if(i<60) continue;                                  // warm-up indicatori
    if(i<=activeUntil) continue;                        // poziÈ›ia anterioarÄƒ Ã®ncÄƒ activÄƒ (expiry)
    const c=DATA[i]; if(!c) continue;
    const bodyPips=Math.abs(c[4]-c[1])/PIP;
    if(bodyPips<MIN_BODY) continue;                     // #13 min body 5p
    const d=new Date(c[0]*1000);
    const mins=d.getUTCHours()*60+d.getUTCMinutes();
    if(mins<SESS0 || mins>=SESS1) continue;             // #9 sesiune 04:00-19:30 UTC
    // pivot-wick activ = ultimul pivot de structurÄƒ opus (pt LONG: ultimul low; pt SHORT: ultimul high)
    let pivot=null;
    for(let p=omar.pivots.length-1;p>=0;p--){
      const pv=omar.pivots[p];
      if(pv.bar<i && pv.bull!==s.bull){ pivot=pv; break; }
    }
    if(!pivot) continue;
    const distPips=Math.abs(c[1]-pivot.price)/PIP;
    let sl=Math.round(distPips*BREATH*10)/10;
    sl=Math.min(MAX_SL, Math.max(MIN_SL, sl));          // #8 clamp [5,15]
    const tp=Math.round(sl*RR*10)/10;                   // RR=1 fix
    const up=s.bull;
    made.push({ id:++mkSeq, bar:i, price:c[1], dir:up?"LONG":"SHORT", ghost:true, tf:TF, ts:DATA[i][0],   // v7.54: evaluare pe M1, ancorat aici
      note:"ðŸ¤– Bot "+(up?"bull":"bear")+" Â· SL "+sl+"p / TP "+tp+"p Â· pivot "+pivot.label+" @"+pivot.price.toFixed(DIG),
      sl, tp, fc:EXPIRY_BARS, created:Date.now(), seen_through:null });
    activeUntil=i+EXPIRY_BARS;                          // expiry 10 bare (decizia #12)
  }
  markers.push(...made);
  // ID-uri SIMPLE 1..N: renumerotez ghost-urile bot secvential (in ordinea barelor) â€” nu 600k, nu ++mkSeq
  let seq=1;
  const bots=markers.filter(m=>m.ghost && m.note && m.note.startsWith("ðŸ¤– Bot")).sort((a,b)=>a.bar-b.bar);
  for(const b of bots) b.id=seq++;
  btOn=true; btOverlay=true;   // backtest vizual ON (liniile WIN/LOSS) â€” dar chart-ul ghost-urilor e controlat de ðŸ‘» NW
  el("btBtn").classList.add("on"); el("btPanel").style.display="block";
  btCache.json=""; btStats(); nwCountCache=-1; updateNwCount();
  save(); requestRender(); renderList();
  toast("ðŸ¤– Bot: "+made.length+" trade-uri generate (config BOT8_SPEC) pe tot istoricul");
}
// Contor live: cÃ¢te semnale NW sunt Ã®n zona vizibilÄƒ (fÄƒrÄƒ sÄƒ apeÈ™i ðŸ‘»)
let nwCountCache=-1;
function updateNwCount(){
  const from=Math.max(0,view.start-60), to=Math.min(DATA.length-1,view.start+view.count-1);
  let n=0;
  for(let i=from;i<=to;i++){
    const c=DATA[i]; if(!c) continue;
    const o=c[1],h=c[2],l=c[3],cl=c[4];
    if(Math.abs((cl-o)/PIP)<3) continue;
    if((o===l&&cl>o)||(o===h&&cl<o)) n++;
  }
  if(n!==nwCountCache){ nwCountCache=n;
    const e=el("nwCount");
    e.textContent = "Â· "+n+" semnale NW vizibile";
    e.title = n+" semnale No-Wick (O==L/O==H, bodyâ‰¥3p) Ã®n zona vizibilÄƒ â€” ðŸ‘» NW le pune ca ghost markers";
  }
}
el("nwBtn").onclick=()=>{ nwVisible=!nwVisible;                 // SWITCH: ON = doar backtest trades (ghost), OFF = doar ale tale (nu È™terge)
  el("nwBtn").classList.toggle("on", nwVisible);
  el("nwBtn").title = nwVisible ? "Ghost ON: vezi DOAR backtest trades â€” apasÄƒ din nou ca sÄƒ revin ale tale" : "Ghost OFF: vezi doar trade-urile tale â€” apasÄƒ ca sÄƒ vezi backtest trades";
  if(nwVisible){ autoNWGhosts(); btOn=true; btOverlay=true;     // pune ce lipseÈ™te + vezi INSTANT trade-urile WIN/LOSS
    el("btBtn").classList.add("on"); el("btPanel").style.display="block"; btCache.json=""; btStats();
  } else { btOn=false; el("btBtn").classList.remove("on"); el("btPanel").style.display="none"; }
  nwCountCache=-1; updateNwCount();
  requestRender(); };
el("lockRRBtn").onclick=()=>{ lockRR=!lockRR;
  el("lockRRBtn").classList.toggle("on", lockRR);
  el("lockRRBtn").title = lockRR ? "ðŸ”’ R:R fix ON: SL È™i TP se mutÄƒ Ã®mpreunÄƒ (acelaÈ™i raport) â€” apasÄƒ ca sÄƒ deblochezi" : "ðŸ”’ R:R fix OFF: SL/TP independente â€” apasÄƒ ca sÄƒ le lege (acelaÈ™i raport la mutare)";
  try{ localStorage.setItem("gbpusd_full_settings", JSON.stringify({lockRR, magnet:magnetMode, isolate:isolateSel, sidebarCollapsed, slAnchor:slAnchorMode})); }catch(e){}   // persistat â€” revine la ultima valoare la refresh
  toast(lockRR ? "ðŸ”’ R:R fix ON â€” SL È™i TP se mutÄƒ proporÈ›ional" : "ðŸ”“ R:R fix OFF â€” SL/TP independente");
  requestRender(); };
el("lockRRBtn").classList.toggle("on", lockRR);   // starea persistata se reflecta pe buton la load
el("magBtn").onclick=()=>{   // ðŸ§² Magnet: ciclare off -> soft -> hard (ca TradingView)
  magnetMode = magnetMode==="off" ? "soft" : magnetMode==="soft" ? "hard" : "off";
  el("magBtn").classList.toggle("on", magnetMode!=="off");
  const label = magnetMode==="hard" ? "HARD (mereu pe cel mai apropiat)" : magnetMode==="soft" ? "SOFT (doar cÃ¢nd eÈ™ti aproape)" : "OFF";
  el("magBtn").title = "ðŸ§² Magnet "+label+". LipeÈ™te preÈ›ul de wick-uri, OHLC, SL/TP È™i desene. Èšine Ctrl Ã®n timpul drag-ului = Hard temporar.";
  el("magBtn").querySelector("span").textContent = "ðŸ§² Magnet: "+label.split(" ")[0];
  try{ localStorage.setItem("gbpusd_full_settings", JSON.stringify({lockRR, magnet:magnetMode, isolate:isolateSel, sidebarCollapsed, slAnchor:slAnchorMode})); }catch(e){}
  toast("ðŸ§² Magnet "+label);
  requestRender(); };
el("magBtn").classList.toggle("on", magnetMode!=="off");
try{ el("magBtn").querySelector("span").textContent = "ðŸ§² Magnet: "+(magnetMode==="hard"?"HARD":magnetMode==="soft"?"SOFT":"OFF"); }catch(e){}
el("botBtn").onclick=()=>{
  // ðŸ¤– Bot = DOAR switch Ã®n object tree: AI trades â†” my trades (2 stÄƒri). NU atinge chart-ul.
  botActivated=true;   // prima apÄƒsare: ghost-urile bot devin vizibile Ã®n listÄƒ (pÃ¢nÄƒ acum erau ascunse la load)
  const hasGhost = markers.some(m=>m.ghost);  if(!hasGhost){ autoBotTrades(); treeView="ai"; el("botBtn").classList.add("on"); renderList(); return; }   // prima apÄƒsare: genereazÄƒ + aratÄƒ AI
  treeView = treeView==="ai" ? "mine" : "ai";   // toggle simplu: AI â†” mine
  el("botBtn").classList.toggle("on", treeView==="ai");
  renderList();
  toast("Object tree: "+(treeView==="ai"?"AI trades (backtest)":"trade-urile tale"));
};

// ðŸ“‹ FinalizeazÄƒ sesiunea â€” raport complet pe deciziile tale (dupÄƒ backtest)
function finalizeSession(){
  const rows=[];
  for(const m of markers){
    const r=btRun(m); if(!r) continue;
    rows.push({m, r});
  }
  const take = rows.filter(x=>!x.m.ghost);                 // marker-ele TALE (nu ghost AI)
  const ghost = rows.filter(x=>x.m.ghost);                 // ghost: le-ai pÄƒstrat â†’ TAKE implicit
  const bySess = {};
  for(const x of take){
    const d=new Date(DATA[x.m.bar][0]*1000);
    const mins=d.getUTCHours()*60+d.getUTCMinutes();
    const sess = mins<540 ? "Pre-London" : mins<720 ? "London" : mins<750 ? "NY open" : mins<870 ? "NY" : mins<990 ? "US news" : "Late";
    (bySess[sess]=bySess[sess]||[]).push(x);
  }
  function stat(arr){
    const w=arr.filter(x=>x.r.res==="WIN").length, l=arr.filter(x=>x.r.res==="LOSS").length, o=arr.filter(x=>x.r.res==="OPEN").length;
    const wp=arr.filter(x=>x.r.res==="WIN").reduce((s,x)=>s+x.m.tp,0);
    const lp=arr.filter(x=>x.r.res==="LOSS").reduce((s,x)=>s+x.m.sl,0);
    const totR=w-l;
    const pf = lp>0 ? wp/lp : (w?Infinity:0);
    return {n:arr.length,w,l,o,wr:w+l?(w/(w+l))*100:0,totR,pf:pf===Infinity?"âˆž":pf.toFixed(2),wp,lp};
  }
  const stT=stat(take), stG=stat(ghost), stAll=stat(rows);
  let sessHtml="";
  for(const s of Object.keys(bySess).sort()){
    const a=stat(bySess[s]);
    sessHtml+='<div class="r"><span>'+s+'</span><span>'+(a.wr.toFixed(0)+'% ('+a.n+')')+'</span></div>';
  }
  let longT=stat(take.filter(x=>x.m.dir==="LONG")), shortT=stat(take.filter(x=>x.m.dir==="SHORT"));
  const p=el("btPanel");
  p.innerHTML='<b>ðŸ“‹ Raport sesiune</b>'+
    '<div class="r"><span>Decizii tale (TAKE)</span><span>'+stT.n+'</span></div>'+
    '<div class="r"><span class="win">WIN</span><span class="win">'+stT.w+'</span></div>'+
    '<div class="r"><span class="loss">LOSS</span><span class="loss">'+stT.l+'</span></div>'+
    '<div class="r"><span class="open">OPEN</span><span class="open">'+stT.o+'</span></div>'+
    '<div class="r"><span>WR %</span><span>'+stT.wr.toFixed(0)+'%</span></div>'+
    '<div class="r"><span>Î£ R</span><span>'+(stT.totR>0?"+":"")+stT.totR+'R</span></div>'+
    '<div class="r"><span>Profit factor</span><span>'+stT.pf+'</span></div>'+
    '<div class="r" style="border-top:1px solid var(--line);margin-top:4px;padding-top:4px"><span>Ghost pÄƒstrate</span><span>'+stG.n+'</span></div>'+
    '<div class="r"><span>Ghost WR</span><span>'+stG.wr.toFixed(0)+'%</span></div>'+
    '<div class="r"><span>Ghost PF</span><span>'+stG.pf+'</span></div>'+
    (sessHtml?'<div style="border-top:1px solid var(--line);margin-top:4px;padding-top:4px"><b>Sesiuni (WR%)</b></div>'+sessHtml:'')+
    '<div style="border-top:1px solid var(--line);margin-top:4px;padding-top:4px"><b>LONG vs SHORT</b></div>'+
    '<div class="r"><span>LONG WR</span><span>'+(longT.wr.toFixed(0)+'% ('+longT.n+')')+'</span></div>'+
    '<div class="r"><span>SHORT WR</span><span>'+(shortT.wr.toFixed(0)+'% ('+shortT.n+')')+'</span></div>'+
    '<div class="r" style="border-top:1px solid var(--line);margin-top:4px;padding-top:4px"><span>Total (toate)</span><span>'+stAll.n+' Â· WR '+stAll.wr.toFixed(0)+'%</span></div>';
  el("btPanel").style.display="block";
  btOn=true; el("btBtn").classList.add("on");
  requestRender();
  toast("ðŸ“‹ Sesiune finalizatÄƒ â€” raport Ã®n panoul din stÃ¢nga");
}
el("finBtn").onclick=()=>finalizeSession();

function markerPartAt(x, y){
  const tol=5;   // toleranta linii SL/TP (pe toata lungimea â€” drag direct, ca inainte)
  for(const m of [...markers].reverse()){
    if(m.ghost !== nwVisible) continue;                  // switch NW: ghost ascuns = NEATINS (hitbox mort, ca sa nu blocheze cursorul)
    if(m.bar<view.start || m.bar>=viewEnd()) continue;
    const ex=xAtBar(m.bar);
    // zona X: de la entry pana la capatul box-ului â€” SINCron cu vizualul (drawMarker):
    // dacÄƒ trade-ul s-a Ã®nchis devreme (WIN/LOSS), vizualul se opreÈ™te la exit, NU la forecast (fc=60)
    const fcEnd=Math.min(DATA.length-1, m.bar+((m.fc>0)?m.fc:60));
    let xEnd=Math.max(ex, xAtBar(fcEnd));
    if(m.sl!=null && m.tp!=null){ const bt=btMapCur(btRun(m));
      if(bt && bt.bar!=null && bt.res!=="OPEN") xEnd=Math.max(ex, xAtBar(bt.bar));   // FIX: hitbox = box-ul vizibil (nu 46 bare mai departe)
      else if(bt && bt.res==="EXPIRED") xEnd=Math.min(xEnd, ex+7*bw()); }   // EXPIRED: doar segmentul plutitor (~4-5 candele)
    if(x<ex-12 || x>xEnd+12) continue;
    const up=m.dir==="LONG";
    const sy=m.sl!=null?yAtPrice(m.price-(up?1:-1)*m.sl*PIP):null;
    const ty=m.tp!=null?yAtPrice(m.price+(up?1:-1)*m.tp*PIP):null;
    // 1) LINIA SL/TP â€” pe TOATA lungimea pentru pozitiile tale; la ghost AI doar langa sageata (ex+40)
    //    (altfel hover-ul/comentariul lung de pe ghost prind slider-ul peste tot â€” hitbox urias)
    const xLineEnd = m.ghost ? Math.min(xEnd, ex+40) : xEnd;
    if(sy!=null && Math.abs(y-sy)<tol && x<=xLineEnd) return {m, part:"sl"};
    if(ty!=null && Math.abs(y-ty)<tol && x<=xLineEnd) return {m, part:"tp"};
    // 2) linia de entry â€” DOAR pe sageata insasi (cerc mic in jurul varfului), nu pe toata lungimea benzii
    if(Math.hypot(x-ex, y-yAtPrice(m.price))<16) return {m, part:"entry"};
    // 3) BODY: interiorul benzii INTRE linii (fill) = muta TOT â€” pe TOATA lungimea box-ului vizual (pana la xEnd)
    //    EXCEPTIE ghost AI: hitbox MIC (doar langa sageata) ca sa nu blocheze click-urile peste pozitiile tale / chart
    const xBodyEnd = m.ghost ? Math.min(xEnd, ex+40) : xEnd;
    if(sy!=null || ty!=null){
      const y1=Math.min(sy??yAtPrice(m.price), ty??yAtPrice(m.price))+tol;
      const y2=Math.max(sy??yAtPrice(m.price), ty??yAtPrice(m.price))-tol;
      if(y>=y1 && y<=y2 && x<=xBodyEnd) return {m, part:"body"};
    } else if(Math.abs(yAtPrice(m.price)-y)<30 && x<=xBodyEnd) return {m, part:"body"};
  }
  return null;
}

// box de comentariu pe desene (linie/zonÄƒ/hline) â€” Ã®n dreapta, ca TV
function drawNoteBox(ctx, x, y, text){
  const w=Math.min(240, text.length*6+12);
  let nx=x; if(nx+w>W-54) nx=W-54-w;   // clamp: nu intra sub pricebar
  ctx.fillStyle="rgba(19,23,34,0.88)"; ctx.fillRect(nx,y,w,20);
  ctx.strokeStyle=COL.line; ctx.strokeRect(nx,y,w,20);
  ctx.fillStyle=COL.text; ctx.font="10px Segoe UI, Arial"; ctx.textAlign="left";
  ctx.fillText(text.length>36?text.slice(0,36)+"â€¦":text, nx+6, y+13);
}
// SHIFT = constrÃ¢ngere la 45Â° (ca TradingView): punctul (x,y) faÈ›Äƒ de ancora (ax,ay) se lipeÈ™te de
// unghiurile 0Â° (orizontal), 90Â° (vertical), 45Â°/135Â° (diagonale) â€” Ã®n PIXELI pe ecran.
function constrain45(x, y, ax, ay){
  const dx=x-ax, dy=y-ay;
  const adx=Math.abs(dx), ady=Math.abs(dy);
  // diagonala la 45Â°: |dx| == |dy|; altfel axa dominantÄƒ (ca TV)
  if(adx<=ady*0.5){ return [ax, y]; }        // aproape vertical â†’ vertical pur
  if(ady<=adx*0.5){ return [x, ay]; }        // aproape orizontal â†’ orizontal pur
  const d=Math.min(adx, ady);                // bandÄƒ diagonalÄƒ â†’ 45Â° exact (semnul pÄƒstrat)
  return [ax + Math.sign(dx)*d, ay + Math.sign(dy)*d];
}

function drawDrawing(d, selected, isDraft){
  const pt=(p,i)=>{ const x=xAtBar(p.bar), y=yAtPrice(p.price);
    if(i>0 && i%3===0){ ctx.fillStyle=COL.draw; ctx.beginPath(); ctx.arc(x,y,3,0,7); ctx.fill(); }
    return [x,y]; };
  ctx.strokeStyle=isDraft?"#ffa726":(selected?"#81d4fa":(d.color||COL.draw));
  ctx.lineWidth=selected?2:1.5;
  const pts=d.pts.map((p,i)=>pt(p,i));
  if(d.type==="hline"){ const y=pts[0][1];
    ctx.setLineDash([6,4]); ctx.beginPath(); ctx.moveTo(60,y); ctx.lineTo(W-52,y); ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle=ctx.strokeStyle; ctx.font="10px Segoe UI, Arial"; ctx.textAlign="left";
    ctx.fillText(fmtP(d.pts[0].price), 62, Math.max(10,y-3)); }
  if(d.type==="pen" && pts.length>=2){
    ctx.beginPath(); ctx.moveTo(pts[0][0],pts[0][1]);
    for(let i=1;i<pts.length;i++) ctx.lineTo(pts[i][0],pts[i][1]);
    ctx.stroke();
    if(selected && pts.length){ const a=pts[pts.length-1];
      ctx.fillStyle=ctx.strokeStyle; ctx.beginPath(); ctx.arc(a[0],a[1],4,0,7); ctx.fill(); } }
  else if(d.type==="line" && pts.length>=2){ ctx.beginPath(); ctx.moveTo(pts[0][0],pts[0][1]); ctx.lineTo(pts[1][0],pts[1][1]); ctx.stroke();
    if(d.text) drawNoteBox(ctx, pts[1][0]+10, pts[1][1]-26, d.text);
    // HANDLES la capete (ca TradingView): cerculete mici, vizibile DOAR pe selectat â€” tragi de ele = schimbi unghi/lungime
    if(selected){ ctx.fillStyle="#fff"; ctx.strokeStyle="#2962ff"; ctx.lineWidth=1.5;
      for(const [hx,hy] of pts){ ctx.beginPath(); ctx.arc(hx,hy,4,0,7); ctx.fill(); ctx.stroke(); } ctx.lineWidth=1; } }
  else if(d.type==="rect" && pts.length>=2){
    const x1=Math.min(pts[0][0],pts[1][0]), x2=Math.max(pts[0][0],pts[1][0]);
    const y1=Math.min(pts[0][1],pts[1][1]), y2=Math.max(pts[0][1],pts[1][1]);
    ctx.globalAlpha=0.12; ctx.fillStyle=ctx.strokeStyle;
    ctx.fillRect(x1,y1,x2-x1,y2-y1); ctx.globalAlpha=1;
    ctx.strokeRect(x1,y1,x2-x1,y2-y1);
    if(d.text) drawNoteBox(ctx, Math.min(x2+10, W-240), Math.max(y1+4, 14), d.text);
    // HANDLES la colturi (ca TradingView): tragi de ele = redimensionezi zona
    if(selected){ ctx.fillStyle="#fff"; ctx.strokeStyle="#2962ff"; ctx.lineWidth=1.5;
      for(const [hx,hy] of pts){ ctx.beginPath(); ctx.arc(hx,hy,4,0,7); ctx.fill(); ctx.stroke(); } ctx.lineWidth=1; } }
  else if(d.type==="hline"){ const y=pts[0][1];
    ctx.setLineDash([6,4]); ctx.beginPath(); ctx.moveTo(60,y); ctx.lineTo(W-52,y); ctx.stroke(); ctx.setLineDash([]);
    ctx.fillStyle=ctx.strokeStyle; ctx.font="10px Segoe UI, Arial"; ctx.textAlign="left";
    ctx.fillText(fmtP(d.pts[0].price), 62, Math.max(10,y-3));
    if(d.text) drawNoteBox(ctx, 90, Math.max(10,y-24), d.text); }
  else if(d.type==="arrow" && pts.length>=1){
    const a=pts[0];
    ctx.fillStyle=ctx.strokeStyle;
    ctx.beginPath(); ctx.moveTo(a[0]-6,a[1]+6); ctx.lineTo(a[0]+6,a[1]+6); ctx.lineTo(a[0],a[1]-6); ctx.fill();
    if(d.text){ ctx.fillStyle="rgba(19,23,34,0.88)";
      const w=Math.min(260, d.text.length*6+12);
      ctx.fillRect(a[0]+10, a[1]-26, w, 20);
      ctx.strokeStyle=COL.line; ctx.strokeRect(a[0]+10,a[1]-26,w,20);
      ctx.fillStyle=COL.text; ctx.font="10px Segoe UI, Arial";
      ctx.fillText(d.text.length>40?d.text.slice(0,40)+"â€¦":d.text, a[0]+16, a[1]-12); } }
  // ruler live pe draft (Linie/Zona): cati pips, cate bare, cat timp
  if(isDraft && (d.type==="line"||d.type==="rect") && pts.length>=2){
    const p0=d.pts[0], p1=d.pts[1];
    const pips=Math.abs(p1.price-p0.price)/PIP, bars=Math.abs(p1.bar-p0.bar);
    const lab=pips.toFixed(1)+" pips Â· "+bars+" bare Â· "+fmtDur(Math.round(bars*15));
    ctx.font="10px Segoe UI, Arial"; ctx.textAlign="left";
    const w=ctx.measureText(lab).width+10;
    let lx=pts[1][0]+10, ly=pts[1][1]-24;
    if(lx+w>W-52) lx=pts[1][0]-10-w;
    if(ly<6) ly=pts[1][1]+10;
    ctx.fillStyle="rgba(19,23,34,0.88)"; ctx.fillRect(lx,ly,w,17);
    ctx.strokeStyle="#3a3f4d"; ctx.strokeRect(lx,ly,w,17);
    ctx.fillStyle="#ffd54f"; ctx.fillText(lab, lx+5, ly+12);
  }
  if(isDraft && pts.length===1){ ctx.fillStyle=COL.draw; ctx.beginPath(); ctx.arc(pts[0][0],pts[0][1],3,0,7); ctx.fill(); }
}

function hitDrawing(x, y, tol){
  // capetele desenului SELECTAT au PRIORITATE (ca TradingView): handles mici la capete/colÈ›uri
  if(sel && sel.pts && sel.pts.length>=2 && (sel.type==="line"||sel.type==="rect")){
    const hTol=Math.max(7, tol+2);
    for(let i=0;i<sel.pts.length;i++){
      const p=sel.pts[i];
      const hx=xAtBar(p.bar), hy=yAtPrice(p.price);
      if(Math.hypot(x-hx, y-hy)<=hTol){ return Object.assign(Object.create(Object.getPrototypeOf(sel)), sel, {_pt:i}); }
    }
  }
  const hits=drawings.map(d=>{
    if(d.type==="hline"){ if(x>=60 && Math.abs(yAtPrice(d.pts[0].price)-y)<tol) return d; return null; }  // pe TOATA linia (nu doar manerul din stanga)
    if(d.type==="arrow"){ return (Math.abs(xAtBar(d.pts[0].bar)-x)<12 && Math.abs(yAtPrice(d.pts[0].price)-y)<12) ? d : null; }
    const p1=[xAtBar(d.pts[0].bar), yAtPrice(d.pts[0].price)];
    const p2=[xAtBar(d.pts[1].bar), yAtPrice(d.pts[1].price)];
    if(d.type==="pen"){
      // distanta la ORICE segment al poliliniei
      for(let i=1;i<d.pts.length;i++){
        const a=[xAtBar(d.pts[i-1].bar), yAtPrice(d.pts[i-1].price)];
        const b=[xAtBar(d.pts[i].bar), yAtPrice(d.pts[i].price)];
        const dx=b[0]-a[0], dy=b[1]-a[1];
        const L2=dx*dx+dy*dy;
        if(L2<1){ if(Math.hypot(x-a[0],y-a[1])<tol) return d; continue; }
        const t=Math.max(0,Math.min(1,((x-a[0])*dx+(y-a[1])*dy)/L2));
        if(Math.hypot(x-(a[0]+t*dx), y-(a[1]+t*dy))<tol) return d;
      }
      return null;
    }
    if(d.type==="line"){
      // distanta punct-segment
      const dx=p2[0]-p1[0], dy=p2[1]-p1[1];
      const L2=dx*dx+dy*dy;
      if(L2<1) return Math.hypot(x-p1[0],y-p1[1])<tol?d:null;
      const t=Math.max(0,Math.min(1,((x-p1[0])*dx+(y-p1[1])*dy)/L2));
      const px=p1[0]+t*dx, py=p1[1]+t*dy;
      return Math.hypot(x-px,y-py)<tol?d:null;
    }
    if(d.type==="rect"){
      const x1=Math.min(p1[0],p2[0]), x2=Math.max(p1[0],p2[0]);
      const y1=Math.min(p1[1],p2[1]), y2=Math.max(p1[1],p2[1]);
      if(x>=x1-4&&x<=x2+4&&y>=y1-4&&y<=y2+4) return d;
      return null;
    }
    return null; }).filter(Boolean);
  return hits.length?hits[hits.length-1]:null;
}

function escapeHtml(s){ return s.replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;"); }

// badge WIN/LOSS/OPEN/no fill pentru lista din dreapta â€” culoare + text mic, ca pe chart
function resBadge(m){
  try{
    const r=btRun(m); if(!r) return "";
    const map={ WIN:["WIN","#26a69a"], LOSS:["LOSS","#ef5350"], OPEN:["OPEN","#f5c542"], NOFILL:["no fill","#787b86"], EXPIRED:["expired","#9aa0ab"] };
    const [txt,col]=map[r.res]||["?","#787b86"];
    return '<span class="resbadge" style="color:'+col+';border-color:'+col+'">'+txt+'</span>';
  }catch(e){ return ""; }
}

function renderList(){
  const l=el("list");
  let html='';
  if(!markers.length && !drawings.length){ l.innerHTML='<div style="font-size:12px;color:#787b86;padding:8px">Nimic Ã®ncÄƒ. Click pe chart = marker; alege o unealtÄƒ de desen din toolbar.</div>'; return; }
  if(drawings.length){
    html+='<div class="sechead">Desene<span class="cnt">'+drawings.length+'</span></div>';
    drawings.forEach((d,i)=>{
      const lab={line:"ðŸ“ Linie",pen:"âœï¸ Pen",rect:"ðŸŸ¦ ZonÄƒ",hline:"âž– H-Linie",arrow:"ðŸ’¬ NotÄƒ"}[d.type]||d.type;
      const a=d.pts[0], b=d.pts[1]||d.pts[0];
      html+='<div class="drw'+(sel===d?" sel":"")+'" data-d="'+i+'"><b>'+(d.tag?'<span style="color:#4a6fd4;font-weight:800">'+d.tag+'</span> ':'')+lab+'</b> Â· '+
        fmtTRO(DATA[a.bar][0])+' â†’ '+fmtTRO(DATA[b.bar][0])+'<br>'+
        '<span style="color:#787b86">x:'+DATA[a.bar][0]+'..'+DATA[b.bar][0]+' Â· y:'+a.price.toFixed(5)+'..'+b.price.toFixed(5)+'</span>'+
        '<div style="margin-top:4px"><button data-dd="'+i+'">ðŸ—‘</button></div></div>';
    });
  }
  if(markers.length){
    const ghosts=markers.filter(m=>m.ghost), mine=markers.filter(m=>!m.ghost);
    // treeView: 'all' = ambele secÈ›iuni Â· 'ai' = doar ghost AI Â· 'mine' = doar ale tale (butonul ðŸ¤– Bot = switch Ã®n object tree, NU atinge chart-ul)
    if(ghosts.length && treeView!=="mine" && botActivated){
      html+='<div class="sechead" style="color:#f5c542;border-top-color:#f5c542;background:rgba(245,197,66,0.08)">ðŸ‘» Ghost AI â€” Backtest<span class="cnt">'+ghosts.length+'</span></div>';
      [...ghosts].sort((a,b)=>a.bar-b.bar).forEach(m=>{
        const c=DATA[m.bar]; if(!c) return;
        const col=m.dir==="LONG"?"#26a69a":"#ef5350";
        const selCls=(selMk===m || (selSet.length>1 && selSet.some(it=>it.kind==="m" && it.ref===m)))?" sel":"";
        html+='<div class="mk ghost'+(m.dir==="SHORT"?" sell":"")+selCls+'" data-mid="'+m.id+'"><div class="top"><span class="tag" style="background:'+col+'">'+(m.tag?m.tag:'#'+m.id)+' '+m.dir+' AI</span>'+
          '<span class="time">'+fmtTRO(c[0])+'</span><span>'+fmtP(m.price)+'</span>'+resBadge(m)+'</div>'+
          (m.sl!=null?'<div class="meta">SL '+m.sl+'p Â· TP '+(m.tp!=null?m.tp:"-")+'p</div>':'')+
          '<textarea class="inote" data-mid="'+m.id+'" placeholder="PASS/SKIP? De ce?â€¦" rows="2">'+(m.note?escapeHtml(m.note):"")+'</textarea>'+
          '<div class="acts"><button data-a="del" data-mid="'+m.id+'">ðŸ—‘ SKIP (È™terge)</button></div></div>';
      });
    }
    if(mine.length && treeView!=="ai"){
      html+='<div class="sechead">Trade-urile tale<span class="cnt">'+mine.length+'</span></div>';
      [...mine].sort((a,b)=>a.bar-b.bar).forEach(m=>{
        const c=DATA[m.bar]; if(!c) return;
        const seen=(m.seen_through!=null && m.seen_through<DATA.length)?fmtTRO(DATA[m.seen_through][0]).slice(0,10):"-";
        const selCls=(selMk===m || (selSet.length>1 && selSet.some(it=>it.kind==="m" && it.ref===m)))?" sel":"";
        html+='<div class="mk '+(m.dir==="SHORT"?"sell":"")+selCls+'" data-mid="'+m.id+'"><div class="top"><span class="tag '+(m.dir==="LONG"?"buy":"sell")+'">#'+m.id+' '+m.dir+
          '</span><span class="time">'+fmtTRO(c[0])+'</span><span>'+fmtP(m.price)+'</span>'+resBadge(m)+'</div>'+
          (m.sl!=null?'<div class="meta">SL '+m.sl+'p Â· TP '+(m.tp!=null?m.tp:"-")+'p Â· R:R '+(m.sl>0?(m.tp/m.sl).toFixed(2):"-")+'</div>':'')+
          '<textarea class="inote" data-mid="'+m.id+'" placeholder="Comentariu (de ce)â€¦" rows="2">'+(m.note?escapeHtml(m.note):"")+'</textarea>'+
          '<div class="meta">grup: <select class="igrp" data-mid="'+m.id+'">'+
            '<option value="">â€”</option>'+[1,2,3,4,5].map(g=>'<option value="'+g+'"'+(m.group==g?" selected":"")+'>Grup '+g+'</option>').join('')+
          '</select> Â· seen pÃ¢nÄƒ la '+seen+(m.blind?' Â· blind':' Â· tot chart-ul')+'</div>'+
          '<div class="acts"><button data-a="edit" data-mid="'+m.id+'">âœŽ detalii</button><button data-a="del" data-mid="'+m.id+'">ðŸ—‘ È™terge</button></div></div>';
      });
    }
  }
  l.innerHTML=html;
  l.querySelectorAll('[data-d]').forEach(b=>b.onclick=ev=>{
    if(ev.target.dataset.dd!==undefined){ drawings.splice(+ev.target.dataset.dd,1); sel=null; save(); requestRender(); return; }
    const i=+b.dataset.d; sel=(sel===drawings[i])?null:drawings[i]; save(); requestRender(); });
  l.querySelectorAll('[data-a="edit"]').forEach(b=>{ const mk=markers.find(x=>x.id===+b.dataset.mid); if(mk) b.onclick=()=>openDlg(mk.bar,mk.price,mk); });
  l.querySelectorAll('[data-a="del"]').forEach(b=>{ const mk=markers.find(x=>x.id===+b.dataset.mid); if(mk) b.onclick=()=>{ markers.splice(markers.indexOf(mk),1); save(); requestRender(); }; });
  // comentariu inline (textarea) + grup (select) â€” salveaza direct, fara dialog
  l.querySelectorAll('.inote').forEach(t=>t.onchange=()=>{ const mk=markers.find(x=>x.id===+t.dataset.mid); if(mk){ mk.note=t.value.trim(); save(); } });
  l.querySelectorAll('.igrp').forEach(s=>s.onchange=()=>{ const mk=markers.find(x=>x.id===+s.dataset.mid); if(mk){ mk.group=s.value?+s.value:null; save(); requestRender(); } });
}
function jumpTo(b){ view.start=Math.max(0, Math.min(b-60, maxStart())); view.count=120; yRangeCache=null; requestRender(); }

// SincronizeazÄƒ lista din dreapta cu selecÈ›ia de pe chart: evidenÈ›iazÄƒ rÃ¢ndul poziÈ›iei selectate
// + face scroll la el (ca sÄƒ nu o cauÈ›i dupÄƒ ID pe un chart aglomerat).
function syncListSel(){
  try{   // FIX: dacÄƒ lista nu are Ã®ncÄƒ rÃ¢nduri (sau altceva crapÄƒ), NU opri click-ul/dblclick-ul pe chart
  const l=el("list");
  // curÄƒÈ›Äƒ evidenÈ›ierea veche, apoi aplicÄƒ pe cea activÄƒ (selMk sau multi-select)
  l.querySelectorAll(".mk").forEach(el2=>{
    const mk=markers.find(x=>x.id===+el2.dataset.mid);
    const on = mk && (mk===selMk || (selSet.length>1 && selSet.some(it=>it.kind==="m" && it.ref===mk)));
    el2.classList.toggle("sel", !!on);
  });
  if(selMk){
    const row=l.querySelector('.mk[data-mid="'+selMk.id+'"]');
    if(row && row.scrollIntoView) row.scrollIntoView({block:"nearest", behavior:"smooth"});
  }
  }catch(e){}
}

function save(){ pushHist();
  if(storageOK){ try{ const prof=JSON.stringify(normalizeToM15({markers,drawings,indicators,omarParams}));   // v7.53: salvÄƒm MEREU Ã®n coordonate M15 (profil TF-safe)
      localStorage.setItem("gbpusd_full_data", prof);                       // compat vechi
      localStorage.setItem("gbpusd_full_profile", prof);                    // PROFIL dedicat (separat de datele chart)
      localStorage.setItem("gbpusd_full_profile_bak", prof);                // backup permanent (anti-suprascriere)
    }catch(e){}
    try{ const cur=JSON.parse(localStorage.getItem("gbpusd_last")||"null")||{};
      cur.sl=lastSl; cur.tp=lastTp; cur.fc=lastFc; cur.exp=lastExp;
      cur.lookaheadTs=DATA[Math.min(cutoff, DATA.length-1)][0];   // progresul lookahead se salveaza si la Ctrl+S (nu doar la butonul dedicat)
      localStorage.setItem("gbpusd_last", JSON.stringify(cur)); }catch(e){} }
  renderList(); }
function exportProfile(){
  const obj={ app:"gbpusd_draw", profile_v:2, ts:new Date().toISOString(), n:markers.length, d:drawings.length,
    markers, drawings, indicators, omarParams };
  const json=JSON.stringify(obj, null, 1);
  try{ const b=new Blob([json],{type:"application/json"}); const a=document.createElement("a"); a.href=URL.createObjectURL(b); a.download="gbpusd_draw.profile.json"; a.click(); }catch(e){}   // nume fix â€” pui JSON-ul in _charts/profiles/ ca sa devina default la urmatorul build
  toast("Profil exportat: "+markers.length+" markers, "+drawings.length+" drawings (JSON)");
  return json;
}
function importProfile(jsonStr){
  try{
    const o=typeof jsonStr==="string"?JSON.parse(jsonStr):jsonStr;
    if(!o || (!Array.isArray(o.markers)&&!Array.isArray(o.drawings))){ toast("Profil invalid â€” lipsesc markers/drawings"); return false; }
    const srcTF=(o.tf==="M1"||o.tf==="M15"||o.tf==="H1"||o.tf==="H4"||o.tf==="D1")?o.tf:detectProfileTF(o);   // v7.53: profil importat pe alt TF â†’ remapat
    if(srcTF && srcTF!=="M15"){ remapProfileTF(o, srcTF); toast("Profil importat pe "+srcTF+" â†’ remapat pe M15"); }
    if(Array.isArray(o.markers)) markers=o.markers.filter(m=>m&&Number.isInteger(m.bar)&&m.bar>=0&&m.bar<DATA.length).map(m=>({...m, ghost:!!m.ghost}));
    if(Array.isArray(o.drawings)) drawings=o.drawings.filter(d=>d&&Array.isArray(d.pts)&&d.pts.length>=1&&d.pts.every(p=>Number.isInteger(p.bar)&&p.bar>=0&&p.bar<DATA.length&&isFinite(p.price)));
    if(Array.isArray(o.indicators)&&o.indicators.length) indicators=o.indicators.filter(x=>IND_TYPES[x.type]).map(x=>({type:x.type, on:x.on!==false, params:Object.assign({}, IND_TYPES[x.type].defaults, x.params||{})}));
    if(o.omarParams) omarParams=Object.assign({}, IND_TYPES.omar.defaults, o.omarParams);
    mkSeq=markers.reduce((mx,m)=>Math.max(mx, typeof m.id==="number"?m.id:0),0);
    drwSeq=drawings.reduce((mx,d)=>Math.max(mx, typeof d.id==="number"?d.id:0),0);
    save(); requestRender(); renderList();
    toast("Profil importat: "+markers.length+" markers, "+drawings.length+" drawings");
    return true;
  }catch(e){ toast("Import esuat: "+e.message); return false; }
}
el("expProfBtn").onclick=()=>{ exportProfile(); };
el("impProfBtn").onclick=()=>{ const f=document.createElement("input"); f.type="file"; f.accept=".json";
  f.onchange=()=>{ const fr=new FileReader(); fr.onload=()=>importProfile(fr.result); fr.readAsText(f.files[0]); }; f.click(); };

// ---- COPY / PASTE (Ctrl+C / Ctrl+V) â€” copiazÄƒ obiectele selectate de pe chart (ca TradingView) ----
let clipData=null;   // {markers:[], drawings:[]} â€” copia din Ctrl+C
function copySelection(){
  const mk = selMk ? [selMk] : selSet.filter(it=>it.kind==="m").map(it=>it.ref);
  const dr = sel ? [sel] : selSet.filter(it=>it.kind==="d").map(it=>it.ref);
  if(!mk.length && !dr.length){ toast("SelecteazÄƒ Ã®ntÃ¢i ce vrei sÄƒ copiezi (click pe poziÈ›ie/desen sau Ctrl+drag box)"); return; }
  // deep copy + id-uri curate (paste-ul genereazÄƒ altele noi)
  clipData={ markers: mk.map(m=>({...m})), drawings: dr.map(d=>({...d, pts:d.pts.map(p=>({...p}))})) };
  toast("ðŸ“‹ Copiat: "+mk.length+" poziÈ›ii, "+dr.length+" desene â€” Ctrl+V sÄƒ lipeÈ™ti");
}
function pasteClipboard(){
  if(!clipData || (!clipData.markers.length && !clipData.drawings.length)){ toast("Clipboard gol â€” mai Ã®ntÃ¢i Ctrl+C pe ceva selectat"); return; }
  const mx=blind?cutoff:DATA.length-1;
  // sincronizez secventa de id-uri cu desenele existente (import/manual push pot fi lasa drwSeq in urma)
  drwSeq = Math.max(drwSeq, drawings.reduce((mx2,d)=>Math.max(mx2, typeof d.id==="number"?d.id:0), 0));
  // offset: 5 bare la dreapta + puÈ›in preÈ› (ca sÄƒ vezi duplicatul lÃ¢ngÄƒ original)
  const dBar=5, dPrice=2*PIP;
  for(const m of clipData.markers){
    const nb=Math.max(0,Math.min(mx,m.bar+dBar));
    markers.push({ ...m, id:++mkSeq, bar:nb, ts:(DATA[nb]?DATA[nb][0]:m.ts), price:m.price+dPrice, created:Date.now() });   // v7.54: ts urmeazÄƒ bara lipitÄƒ
  }
  for(const d of clipData.drawings){
    const nd={ ...d, id:++drwSeq, pts:d.pts.map(p=>({ bar:Math.max(0,Math.min(mx,p.bar+dBar)), price:p.price+dPrice })) };
    drawings.push(nd); drwSeq=Math.max(drwSeq, nd.id);   // siguranta: id-ul nou nu colizioneaza
  }
  save(); requestRender();
  toast("ðŸ“‹ Lipit: "+clipData.markers.length+" poziÈ›ii, "+clipData.drawings.length+" desene (offset +5 bare)");
}

// ---- UNDO / REDO (Ctrl+Z / Ctrl+Shift+Z / Ctrl+Y + butoane â†©ï¸ â†ªï¸) ----
// (hist declarat sus, inainte de save â€” vezi 'let hist' langa markers)
function pushHist(){
  const snap=JSON.stringify({markers,drawings});
  if(hist.length && hist[histIdx]===snap) return;       // dedupe: nimic schimbat
  hist=hist.slice(0, histIdx+1);                         // taie redo la o noua actiune
  hist.push(snap); if(hist.length>60) hist.shift();
  histIdx=hist.length-1;
  el("undoBtn").disabled=histIdx<=0; el("redoBtn").disabled=histIdx>=hist.length-1;
}
function undo(){
  if(histIdx<=0) return;
  histIdx--; const s=JSON.parse(hist[histIdx]);
  markers=s.markers; drawings=s.drawings; selMk=null; sel=null; posDraft=null;
  requestRender(); renderList();
  el("undoBtn").disabled=histIdx<=0; el("redoBtn").disabled=histIdx>=hist.length-1;
}
function redo(){
  if(histIdx>=hist.length-1) return;
  histIdx++; const s=JSON.parse(hist[histIdx]);
  markers=s.markers; drawings=s.drawings; selMk=null; sel=null; posDraft=null;
  requestRender(); renderList();
  el("undoBtn").disabled=histIdx<=0; el("redoBtn").disabled=histIdx>=hist.length-1;
}
el("undoBtn").onclick=undo; el("redoBtn").onclick=redo;
pushHist();

function toast(t){ const e=el("toast"); e.textContent=t;
  e.style.display="block"; clearTimeout(e._t); e._t=setTimeout(()=>e.style.display="none",1800); }

function reveal(n){ if(!blind) return; cutoff=Math.min(DATA.length-1, cutoff+n); yLock=null; yRangeCache=null;
  if(view.start+view.count-1 < cutoff) view.start=Math.min(maxStart(), cutoff-view.count+1);
  requestRender(); }
// ---- PLAY: dezvÄƒluie candela urmÄƒtoare; Space = toggle, È›ine apÄƒsat = accelerare ----
let playing=false, playTimer=null, playSpeed=1, playHold=false;
function startPlay(){
  if(!blind){ blind=true; cutoff=Math.min(DATA.length-1, view.start+view.count-1);
    toggleBlindUI(); }
  playing=true; setPlayIcon(true);
  playTimer=setInterval(()=>{
    if(cutoff>=DATA.length-1){ stopPlay(); return; }
    reveal(playSpeed);
    if(playSpeed>1 && cutoff<DATA.length-1) reveal(playSpeed-1);  // accelerare: mai multe candele pe tick
  }, 110);
}
function stopPlay(){ playing=false; setPlayIcon(false);
  if(playTimer){ clearInterval(playTimer); playTimer=null; } }
function togglePlay(){ playing?stopPlay():startPlay(); }
el("playBtn").onclick=togglePlay;
function toggleBlind(){
  if(blind){ blind=false; cutoff=DATA.length-1; toggleBlindUI();
    el("blindBtn").title="Blind OFF: vezi tot chart-ul";
    toast("Blind dezactivat â€” vezi tot chart-ul"); }
  else { blind=true; cutoff=Math.min(DATA.length-1, view.start+view.count-1);
    toggleBlindUI();
    el("blindBtn").title="Blind ON: ascunde viitorul â€” dezvÄƒlui cu +10/+60";
    toast("Lookahead ON â€” candelele viitoare ascunse"); }
  yLock=null; yRangeCache=null;   // FIX: cutoff-ul s-a schimbat â€” scala veche e stale
  requestRender(); }

function openDlg(bar, price, m){
  if(bar<0||bar>=DATA.length) return;
  if(blind && bar>cutoff) bar=cutoff;      // ancoreaza dialogul, NU muta marker-ul
  const saveBar=m?m.bar:bar;               // marker-ul editat isi pastreaza bara originala
  const box=el("chartBox"), dlg=el("dlg");
  const up=m?m.dir==="LONG":DATA[bar][4]>=DATA[bar][1];
  const sl=m&&m.sl!=null?m.sl:lastSl, tp=m&&m.tp!=null?m.tp:lastTp;
  const fc=m&&m.fc>0?m.fc:lastFc;   // "same size": ultimele setari devin default la urmatorul marker
  const exp=(m&&m.exp>0)?m.exp:lastExp;   // expiry entry (bare) â€” dacÄƒ nu e atins Ã®n N candele => expired
  dlgTarget=m||null; dlgNoteBase=(m&&m.note)||"";   // v7.43: target + valoare initiala pt auto-save
  dlg.innerHTML='<h4>'+(m?"EditeazÄƒ":"MarcheazÄƒ")+' poziÈ›ie â€” '+fmtTRO(DATA[bar][0])+' @ '+fmtP(price)+'</h4>'+
    '<div class="row"><label>DirecÈ›ie</label><div class="dirbtns">'+
    '<button class="dir buy '+(up?"on":"")+'" data-dir="LONG">â–² LONG</button>'+
    '<button class="dir sell '+(!up?"on":"")+'" data-dir="SHORT">â–¼ SHORT</button></div></div>'+
    '<div class="row"><label>SL / TP (pips)</label><div style="display:flex;gap:6px">'+
    '<input id="sl" type="number" step="0.1" min="0.5" value="'+sl+'"><input id="tp" type="number" step="0.1" min="0.5" value="'+tp+'"></div></div>'+
    '<div class="row"><label>Forecast (bare) â€” lÄƒÈ›imea box-ului</label>'+
    '<div style="display:flex;align-items:center;gap:6px">'+
    '<input id="fc" type="range" min="5" max="240" step="1" value="'+fc+'">'+
    '<span id="fcVal" style="min-width:34px;text-align:right">'+fc+'</span></div></div>'+
    '<div class="row"><label>Expiry entry (bare) â€” dacÄƒ preÈ›ul nu atinge entry-ul Ã®n N candele â‡’ expired</label>'+
    '<div style="display:flex;align-items:center;gap:6px">'+
    '<input id="exp" type="range" min="0" max="60" step="1" value="'+exp+'">'+
    '<span id="expVal" style="min-width:34px;text-align:right">'+(exp>0?exp:"âˆž")+'</span></div></div>'+
    '<div class="row"><label>DE CE ai lua trade-ul? (ce vezi pe chart)</label>'+
    '<textarea id="note" placeholder="ex: trend clar, NW la pullback, CHoCH recent, sesiune bunÄƒâ€¦">'+(m?escapeHtml(m.note):"")+'</textarea></div>'+
    '<div class="acts"><button class="cancel">AnuleazÄƒ</button><button class="save">SalveazÄƒ</button></div>';
  dlg.style.display="block"; dlgOpen=true; dlgOpenedAt=Date.now();
  // CENTRAT (ca TradingView) â€” dialogul nu mai acoperÄƒ locul de pe chart pe care Ã®l descrii
  const r=box.getBoundingClientRect();
  const w=dlg.offsetWidth||300, h=dlg.offsetHeight||240;
  const x=Math.max(10, Math.round((r.width-w)/2));
  const y=Math.max(10, Math.round((r.height-h)/2));
  dlg.style.left=x+"px"; dlg.style.top=y+"px";
  let dir=up?"LONG":"SHORT";
  function updPrev(){ const slv=parseFloat(dlg.querySelector("#sl").value), tpv=parseFloat(dlg.querySelector("#tp").value);
    const fcv=parseInt(dlg.querySelector("#fc").value,10)||60;
    const expv=parseInt(dlg.querySelector("#exp").value,10)||0;
    el("fcVal").textContent=fcv;
    el("expVal").textContent=expv>0?expv:"âˆž";
    dlgPreview={ bar:saveBar, price, dir, fc:fcv, exp:expv,
      sl:(isFinite(slv)&&slv>0)?slv:null, tp:(isFinite(tpv)&&tpv>0)?tpv:null };
    requestRender(); }
  dlgPreview={ bar:saveBar, price, dir, fc, exp, sl, tp };
  dlg.querySelectorAll(".dir").forEach(b=>b.onclick=()=>{
    dir=b.dataset.dir; dlg.querySelectorAll(".dir").forEach(x=>x.classList.remove("on")); b.classList.add("on"); updPrev(); });
  dlg.querySelector("#sl").addEventListener("input", updPrev);
  dlg.querySelector("#tp").addEventListener("input", updPrev);
  dlg.querySelector("#fc").addEventListener("input", updPrev);
  dlg.querySelector("#exp").addEventListener("input", updPrev);
  dlg.querySelector(".save").onclick=()=>{
    const note=dlg.querySelector("#note").value.trim();
    const slv=parseFloat(dlg.querySelector("#sl").value), tpv=parseFloat(dlg.querySelector("#tp").value);
    const fcv=parseInt(dlg.querySelector("#fc").value,10)||60;
    const expv=parseInt(dlg.querySelector("#exp").value,10)||0;
    lastSl=isFinite(slv)&&slv>0?slv:lastSl; lastTp=isFinite(tpv)&&tpv>0?tpv:lastTp; lastFc=fcv; lastExp=expv;   // same size la urmatorul
    const mk={ id:(m&&m.id>0)?m.id:++mkSeq, bar:saveBar, price, dir, note, fc:fcv, exp:expv,
               tf:(m&&m.tf)?m.tf:TF, ts:(m&&m.ts!=null)?m.ts:(DATA[saveBar]?DATA[saveBar][0]:undefined),   // v7.54: TF de plasare + ancora de timp
               sl:(isFinite(slv)&&slv>0)?slv:6.5, tp:(isFinite(tpv)&&tpv>0)?tpv:6.5,
               created:m?m.created:Date.now(),
               seen_through:m?m.seen_through:(blind?cutoff:null), blind:m?m.blind:blind,
               ghost:m?m.ghost:false,   // FIX CRITIC: fara asta, marker-ul editat prin dialog avea ghost=undefined
               group:m?m.group:null };  // => drawMarker face early-return (ghost!==nwVisible) => DISPAREA de pe chart (ex. #92)
    if(m){ const i=markers.indexOf(m); markers[i]=mk;
      // FIX: marker-ul editat e ÃŽNLOCUIT cu obiect nou (mk) â€” selMk/selSet trebuie sa pointeze la NOUL obiect,
      // altfel cu izolarea ON se deseneaza cel VECHI (fara comentariul nou) => comentariul "dispare" de pe chart
      if(selMk===m) selMk=mk;
      if(selSet.length) selSet.forEach(it=>{ if(it.kind==="m" && it.ref===m) it.ref=mk; });
    } else markers.push(mk);
    save(); closeDlg(); requestRender();
    toast("Marker salvat (SL "+mk.sl+"p / TP "+mk.tp+"p / forecast "+fcv+"b)"+(note?" â€” "+note.slice(0,40):"")); };
  dlg.querySelector(".cancel").onclick=closeDlg;
  dlg.querySelector("#note").focus();
}
function openArrowDlg(d, isNew){
  const box=el("chartBox"), dlg=el("dlg");
  const p=d.pts[0];
  dlgTarget=d; dlgNoteBase=(d.text||"");   // v7.43: target + valoare initiala pt auto-save
  dlg.innerHTML='<h4>ðŸ’¬ NotÄƒ â€” '+fmtTRO(DATA[p.bar][0])+' @ '+fmtP(p.price)+'</h4>'+
    '<div class="row"><label>DE CE? Subiectivitatea ta, Ã®n cuvintele tale (ce vezi aici):</label>'+
    '<textarea id="note" placeholder="ex: trendul s-a stricat aici, nivelul a rezistat de 3 ori, aici aÈ™ fi intrat dar era lÃ¢ngÄƒ È™tiriâ€¦">'+escapeHtml(d.text||"")+'</textarea></div>'+
    '<div class="acts"><button class="cancel">AnuleazÄƒ</button><button class="save">SalveazÄƒ</button></div>';
  dlg.style.display="block"; dlgOpen=true; dlgOpenedAt=Date.now();
  // CENTRAT (ca TradingView) â€” dialogul nu mai acoperÄƒ locul de pe chart pe care Ã®l descrii
  const r=box.getBoundingClientRect();
  const w=dlg.offsetWidth||300, h=dlg.offsetHeight||240;
  const x=Math.max(10, Math.round((r.width-w)/2));
  const y=Math.max(10, Math.round((r.height-h)/2));
  dlg.style.left=x+"px"; dlg.style.top=y+"px";
  dlg.querySelector(".save").onclick=()=>{ d.text=dlg.querySelector("#note").value.trim();
    if(isNew){ drawings.push(d); }   // arrow nou: abia ACUM intra in drawings
    save(); closeDlg(); requestRender(); toast("NotÄƒ salvatÄƒ"); };
  dlg.querySelector(".cancel").onclick=()=>{ closeDlg(); requestRender(); };  // CANCEL NU STERGE NIMIC â€” desenul rÄƒmÃ¢ne (Delete = È™tergere)
  dlg.querySelector("#note").focus();
}

function closeDlg(saveIfDirty){   // v7.43: saveIfDirty=true => click-out â€” salveaza nota daca s-a modificat (nu o pierzi la click gresit)
  if(saveIfDirty && dlgTarget){
    const ta=el("dlg").querySelector("#note");
    if(ta && ta.value!==dlgNoteBase){
      const val=ta.value.trim();
      if(dlgTarget.dir!==undefined && !dlgTarget.pts) dlgTarget.note=val;      // marker trade
      else if(dlgTarget.pts) dlgTarget.text=val;                                // drawing
      save();
    }
  }
  el("dlg").style.display="none"; dlgOpen=false; dlgPreview=null; dlgTarget=null; requestRender(); }
function saveDlgOnClose(){ closeDlg(true); }

// DIALOG MUTABIL (ca TradingView): trage de ORICARE din dialog ca sÄƒ-l muÈ›i â€” doar cÃ¢mpurile unde scrii nu se trage de pe ele
let dlgDrag=null;   // {dx,dy} offset mouseâ†”dialog (null = nu se trage)
el("dlg").addEventListener("mousedown", ev=>{
  if(!dlgOpen) return;
  const t=ev.target;
  // cÃ¢mpuri editabile / interactive: cursor normal, drag NU porneÈ™te de pe ele
  if(t && t.closest && t.closest("input,textarea,select,button")) return;
  const d=el("dlg");
  dlgDrag={ dx: ev.clientX-d.offsetLeft, dy: ev.clientY-d.offsetTop };
  ev.preventDefault();
});
window.addEventListener("mousemove", ev=>{
  if(!dlgDrag) return;
  const d=el("dlg"), box=el("chartBox").getBoundingClientRect();
  let x=ev.clientX-dlgDrag.dx, y=ev.clientY-dlgDrag.dy;
  x=Math.max(6, Math.min(x, box.width-d.offsetWidth-6));    // nu iese din chart
  y=Math.max(6, Math.min(y, box.height-d.offsetHeight-6));
  d.style.left=x+"px"; d.style.top=y+"px";
});

function setPlayIcon(p){ el("playBtn").querySelector("use").setAttribute("href", p?"#i-pause":"#i-play"); }
function toggleBlindUI(){
  el("blindBtn").querySelector("use").setAttribute("href", blind?"#i-lock":"#i-unlock");
  el("blindBtn").title = blind ? "Lookahead ON: viitorul e ascuns (gri) â€” dezvÄƒlui cu +10/+60 sau Play" : "Lookahead OFF: vezi tot chart-ul â€” apasÄƒ ca sÄƒ ascunzi viitorul";
  el("blindBtn").classList.toggle("on", blind);
  try{ el("blindBtn").querySelector("span").textContent = blind ? "Lookahead ON" : "Lookahead OFF"; }catch(e){}
}
function resetView(){   // FIT CONTENT (ca TradingView) â€” buton nou + tasta A + dblclick pe pricebar â†’ un singur loc
  view.start=0; view.count=250; vzoom=1; yOff=0;
  yLock=null; yRangeCache=null; zoomAnim=null; vzoomAnim=null;
  requestRender();
  toast("Reset view â€” 250 bare, zoom 100%");
}
function setTool(t){
  tool=t; draft=null; sel=null;
  document.querySelectorAll("#toolbar [data-t], #toolrail [data-t], #drawbar [data-t], #favbar [data-t]").forEach(b=>b.classList.toggle("on", b.dataset.t===t));
  cv.style.cursor="crosshair"; requestRender(); save(); }
el("delD").onclick=()=>{ if(sel){ drawings.splice(drawings.indexOf(sel),1); sel=null; save(); requestRender(); toast("Desen È™ters"); } };

// â­ FAVORITES plutitoare (ca TradingView): PILL mic â­ = grab handle (tragi de el oriunde pe chart).
// Click pe â­ = deschide popup cu uneltele favorite (nu se lungeÈ™te pe chart). Click dreapta pe o
// unealtÄƒ din toolrail = adaugi/scoti din favorite.
let favTools=[];
try{ const f=JSON.parse(localStorage.getItem("gbpusd_favs")||"null"); if(Array.isArray(f)) favTools=f; }catch(e){}
function saveFavs(){ try{ localStorage.setItem("gbpusd_favs", JSON.stringify(favTools)); }catch(e){} }
const FAV_ICONS={ pointer:"i-pointer", long:"i-long", short:"i-short", line:"i-line", pen:"i-pen", rect:"i-rect", hline:"i-hline", arrow:"i-note" };
const FAV_NAMES={ pointer:"Select", long:"LONG", short:"SHORT", line:"Linie", pen:"Pen", rect:"ZonÄƒ", hline:"H-Linie", arrow:"NotÄƒ" };
function favPopupOpen(){ return false; }
let favPlaced=false;   // pill-ul a primit o pozitie initiala (left/top) â€” fara asta depindea de 'right' si se intindea
function ensureFavPos(){
  if(favPlaced) return;
  const fb=el("favbar"), box=el("chartBox").getBoundingClientRect();
  fb.style.left=Math.max(4, box.width-fb.offsetWidth-70)+"px";   // colt dreapta-sus, sub drawbar
  fb.style.top="70px";
  favPlaced=true;
}
function renderFavBar(){
  const fb=el("favbar");
  // TOATE uneltele favorite vizibile direct in bara (fara popup) â€” click = unealta, click dreapta = scoate
  const cntEl=el("favbar").querySelector(".favcnt");
  fb.querySelectorAll("button[data-t]").forEach(b=>b.remove());
  for(const t of favTools){
    const b=document.createElement("button");
    b.dataset.t=t; b.title=FAV_NAMES[t]+" (click = alege Â· click dreapta = scoate din favorite)";
    b.innerHTML='<svg><use href="#'+FAV_ICONS[t]+'"/></svg>';
    b.onclick=()=>setTool(t);
    b.oncontextmenu=ev=>{ ev.preventDefault(); favTools=favTools.filter(x=>x!==t); saveFavs(); renderFavBar(); toast("â­ scos din favorite: "+FAV_NAMES[t]); };
    fb.appendChild(b);
  }
  if(cntEl) cntEl.textContent = favTools.length ? String(favTools.length) : "";
  fb.style.display = favTools.length ? "flex" : "none";
  if(favTools.length) ensureFavPos();
}
function renderFavPop(){ /* popup eliminat â€” uneltele sunt direct in bara */ }
function positionFavPop(){ /* noop */ }
function closeFavPop(){ /* noop */ }
function closeFavPop(){ el("favpop").style.display="none"; }
// click pe pill â­ = toggle popup (doar daca nu a fost drag)
el("favbar").addEventListener("click", ev=>{
  if(favDrag && favDrag.moved) return;   // a fost drag â€” nu deschide popup
  if(favPopupOpen()) closeFavPop(); else { renderFavPop(); el("favpop").style.display="flex"; positionFavPop(); }
});
// click oriunde altundeva Ã®nchide popup-ul
document.addEventListener("click", ev=>{ if(!el("favbar").contains(ev.target) && !el("favpop").contains(ev.target)) closeFavPop(); });
document.querySelectorAll("#toolrail [data-t]").forEach(b=>b.addEventListener("contextmenu", ev=>{
  ev.preventDefault();
  const t=b.dataset.t;
  if(favTools.includes(t)){ favTools=favTools.filter(x=>x!==t); toast("â­ scos din favorite: "+FAV_NAMES[t]); }
  else { favTools.push(t); toast("â­ adÄƒugat la favorite: "+FAV_NAMES[t]+" â€” click pe â­ sÄƒ-l foloseÈ™ti"); }
  saveFavs(); renderFavBar();
}));
// drag pe PILL (â­ = grab handle) = muti pill-ul oriunde pe chart; popup-ul urmeazÄƒ
let favDrag=null;
el("favbar").addEventListener("mousedown", ev=>{
  if(ev.button!==0) return;
  const fb=el("favbar");
  favDrag={ dx: ev.clientX-fb.offsetLeft, dy: ev.clientY-fb.offsetTop, moved:false };
  fb.classList.add("dragging");
  ev.preventDefault();
});
window.addEventListener("mousemove", ev=>{
  if(!favDrag) return;
  favDrag.moved=true;
  const fb=el("favbar"), box=el("chartBox").getBoundingClientRect();
  let x=ev.clientX-favDrag.dx, y=ev.clientY-favDrag.dy;
  x=Math.max(2, Math.min(x, box.width-fb.offsetWidth-2));   // doar left/top â€” fara right, pill-ul nu se intinde
  y=Math.max(2, Math.min(y, box.height-fb.offsetHeight-2));
  fb.style.left=x+"px"; fb.style.top=y+"px";
  if(favPopupOpen()) positionFavPop();   // popup-ul sta lipit sub pill (clampat)
});
window.addEventListener("mouseup", ()=>{ if(favDrag){ favDrag=null; el("favbar").classList.remove("dragging"); } });
renderFavBar();

// ---- MENIU CLICK DREAPTA (ca TradingView) â€” Ã®nlocuieÈ™te meniul default al browser-ului pe chart ----
const ctxMenu=el("ctxMenu");
function showCtxMenu(x,y){ ctxMenu.style.display="block";
  ctxMenu.style.left=Math.min(x, window.innerWidth-ctxMenu.offsetWidth-8)+"px";
  ctxMenu.style.top=Math.min(y, window.innerHeight-ctxMenu.offsetHeight-8)+"px";
  // starea lockRR vizibila in meniu (âœ“ / âœ—)
  const lr=el("ctxLockRR");
  lr.classList.toggle("on", lockRR);
  lr.textContent = lockRR ? "ðŸ”’ R:R fix â€” ON âœ“" : "ðŸ”’ R:R fix â€” OFF";
  // starea IZOLARE vizibila in meniu (âœ“ / âœ—)
  const iso=el("ctxIsolate");
  iso.classList.toggle("on", isolateSel);
  iso.textContent = isolateSel ? "ðŸ” IzoleazÄƒ la selectare â€” ON âœ“" : "ðŸ” IzoleazÄƒ la selectare â€” OFF";
  // starea SL Anchor vizibila in meniu (âœ“ / âœ—)
  const slA=el("ctxSlAnchor");
  slA.classList.toggle("on", slAnchorMode);
  slA.textContent = slAnchorMode ? "ðŸ“Œ SL Anchor â€” ON âœ“" : "ðŸ“Œ SL Anchor â€” OFF";
  // v7.50: setari pozitie â€” vizibile doar cand e selectata o pozitie (expiry on/off + candele + entry)
  const posSet=el("ctxPosSet");
  const t=selMk || (selSet.length && selSet.find(it=>it.kind==="m") ? selSet.find(it=>it.kind==="m").ref : null);
  if(t && t.dir && !t.pts){
    posSet.style.display="flex";
    el("ctxExpOn").checked = t.exp!==0;
    el("ctxExpN").value = (t.exp>0?t.exp:(lastExp||10));
  } else posSet.style.display="none"; }
function hideCtxMenu(){ ctxMenu.style.display="none"; }
cv.addEventListener("contextmenu", ev=>{ ev.preventDefault();
  // click dreapta pe o poziÈ›ie = o selecteazÄƒ automat (ca TradingView) â€” preset-ul R:R se aplicÄƒ pe ea
  const r=cv.getBoundingClientRect(); const cx=ev.clientX-r.left, cy=ev.clientY-r.top;
  const mp=markerPartAt(cx, cy);
  if(mp){ selMk=mp.m; sel=null; selSet=[{kind:"m", ref:mp.m}]; syncListSel(); requestRender(); }
  showCtxMenu(ev.clientX, ev.clientY); });
document.addEventListener("click", ev=>{ if(!ctxMenu.contains(ev.target)) hideCtxMenu(); });
document.addEventListener("keydown", ev=>{ if(ev.key==="Escape") hideCtxMenu(); });
ctxMenu.querySelectorAll(".ci").forEach(ci=>ci.onclick=ev=>{
  ev.stopPropagation(); hideCtxMenu();
  const cmd=ci.dataset.cmd;
  if(cmd==="pointer") setTool(TOOLS.POINTER);
  else if(cmd==="long") setTool(TOOLS.LONG);
  else if(cmd==="short") setTool(TOOLS.SHORT);
  else if(cmd==="line") setTool(TOOLS.LINE);
  else if(cmd==="rect") setTool(TOOLS.RECT);
  else if(cmd==="hline") setTool(TOOLS.HLINE);
  else if(cmd==="arrow") setTool(TOOLS.ARROW);
  else if(cmd==="lockrr"){ el("lockRRBtn").onclick(); showCtxMenu(ev.clientX||100, ev.clientY||100); }   // refresh starea in meniu (ramane deschis)
  else if(cmd==="isolate"){ isolateSel=!isolateSel;
    try{ localStorage.setItem("gbpusd_full_settings", JSON.stringify({lockRR, magnet:magnetMode, isolate:isolateSel, sidebarCollapsed, slAnchor:slAnchorMode})); }catch(e){}
    showCtxMenu(ev.clientX||100, ev.clientY||100);
    toast(isolateSel ? "ðŸ” Izolare ON â€” la selectare se vede doar poziÈ›ia respectivÄƒ" : "ðŸ” Izolare OFF â€” se vÄƒd toate poziÈ›iile");
    requestRender(); }
  else if(cmd==="slanchor"){ slAnchorMode=!slAnchorMode;
    try{ localStorage.setItem("gbpusd_full_settings", JSON.stringify({lockRR, magnet:magnetMode, isolate:isolateSel, sidebarCollapsed, slAnchor:slAnchorMode})); }catch(e){}
    showCtxMenu(ev.clientX||100, ev.clientY||100);
    toast(slAnchorMode ? "ðŸ“Œ SL Anchor ON â€” trage SL-ul pe o lumÃ¢nare cu Ctrl ca sÄƒ ancorezi referinÈ›a" : "ðŸ“Œ SL Anchor OFF");
    requestRender(); }
  else if(cmd==="bt") el("btBtn").onclick();
  else if(cmd==="export") el("exp").onclick();
});
// v7.50: setari pozitie din click-dreapta â€” expiry on/off + nr candele + entry aici/urmatoarea
function ctxSelectedPos(){ return selMk || (selSet.length && selSet.find(it=>it.kind==="m") ? selSet.find(it=>it.kind==="m").ref : null); }
el("ctxExpOn").onchange=()=>{ const t=ctxSelectedPos(); if(!t) return;
  t.exp = el("ctxExpOn").checked ? (parseInt(el("ctxExpN").value,10)||10) : 0;
  save(); requestRender(); toast("Expiry "+(t.exp>0?("ON â€” "+t.exp+" candele"):"OFF")); };
el("ctxExpN").onchange=()=>{ const t=ctxSelectedPos(); if(!t) return;
  const n=parseInt(el("ctxExpN").value,10)||0;
  t.exp = el("ctxExpOn").checked ? n : 0; if(t.exp>0){ lastExp=t.exp; }
  save(); requestRender(); toast("Expiry: "+n+" candele"); };
el("ctxEntryNow").onclick=()=>{ const t=ctxSelectedPos(); if(!t) return;
  t.entryMode="now"; save(); requestRender(); toast("Entry pe bara semnalului (imediat)"); };
el("ctxEntryNext").onclick=()=>{ const t=ctxSelectedPos(); if(!t) return;
  t.entryMode="next"; save(); requestRender(); toast("Entry la candela urmÄƒtoare"); };
// preset R:R: aplica raportul pe pozitia selectata (TP = SL Ã— rr, pastrand directia)
ctxMenu.querySelectorAll(".rrpreset").forEach(btn=>btn.onclick=ev=>{
  ev.stopPropagation();
  const rr=parseFloat(btn.dataset.rr);
  const t=selMk || (selSet.length && selSet.find(it=>it.kind==="m") ? selSet.find(it=>it.kind==="m").ref : null);
  if(!t || t.sl==null || t.sl<=0){ toast("SelecteazÄƒ Ã®ntÃ¢i o poziÈ›ie cu SL"); return; }
  t.tp=Math.round(t.sl*rr*10)/10;
  save(); requestRender(); hideCtxMenu();
  toast("PoziÈ›ie #"+(t.id??"")+" â†’ R:R "+rr+" (TP "+t.tp+"p)");
});

// ---- interactiune ----
cv.addEventListener("mousemove", ev=>{
  const r=cv.getBoundingClientRect(); const x=ev.clientX-r.left, y=ev.clientY-r.top;
  lastPx=x;
  if(!drag && !yRangeCache) yRangeCache=yrange();   // hover smooth: scala O DATA, doar cand NU tragi (la drag se recalculeaza pe view-ul curent)
  const bar=barAtX(x);
  let price=priceAtY(y);
  // ðŸ§² MAGNET: lipeÈ™te preÈ›ul de OHLC/wick/SL/TP/desene â€” Ctrl È›inut (inclusiv Ã®n drag) = hard temporar
  ctrlPressedMagnet=!!ev.ctrlKey;
  if(magnetMode!=="off" || ctrlPressedMagnet) price=snapPrice(bar, price, y);
  if(drag){
    if(drag.mode==="measure"){ measure.b1=bar; measure.p1=price; requestRender(); return; }
    let ddx=ev.clientX-drag.downX, ddy=ev.clientY-drag.downY;
    const dm=Math.hypot(ddx,ddy);
    if(!drag.moved && dm>6){
      drag.moved=true;
      // FIX TELEPORT: pan-ul re-baselineaza la pozitia ACTUALA a mouse-ului cand porneste (nu de la click)
      // â€” fara asta, primii 6px se aplicau dintr-o data = chart-ul sarea sub mouse la inceputul drag-ului
      if(drag.mode==="pan"){
        const prevX = drag.downX, prevY = drag.downY;
        drag.downX=ev.clientX; drag.downY=ev.clientY; drag.start0=view.start; drag.yOff0=yOff;
        // FIX PAN MORT: dupa re-baseline, miÈ™carea din ACEST eveniment trebuie aplicata (nu zero).
        // Altfel primul mousemove real dupa pragul de 6px nu misca nimic => chart-ul pare blocat.
        ddx = ev.clientX - prevX; ddy = ev.clientY - prevY;
      } else { ddx = ev.clientX - drag.downX; ddy = ev.clientY - drag.downY; }
    }
    if(drag.mode==="posdraft" && posDraft){
      // muti box-ul liber pe chart (slide across) â€” bar + price urmeaza cursorul
      const mx=blind?cutoff:DATA.length-1;
      posDraft.bar=Math.max(0, Math.min(mx, bar)); posDraft.price=price;
      requestRender(); return; }
    if(drag.mode==="pospart" && posDraft){
      const up=posDraft.dir==="LONG";
      if(drag.mp.part==="entry"){ posDraft.price=price; requestRender(); return; }
      const pips=Math.abs(posDraft.price-price)/PIP;
      if(pips>=0.5 && pips<=100){
        const okDir=(drag.mp.part==="sl") ? (up?price<posDraft.price:price>posDraft.price) : (up?price>posDraft.price:price<posDraft.price);
        if(okDir){ const v=Math.round(pips*10)/10;
          if(drag.mp.part==="sl"){
            const rr=(posDraft.sl>0 && posDraft.tp!=null) ? posDraft.tp/posDraft.sl : null;
            posDraft.sl=v;
            if(lockRR && rr!=null) posDraft.tp=Math.round(v*rr*10)/10;
          } else {
            const rr=(posDraft.tp>0 && posDraft.sl!=null) ? posDraft.tp/posDraft.sl : null;
            posDraft.tp=v;
            if(lockRR && rr!=null && posDraft.sl>0) posDraft.sl=Math.round(v/rr*10)/10;
          }
        }
      }
      requestRender(); return; }
    if(drag.mode==="mkpart"){
      const m=drag.mp.m, up=m.dir==="LONG";
      const inMulti = selSet.length>1 && selSet.some(it=>it.ref===m);   // marker parte din multi-select
      if(drag.mp.part==="entry"){ m.price=price; requestRender(); return; }
      if(drag.mp.part==="body"){
        // muta TOT box-ul pe chart (bar + price), SL/TP/fc raman la fel
        const mx=blind?cutoff:DATA.length-1;
        if(inMulti){  // muta TOATE pozitiile din selSet impreuna
          const dBar=bar-m.bar, dPrice=price-m.price;
          for(const it of selSet){
            if(it.kind==="m"){ it.ref.bar=Math.max(0,Math.min(mx,it.ref.bar+dBar)); it.ref.price+=dPrice; it.ref.ts=DATA[it.ref.bar]?DATA[it.ref.bar][0]:it.ref.ts; }   // v7.54: ancora urmeazÄƒ bara nouÄƒ
            else it.ref.pts.forEach(p=>{ p.bar=Math.max(0,Math.min(mx,p.bar+dBar)); p.price+=dPrice; });
          }
        } else {
          m.bar=Math.max(0, Math.min(mx, bar)); m.price=price; m.ts=DATA[m.bar]?DATA[m.bar][0]:m.ts;   // v7.54: ancora urmeazÄƒ bara nouÄƒ
        }
        requestRender(); return; }
      if(!inMulti){  // SL/TP se trage doar individual
      const pips=Math.abs(m.price-price)/PIP;
      if(pips>=0.5 && pips<=100){
        const okDir=(drag.mp.part==="sl") ? (up?price<m.price:price>m.price) : (up?price>m.price:price<m.price);
        if(okDir){ const v=Math.round(pips*10)/10;
          if(drag.mp.part==="sl"){
            const rr=(m.sl>0 && m.tp!=null) ? m.tp/m.sl : null;   // raportul curent inainte de modificare
            m.sl=v;
            if(lockRR && rr!=null) m.tp=Math.round(v*rr*10)/10;   // ðŸ”’ muta si TP-ul proporÈ›ional
          } else {
            const rr=(m.tp>0 && m.sl!=null) ? m.tp/m.sl : null;
            m.tp=v;
            if(lockRR && rr!=null && m.sl>0) m.sl=Math.round(v/rr*10)/10;   // ðŸ”’ muta si SL-ul proporÈ›ional
          }
        }
      }
      }
      requestRender(); return; }
    if(drag.mode==="selbox"){          // marquee box de selectie multipla
      drag.x1=x; drag.y1=y; drag.moved=true; requestRender(); return; }
    if(drag.mode==="arrowclick"){ if(dm>6) drag.mode="move"; }
    if(drag.mode==="ptmove" && drag.d){
      // drag pe CAPÄ‚TUL liniei/rect-ului: muta DOAR acel punct (unghi/lungime, ca TradingView)
      const d=drag.d, pi=drag.pi, mx=blind?cutoff:DATA.length-1;
      let pBar=bar, pPrice=price;
      if(ev.shiftKey){   // SHIFT = constrangere 45Â° fata de celalalt capat (ca desenare)
        const other=d.pts[pi===0?1:0];
        const c=constrain45(x, y, xAtBar(other.bar), yAtPrice(other.price));
        pBar=barAtX(c[0]); pPrice=priceAtY(c[1]);
      }
      d.pts[pi].bar=Math.max(0,Math.min(mx,pBar));
      d.pts[pi].price=pPrice;
      requestRender(); return; }
    if(drag.mode==="move" && sel){
      // SHIFT = constrÃ¢ngere la mutare pe o singurÄƒ axÄƒ (ca TradingView): orizontal SAU vertical (dominantÄƒ)
      let dBar=bar-drag.bar, dPrice=price-drag.price;
      if(ev.shiftKey){
        const dxPx=(xAtBar(bar)-xAtBar(drag.bar)), dyPx=(yAtPrice(price)-yAtPrice(drag.price));
        if(Math.abs(dyPx)>Math.abs(dxPx)) dBar=0; else dPrice=0;
      }
      const mx=blind?cutoff:DATA.length-1;
      // daca desenul e in multi-select â†’ muta TOATE elementele din selSet impreuna
      if(selSet.length>1 && selSet.includes(sel)){
        for(const it of selSet){
          if(it.kind==="d"){ it.ref.pts.forEach(p=>{ p.bar=Math.max(0,Math.min(mx,p.bar+dBar)); p.price+=dPrice; }); }
          else { it.ref.bar=Math.max(0,Math.min(mx,it.ref.bar+dBar)); it.ref.price+=dPrice; it.ref.ts=DATA[it.ref.bar]?DATA[it.ref.bar][0]:it.ref.ts; }   // v7.54: ancora urmeazÄƒ bara nouÄƒ
        }
      } else {
        sel.pts.forEach(p=>{ p.bar=Math.max(0,Math.min(mx,p.bar+dBar)); p.price+=dPrice; });
      }
      drag.bar=bar; drag.price=price; requestRender(); return; }
    if(drag.mode==="cutoff"){
      if(Math.abs(x-drag.downX)>3) drag.moved=true;
      if(drag.moved){ cutoff=Math.max(0, Math.min(DATA.length-1, bar)); yLock=null; yRangeCache=null; requestRender(); }
      return;
    }
    if(drag.mode==="pan" && drag.moved){
      const perPx=view.count/(W-60);
      view.start=Math.max(0, Math.min(maxStart(), Math.round(drag.start0 - ddx*perPx)));
      // FIX WARP v3: shift vertical cu scala COMPLETA inghetata (include vzoom+pad) â€” imaginea ramane LIPITA de mouse
      yOff=drag.yOff0 + ddy*(drag.yr.hi-drag.yr.lo)/H;
      yRangeCache=null;   // view-ul s-a schimbat â€” scala veche e stale; se recalculeaza pe view-ul curent
      // OPTIMIZARE LAG: pan-ul = doar mutarea imaginii. Skip hover/magnet/hit-test (inutile in timpul
      // pan-ului) â€” fara asta, fiecare mousemove rula snapPrice+markerPartAt+hitDrawing (sute de apeluri
      // scumpe cu yRangeCache null) => lag la miscarea chart-ului, mai ales cu mouse de polling mare.
      requestRender(); return;
    }
  }
  if(draft && drag && drag.mode==="pen"){
    const last=draft.pts[draft.pts.length-1];
    const lx=xAtBar(last.bar), ly=yAtPrice(last.price);
    if(Math.hypot(x-lx, y-ly)>=2.5){           // sub-sampling: un punct la ~2.5px (freehand curat, fara mii de puncte)
      draft.pts.push({bar, price}); drag.moved=true;
    }
    requestRender(); return; }
  if(draft && (tool===TOOLS.LINE||tool===TOOLS.RECT)){
    // SHIFT = constrÃ¢ngere la 45Â° (ca TradingView): Linie â†’ unghiuri 0/45/90Â°; Rect â†’ pÄƒtrat
    if(ev.shiftKey && draft.pts[0]){
      const p0=draft.pts[0];
      const ax=xAtBar(p0.bar), ay=yAtPrice(p0.price);
      const c=constrain45(x, y, ax, ay);
      draft.pts[1]={ bar:barAtX(c[0]), price:priceAtY(c[1]) }; draft.sx2=c[0]; draft.sy2=c[1];
    } else { draft.pts[1]={bar, price}; draft.sx2=x; draft.sy2=y; }   // actualizeaza CONTINUU in timp ce tii apasat
  }
  xhair={ bar, price };
  // hover: doar CURSORUL se schimba (fara handles galbene) â€” grab pe body/mijloc, ns-resize pe SL/TP/entry
  const hp=markerPartAt(x,y);
  const hpart=hp?hp.part:null;
  if(hp){ hoverMk=hp.m;
    cv.style.cursor = (hpart==="sl"||hpart==="tp"||hpart==="entry") ? "ns-resize" : "grab"; }
  else {
    const hd=hitDrawing(x,y,8);
    if(hd){ cv.style.cursor="grab"; }              // liniile desenate: grab (muta)
    else { if(hoverMk) hoverMk=null; cv.style.cursor="crosshair"; }
  }
  requestRender();
});
cv.addEventListener("mouseleave", ()=>{ xhair=null; hoverMk=null; cv.style.cursor="crosshair"; requestRender(); });
cv.addEventListener("mousedown", ev=>{
  if(ev.button!==0) return;
  const r=cv.getBoundingClientRect(); const x=ev.clientX-r.left, y=ev.clientY-r.top;
  // v7.42: Ctrl+click pe desen/trade in timp ce scrii intr-un comentariu -> insereaza #tag in campul activ, fara sa inchida dialogul
  if(ev.ctrlKey && dlgOpen){
    const ta=document.activeElement;
    const tagH=(ta && (ta.tagName==="TEXTAREA"||ta.tagName==="INPUT")) ? (hitTagAt(x,y)) : null;
    if(tagH){ insertAtCursor(ta, tagH); dlgCtrlInsert=true; ev.preventDefault(); requestRender(); return; }
    return;
  }
  if(dlgOpen) return;
  const bar=barAtX(x);
  let price=priceAtY(y);
  // ðŸ§² MAGNET la plasare: primul click (LONG/SHORT/line/rect/hline/arrow) prinde direct wick-ul/OHLC/SL/TP
  ctrlPressedMagnet=!!ev.ctrlKey;
  if(magnetMode!=="off" || ctrlPressedMagnet) price=snapPrice(bar, price, y);
  // v7.44: DRAG pe linia de lookahead (cutoff) â€” o muti pe orice candela; viitorul dispare dupa ea
  if(blind && tool===TOOLS.POINTER && Math.abs(x - (xAtBar(cutoff)+bw()/2)) < 10){
    drag={ mode:"cutoff", downX:x, downY:y, bar, moved:false }; requestRender(); return;
  }
  // v7.45: Shift+click pe GOL = pune linia de lookahead direct la bara sub cursor (nu doar drag pe linie)
  // v7.49: Shift+click NU mai pune bara de lookahead (Shift e pt toolurile de masurare/constrangere) â€” foloseste butonul ðŸ“ Bara sau drag pe linie
  // v7.47: click pe gol DOAR in mod plasare lookahead (butonul Lookahead) â€” pune linia O DATA, apoi click-ul revine la normal
  if(blind && lookaheadPlacing && tool===TOOLS.POINTER && !ev.ctrlKey && x>=60 && x<=W-52
     && !markerPartAt(x,y) && !hitDrawing(x,y,8)){
    cutoff=Math.max(0, Math.min(DATA.length-1, bar)); lookaheadPlacing=false; yLock=null; yRangeCache=null; requestRender();
    toast("Lookahead setat la candela "+(bar+1)+" â€” click-ul a revenit la normal"); return;
  }
  if(ev.shiftKey && tool===TOOLS.POINTER){   // Shift+drag = masura (ca TradingView) â€” DOAR cu unealta Select; cu unealta de desen, Shift = constrangere 45Â°
    drag={ mode:"measure", downX:x, downY:y, bar, price, moved:false };
    measure={ b0:bar, p0:price, b1:bar, p1:price };
    requestRender(); return; }
  // NOTÄ‚: Ctrl+drag (selbox multi-select) e verificat MAI JOS, DUPÄ‚ hit-test-ul de obiecte â€”
  // ca Ã®n TradingView, Ctrl+click pe un marker/desen = DRAG CU MAGNET (precizie), nu selbox.
  // Ctrl+drag pe GOL = selbox (rÄƒmÃ¢ne).
  if(tool!==TOOLS.POINTER){
    if(x<60 || x>W-52) return;                    // marginea axei
    const mx=blind?cutoff:DATA.length-1;
    const bb=Math.max(0, Math.min(mx, bar));                   // desenele nu depasesc limita de revelare
    if(tool===TOOLS.LONG || tool===TOOLS.SHORT){
      // UN singur click plaseaza box-ul si revine la Select â€” click-ul stanga ramane liber dupa
      const dir=tool===TOOLS.LONG?"LONG":"SHORT";
      posDraft={ id:0, bar:bb, price, dir, note:"", sl:lastSl, tp:lastTp, fc:lastFc, exp:lastExp, ghost:false, _placed:true,
        tf:TF, ts:(DATA[bb]?DATA[bb][0]:undefined) },   // v7.54: TF de plasare + ancora de timp
      setTool(TOOLS.POINTER);   // click-ul e liber de acum â€” doar tragi box-ul / click pe el = dialog
      toast(dir+" plasat â€” trage box-ul unde vrei; click pe box = salvezi cu comentariu; Esc = anulezi");
      requestRender(); return;
    }
    if(tool===TOOLS.HLINE){
      drawings.push({ id:++drwSeq, type:"hline", pts:[{bar:bb, price}], tag:nextDrawTag("hline") });
      save(); requestRender(); toast("H-Linie salvatÄƒ â€” revenit la Select"); setTool(TOOLS.POINTER); return; }
    if(tool===TOOLS.ARROW){
      const d={ id:++drwSeq, type:"arrow", pts:[{bar:bb, price}], text:"" };
      // arrow-ul NU e inca in drawings â€” se adauga DOAR la Save; Cancel/close = dispare fara urma
      openArrowDlg(d, true); setTool(TOOLS.POINTER); return; }
    if(tool===TOOLS.PEN){
      draft={ type:"pen", pts:[{bar:bb, price}], t0:Date.now(), sx:x, sy:y };
      drag={ mode:"pen", downX:x, downY:y, moved:false };   // freehand: tii apasat si desenezi, mouseup = finalizeaza
      requestRender(); return; }
    // LINE / RECT: CLICK-CLICK (ca TradingView) â€” click 1 pune primul punct, muti mouse-ul (preview), click 2 finalizeaza
    if(draft && (tool===TOOLS.LINE||tool===TOOLS.RECT)){
      if(Date.now()-draft.t0<250 && Math.hypot(x-draft.sx, y-draft.sy)<8) return;  // bounce (mouse/touchpad)
      // click 2: finalizeaza â€” pune linia/zona unde e preview-ul (SHIFT = constrangere 45Â° ca la preview)
      let p1={bar:bb, price};
      if(ev.shiftKey && draft.pts[0]){
        const p0=draft.pts[0];
        const c=constrain45(x, y, xAtBar(p0.bar), yAtPrice(p0.price));
        p1={ bar:barAtX(c[0]), price:priceAtY(c[1]) };
      }
      const p0=draft.pts[0], ok=Math.abs(p1.bar-p0.bar)>0 || Math.abs(p1.price-p0.price)>1e-5;
      if(ok){ const nd2={ id:++drwSeq, type:draft.type, pts:[p0,p1] }; nd2.tag=nextDrawTag(draft.type); drawings.push(nd2);
        toast("Desen salvat â€” revenit la Select"); }
      else { toast("Prea mic â€” click pe alt punct pentru Linie/ZonÄƒ"); }
      draft=null; setTool(TOOLS.POINTER); save(); requestRender();
      return; }
    draft={ type:tool, pts:[{bar:bb, price}], t0:Date.now(), sx:x, sy:y, sx2:x, sy2:y };
    toast("Click 1 pus â€” mutÄƒ mouse-ul, click din nou ca sÄƒ pui linia (Esc = anulezi)");
    requestRender();
    return; }
  // pointer: marker (click=edit, drag pe SL/TP/intrare = modifici)
  if(posDraft){   // draft-ul e prioritar: tragi direct pe el (linii SL/TP + interior)
    const up=posDraft.dir==="LONG";
    const ex=xAtBar(posDraft.bar);
    const fcEnd=Math.min(DATA.length-1, posDraft.bar+((posDraft.fc>0)?posDraft.fc:60));
    const xEnd=Math.max(ex, xAtBar(fcEnd));
    if(x>=ex-12 && x<=xEnd+12){
      const sy=posDraft.sl!=null?yAtPrice(posDraft.price-(up?1:-1)*posDraft.sl*PIP):null;
      const ty=posDraft.tp!=null?yAtPrice(posDraft.price+(up?1:-1)*posDraft.tp*PIP):null;
      // SL/TP prin LINIILE lor (drag direct pe linie = slider de lungire), fara cerculete/handles
      if(sy!=null && Math.abs(y-sy)<7){ drag={mode:"pospart", mp:{part:"sl"}, downX:x, downY:y, moved:false}; return; }
      if(ty!=null && Math.abs(y-ty)<7){ drag={mode:"pospart", mp:{part:"tp"}, downX:x, downY:y, moved:false}; return; }
      // entry â€” DOAR pe sageata insasi (cerc mic in jurul varfului), nu pe toata lungimea benzii
      if(Math.hypot(x-ex, y-yAtPrice(posDraft.price))<16){ drag={mode:"posdraft", mp:{part:"entry"}, downX:x, downY:y, moved:false}; return; }
      // body: interiorul benzii INTRE linii â†’ muta tot (pe tot box-ul vizual)
      if(sy!=null||ty!=null){
        const y1=Math.min(sy??yAtPrice(posDraft.price), ty??yAtPrice(posDraft.price))+7;
        const y2=Math.max(sy??yAtPrice(posDraft.price), ty??yAtPrice(posDraft.price))-7;
        if(y>=y1 && y<=y2){ drag={mode:"posdraft", mp:{part:"body"}, downX:x, downY:y, moved:false}; return; }
      }
    }
  }
  const mp=markerPartAt(x,y);
  if(mp){ 
    if(!(selSet.length>1 && selSet.some(it=>it.ref===mp.m))){ selSet=[{kind:"m", ref:mp.m}]; }
    sel=null;
    selMk=mp.m; drag={ mode:"mkpart", mp, downX:x, downY:y, moved:false,
    undo:{bar:mp.m.bar, price:mp.m.price, sl:mp.m.sl, tp:mp.m.tp, ts:mp.m.ts} };
    cv.style.cursor = (mp.part==="sl"||mp.part==="tp"||mp.part==="entry") ? "ns-resize" : "grabbing";
    syncListSel();   // evidenÈ›iazÄƒ + scroll la poziÈ›ie Ã®n lista din dreapta (nu o mai cauÈ›i dupÄƒ ID)
    requestRender(); return; }
  // select desen / pan
  const h=hitDrawing(x,y,10);
  if(h){
    if(!(selSet.length>1 && selSet.some(it=>it.ref===h))){ selSet=[{kind:"d", ref:h}]; }
    sel=h; save(); requestRender();
    cv.style.cursor="grabbing";
    // capÄƒt de linie/rect prins (_pt setat de hitDrawing) => drag DOAR pe acel punct (schimbi unghi/lungime, ca TV)
    if(typeof h._pt==="number"){
      const pt=h.pts[h._pt];
      drag={ downX:x, downY:y, bar, price, moved:false,
             mode:"ptmove", d:h, pi:h._pt, p0:{bar:pt.bar, price:pt.price} };
      return;
    }
    drag={ downX:x, downY:y, bar, price, moved:false,
           mode:(h.type==="arrow")?"arrowclick":"move" };
    return; }
  // Ctrl+drag pe GOL = box de selectie multipla (ca TradingView) â€” verificat DOPÄ‚ hit-test-ul,
  // ca Ctrl+click pe un marker/desen sÄƒ fie drag cu magnet, nu selbox
  if(ev.ctrlKey){
    drag={ mode:"selbox", x0:x, y0:y, x1:x, y1:y, downX:x, downY:y, moved:false };
    requestRender(); return; }
  drag={ downX:x, downY:y, start0:view.start, yOff0:yOff, moved:false, mode:"pan" };
  // FIX TELEPORTARE (zoom orizontal + click): yLock Ã®ngheaÈ›Äƒ scala la wheel â€” dacÄƒ Ã®l resetam ÃŽNAINTE
  // de drag.yr, scala sÄƒrea de la cea desenatÄƒ (yLock) la baseRange recalculat => imaginea "teleportatÄƒ".
  // Scala trebuie Ã®ngheÈ›atÄƒ pe ce e DESENAT ACUM, apoi yLock poate fi resetat.
  // v7.33: drag.yr = scala ABSOLUTA DESENATA (yrange aplica yLock+vzoom+yOff) â€” un singur apel, fara
  // ramura if(yLock) separatÄƒ care dubla yOff la pan dupÄƒ freeze (bug: pan vertical â†’ drag pricebar â†’ teleport).
  drag.yr=yrange();
  yLock=null;
  vzoomAnim=null; zoomAnim=null;   // FIX: opreÈ™te animaÈ›iile de zoom la mousedown â€” dacÄƒ vzoom-ul se schimba
  // Ã®n timpul pan-ului, drag.yr (Ã®ngheÈ›at) rÄƒmÃ¢nea Ã®n urmÄƒ => imaginea sÄƒrea la fiecare pas de animaÈ›ie
  if(selMk){ selMk=null; syncListSel(); requestRender(); }   // click pe gol = deselectezi pozitia (stergi si evidenÈ›ierea din listÄƒ)
});
cv.addEventListener("dblclick", ev=>{
  if(dlgOpen) return;
  const r=cv.getBoundingClientRect(); const x=ev.clientX-r.left, y=ev.clientY-r.top;
  // FIX: hit-test pe box-ul VIZUAL complet (markerPartAt prinde SL/TP/entry/body pe toatÄƒ lÄƒÈ›imea vizibilÄƒ),
  // nu doar pe bara exactÄƒ a marker-ului â€” altfel dblclick pe linia SL/TP sau pe corpul box-ului nu deschidea dialogul
  const mp=markerPartAt(x,y);
  if(mp) openDlg(mp.m.bar, mp.m.price, mp.m);
  else {
    // dblclick pe gol cu IZOLARE ON = dezizoleazÄƒ (revine tot) â€” ca sÄƒ poÈ›i edita alt trade/bot fÄƒrÄƒ sÄƒ cauÈ›i comutatorul
    if(isolateSel && selMk){ selMk=null; selSet=[]; syncListSel(); requestRender(); return; }
    const hd=hitDrawing(x,y,14); if(hd) openArrowDlg(hd);   // dublu-click pe ORICE desen = comentariu
  }
});
window.addEventListener("mouseup", ev=>{
  priceBarDrag=null;                       // opreste drag-ul pe price bar
  if(dlgDrag){ dlgDrag=null; return; }     // sfÃ¢rÈ™it drag dialog â€” nu Ã®nchide
  // LINE/RECT: finalizarea se face la CLICK 2 (in mousedown) â€” mouseup-ul nu mai deseneaza nimic
  if(dlgOpen){
    if(Date.now()-dlgOpenedAt<300) return;    // mouseup-ul care a deschis dialogul (Nota) â€” ignorat
    const t=ev.target;
    if(t && el("dlg").contains(t)) return;   // click in dialog â€” butoanele merg
    if(dlgCtrlInsert){ dlgCtrlInsert=false; return; }   // v7.42c: era Ctrl+click pt tag â€” NU inchide dialogul
    closeDlg(true); return;                    // v7.43: click in afara â€” AUTO-SAVE nota daca s-a modificat (nu o pierzi)
  }
  if(!drag) return;
  if(drag.mode==="measure"){ measure=null; drag=null; return; }
  if(drag.mode==="posdraft" && posDraft){
    const ddx=ev.clientX - (cv.getBoundingClientRect().left + drag.downX);
    const ddy=ev.clientY - (cv.getBoundingClientRect().top + drag.downY);
    const wasMoved=drag.moved;
    drag=null;
    if(!wasMoved && Math.hypot(ddx,ddy)<=6){
      // click simplu pe box-ul plasat = SALVEAZA DIRECT (fara dialog â€” click-ul stanga nu mai marcheaza)
      const mk=posDraft; posDraft=null;
      mk.id=++mkSeq; mk.created=Date.now(); mk.seen_through=blind?cutoff:null; mk.blind=blind;
      if(!mk.tag) mk.tag=nextTradeTag();
    markers.push(mk); save(); requestRender();
      toast(mk.dir+" salvat (SL "+mk.sl+"p / TP "+mk.tp+"p) â€” dublu-click sau âœŽ pt. comentariu");
    } else {
      requestRender();
    }
    return; }
  if(drag.mode==="pospart"){ drag=null; requestRender(); return; }
  if(drag.mode==="ptmove"){ drag=null; save(); requestRender(); return; }   // capÄƒt de linie/rect: salveazÄƒ poziÈ›ia nouÄƒ
  if(drag.mode==="mkpart"){
    // ðŸ“Œ SL ANCHOR: cÃ¢nd slAnchorMode e ON È™i s-a tras SL-ul, salveazÄƒ referinÈ›a la lumÃ¢nare Ã®n notÄƒ
    if(slAnchorMode && drag.mp.part==="sl" && drag.moved){
      const r=cv.getBoundingClientRect(); const x=ev.clientX-r.left;
      const bar=barAtX(x);
      const c=DATA[bar];
      if(c){
        const m=drag.mp.m, up=m.dir==="LONG";
        const slPrice=m.price-(up?1:-1)*m.sl*PIP;
        const levels={open:c[1], high:c[2], low:c[3], close:c[4]};
        let bestL="", bestD=Infinity;
        for(const [lb,pr] of Object.entries(levels)){ const d=Math.abs(pr-slPrice); if(d<bestD){ bestD=d; bestL=lb; } }
        const anchor=`ðŸ“Œ SL ancorat pe bara #${bar} (${bestL} ${fmtP(levels[bestL])})`;
        m.note=m.note ? m.note.replace(/ðŸ“Œ SL ancorat.*/,"")+" Â· "+anchor : anchor;
      }
    }
    drag=null; save(); return; }
  if(drag.mode==="arrowclick"){
    const ddx=ev.clientX - (cv.getBoundingClientRect().left + drag.downX);
    const ddy=ev.clientY - (cv.getBoundingClientRect().top + drag.downY);
    const wasMoved=drag.moved;
    drag=null;
    if(!wasMoved && Math.hypot(ddx,ddy)<=6 && sel && sel.type==="arrow") openArrowDlg(sel);
    return; }
  if(drag.mode==="selbox"){
    const x0=Math.min(drag.x0,drag.x1), x1=Math.max(drag.x0,drag.x1);
    const y0=Math.min(drag.y0,drag.y1), y1=Math.max(drag.y0,drag.y1);
    selSet=[]; sel=null; selMk=null;
    if(drag.moved){
      for(const d of drawings){
        if(d.type==="hline"){ if(yAtPrice(d.pts[0].price)>=y0 && yAtPrice(d.pts[0].price)<=y1){ selSet.push({kind:"d", ref:d}); continue; } }
        else if(d.pts.some(p=>{ const px=xAtBar(p.bar), py=yAtPrice(p.price); return px>=x0&&px<=x1&&py>=y0&&py<=y1; })){ selSet.push({kind:"d", ref:d}); }
      }
      for(const m of markers){
        const px=xAtBar(m.bar), py=yAtPrice(m.price);
        if(px>=x0&&px<=x1&&py>=y0&&py<=y1) selSet.push({kind:"m", ref:m});
      }
    }
    drag=null; save(); requestRender();
    return; }
  if(drag.mode==="pen"){
    if(draft && draft.type==="pen" && draft.pts.length>=2){
      drawings.push({ id:++drwSeq, type:"pen", pts:draft.pts.map(p=>({...p})), tag:nextDrawTag("pen") });
      toast("Pen salvat ("+draft.pts.length+" puncte) â€” revenit la Select");
    } else if(draft && draft.pts.length<2){ toast("Prea mic â€” deseneazÄƒ È›inÃ¢nd apÄƒsat"); }
    draft=null; setTool(TOOLS.POINTER); save(); requestRender();
    return; }
  if(drag.mode==="move"){ drag=null; return; }
  // click simplu pe fundal (fara drag) â†’ deselecteaza tot multi-selectul
  if(selSet.length>1 && !drag.moved){ selSet=[]; sel=null; selMk=null; save(); }
  drag=null;   // click stanga = doar select/pan â€” NU marcheaza pozitii (fara dialog)
});
cv.addEventListener("wheel", ev=>{
  ev.preventDefault();                 // suprimÄƒ zoom-ul de paginÄƒ al browser-ului, inclusiv Ctrl+wheel (ca TV)
  if(dlgOpen) return;                  // nu misca chart-ul sub dialog
  vzoomAnim=null; zoomAnim=null;       // FIX TELEPORTARE: opreÈ™te animaÈ›iile de zoom vertical la scroll pe chart â€”
  // altfel animaÈ›ia (rÄƒmasÄƒ de la scroll pe pricebar) continua pe view-ul NOU È™i scala sare sus/jos
  let dy=ev.deltaY, dx=ev.deltaX;
  if(ev.deltaMode===1){ dy*=16; dx*=16; } else if(ev.deltaMode===2){ dy*=100; dx*=100; }
  // Shift+wheel / tilt-wheel (deltaX) = pan ORIZONTAL (ca TradingView)
  if(ev.shiftKey || Math.abs(dx)>Math.abs(dy)){
    const perPx=view.count/(W-60);
    const panAmt = Math.abs(dx)>Math.abs(dy) ? -dx*0.35 : dy*1.2;   // tilt: px; shift+wheel: linii
    view.start=Math.max(0, Math.min(maxStart(), view.start + Math.round(panAmt*perPx)));
    yRangeCache=null; requestRender(); return;
  }
  // ZOOM CA TRADINGVIEW (v7.32): Ctrl+scroll = zoom la POINTER (bara sub cursor fixa) Â· scroll simplu = zoom la
  // right bar (ULTIMA candela vizibila din dreapta ramane fixa) â€” modelul lightweight-charts right_bar_stays_on_scroll.
  if(ev.ctrlKey){ lastPx = ev.clientX; wheelZoom(dy, true); }
  else wheelZoom(dy, false);
}, {passive:false});
window.addEventListener("keydown", ev=>{
  const tgt=ev.target;
  const inField = tgt && (tgt.tagName==="INPUT" || tgt.tagName==="TEXTAREA");
  // UNDO/REDO â€” prioritar, chiar si peste textarea (dar acolo lasa browser-ul sa faca undo de text)
  if(ev.ctrlKey && !ev.shiftKey && (ev.key==="z"||ev.key==="Z") && !inField){ ev.preventDefault(); undo(); return; }
  if(ev.ctrlKey && ev.shiftKey && (ev.key==="z"||ev.key==="Z")){ ev.preventDefault(); redo(); return; }
  if(ev.ctrlKey && (ev.key==="y"||ev.key==="Y")){ ev.preventDefault(); redo(); return; }
  // COPY / PASTE (Ctrl+C / Ctrl+V) â€” obiectele selectate de pe chart (marker-e + desene), ca TradingView
  if(ev.ctrlKey && !ev.shiftKey && (ev.key==="c"||ev.key==="C") && !inField){ ev.preventDefault(); copySelection(); return; }
  if(ev.ctrlKey && !ev.shiftKey && (ev.key==="v"||ev.key==="V") && !inField){ ev.preventDefault(); pasteClipboard(); return; }
  // SAVE (Ctrl+S) â€” persisteazÄƒ tot (marker-e, desene, indicatori, setÄƒri) ca "profil"
  if(ev.ctrlKey && !ev.shiftKey && (ev.key==="s"||ev.key==="S") && !inField){ ev.preventDefault(); save(); toast("ðŸ’¾ Salvat (Ctrl+S) â€” tot ce ai pe chart e persistat"); return; }
  // TASTE UNELTE (ca TradingView) â€” doar cand nu scrii intr-un camp si nu e dialog deschis
  if(!inField && !dlgOpen){
    const k=ev.key.toLowerCase();
    const toolMap={ v:"pointer", b:"long", s:"short", l:"line", p:"pen", r:"rect", h:"hline", n:"arrow" };
    if(toolMap[k]){ ev.preventDefault(); setTool(toolMap[k]); toast("UnealtÄƒ: "+toolMap[k]); return; }
    // timeframes: 1=M15, 2=H1, 3=H4, 4=D1
    const tfMap={ "1":"M15", "2":"H1", "3":"H4", "4":"D1" };
    if(tfMap[k]){ ev.preventDefault(); switchTF(tfMap[k]); return; }
    if(k==="m"){ ev.preventDefault(); toast("MÄƒsurÄƒ: È›ine Shift + drag pe chart"); return; }
    if(k==="a"){ ev.preventDefault(); resetView(); return; }
    if(k==="f"){ ev.preventDefault(); toast("Filtre: vezi panoul ðŸ‘» NW + PASS/SKIP"); return; }
  }
  if(ev.key==="Escape"){ if(posDraft){ posDraft=null; setTool(TOOLS.POINTER); requestRender(); return; }
    if(drag && drag.mode==="mkpart" && drag.undo){ const u=drag.undo, m=drag.mp.m;
      m.bar=u.bar; m.price=u.price; m.sl=u.sl; m.tp=u.tp; m.ts=u.ts; drag=null; save(); requestRender(); return; }
    if(drag && drag.mode==="measure"){ measure=null; drag=null; requestRender(); return; }
    if(draft){ draft=null; if(drag&&drag.mode==="pen") drag=null; requestRender(); return; } if(dlgOpen){ closeDlg(true); return; }   // v7.43: Escape/inchidere = auto-save nota
    if(selMk){ selMk=null; selSet=[]; syncListSel(); requestRender(); return; } if(sel){ sel=null; selSet=[]; save(); requestRender(); } }
  if(!inField){
    if(ev.key==="Enter" && posDraft){ openDlg(posDraft.bar, posDraft.price, posDraft); posDraft=null; setTool(TOOLS.POINTER); return; }
    if(ev.key==="Enter" && selMk){ openDlg(selMk.bar, selMk.price, selMk); return; }
    // Play: Space/Ctrl+Space = toggle; È›ine apÄƒsat = accelerare (repeat keydown)
    if(ev.code==="Space"){
      ev.preventDefault();
      if(ev.repeat){ playSpeed=Math.min(60, playSpeed+2); if(playing) reveal(2); }
      else { playSpeed=1; togglePlay(); }
      return; }
    if(ev.key==="+"||ev.key==="="){ ev.preventDefault(); startZoom(view.count, view.count*0.85); return; }
    if(ev.key==="-"||ev.key==="_"){ ev.preventDefault(); startZoom(view.count, view.count*1.18); return; }
    if(ev.key==="ArrowRight"){ ev.preventDefault();
      if(selMk){ const mx=blind?cutoff:DATA.length-1; selMk.bar=Math.min(mx, selMk.bar+(ev.shiftKey?5:1)); selMk.ts=DATA[selMk.bar]?DATA[selMk.bar][0]:selMk.ts; save(); requestRender(); return; }
      view.start=Math.max(0, Math.min(maxStart(), view.start+Math.round(view.count*0.15))); yRangeCache=null; requestRender(); return; }
    if(ev.key==="ArrowLeft"){ ev.preventDefault();
      if(selMk){ selMk.bar=Math.max(0, selMk.bar-(ev.shiftKey?5:1)); selMk.ts=DATA[selMk.bar]?DATA[selMk.bar][0]:selMk.ts; save(); requestRender(); return; }
      view.start=Math.max(0, Math.min(maxStart(), view.start-Math.round(view.count*0.15))); yRangeCache=null; requestRender(); return; }
    if(ev.key==="ArrowUp" && selMk){ ev.preventDefault(); selMk.price+=(ev.shiftKey?10:1)*PIP; save(); requestRender(); return; }
    if(ev.key==="ArrowDown" && selMk){ ev.preventDefault(); selMk.price-=(ev.shiftKey?10:1)*PIP; save(); requestRender(); return; }
  }
  if(ev.key==="Delete" && !dlgOpen && !inField){
    // Delete pe multi-select â†’ È™terge TOATE elementele selectate (desene + poziÈ›ii)
    if(selSet.length>1){
      for(const it of selSet){
        if(it.kind==="d"){ const i=drawings.indexOf(it.ref); if(i>=0) drawings.splice(i,1); }
        else { const i=markers.indexOf(it.ref); if(i>=0) markers.splice(i,1); }
      }
      toast(selSet.length+" elemente È™terse"); selSet=[]; sel=null; selMk=null; save(); requestRender(); return;
    }
    if(selMk){ const i=markers.indexOf(selMk); if(i>=0){ markers.splice(i,1); toast("Marker È™ters"); } selMk=null; selSet=[]; save(); requestRender(); return; }
    if(sel){ drawings.splice(drawings.indexOf(sel),1); sel=null; selSet=[]; save(); requestRender(); }
  }});
window.addEventListener("keyup", ev=>{ if(ev.code==="Space"){ playSpeed=1; playHold=false; } });

document.querySelectorAll("#toolbar [data-t], #toolrail [data-t]").forEach(b=>b.onclick=()=>setTool(b.dataset.t));

// ---- zoom smooth orizontal (rAF) â€” ancorat la MOUSE, ca TradingView ----
const ZOOM_MS=150;
function clampCount(c){ return Math.max(4, Math.min(DATA.length, Math.round(c))); }  // FIX P3: zoom-in pana la 4 bare (era 30) â€” ca TradingView/lightweight-charts; max zoom out = tot dataset-ul, zero void
function anchorFrac(){
  // ON = right bar (frac 1 â€” right_bar_stays_on_scroll, default TradingView)
  // OFF = cursor exact (libertate totala, ca TV/FXReplay)
  if(anchored) return 1;
  return (lastPx!=null && lastPx>=60 && lastPx<=W-52) ? Math.max(0,Math.min(1,(lastPx-60)/(W-60))) : 0.5;
}
function startZoom(fromCount, toCount){
  yLock=null; yRangeCache=null;   // FIX P2: zoom-ul ORIZONTAL reseteaza scala verticala inghetata (altfel yrange() deseneaza pe yLock stale -> salt la primul pan)
  const frac=anchorFrac();
  const anchorF=view.start + frac*view.count;                              // float anchor (cursor sau right bar)
  zoomAnim={ from:fromCount, to:clampCount(toCount), anchorF, frac,
             lastCount:fromCount, t0:performance.now() };
  stepZoom();
}
function stepZoom(){
  const a=zoomAnim; if(!a) return;
  const t=Math.min(1,(performance.now()-a.t0)/ZOOM_MS);
  const e=1-Math.pow(1-t,3);               // ease-out cubic
  let c=clampCount(a.from+(a.to-a.from)*e);
  if(a.frac===1) c=Math.min(c, Math.max(30, Math.floor(a.anchorF)));   // right-bar-stays: nu zooma out peste barele din stanga right edge-ului fixat (fara off-by-one)
  if(c!==a.lastCount){                     // skip frame fara schimbare (fara flicker la plateaus)
    const target=a.anchorF - a.frac*c;     // start-ul care tine cursorul fix
    const ms=Math.max(0, DATA.length-c);   // FIX: maxStart cu count-ul NOU (nu cel vechi) â€” fara derapaj la zoom
    view.start=Math.max(0, Math.min(ms, Math.round(target)));
    view.count=c; a.lastCount=c;
    yRangeCache=null;                        // FIX: view-ul s-a schimbat â€” scala veche e stale
  }
  requestRender();
  if(t<1) requestAnimationFrame(stepZoom); else zoomAnim=null;
}
// zoom INSTANT la wheel (ca TV): factor proportional cu delta, ancorat la cursor, rAF-coalesced â€” fara coada elastica
function wheelZoom(dy, atCursor){
  yLock=null; yRangeCache=null;   // FIX P2: zoom instant la wheel â€” reseteaza si el yLock (startZoom nu e apelat aici)
  // PATTERN LIGHTWEIGHT-CHARTS (TradingView): k=1.1/0.9 per notch, CAPAT la 1 notch/event
  // (un scroll agresiv nu sari), anchor capturat o singura data INAINTE de schimbarea scalei.
  const steps = Math.min(1, Math.abs(dy)/120);   // cap 1 notch per event (nu hiper-sensibil)
  const k = dy<0 ? 1/(1+0.10*steps) : (1+0.10*steps);   // 10% per notch = 1.1/0.9 (ca LWC)
  const frac = atCursor ? Math.max(0,Math.min(1,(lastPx!=null&&lastPx>=60&&lastPx<=W-52)?(lastPx-60)/(W-60):0.5)) : 1;
  const anchorF = view.start + frac*view.count;
  let c = clampCount(view.count * k);
  if(frac===1) c=Math.min(c, Math.max(30, Math.floor(anchorF)));   // right-bar-stays limit
  const ms=Math.max(0, DATA.length-c);
  view.start=Math.max(0, Math.min(ms, Math.round(anchorF - frac*c)));
  view.count=c;
  yRangeCache=null;
  requestRender();
}// ---- price bar (dreapta, full-height) = zoom VERTICAL: scroll sau click+slide, ancorat la cursor ----
function applyVzoom(nv, anchorPrice){
  // FIX TELEPORTARE (research deep): yrange() deseneazÄƒ cu b=yLock (scala Ã®ngheÈ›atÄƒ de zoom-ul orizontal),
  // dar aici foloseam baseRange() â€” fracÈ›ia de ancorare era calculatÄƒ pe o BAZÄ‚ DIFERITÄ‚ de cea afiÈ™atÄƒ
  // => la primul zoom vertical dupÄƒ un zoom orizontal, punctul de sub cursor sÄƒrea (cel mai vizibil la zoom out).
  // Trebuie exact aceeaÈ™i bazÄƒ ca yrange(): yLock ?? baseRange().
  const b = yLock ? {lo:yLock.lo, hi:yLock.hi} : baseRange(); const mid=(b.lo+b.hi)/2;
  const r0=(b.hi-b.lo)/vzoom, lo0=mid-r0/2+yOff;
  const frac=anchorPrice!=null ? Math.max(0,Math.min(1,(anchorPrice-lo0)/r0)) : 0.5;
  vzoom=Math.max(0.4, Math.min(2.5, nv));
  const r1=(b.hi-b.lo)/vzoom, lo1=anchorPrice!=null ? (anchorPrice-frac*r1) : (mid-r1/2);
  yOff=lo1-(mid-r1/2);                     // pastreaza punctul de sub cursor pe loc
  yRangeCache=null;                         // FIX: scala s-a schimbat â€” cache-ul vechi e stale (altfel candelele sar)
}
function startVzoom(to, anchorPrice){   // FIX: NU mai È™tergem yLock aici â€” zoom-ul vertical lucreazÄƒ corect pe scala
  // Ã®ngheÈ›atÄƒ (yLock) exact ca TV (manual price scale persistÄƒ); È™tergerea anticipatÄƒ cauza teleportare.
  vzoomAnim={ from:vzoom, to:Math.max(0.4, Math.min(2.5, to)), anchor:anchorPrice!=null?anchorPrice:null, t0:performance.now() };
  stepVzoom();
}
function stepVzoom(){
  const a=vzoomAnim; if(!a) return;
  const t=Math.min(1,(performance.now()-a.t0)/ZOOM_MS);
  const e=1-Math.pow(1-t,3);
  applyVzoom(a.from+(a.to-a.from)*e, a.anchor);
  requestRender();
  if(t<1) requestAnimationFrame(stepVzoom); else vzoomAnim=null;
}
const pbar=el("pricebar");
function pbarFreezeScale(){   // FIX TELEPORTARE: orice gest pe pricebar = scala devine MANUALÄ‚ (ca TV dupÄƒ price-scale
  // gesture) â€” yLock Ã®ngheÈ›at pe scala curentÄƒ, ca zoom-ul ORIZONTAL ulterior sÄƒ NU o recalculeze (baseRange
  // pe bare noi) => fÄƒrÄƒ teleportare verticalÄƒ cÃ¢nd scroll-ezi pe chart dupÄƒ ce ai scroll-at pe barÄƒ.
  // ROOT CAUSE v7.33 (bug raportat: pan vertical â†’ drag pricebar â†’ teleport sus de tot):
  // yLock trebuie sÄƒ fie un SNAPSHOT PUR din baseRange() â€” NICIODATÄ‚ scala absolutÄƒ (vzoom+yOff incluse).
  // De ce: yrange() (linia 605) re-aplicÄƒ vzoom+yOff PESTE yLock. DacÄƒ yLock conÈ›ine deja vzoom+yOff,
  // scala desenatÄƒ se comprimÄƒ/deplaseazÄƒ dublu = teleportare (confirmat matematic: span 0.02585â†’0.01775
  // cu yLock vechi; identic cu fix-ul nou). Modelul lightweight-charts: priceRange = snapshot din sources,
  // scaleOffset (vzoom/yOff) separat.
  if(yLock==null){ yLock = {lo:baseRange().lo, hi:baseRange().hi}; }
}
pbar.addEventListener("wheel", ev=>{
  ev.preventDefault();
  if(dlgOpen) return;
  pbarFreezeScale();
  let dy=ev.deltaY;
  if(ev.deltaMode===1) dy*=16; else if(ev.deltaMode===2) dy*=100;
  const r=pbar.getBoundingClientRect(); const y=ev.clientY-r.top;
  const k=dy<0?1.1:1/1.1;   // 10% per notch (ca lightweight-charts), nu 12%
  if(vzoomAnim){ vzoomAnim.to=Math.max(0.4,Math.min(2.5,vzoomAnim.to*k)); return; }
  startVzoom(vzoom*k, priceAtY(y));
}, {passive:false});
pbar.addEventListener("mousedown", ev=>{
  if(ev.button!==0 || dlgOpen) return;
  vzoomAnim=null; zoomAnim=null;   // FIX: opreÈ™te animaÈ›iile la grab â€” altfel drag-ul lupta cu scala in miscare
  pbarFreezeScale();                // scala devine manualÄƒ (ca TV) â€” zoom orizontal ulterior nu o recalculeazÄƒ
  const r=pbar.getBoundingClientRect();
  priceBarDrag={ y:ev.clientY-r.top, v0:vzoom, moved:false };
  ev.preventDefault();
});
// dublu-click pe bara de pret (sidebar dreapta) = reset view (ca TradingView) â€” te de-pierzi instant
pbar.addEventListener("dblclick", ev=>{
  ev.preventDefault();
  resetView();
});
window.addEventListener("mousemove", ev=>{
  if(!priceBarDrag) return;
  const r=pbar.getBoundingClientRect(); const y=ev.clientY-r.top;
  const dy=y-priceBarDrag.y;
  if(Math.abs(dy)>3) priceBarDrag.moved=true;
  if(priceBarDrag.moved){
    // PATTERN LIGHTWEIGHT-CHARTS (price-scale drag): scaleCoeff cu termen aditiv +0.2*height ca
    // sa NU explodeze langa margini (1/0 = teleport), clamp min 0.1 (zoom-out max 10x).
    // Inainte: Math.pow(2,-dy/120) = factor 2 la fiecare 120px = HIPERSENSIBIL.
    const h = r.height || 900;
    const anchorY = Math.max(0, Math.min(h, priceBarDrag.y));
    let coeff = (anchorY + h*0.2) / (y + h*0.2);
    coeff = Math.max(coeff, 0.1);
    const nv = priceBarDrag.v0 * coeff;
    applyVzoom(Math.max(0.4, Math.min(2.5, nv)), priceAtY(priceBarDrag.y));
    requestRender();
  }
});

// ðŸ“Œ PRICEBAR LABELS: crosshair la Y-ul cursorului + SL/TP/Entry pentru poziÈ›ia selectatÄƒ (ca TradingView)
function updatePricebar(){
  const pb=el("pbtag");
  // crosshair price: poziÈ›ionat DINAMIC la Y-ul cursorului (nu fix sus)
  if(xhair){
    pb.textContent=fmtP(xhair.price);
    pb.style.top=Math.max(2, Math.min(H-14, yAtPrice(xhair.price)-9))+"px";
    pb.style.display="block";
  } else {
    const R=yRangeCache||yrange();
    pb.textContent=fmtP((R.lo+R.hi)/2);
    pb.style.top="8px";
    pb.style.display="block";
  }
  // SL/TP/Entry labels: vizibile DOAR cÃ¢nd o poziÈ›ie e selectatÄƒ
  const pe=el("pbEntry"), ps=el("pbSL"), pt=el("pbTP");
  const t=selMk || (selSet.length && selSet.find(it=>it.kind==="m") ? selSet.find(it=>it.kind==="m").ref : null);
  if(t && t.dir && t.sl!=null && t.tp!=null && !t.pts){
    const up=t.dir==="LONG";
    const eP=t.price, sP=t.price-(up?1:-1)*t.sl*PIP, tP=t.price+(up?1:-1)*t.tp*PIP;
    pe.textContent=fmtP(eP); pe.style.top=yAtPrice(eP)+"px"; pe.style.display="block";
    ps.textContent="SL "+fmtP(sP); ps.style.top=yAtPrice(sP)+"px"; ps.style.display="block";
    pt.textContent="TP "+fmtP(tP); pt.style.top=yAtPrice(tP)+"px"; pt.style.display="block";
  } else {
    pe.style.display="none"; ps.style.display="none"; pt.style.display="none";
  }
}

el("r1").onclick=()=>reveal(1);
el("r10").onclick=()=>reveal(10);
el("r60").onclick=()=>reveal(60);
el("blindBtn").onclick=toggleBlind;
el("saveBtn").onclick=()=>{ save(); toast("ðŸ’¾ Profil salvat (Ctrl+S) â€” tot ce ai pe chart e persistat"); };
el("laPlaceBtn").onclick=()=>{   // v7.48: mod plasare bara lookahead (one-shot) â€” SEPARAT de switch-ul Lookahead
  if(!blind){ blind=true; toggleBlindUI(); }
  lookaheadPlacing=true; requestRender();
  toast("Mod plasare bara â€” click pe chart o pune (o datÄƒ), apoi revine la normal"); };
el("laDefaultBtn").onclick=()=>{
  const ts=DATA[Math.min(cutoff, DATA.length-1)][0];
  try{ const cur=JSON.parse(localStorage.getItem("gbpusd_last")||"null")||{};
    cur.lookaheadTs=ts; localStorage.setItem("gbpusd_last", JSON.stringify(cur)); }catch(e){}
  toast("ðŸŽ¯ Lookahead default salvat â€” la restart, chart-ul porneÈ™te dezvÄƒluit pÃ¢nÄƒ la "+fmtTRO(ts).slice(0,10)+" "+fmtTRO(ts).slice(11,16));
};
el("resetViewBtn").onclick=()=>{ resetView(); };

el("exp").onclick=()=>{  const data={ version:5, session_id:sessionId,
    markers:markers.map(m=>{ const c=DATA[m.bar]; if(!c) return null; const up=m.dir==="LONG"; return {
      time:fmtT(c[0]), ts:c[0], price:m.price, dir:m.dir, note:m.note||"",
      sl:m.sl!=null?m.sl:null, tp:m.tp!=null?m.tp:null,
      fc:m.fc>0?m.fc:null,
      sl_price:(m.sl!=null)?+(m.price-(up?1:-1)*m.sl*PIP).toFixed(DIG):null,
      tp_price:(m.tp!=null)?+(m.price+(up?1:-1)*m.tp*PIP).toFixed(DIG):null,
      created:m.created||null,
      seen_through:(m.seen_through!=null && m.seen_through<DATA.length)?fmtT(DATA[m.seen_through][0]):null,
      seen_through_ts:(m.seen_through!=null && m.seen_through<DATA.length)?DATA[m.seen_through][0]:null,
      blind:m.blind!=null?m.blind:true }; }).filter(Boolean),
    drawings:drawings.map(d=>({ id:d.id, type:d.type, text:d.text||"",
      points:d.pts.map(p=>({ x:DATA[p.bar][0], y:p.price })) })) };
  const blob=new Blob([JSON.stringify(data,null,2)],{type:"application/json"});
  const a=document.createElement("a");
  a.href=URL.createObjectURL(blob);
  // nume cu data+ora in TIMESTAMP-UL ROMANIEI (Europe/Bucharest: vara UTC+3, iarna UTC+2) â€” nu ora sistemului (care poate fi UTC)
  const p=n=>String(n).padStart(2,"0");
  const tz=new Intl.DateTimeFormat("en-GB",{ timeZone:"Europe/Bucharest", year:"numeric", month:"2-digit", day:"2-digit",
    hour:"2-digit", minute:"2-digit", hour12:false }).formatToParts(new Date());
  const g=t=>{ const x=tz.find(v=>v.type===t); return x?x.value:"00"; };
  a.download="gbpusd_trades_"+g("year")+"-"+g("month")+"-"+g("day")+"_"+g("hour")+"-"+g("minute")+".json";
  document.body.appendChild(a); a.click();
  setTimeout(()=>{ document.body.removeChild(a); URL.revokeObjectURL(a.href); }, 200);
  toast("JSON exportat ("+data.markers.length+" marker-e, "+data.drawings.length+" desene) â€” "+a.download+" â†’ Downloads / collect_exports.py");
};

// ðŸ“¤ Export MT5 EA â€” genereazÄƒ un Expert Advisor de replay cu marker-ele tale (ruleazÄƒ Ã®n MT5 Tester Model=2)
el("expEA").onclick=()=>{
  const sig=markers.filter(m=>m.sl!=null && m.tp!=null && m.price>0 && DATA[m.bar]);
  if(!sig.length){ toast("Niciun marker cu SL/TP â€” pune poziÈ›ii Ã®ntÃ¢i"); return; }
  let rows='';
  for(const m of sig){
    const ts=DATA[m.bar][0];                    // timestamp UTC (secunde)
    const up=m.dir==="LONG";
    const entry=+m.price.toFixed(DIG);
    const slp=+(m.price-(up?1:-1)*m.sl*PIP).toFixed(DIG);
    const tpp=+(m.price+(up?1:-1)*m.tp*PIP).toFixed(DIG);
    rows+='    {'+ts+', "'+m.dir+'", '+entry+', '+slp+', '+tpp+'},\r\n';
  }
  const ea=
"//+------------------------------------------------------------------+\r\n"+
"//| ReplayEA_ChartSignals.mq5 â€” genereazÄƒ din chart (v7.27.11)       |\r\n"+
"//| RuleazÄƒ Ã®n Strategy Tester: GBPUSD.pro Â· M15 Â· Model=2 (every tick) |\r\n"+
"//+------------------------------------------------------------------+\r\n"+
"#property strict\r\n"+
"input int    ServerUTCOffset = 2;   // OANDA server = GMT+2 fixed; UTC = server âˆ’ offset\r\n"+
"input double LotSize         = 0.01;\r\n"+
"input int    Magic           = 20260807;\r\n"+
"struct Sig { long ts; string dir; double entry, sl, tp; };\r\n"+
"input string SignalsBlock=\"---\";\r\n"+
"// semnalele tale (ts = timestamp UTC al barei de intrare)\r\n"+
"Sig sigs[] = {\r\n"+rows+
"};\r\n"+
"int sigCount = ArraySize(sigs);\r\n"+
"bool done[];\r\n"+
"int OnInit(){\r\n  ArrayResize(done, sigCount);\r\n  for(int i=0;i<sigCount;i++) done[i]=false;\r\n  return INIT_SUCCEEDED;\r\n}\r\n"+
"void OnTick(){\r\n  if(sigCount==0) return;\r\n  long barUTC = (long)(iTime(_Symbol, PERIOD_M15, 0) - ServerUTCOffset*3600);\r\n  for(int i=0;i<sigCount;i++){\r\n    if(done[i]) continue;\r\n    if(barUTC < sigs[i].ts) continue;                  // aÈ™teaptÄƒ bara de intrare\r\n    done[i]=true;\r\n    // o singurÄƒ poziÈ›ie per semnal (dacÄƒ mai existÄƒ una deschisÄƒ de la semnalul precedent, o Ã®nchidem la intrarea urmÄƒtoare)\r\n    for(int p=PositionsTotal()-1;p>=0;p--){\r\n      ulong tk=PositionGetTicket(p);\r\n      if(PositionSelectByTicket(tk) && PositionGetInteger(POSITION_MAGIC)==Magic)\r\n        if(!PositionClose(tk)) Print(\"close fail \",tk);\r\n    }\r\n    long type = (sigs[i].dir==\"LONG\") ? POSITION_TYPE_BUY : POSITION_TYPE_SELL;\r\n    MqlTradeRequest req={}; MqlTradeResult res={};\r\n    req.action=TRADE_ACTION_DEAL;\r\n    req.symbol=_Symbol;\r\n    req.volume=LotSize;\r\n    req.type=(sigs[i].dir==\"LONG\")?ORDER_TYPE_BUY:ORDER_TYPE_SELL;\r\n    req.price=(sigs[i].dir==\"LONG\")?SymbolInfoDouble(_Symbol,SYMBOL_ASK):SymbolInfoDouble(_Symbol,SYMBOL_BID);\r\n    req.sl=sigs[i].sl;\r\n    req.tp=sigs[i].tp;\r\n    req.magic=Magic;\r\n    req.comment=\"sig#\"+IntegerToString(i);\r\n    if(!OrderSend(req,res)) Print(\"order fail \",i,\" err=\",res.retcode);\r\n  }\r\n}\r\n";
  const blob=new Blob([ea],{type:"text/plain"});
  const a=document.createElement("a");
  a.href=URL.createObjectURL(blob);
  a.download="ReplayEA_ChartSignals.mq5";
  document.body.appendChild(a); a.click();
  setTimeout(()=>{ document.body.removeChild(a); URL.revokeObjectURL(a.href); }, 200);
  toast("ðŸ“¤ EA MT5 generat cu "+sig.length+" semnale â€” copiazÄƒ Ã®n MQL5/Experts, compileazÄƒ, ruleazÄƒ Ã®n Tester (Model=2)");
};

function findBar(ts){ let lo=0, hi=DATA.length-1;
  while(lo<=hi){ const mid=(lo+hi)>>1;
    if(DATA[mid][0]===ts) return mid;
    if(DATA[mid][0]<ts) lo=mid+1; else hi=mid-1; }
  return null; }
// v7.53: PROFIL TF-SAFE â€” profilul e salvat MEREU Ã®n coordonate M15; la load, dacÄƒ un profil vechi
// e pe alt TF (ex. salvat din greÈ™ealÄƒ pe M1), Ã®l detectÄƒm È™i remapÄƒm prin timestamp. Evaluarea
// WIN/LOSS/expired NU se schimbÄƒ â€” doar poziÈ›iile marker-elor/desenelor sunt corectate.
function findBarFloor(ts){ let lo=0, hi=DATA.length-1, ans=-1;
  while(lo<=hi){ const mid=(lo+hi)>>1;
    if(DATA[mid][0]<=ts){ ans=mid; lo=mid+1; } else hi=mid-1; }
  return ans; }
function findBarFloorIn(arr, ts){ let lo=0, hi=arr.length-1, ans=-1;
  while(lo<=hi){ const mid=(lo+hi)>>1;
    if(arr[mid][0]<=ts){ ans=mid; lo=mid+1; } else hi=mid-1; }
  return ans; }
let tfDataCache={};
function tfData(tf){
  if(tf==="M15") return DATA_BASE;
  if(tf==="M1") return DATA_M1.length?DATA_M1:DATA_BASE;
  if(!tfDataCache[tf]) tfDataCache[tf]=buildTF(tf);
  return tfDataCache[tf];
}
// detecteazÄƒ TF-ul Ã®n care e salvat profilul: toate barele trebuie sÄƒ Ã®ncapÄƒ Ã®n datele acelui TF,
// iar marker-ele trebuie sÄƒ fie la timpul real de creare (TF-ul corect minimizeazÄƒ |ts(bar)-created|)
function detectProfileTF(o){
  const cands=["M15","M1","H1","H4","D1"];
  let best=null, bestErr=Infinity;
  for(const tf of cands){
    if(tf==="M1" && !DATA_M1.length) continue;   // M1 nu existÄƒ pe acest chart â€” nu e candidat
    const d=tfData(tf); if(!d || !d.length) continue;
    let maxB=-1;
    for(const m of (o.markers||[])) if(m&&Number.isInteger(m.bar)) maxB=Math.max(maxB,m.bar);
    for(const dr of (o.drawings||[])) if(dr&&Array.isArray(dr.pts)) for(const p of dr.pts) if(p&&Number.isInteger(p.bar)) maxB=Math.max(maxB,p.bar);
    if(maxB<0) continue;               // niciun bar Ã®n profil
    if(maxB>=d.length) continue;       // nu Ã®ncape Ã®n acest TF
    let err=0, n=0;
    for(const m of (o.markers||[])){
      if(!m||!Number.isInteger(m.bar)||m.bar<0||!m.created||!d[m.bar]) continue;
      n++; err+=Math.abs(d[m.bar][0]-m.created/1000);
    }
    if(n===0){ if(!best) best=tf; continue; }   // fÄƒrÄƒ marker-e cu created: primul care Ã®ncape (M15 implicit)
    if(err<bestErr){ bestErr=err; best=tf; }
  }
  return best||"M15";
}
// remapeazÄƒ barele profilului din TF-ul sursÄƒ Ã®n DATA curentÄƒ prin timestamp + pune ts de ancorÄƒ
function remapProfileTF(o, srcTF){
  const src = (srcTF && srcTF!=="M15") ? tfData(srcTF) : DATA;
  const mts = i => (src[i]?src[i][0]:null);
  for(const m of (o.markers||[])){
    if(!m || !Number.isInteger(m.bar) || m.bar<0) continue;
    const ts=mts(m.bar);
    if(ts!=null){ const nb=findBarFloor(ts); if(nb>=0) m.bar=nb; m.ts=ts; }
  }
  for(const dr of (o.drawings||[])){
    if(!dr||!Array.isArray(dr.pts)) continue;
    for(const p of dr.pts){
      if(!p||!Number.isInteger(p.bar)||p.bar<0) continue;
      const ts=mts(p.bar);
      if(ts!=null){ const nb=findBarFloor(ts); if(nb>=0) p.bar=nb; p.ts=ts; }
    }
  }
  return o;
}
// copie de salvare cu toate barele Ã®n coordonate M15 (DATA_BASE) + ts de ancorÄƒ + tf â€” profilul
// persistat nu mai depinde de TF-ul afiÈ™at la momentul salvÄƒrii.
function normalizeToM15(prof){
  const out={markers:(prof.markers||[]).map(m=>{ const mm={...m};
    if(mm.bar!=null && DATA[mm.bar]){ const ts=DATA[mm.bar][0]; const nb=findBarFloorIn(DATA_BASE, ts); mm.ts=ts; mm.bar=nb>=0?nb:mm.bar; }
    return mm; }),
    drawings:(prof.drawings||[]).map(d=>({...d, pts:d.pts.map(p=>{ const pp={...p};
      if(pp.bar!=null && DATA[pp.bar]){ const ts=DATA[pp.bar][0]; const nb=findBarFloorIn(DATA_BASE, ts); pp.ts=ts; pp.bar=nb>=0?nb:pp.bar; }
      return pp; })})),
    indicators:prof.indicators||[], omarParams:prof.omarParams||{}, tf:"M15"};
  return out;
}

el("imp").onclick=()=>el("impFile").click();
el("impFile").onchange=ev=>{
  const f=ev.target.files[0]; if(!f) return;
  const rd=new FileReader();
  rd.onload=()=>{ try{
    const o=JSON.parse(rd.result);
    const arr=Array.isArray(o)?o:(o.markers||[]);
    const imp=[];
    for(const e of arr){
      let ts=typeof e.ts==="number"?e.ts:NaN;
      if(!isFinite(ts) && e.time){ const p=Date.parse(String(e.time).replace(" ","T")); if(isFinite(p)) ts=p/1000; }
      const idx=findBar(ts); if(idx===null) continue;
      const st=(typeof e.seen_through_ts==="number")?findBar(e.seen_through_ts):null;
      imp.push({ id:++mkSeq, bar:idx, price:e.price, dir:(e.dir==="SELL"||e.dir==="SHORT")?"SHORT":"LONG",
                 note:e.note||"", sl:e.sl!=null?e.sl:6.5, tp:e.tp!=null?e.tp:6.5,
                 tf:TF, ts:DATA[idx]?DATA[idx][0]:undefined,   // v7.54: TF de plasare + ancora de timp
                 created:e.created||Date.now(),
                 seen_through:(st!=null)?st:idx, blind:e.blind!==false });
    }
    const impd=[];
    if(o.drawings){ for(const d of o.drawings){ const pts=[];
        for(const p of d.points||[]){ let idx=findBar(p.x); if(idx===null){ pts.length=0; break; }
          if(blind && idx>cutoff) idx=cutoff;   // importul nu re-injecteaza viitorul
          pts.push({bar:idx, price:p.y}); }
        if(pts.length) impd.push({ id:++drwSeq, type:d.type||"line", text:d.text||"", pts }); } }
    markers=imp; drawings=impd; save(); requestRender();
    toast("Importat "+imp.length+" marker-e, "+impd.length+" desene"); }
    catch(err){ toast("Import eÈ™uat: "+err.message); } };
  rd.readAsText(f);
  ev.target.value="";
};

el("cls").onclick=()=>{
  if((markers.length||drawings.length) && confirm("È˜tergi tot ("+markers.length+" marker-e, "+drawings.length+" desene)?")){ markers=[]; drawings=[]; sel=null; save(); requestRender(); toast("Totul È™ters"); }
};

function __boot(){
__restoreState();
ensureTags();   // v7.42: tag-uri permanente pe desene (backfill pentru cele existente)
renderList();
resize();
computeOmar();
renderIndList();
try{ const th=JSON.parse(localStorage.getItem("gbpusd_theme")||"null");
  if(th&&th.name){ themeName=th.name; themeAccent=th.accent||null; } }catch(e){}
applyTheme(themeName, themeAccent);
}
</script>
<svg xmlns="http://www.w3.org/2000/svg" style="display:none">
  <defs>
    <symbol id="i-pointer" viewBox="0 0 24 24"><path d="M3 3l7.07 16.97 2.51-7.39 7.39-2.51L3 3z"/><path d="M13 13l6 6"/></symbol>
    <symbol id="i-long" viewBox="0 0 24 24"><path d="M5 3h14"/><path d="m18 13-6-6-6 6"/><path d="M12 7v14"/></symbol>
    <symbol id="i-short" viewBox="0 0 24 24"><path d="M12 17V3"/><path d="m6 11 6 6 6-6"/><path d="M19 21H5"/></symbol>
    <symbol id="i-line" viewBox="0 0 24 24"><path d="M3 20 21 4"/><circle cx="3" cy="20" r="2" fill="currentColor" stroke="none"/><circle cx="21" cy="4" r="2" fill="currentColor" stroke="none"/></symbol>
    <symbol id="i-pen" viewBox="0 0 24 24"><path d="M17 3a2.828 2.828 0 1 1 4 4L7.5 20.5 2 22l1.5-5.5L17 3z"/></symbol>
    <symbol id="i-rect" viewBox="0 0 24 24"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"/></symbol>
    <symbol id="i-hline" viewBox="0 0 24 24"><line x1="4" y1="12" x2="20" y2="12"/><circle cx="12" cy="12" r="1.5" fill="currentColor" stroke="none"/></symbol>
    <symbol id="i-note" viewBox="0 0 24 24"><path d="M22 17a2 2 0 0 1-2 2H6.828a2 2 0 0 0-1.414.586l-2.202 2.202A.71.71 0 0 1 2 21.286V5a2 2 0 0 1 2-2h16a2 2 0 0 1 2 2z"/><path d="M7 11h10"/><path d="M7 15h6"/></symbol>
    <symbol id="i-test" viewBox="0 0 24 24"><path d="M14 2v6a2 2 0 0 0 .245.96l5.51 10.08A2 2 0 0 1 18 22H6a2 2 0 0 1-1.755-2.96l5.51-10.08A2 2 0 0 0 10 8V2"/><path d="M6.453 15h11.094"/><path d="M8.5 2h7"/></symbol>
    <symbol id="i-ai" viewBox="0 0 24 24"><path d="M11.017 2.814a1 1 0 0 1 1.966 0l1.051 5.558a2 2 0 0 0 1.594 1.594l5.558 1.051a1 1 0 0 1 0 1.966l-5.558 1.051a2 2 0 0 0-1.594 1.594l-1.051 5.558a1 1 0 0 1-1.966 0l-1.051-5.558a2 2 0 0 0-1.594-1.594l-5.558-1.051a1 1 0 0 1 0-1.966l5.558-1.051a2 2 0 0 0 1.594-1.594z"/><path d="M20 2v4"/><path d="M22 4h-4"/></symbol>
    <symbol id="i-bot" viewBox="0 0 24 24"><rect x="4" y="8" width="16" height="12" rx="2"/><path d="M12 8V4"/><circle cx="12" cy="2" r="1.5"/><circle cx="9" cy="13" r="1.2" fill="currentColor" stroke="none"/><circle cx="15" cy="13" r="1.2" fill="currentColor" stroke="none"/><path d="M9.5 17h5"/></symbol>
    <symbol id="i-eye" viewBox="0 0 24 24"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></symbol>
    <symbol id="i-eyeoff" viewBox="0 0 24 24"><path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/><line x1="1" y1="1" x2="23" y2="23"/></symbol>
    <symbol id="i-play" viewBox="0 0 24 24"><polygon points="6 3 20 12 6 21 6 3"/></symbol>
    <symbol id="i-pause" viewBox="0 0 24 24"><rect x="5" y="3" width="4" height="18" rx="1"/><rect x="15" y="3" width="4" height="18" rx="1"/></symbol>
    <symbol id="i-unlock" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 9.9-1"/></symbol>
    <symbol id="i-lock" viewBox="0 0 24 24"><rect x="3" y="11" width="18" height="11" rx="2" ry="2"/><path d="M7 11V7a5 5 0 0 1 10 0v4"/></symbol>
    <symbol id="i-magnet" viewBox="0 0 24 24"><path d="m6 15-4-4 6.75-6.77a7.79 7.79 0 0 1 11 11L13 22l-4-4 6.39-6.36a2.14 2.14 0 0 0-3-3L6 15z"/><path d="m5 8 4 4"/><path d="m12 15 4 4"/></symbol>
    <symbol id="i-save" viewBox="0 0 24 24"><path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"/><path d="M17 21v-8H7v8"/><path d="M7 3v5h8"/></symbol>
    <symbol id="i-flag" viewBox="0 0 24 24"><path d="M4 22V4a1 1 0 0 1 1-1h13l-3 4 3 4H5"/><path d="M4 4h16"/></symbol>
    <symbol id="i-pin" viewBox="0 0 24 24"><path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0 1 18 0z"/><circle cx="12" cy="10" r="3"/></symbol>
    <symbol id="i-theme" viewBox="0 0 24 24"><path d="M12 22a1 1 0 0 1 0-20 10 9 0 0 1 10 9 5 5 0 0 1-5 5h-2.25a1.75 1.75 0 0 0-1.4 2.8l.3.4a1.75 1.75 0 0 1-1.4 2.8z"/><circle cx="13.5" cy="6.5" r=".5" fill="currentColor"/><circle cx="17.5" cy="10.5" r=".5" fill="currentColor"/><circle cx="6.5" cy="12.5" r=".5" fill="currentColor"/><circle cx="8.5" cy="7.5" r=".5" fill="currentColor"/></symbol>
    <symbol id="i-report" viewBox="0 0 24 24"><rect width="8" height="4" x="8" y="2" rx="1" ry="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/><path d="m9 14 2 2 4-4"/></symbol>
    <symbol id="i-ruler" viewBox="0 0 24 24"><path d="M21.3 15.3a2.4 2.4 0 0 1 0 3.4l-2.6 2.6a2.4 2.4 0 0 1-3.4 0L2.7 8.7a2.41 2.41 0 0 1 0-3.4l2.6-2.6a2.41 2.41 0 0 1 3.4 0Z"/><path d="m14.5 12.5 2-2"/><path d="m11.5 9.5 2-2"/><path d="m8.5 6.5 2-2"/><path d="m17.5 15.5 2-2"/></symbol>
    <symbol id="i-undo" viewBox="0 0 24 24"><path d="M9 14 4 9l5-5"/><path d="M4 9h10.5a5.5 5.5 0 0 1 5.5 5.5a5.5 5.5 0 0 1-5.5 5.5H11"/></symbol>
    <symbol id="i-redo" viewBox="0 0 24 24"><path d="m15 14 5-5-5-5"/><path d="M20 9H9.5a5.5 5.5 0 0 0-5.5 5.5a5.5 5.5 0 0 0 5.5 5.5H13"/></symbol>
  </defs>
</svg>
</body>
</html>
"""

html = HTML

# --- SABIN: injecteaza seed_profile.json (trade-urile reale + MSS/FVG/liquidity/OB)
#     in window.GBPUSD_DEFAULT_PROFILE, ca profilul default al chart-ului.
SEED = os.path.join(HERE, "seed_profile.json")
if os.path.exists(SEED):
    with open(SEED, encoding="utf-8") as _f:
        _seed = _f.read()
    _mark = "window.GBPUSD_DEFAULT_PROFILE="
    _i = html.find(_mark)
    if _i >= 0:
        _j = html.find(";", _i)
        html = html[:_i] + _mark + _seed + ";" + html[_j + 1:]
        print("[seed] profil default inlocuit din", os.path.basename(SEED))
    else:
        print("[seed] ATENTIE: nu am gasit window.GBPUSD_DEFAULT_PROFILE")
else:
    print("[seed] lipseste", os.path.basename(SEED), "- pastrez profilul default din template")

OHLC_OUT = os.path.join(HERE, "gbpusd_ohlc.json")
OHLC_JS = os.path.join(HERE, "gbpusd_ohlc.js")
ohlc_obj = {"m15": rows, "m1": rows_m1}
ohlc_js = json.dumps(ohlc_obj, separators=(",", ":"))
with open(OHLC_OUT, "w", encoding="utf-8") as f:
    f.write(ohlc_js)
with open(OHLC_JS, "w", encoding="utf-8") as f:
    f.write("window.GBPUSD_OHLC=" + ohlc_js + ";")
with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print("scris", OUT, os.path.getsize(OUT), "bytes |", OHLC_OUT, os.path.getsize(OHLC_OUT), "bytes |", OHLC_JS, os.path.getsize(OHLC_JS), "bytes |", len(rows), "bare")
