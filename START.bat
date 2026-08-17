@echo off
cd /d "%~dp0"
echo ========================================
echo   TRADING PROJECT — START
echo ========================================
echo.
echo [1/2] Sync (pull ultimele modificari)...
git pull origin main
echo.
echo [2/2] Deschid Chat.md in Obsidian...
start "" "obsidian://open?vault=SecondBrain&file=Trading/Chat"
echo.
echo ========================================
echo   Chat.md e deschis in Obsidian!
echo   Scrie-ti mesajul, apoi da sync.bat
echo   ca sa-l trimiti celorlalti.
echo ========================================
pause
