@echo off
setlocal EnableExtensions DisableDelayedExpansion
title VelvetVerse Noticias - RECECAO PRIVADA (sem emissao)
cd /d "%~dp0.."
echo ===================================================
echo VelvetVerse Radio - Noticias com Ricky Sousa
echo RECECAO DE ENSAIO - NAO ALTERA O RADIODJ
echo ===================================================
echo.
echo Este comando apenas transfere um MP3 aprovado do
echo R2 PRIVADO para uma pasta local de ensaio.
echo Nao importa musica, nao agenda e nao emite.
echo.
if not exist "scripts\velvetverse_noticias_transferencia.py" (
  echo ERRO: pasta do projeto incompleta.
  pause
  exit /b 2
)
if "%R2_ACCOUNT_ID%"=="" goto :credentials
if "%R2_ACCESS_KEY_ID%"=="" goto :credentials
if "%R2_SECRET_ACCESS_KEY%"=="" goto :credentials
if "%R2_BUCKET%"=="" goto :credentials
where py >nul 2>nul
if not errorlevel 1 (
  set "PY=py -3"
) else (
  where python >nul 2>nul
  if errorlevel 1 (
    echo ERRO: Python nao encontrado.
    pause
    exit /b 2
  )
  set "PY=python"
)
%PY% -c "import boto3" >nul 2>nul
if errorlevel 1 (
  echo ERRO: falta boto3. Instalar manualmente num ambiente seguro.
  pause
  exit /b 2
)
set "DST=C:\VelvetVerseNoticias\Staging"
echo A receber ficheiro privado para: %DST%
%PY% "scripts\velvetverse_noticias_transferencia.py" receive --destination "%DST%"
if errorlevel 1 (
  echo.
  echo Rececao falhou ou nao existe edicao aprovada.
  echo Nenhuma mudanca foi feita na RadioDJ.
  pause
  exit /b 2
)
echo.
echo Ficheiro recebido para staging.
echo ESTE FICHEIRO NAO ESTA AGENDADO NEM AUTORIZADO PARA EMISSAO.
pause
exit /b 0
:credentials
echo ERRO: configuracao R2 privada em falta neste PC.
echo Nao colocar chaves neste ficheiro nem no GitHub.
pause
exit /b 2
