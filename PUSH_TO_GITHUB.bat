@echo off
title Pushing TravelPilot to GitHub
echo =======================================================
echo Pushing TravelPilot to https://github.com/Pushkarpatade/travel-agent-final99
echo =======================================================
cd /d "F:\dek\ai agent"
"F:\dek\mingit\cmd\git.exe" branch -M main
"F:\dek\mingit\cmd\git.exe" push -u origin main --force
echo.
echo =======================================================
if %ERRORLEVEL% equ 0 (
    echo SUCCESS! All files pushed to travel-agent-final99!
) else (
    echo Please check error above.
)
echo =======================================================
pause
