# Idei — Stefan

> Jurnal personal de idei de trading. Doar Stefan scrie aici.

## Format

Fiecare idee trebuie să conțină:
- **Data**
- **Tip** (crypto / forex / stocks / altul)
- **Descriere**
- **De ce?** (cea mai importantă întrebare)
- **Status** (de discutat / testat / implementat / abandonat)

---

## Idei

### 2026-08-29 — Signal library / ensemble de filtre mici (confirmată de Claude)
- **Tip:** forex / algo
- **Descriere:** În loc de un model mare (confidence score — a picat: AUC 0.44–0.59), o bibliotecă de filtre mici, fiecare validat SEPARAT pe ipoteza lui, combinate prin AND/scor simplu. "Un model per parametru meu cu higher winrate la ăla."
- **De ce?:** Grid mare ≈ p-hacking; multe ipoteze mici testate una câte una = pipeline hedge fund real.
- **Status:** testat / de continuat (Goal 1 din plan)

### 2026-08-29 — Hibrid uman-bot (adnotare PASS/SKIP)
- **Tip:** forex
- **Descriere:** Singura cale cu PF real dovedit. Adnotez PASS/SKIP pe chart tool (chart v7.57 cu categorii fixe + motiv), apoi `analyze_markers.py` extrage ipoteze de nivel fin per-trade. Țintă: 100+ adnotări. Confidence score = risk-dial DOAR după ce hibridul produce date.
- **De ce?:** Confidența mea de om, nu parametri, separă semnalul de zgomot.
- **Status:** de implementat (chart tool gata, commit 272b8ee)

### 2026-08-29 — USDCHF reversal / contrarian (V6)
- **Tip:** forex
- **Descriere:** Reversal pe USDCHF: WR real 26.4% → 73.6% pe 178 trade-uri (V2–V5). Schimbă ambele direcții, SL pe structura opusă, doar 1RR pe V2/V3. Zilele de aur: Miercuri + Vineri.
- **De ce?:** Edge istoric real (p<0.005, 2 configuri independente). Cifră realistă +5–15%/lună.
- **Status:** implementat — V6 rulează pe PC (REVERSE_USDCHF), a luat WIN prima zi. În validare live.

### 2026-08-29 — Plan 3 obiective pe 3 niveluri de backtest
- **Tip:** metodologie / forex
- **Descriere:** (1) Bibliotecă filtre validate individual pe TOATE datele (V2–V9 = 1185 trade-uri), (2) adnotare 100+, (3) walk-forward mic abia pe filtrele trecute. 3 niveluri: test filtru → WF 4 ferestre → shadow VPS.
- **De ce?:** Filtru izolat pe N mare == ce fac hedge fund-urile (iploteză > grid).
- **Status:** de executat

### 2026-08-31 — Expectancy Grid V9f (5$/lot) + prognoză pe zi
- **Tip:** forex
- **Descriere:** Simulare pe grid-ul v9f cu comision $5/lot FundingPips: +$3,211 (+32.7%) pe 4 săptămâni, mediană ~+$101/trade, N=60. Luni = cea mai bună zi (GBPUSD Long 1.5% + Short). Capcană: blocare per-symbol (o poziție GBPUSD 5–6h blochează toate celelalte GBPUSD, MAX 3 poziții global).
- **De ce?:** Să știu ce e cel mai probabil per zi + limitele reale (ocuparea poziției).
- **Status:** testat / de discutat

---

### Candidați de filtru testați → ÎNCHIȘI (rezultat)
- **CHoCH ca filtru** → închis (PF_real < 1.0)
- **Swing length PL=13** (ipoteza lui Sabin) → închis (PF_real 1.03 = breakeven; inconsistent pe ferestre recente)
- **skip_chop** → închis (3/4 ferestre baseline bate; chop taie trade-uri bune)
- **Grid GBPUSD M1-fill** → 0/4 ferestre trec Gate 0
- **Grid 100k combos** → respins (overfitting garantat, PBO)
- **skip Miercuri+Vineri** → ≈ deja implementat în v9f

---
