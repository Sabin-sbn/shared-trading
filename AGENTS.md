# AGENTS.md — TRADING PROJECT (reguli pentru AI)

Acest fisier este citit de asistentii AI (Obsidian Copilot, Claude, opencode etc.)
de pe TOATE calculatoarele. Citeste-l si respecta-l inainte de orice actiune.

## Ce este proiectul

Colaborare Sabin + Stefan + Nicolas pentru trading (crypto, forex, stocks, orice tip).
Trei persoane, trei PC-uri diferite, un singur repository Git partajat.

## Structura repository-ului

- `Sabin_Logs/` — doar Sabin scrie aici. AI-ul lui Sabin POATE scrie aici.
  AI-ul lui Stefan si Nicolas NU are voie sa modifice nimic aici.
- `Stefan_Logs/` — doar Stefan scrie aici. AI-ul lui Stefan POATE scrie aici.
  AI-ul lui Sabin si Nicolas NU are voie sa modifice nimic aici.
- `Nicolas_Logs/` — doar Nicolas scrie aici. AI-ul lui Nicolas POATE scrie aici.
  AI-ul lui Sabin si Stefan NU are voie sa modifice nimic aici.
- `Project_Board.md` — tablou de sarcini comun. POATE fi editat de TOTI
  (sync inainte + sync dupa; git tine evidenta cine a modificat ce).
- `Chat.md` — chat async intre cei trei (doar adaugare de mesaje la final).
- `Research/` — note de research COMUNE (strategii, analize, tutoriale, indicatori).
  TOTI pot adauga aici (cu sync inainte + sync dupa).
- `START.bat` — dublu-clic pentru a deschide Chat.md in Obsidian (cu sync automat).
- `sync.bat` — scriptul de sincronizare (git pull + commit + push cu dublu-clic).
- `history.bat` — scriptul de audit (arata cine a modificat ce si cand).

Regula generala: singurele foldere PERSONALE sunt `Sabin_Logs/`, `Stefan_Logs/` si `Nicolas_Logs/`.
Orice altceva din repository e COMUN si poate fi modificat de toti trei
(Git tine evidenta cine a schimbat ce — vezi `history.bat`).

## Audit trail (cine a modificat ce si cand)

- Git inregistreaza AUTOMAT totul: autorul (numele din `git config`), data, ora
  si exact ce linii s-au schimbat (inclusiv in fisierele comune).
- `history.bat` (dublu-clic) afiseaza istoricul: cine, cand, ce fisier.
- Pentru ca auditul sa mearga, fiecare utilizator TREBUIE sa aiba identitatea
  git setata (`git config --global user.name` / `user.email`) — altfel
  commit-urile apar anonime.
- Fisierele comune (Project_Board, Chat.md) pot fi editate
  de toti; la conflict, pastrati ambele parti.

## Reguli obligatorii pentru AI

1. **Sync inainte + sync dupa** orice editare: ruleaza `sync.bat`
   (sau direct: `git pull origin main` / `git push origin main`).
2. **Scrie in folderul utilizatorului tau** (Sabin_Logs, Stefan_Logs sau Nicolas_Logs) pentru
   jurnalele personale, si oriunde in fisierele COMUNE (Research/, Project_Board,
   Chat.md) cand e nevoie — cu sync inainte + sync dupa.
3. **NU edita niciodata** fisierele din folderul personal al celuilalt.
4. **NU pune fisiere video** (.mp4, .mov) sau alte fisiere mari in Git.
5. **NU pune secrete, chei API sau parole** in niciun fisier din repo.
6. La **conflict de merge**: pastreaza AMBELE parti, nu sterge munca nimanui,
   si raporteaza utilizatorului ce s-a intamplat.
7. In `Chat.md` scrie mesaje doar in formatul existent, cu data + ora + nume,
   si NU sterge mesajele existente.
8. Daca esti intrebat despre note private din seifurile personale:
   acel continut NU se copiaza in acest repository.

## Informatii Git

- Remote: `git@github.com:Sabin-sbn/shared-trading.git` (SSH)
  sau `https://github.com/Sabin-sbn/shared-trading.git` (HTTPS)
- Branch principal: `main`
- Repo-ul e un "nested repo": se afla fizic in interiorul seifurilor Obsidian
  personale, dar fiecare seif personal il IGNORA in git-ul lui (privacy garantata).
- Fiecare utilizator are propriul folder de logs -> risc minim de conflicte.

## Model de lucru recomandat

1. Citeste cerinta utilizatorului
2. `git pull origin main` (vezi ce e nou)
3. Scrie/editeaza doar in folderul potrivit
4. `git add .` + `git commit -m "descriere"` + `git push origin main`
5. Confirma utilizatorului ca modificarile au fost sincronizate
