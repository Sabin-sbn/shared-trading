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

- **2026-08-21 — Sabin (sesiune Copilot):** Am analizat COMPLET strategia No Wick a lui Omar Nowick:
  - Descărcat și analizat transcrierile a **66 de clipuri YouTube** de la @omarnowick (~386.000 cuvinte), inclusiv cursul complet de 5 ore
  - Creat [[Research/Strategia_NoWick_OmarNowick_Analiza_Completa]] — toate regulile: definiția no-wick candle, cele 5 reguli de bază, mecanica intrării, SL/TP, setup-urile A/B/C, Omar entry, filtre știri/sesiuni, risk management
  - Creat [[Research/NoWick_Cheat_Sheet]] — checklist rapid de folosit la fiecare trade
  - **Următorul pas propus:** backtest manual 100 trade-uri pe USDCHF + GBPUSD pe 15min înainte de bani reali
  - ⚠️ Important: feed-ul TradingView trebuie setat pe OANDA, altfel lumânările no-wick diferă!
