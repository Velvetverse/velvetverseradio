# Recebe a edicao aprovada do R2 para STAGING, sem tocar na radio.
# Preparado para execucao automatica pelo Agendador de Tarefas Windows.
# Necessita de Python+boto3 e credenciais R2 no ambiente do utilizador Windows.
$ErrorActionPreference = 'Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
# As credenciais são guardadas com DPAPI, acessíveis só ao mesmo utilizador Windows.
$cfgRoot='C:\VelvetVerseNoticias'
$securePath=Join-Path $cfgRoot 'r2-download-credential.xml'
$metaPath=Join-Path $cfgRoot 'r2-download-account.txt'
if(-not (Test-Path -LiteralPath $securePath) -or -not (Test-Path -LiteralPath $metaPath)){
    Write-Error 'Falta configuração DPAPI. Executar configurar-r2-seguro.ps1 primeiro.'
    exit 2
}
$account=(Get-Content -LiteralPath $metaPath -Raw -Encoding UTF8).Trim()
if($account -notmatch '^[a-fA-F0-9]{32}$'){ Write-Error 'Account ID inválido'; exit 2 }
$cred=Import-Clixml -LiteralPath $securePath
if($cred -isnot [pscredential]){Write-Error 'Credencial cifrada inválida'; exit 2}
$env:R2_ACCOUNT_ID=$account
$env:R2_ACCESS_KEY_ID=$cred.UserName
$env:R2_SECRET_ACCESS_KEY=$cred.GetNetworkCredential().Password
$env:R2_BUCKET='velvetverse-noticias'
$py=Get-Command py -ErrorAction SilentlyContinue
if($py){ $program='py'; $prefix=@('-3') }
else {
    $py=Get-Command python -ErrorAction SilentlyContinue
    if(-not $py){ Write-Error 'Python nao encontrado'; exit 2 }
    $program='python'; $prefix=@()
}
$destination='C:\VelvetVerseNoticias\Staging'
$cmdargs=@($prefix)+@('scripts/velvetverse_noticias_transferencia.py','receive','--destination',$destination)
& $program @cmdargs
if($LASTEXITCODE -ne 0){ exit $LASTEXITCODE }
Write-Output 'Rececao de staging concluida. Nenhum evento RadioDJ foi alterado.'
exit 0
