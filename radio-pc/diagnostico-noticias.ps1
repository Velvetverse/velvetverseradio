# VelvetVerse Noticias - diagnóstico em modo LEITURA APENAS.
# Nao requer administrador, nao altera RadioDJ, MariaDB, tarefas Windows nem credenciais.
$ErrorActionPreference = 'Continue'
Write-Host '=== VelvetVerse Noticias - diagnostico (sem alteracoes) ==='
Write-Host ('Computador: ' + $env:COMPUTERNAME)
Write-Host ('Hora local: ' + (Get-Date).ToString('yyyy-MM-dd HH:mm:ss zzz'))
Write-Host ('Fuso Windows: ' + (Get-TimeZone).Id)
Write-Host ''
$commands = @('python', 'py', 'ffmpeg', 'ffprobe')
foreach ($cmd in $commands) {
    $item = Get-Command $cmd -ErrorAction SilentlyContinue
    if ($item) { Write-Host ('Comando ' + $cmd + ': OK') }
    else { Write-Host ('Comando ' + $cmd + ': NAO ENCONTRADO') }
}
$dirs = @(
  'C:\RadioWeb',
  'C:\VelvetVerseNoticias',
  'C:\VelvetVerseNoticias\Staging',
  'C:\Program Files\RadioDJ',
  'C:\RadioDJ',
  'D:\RadioDJ'
)
foreach ($dir in $dirs) {
  Write-Host ('Pasta ' + $dir + ': ' + $(if (Test-Path -LiteralPath $dir) {'EXISTE'} else {'NAO ENCONTRADA'}))
}
$envnames = @('R2_ACCOUNT_ID','R2_ACCESS_KEY_ID','R2_SECRET_ACCESS_KEY','R2_BUCKET')
foreach ($name in $envnames) {
  # Somente presenca: NAO mostrar valores nem copiar screenshots com credenciais.
  $v=[Environment]::GetEnvironmentVariable($name,'Process')
  Write-Host ($name + ': ' + $(if ($v) {'CONFIGURADA'} else {'NAO CONFIGURADA'}))
}
Write-Host ''
Write-Host 'Fim. Nenhum ficheiro, agendamento ou programa foi alterado.'
