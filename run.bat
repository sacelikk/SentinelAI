@echo off
chcp 65001 >nul
title SentinelAI Baslatici

echo ====================================================
echo          🛡️ SentinelAI Baslatiliyor...
echo ====================================================
echo.

echo [1/2] Python API Sunucusu arka planda baslatiliyor...
start "SentinelAI API (FastAPI)" cmd /k ".\venv\Scripts\activate && python api\server.py"

:: API'nin acilmasi icin 3 saniye bekle
timeout /t 3 /nobreak >nul

echo [2/2] C# WPF Arayuzu baslatiliyor...
cd ui\SentinelUI
start "SentinelAI Dashboard" cmd /c "dotnet run"

echo.
echo Her sey hazir! Iyi taramalar dileriz.
echo ====================================================
exit
