# Chat — Trading Project

Chat async prin Git. Mesajele se vad dupa sync (dublu-clic pe `sync.bat`).

## Reguli (ca sa nu avem conflicte)

1. Inainte sa scrii: ruleaza `sync.bat` (descarca mesajele celorlalti)
2. Scrie mesajul la finalul listei, cu data + ora + numele tau
3. Dupa ce scrii: ruleaza `sync.bat` (urca mesajul tau)
4. Daca apare conflict: pastreaza AMBELE parti si sync din nou
5. Nu sterge mesajele celorlalti
6. Pentru discutii instant (nu async): WhatsApp / Discord

## Mesaje

- **2026-08-17 23:22 — Sabin:** Repo-ul de trading e creat! Structura e identică cu cea de Clippings, adaptată pentru 3 persoane și trading. Fiecare are folderul lui de Logs. `Research/` e comun pentru strategii, analize, tooluri. Dați sync.bat ca să vedeți totul. Spor la trading! 🚀

- **2026-08-17 23:32 — Sabin (sesiune Copilot):**
  **Ce am făcut:**
  1. Am creat repository-ul complet: `https://github.com/Sabin-sbn/shared-trading`
  2. Structură identică cu Clippings (Stefan/Sabin), adaptată pentru 3 persoane
  3. Am adăugat pe **Stefan (Predy1)** și **Nicolas (Tioping)** ca colaboratori cu permisiune write
  4. Invitațiile au fost trimise — trebuie să le accepte de pe GitHub

  **Structura repo-ului:**
  - `Sabin_Logs/`, `Stefan_Logs/`, `Nicolas_Logs/` — jurnale personale (fiecare scrie doar în al său)
  - `Research/` — note comune (strategii crypto, forex, stocks, tooluri, management risc)
  - `Project_Board.md` — tablou sarcini comun
  - `Chat.md` — acest chat (async prin Git)
  - `sync.bat` — dublu-clic pentru pull + commit + push
  - `history.bat` — dublu-clic pentru audit (cine a modificat ce)
  - `_obsidian_setup/` — config Graph View (copy în .obsidian)

  **Ce trebuie să faceți (Stefan + Nicolas):**
  1. Acceptați invitația: mergeți la `https://github.com/Sabin-sbn/shared-trading` → "Accept invitation"
  2. Clone: `git clone https://github.com/Sabin-sbn/shared-trading.git`
  3. Set git identity: `git config --global user.name "Stefan"` (sau "Nicolas")
  4. `git config --global user.email "emailul@users.noreply.github.com"`
  5. Dublu-clic pe `START.bat` — deschide Chat.md direct în Obsidian
  6. Dublu-clic pe `sync.bat` — sincronizează (pull + commit + push)

  **Reguli de aur (ca la Clippings):**
  - Fiecare scrie doar în folderul lui de Logs
  - `Research/`, `Project_Board`, `Chat` — comune (sync înainte + după)
  - Git ține evidența cine a schimbat ce (vezi `history.bat`)
  - La conflict: păstrezi AMBELE părți
  - Fisiere video/mari nu în Git

  **Trading:** crypto, forex, stocks, orice tip. Proiect separat de Clippings, dar în același vault SecondBrain.

- **2026-08-18 00:00 — Stefan:**
  Am pus în `Research/` baza de cunoștințe completă de **backtest în Python** — cum îți construiești o strategie și o testezi corect:
  - **Docs:** `Research/backtest/00_START_HERE.md` (începe de aici) → ghid complet, descărcare date din MT5, gates de validare, lecții învățate, metrici + calibrare, audit forward-test.
  - **Cod (gata de rulat):** `Research/code/` — `ExportM1History_EA.mq5` (compilezi în MetaEditor), `download_m1.py` (descarcă 2.5 ani M1), `data_loader.py`, `backtest_minimal.py` (motorul — editezi funcția `signal()`), `walk_forward.py`, `monte_carlo.py`.
  - **Regula de bază:** backtest-ul e orientativ, live-ul e adevărul. Python umflă rezultatele ~2.22× → pragul real de breakeven e PF ≥ 2.3. Validați pe date unseen (walk-forward 3/4 + blind + Monte Carlo <5% breach) înainte de orice ban real.
  Dați sync ca să le aveți. Spor! 🚀
