# Top 5 VelvetVerse - prepara 5 excertos MP3 de 30 segundos SEM publicar online.
# Os ficheiros locais continuam privados. Só publicar após confirmação dos direitos.
param([string]$Root = 'D:\mp3\Top 5 Velvetverse\TOP5_VELVETVERSE_V3')
$ErrorActionPreference='Stop'
$ffmpeg='C:\ffmpeg\ffmpeg-9.0.2-essentials_build\bin\ffmpeg.exe'
if (!(Test-Path -LiteralPath $ffmpeg)){throw "FFmpeg nao encontrado: $ffmpeg"}
if (!(Test-Path -LiteralPath $Root)){throw "Pasta de origem nao encontrada: $Root"}
$folders = Get-ChildItem -LiteralPath $Root -Directory | Where-Object Name -Like 'TOP 5 VELVETVERSE_*' | Sort-Object Name -Descending
$source = if($folders.Count){$folders[0].FullName}else{$Root}
$files = @(Get-ChildItem -LiteralPath $source -Recurse -File | Where-Object { $_.Extension -match '^\.(mp3|m4a|aac|wav|flac)$' })
$tracks = @(
  @{No='01';Title='Sou Camionista Madrugador';Patterns=@('camionista','madrugador')},
  @{No='02';Title='Self Control';Patterns=@('self control','self_control','self-control')},
  @{No='03';Title='Goteira';Patterns=@('goteira')},
  @{No='04';Title='Groove Bom';Patterns=@('groove bom','groove_bom','groove-bom')},
  @{No='05';Title='Deriram';Patterns=@('deriram')}
)
$out = Join-Path $source 'TOP5_EXCERTOS_30S'
New-Item -ItemType Directory -Force -Path $out | Out-Null
$used = @()
foreach($song in $tracks){
  $matches = @($files | Where-Object {
    $name = $_.BaseName.ToLowerInvariant()
    $ok = $false
    foreach($pattern in $song.Patterns){if($name.Contains($pattern)){$ok=$true;break}}
    $ok -and ($used -notcontains $_.FullName)
  })
  if($matches.Count -ne 1){throw "Faixa '$($song.Title)': encontrados $($matches.Count) ficheiros. Nao vou adivinhar. Verifique os nomes no BAT V3."}
  $file=$matches[0];$used+= $file.FullName
  $dest=Join-Path $out ($song.No+'.mp3')
  Write-Host ("A preparar {0}: {1}" -f $song.No,$file.Name)
  & $ffmpeg -hide_banner -loglevel error -y -i $file.FullName -t 30 -map 0:a:0 -vn -ac 2 -ar 44100 -codec:a libmp3lame -b:a 192k $dest
  if($LASTEXITCODE -ne 0 -or !(Test-Path -LiteralPath $dest)){throw "Erro ao criar $dest"}
}
Write-Host ''
Write-Host 'CONCLUIDO: cinco excertos de 30 segundos em:' -ForegroundColor Green
Write-Host $out -ForegroundColor Cyan
Write-Host 'Nenhum ficheiro foi enviado para a Internet.'
