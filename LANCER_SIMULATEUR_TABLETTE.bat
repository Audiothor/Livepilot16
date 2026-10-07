@echo off
title LivePilot 16 - Simulateur Cockpit Tablette
color 0B
echo =================================================================
echo        LIVEPILOT 16 - COCKPIT HUD POUR TABLETTE & ABLETON
echo =================================================================
echo.
echo [*] Adresse locale PC     : http://localhost:8080
echo [*] Adresse Wi-Fi Tablette : http://192.168.1.105:8080
echo.
echo Ouvrez cette adresse Wi-Fi dans le navigateur de votre tablette !
echo.
start http://localhost:8080
python "%~dp0tools\cockpit_bridge.py"
pause
