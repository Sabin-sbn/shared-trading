@echo off
cd /d "%~dp0"
echo ========================================
echo   SYNC TRADING PROJECT (Sabin/Stefan/Nicolas)
echo ========================================
echo.
echo [1/3] Pull (descarca modificarile celorlalti)...
git pull origin main || (echo [EROARE] Pull esuat! Verifica conflictele. & pause & exit /b 1)
echo.
echo [2/3] Commit...
git add .
git diff --cached --quiet || git commit -m "sync: %date% %time%"
echo.
echo [3/3] Push (urc modificarile tale)...
git push origin main || (echo [EROARE] Push esuat! Verifica conexiunea. & pause & exit /b 1)
echo.
echo ========================================
echo   Sincronizare reusita! Te poti inchide.
echo ========================================
pause
