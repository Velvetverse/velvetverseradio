# Recebe a edicao aprovada do R2 para STAGING, sem tocar na radio.
# Preparado para execucao automatica pelo Agendador de Tarefas Windows.
# Necessita de Python+boto3 e credenciais R2 no ambiente do utilizador Windows.
$ErrorActionPreference = 'Stop'
Set-Location (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$names=@('R2_ACCOUNT_ID','R2_ACCESS_KEY_ID','R2_SECRET_ACCESS_KEY','R2_BUCKET')
foreach($name in $names){
    if(-not [Environment]::GetEnvironmentVariable($name,'Process')){
        Write-Error "Falta variavel R2: $name (valor nao sera apresentado)."
        exit 2
    }
}
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
