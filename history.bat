@echo off
cd /d "%~dp0"
echo ================================================
echo   AUDIT: cine a modificat ce si cand
echo ================================================
echo.
echo --- Cine esti tu in git (cum apare in istoric) ---
git config user.name
git config user.email
echo.
echo --- Ultimele 25 de modificari (autor, data, mesaj) ---
git log --pretty=format:"[%%h] %%an (%%ad): %%s" --date=format:"%%d.%%m.%%Y %%H:%%M" -25
echo.
echo.
echo --- Fisiere modificate in ultimele 5 commit-uri ---
git log --name-only --pretty=format:"[%%an] %%ad" --date=format:"%%d.%%m.%%Y %%H:%%M" -5
echo.
echo ================================================
echo   Sfat: in Obsidian deschide fisierul, mergi la
echo   git history, sau ruleaza in terminal:
echo   git blame NumeFisier.md  (cine a scris fiecare linie)
echo ================================================
pause
