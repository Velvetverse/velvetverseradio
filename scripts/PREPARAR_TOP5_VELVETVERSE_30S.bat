@echo off
setlocal
chcp 65001 >nul
echo.
echo === TOP 5 VELVETVERSE - 5 EXCERTOS DE 30 SEGUNDOS ===
echo.
set "script=%~dp0PREPARAR_TOP5_VELVETVERSE_30S.ps1"
if not exist "%script%" (
 echo Falta o ficheiro PREPARAR_TOP5_VELVETVERSE_30S.ps1 na mesma pasta.
 pause
 exit /b 1
)
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%script%" %*
if errorlevel 1 (
 echo.
 echo ERRO: nenhum ficheiro deve ser publicado sem verificacao.
 pause
 exit /b 1
)
echo.
pause
endlocal