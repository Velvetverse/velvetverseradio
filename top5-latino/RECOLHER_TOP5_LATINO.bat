@echo off
setlocal
title Top 5 Latino - Recolher musicas aprovadas
echo TOP 5 LATINO - VelvetVerse Radio
echo A ler a selecao aprovada no GitHub...
powershell.exe -NoLogo -NoProfile -ExecutionPolicy Bypass -Command "$ErrorActionPreference='Stop'; try { [Net.ServicePointManager]::SecurityProtocol=[Net.SecurityProtocolType]::Tls12; $src='D:\mp3\RITMO LATINO'; if(!(Test-Path -LiteralPath $src -PathType Container)){throw 'Pasta RITMO LATINO nao encontrada'}; $url='https://raw.githubusercontent.com/Velvetverse/velvetverseradio/main/top5-latino/selecao-atual.json'; $data=Invoke-RestMethod -Uri $url -UseBasicParsing; if($data.estado -ne 'aprovada' -or [string]$data.edicao -notmatch '^\d{4}-\d{2}-\d{2}$' -or @($data.posicoes).Count -ne 5){throw 'Selecao nao aprovada ou incompleta'}; $ranks=@($data.posicoes | ForEach-Object { [int]$_.posicao }); if((@($ranks | Sort-Object -Unique) -join ',') -ne '1,2,3,4,5'){throw 'Posicoes invalidas'}; $items=@($data.posicoes | Sort-Object posicao -Descending); $plan=@(); foreach($x in $items){ $name=[string]$x.ficheiro; if(!$name -or $name -ne [IO.Path]::GetFileName($name) -or [IO.Path]::GetExtension($name) -notin @('.mp3','.m4a')){throw 'Nome de musica invalido'}; $source=Join-Path $src $name; if(!(Test-Path -LiteralPath $source -PathType Leaf)){throw ('Musica nao encontrada: '+$name)}; $plan+= [pscustomobject]@{ Source=$source; Name=('{0:D2} - {1}' -f [int]$x.posicao,$name) } }; $dest=Join-Path 'D:\mp3\TOP5_LATINO' ([string]$data.edicao); if(Test-Path -LiteralPath $dest){throw ('Ja existe uma pasta para esta edicao: '+$dest+'; nada foi substituido')}; New-Item -Path $dest -ItemType Directory -Force | Out-Null; foreach($item in $plan){Copy-Item -LiteralPath $item.Source -Destination (Join-Path $dest $item.Name) -ErrorAction Stop; Write-Host ('COPIADO: '+$item.Name)}; Write-Host ('CONCLUIDO: 5 musicas copiadas para '+$dest) -ForegroundColor Green } catch { Write-Host ('PARADO: '+$_.Exception.Message) -ForegroundColor Red; exit 1 }"
set "RESULT=%ERRORLEVEL%"
echo.
if not "%RESULT%"=="0" echo Nenhum ficheiro original foi movido ou apagado.
pause
exit /b %RESULT%
