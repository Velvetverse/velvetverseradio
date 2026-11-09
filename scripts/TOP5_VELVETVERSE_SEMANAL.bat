@echo off
setlocal
chcp 65001 >nul
if "%~1"=="" (
 echo Arrasta um CSV RCast para cima deste BAT.
 pause
 exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%~dp0TOP5_VELVETVERSE_SEMANAL.ps1" -Csv "%~1"
if errorlevel 1 echo Processo bloqueado; nao foi publicado nenhum ficheiro.
pause