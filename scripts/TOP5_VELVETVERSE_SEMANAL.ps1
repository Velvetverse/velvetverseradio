param([Parameter(Mandatory=$true)][string]$Csv,[string]$MusicRoot='D:\mp3')
$ErrorActionPreference='Stop'
function N([string]$s){
 $s=[regex]::Replace($s,'\s*\|\s*(VEVO|Official Video|Video|Audio)\s*$','',[Text.RegularExpressions.RegexOptions]::IgnoreCase)
 $t=$s.Normalize([Text.NormalizationForm]::FormD)
 $b=New-Object Text.StringBuilder
 foreach($c in $t.ToCharArray()){if([Globalization.CharUnicodeInfo]::GetUnicodeCategory($c) -ne 'NonSpacingMark'){[void]$b.Append($c)}}
 return ([regex]::Replace($b.ToString().ToLowerInvariant(),'[^a-z0-9]+',' ')).Trim()
}
if(!(Test-Path -LiteralPath $Csv -PathType Leaf)){throw 'CSV nao encontrado'}
if(!(Test-Path -LiteralPath $MusicRoot -PathType Container)){throw 'Biblioteca D: nao encontrada'}
$first=Get-Content -LiteralPath $Csv -TotalCount 1
$sep=if($first.Contains(';')){';'}elseif($first.Contains([char]9)){[char]9}else{','}
$rows=@(Import-Csv -LiteralPath $Csv -Delimiter $sep -Encoding UTF8)
if(!$rows.Count){throw 'CSV vazio'}
$cols=@($rows[0].PSObject.Properties.Name)
function Col([string[]]$names){
 $found=@($cols|Where-Object {$names -contains $_.ToLowerInvariant().Trim()})
 if($found.Count -ne 1){throw "Coluna ausente: $($names -join ',')"}
 return $found[0]
}
$titleCol=Col @('track','track title','song','song title','title')
$artistCol=Col @('artist','artista')
$playsCol=Col @('times played','plays','playbacks','play count')
$technical='(?i)(jingle|intro|sweeper|sweep |vinheta|slogan|station id|promo|sinal horario|velvet after dark)'
$agg=@{}
foreach($r in $rows){
 $title=([string]$r.$titleCol).Trim();$artist=([string]$r.$artistCol).Trim()
 if(!$title -or !$artist -or $title -match $technical -or $artist -match '^(?i:cmli|radiodj|unknown artist)$'){continue}
 [int]$count=0
 if(![int]::TryParse(([string]$r.$playsCol).Trim(),[ref]$count)){throw 'Contagem invalida'}
 if($count -le 0){continue}
 $title=[regex]::Replace($title,'\s*\|\s*(VEVO|Official Video|Video|Audio)\s*$','',[Text.RegularExpressions.RegexOptions]::IgnoreCase).Trim()
 $key=(N $title)+'|'+(N $artist)
 if(!$agg.ContainsKey($key)){$agg[$key]=[pscustomobject]@{title=$title;artist=$artist;plays=0}}
 $agg[$key].plays+=$count
}
$all=@($agg.Values|Sort-Object @{Expression='plays';Descending=$true},artist,title)
if($all.Count -lt 5){throw 'Menos de 5 musicas validas'}
if($all.Count -gt 5 -and $all[4].plays -eq $all[5].plays){throw 'Empate no 5 lugar: confirmar manualmente'}
$top=@($all|Select-Object -First 5)
# So converter depois de TODAS as cinco faixas terem sido encontradas inequivocamente.
$files=@(Get-ChildItem -LiteralPath $MusicRoot -Recurse -File -ErrorAction SilentlyContinue|Where-Object {$_.Extension -match '^\.(mp3|m4a|wav|flac|aac)$' -and $_.FullName -notmatch 'TOP5_EXCERTOS_30S|SEMANAIS_CANDIDATOS'})
$matches=@()
foreach($song in $top){
 $t=N $song.title;$a=N $song.artist
 $found=@($files|Where-Object {$b=N $_.BaseName;$b.Contains($t) -and $b.Contains($a)})
 if($found.Count -ne 1){throw "Nao foi encontrada uma correspondencia unica para $($song.title) de $($song.artist): $($found.Count). Nenhum audio alterado."}
 $matches+=,$found[0]
}
$ff=Get-Command ffmpeg.exe -ErrorAction SilentlyContinue
$ffmpeg=if($ff){$ff.Source}else{$null}
if(!$ffmpeg){
 $folders=@($PSScriptRoot,(Join-Path $env:USERPROFILE 'OneDrive\Desktop\TOP5-30S'),(Join-Path $env:USERPROFILE 'Desktop\TOP5-30S'))
 foreach($folder in $folders){
  if(!(Test-Path -LiteralPath $folder)){continue}
  $found=@(Get-ChildItem -LiteralPath $folder -Recurse -File -Filter 'ffmpeg.exe' -ErrorAction SilentlyContinue)
  if($found.Count){$ffmpeg=$found[0].FullName;break}
 }
}
if(!$ffmpeg){throw 'Conversor ffmpeg.exe nao encontrado nas pastas da preparacao anterior.'}
$date=(Get-Date).ToString('yyyy-MM-dd')
$out=Join-Path $MusicRoot ('Top 5 Velvetverse\SEMANAIS_CANDIDATOS\'+$date)
if(Test-Path -LiteralPath $out){throw "Edicao existente, nao substituir: $out"}
New-Item -ItemType Directory -Force -Path $out|Out-Null
$tracks=@()
for($i=0;$i -lt 5;$i++){
 $num='{0:d2}' -f ($i+1)
 $dest=Join-Path $out ($num+'.mp3')
 & $ffmpeg -nostdin -hide_banner -loglevel error -y -i $matches[$i].FullName -t 30 -map 0:a:0 -vn -ac 2 -ar 44100 -c:a libmp3lame -b:a 192k $dest
 if($LASTEXITCODE -ne 0 -or !(Test-Path -LiteralPath $dest)){throw "Conversao falhou: $num"}
 $tracks+=@{rank=$i+1;id='vv-'+$date+'-'+($i+1);title=$top[$i].title;artist=$top[$i].artist;playbacks=$top[$i].plays;artwork='';preview=''}
}
@{edition='velvetverse-'+$date;week=$date;source='RCast CSV - periodo por confirmar';status='provisional';voting_enabled=$false;preview_permission_confirmed=$false;previews_seconds=30;songs=$tracks}|ConvertTo-Json -Depth 7|Set-Content -LiteralPath (Join-Path $out 'top5-candidato.json') -Encoding UTF8
Write-Host "SUCESSO: edicao candidata em $out" -ForegroundColor Green
Write-Host 'Nenhum ficheiro publicado. RadioDJ, RCast e votos inalterados.'
