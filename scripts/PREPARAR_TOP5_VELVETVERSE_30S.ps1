# Top 5 VelvetVerse — preparacao local segura dos 5 excertos de 30 segundos.
# Nao altera a emissao, os MP3 originais ou o RadioDJ. Nao publica ficheiros.
param([string]$Root = 'D:\mp3\Top 5 Velvetverse\TOP5_VELVETVERSE_V3')
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
Write-Host 'TOP 5 VELVETVERSE | CINCO EXCERTOS DE 30 SEGUNDOS' -ForegroundColor Cyan
if (!(Test-Path -LiteralPath $Root -PathType Container)) { throw "Pasta D: nao encontrada: $Root" }
$folders = @(Get-ChildItem -LiteralPath $Root -Directory | Where-Object { $_.Name -like 'TOP 5 VELVETVERSE_*' } | Sort-Object Name -Descending)
$source = if ($folders.Count -gt 0) { $folders[0].FullName } else { $Root }
Write-Host "Origem: $source"
$files = @(Get-ChildItem -LiteralPath $source -File | Where-Object { $_.Extension -match '^\.(mp3|m4a|aac|wav|flac)$' })
$selected = @()
foreach ($n in 1..5) {
  $matches = @($files | Where-Object { $_.BaseName -match ('^0?' + $n + '\s*[-_. ]') })
  if ($matches.Count -ne 1) { throw "Numero ${n}: encontrados $($matches.Count) ficheiros. Esperava exatamente um prefixo 0$n." }
  $selected += $matches[0]
}
Write-Host 'As cinco faixas foram identificadas pela numeracao original (01 a 05):'
$selected | ForEach-Object { Write-Host ('  ' + $_.Name) }
# Procurar FFmpeg nas localizacoes mais provaveis antes de descarregar.
$ffmpeg = $null
$command = Get-Command ffmpeg.exe -ErrorAction SilentlyContinue
if ($command) { $ffmpeg = $command.Source }
$candidates = @(
  'C:\ffmpeg\ffmpeg-9.0.2-essentials_build\bin\ffmpeg.exe',
  'C:\ffmpeg\bin\ffmpeg.exe',
  (Join-Path $PSScriptRoot 'ferramentas\ffmpeg.exe')
)
foreach ($candidate in $candidates) { if (!$ffmpeg -and (Test-Path -LiteralPath $candidate -PathType Leaf)) { $ffmpeg = $candidate } }
if (!$ffmpeg) {
  $localDir = Join-Path $PSScriptRoot 'ferramentas'
  $zip = Join-Path $localDir 'ffmpeg-release-essentials.zip'
  $extract = Join-Path $localDir 'extraido'
  New-Item -ItemType Directory -Path $localDir -Force | Out-Null
  $base = 'https://www.gyan.dev/ffmpeg/builds/'
  Write-Host 'FFmpeg nao encontrado. A descarregar o pacote oficial de distribuicao (aprox. 109 MB)...' -ForegroundColor Yellow
  # Download so e permitido do dominio HTTPS especificado. Integridade verificada por SHA256 oficial.
  [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
  $hashText = (Invoke-WebRequest -Uri ($base + 'ffmpeg-release-essentials.zip.sha256') -UseBasicParsing).Content
  if ($hashText -is [byte[]]) { $hashText = [Text.Encoding]::UTF8.GetString($hashText) }
  $expectedMatch = [regex]::Match([string]$hashText,'(?i)\b[a-f0-9]{64}\b')
  if (!$expectedMatch.Success) { throw 'Nao foi possivel verificar o SHA256 oficial. Operacao cancelada.' }
  $expected = $expectedMatch.Value.ToLowerInvariant()
  $download = $true
  if (Test-Path -LiteralPath $zip -PathType Leaf) {
    $actual = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
    if ($actual -eq $expected) { $download = $false }
  }
  if ($download) { Invoke-WebRequest -Uri ($base + 'ffmpeg-release-essentials.zip') -UseBasicParsing -OutFile $zip }
  $actual = (Get-FileHash -LiteralPath $zip -Algorithm SHA256).Hash.ToLowerInvariant()
  if ($actual -ne $expected) { Remove-Item -LiteralPath $zip -Force; throw 'Hash SHA256 incorreto; descarregamento cancelado.' }
  New-Item -ItemType Directory -Path $extract -Force | Out-Null
  Expand-Archive -LiteralPath $zip -DestinationPath $extract -Force
  $found = @(Get-ChildItem -LiteralPath $extract -Recurse -File -Filter 'ffmpeg.exe' | Where-Object { $_.Directory.Name -eq 'bin' })
  if ($found.Count -ne 1) { throw 'Nao foi encontrado o ffmpeg.exe no pacote verificado.' }
  $ffmpeg = $found[0].FullName
}
Write-Host "Conversor: $ffmpeg"
$out = Join-Path $source 'TOP5_EXCERTOS_30S'
New-Item -Path $out -ItemType Directory -Force | Out-Null
foreach ($i in 0..4) {
  $number = '{0:d2}' -f ($i + 1)
  $dest = Join-Path $out ($number + '.mp3')
  $tmp = Join-Path $out ($number + '.parcial.mp3')
  Write-Host ('A converter ' + $number + ': ' + $selected[$i].Name)
  & $ffmpeg -nostdin -hide_banner -loglevel error -y -i $selected[$i].FullName -t 30 -map 0:a:0 -vn -ac 2 -ar 44100 -codec:a libmp3lame -b:a 192k $tmp
  if ($LASTEXITCODE -ne 0 -or !(Test-Path -LiteralPath $tmp -PathType Leaf)) { throw "Falha ao criar o excerto $number" }
  Move-Item -LiteralPath $tmp -Destination $dest -Force
}
Write-Host ''
Write-Host 'CONCLUIDO: cinco excertos de 30 segundos criados.' -ForegroundColor Green
Write-Host "Pasta: $out" -ForegroundColor Cyan
Write-Host 'Nao foi publicado nada na Internet. Originais e RadioDJ inalterados.'
