# IMPORTANTE: correr no mesmo utilizador Windows que executará a rececao agendada.
# Pede credenciais de leitura e guarda via DPAPI (Export-Clixml) para este utilizador neste PC.
# Não mostra chave secreta nem altera RadioDJ, nem se liga à internet.
$ErrorActionPreference = 'Stop'
$root='C:\VelvetVerseNoticias'
New-Item -Path $root -ItemType Directory -Force | Out-Null
$account=(Read-Host 'Cloudflare R2 Account ID (32 caracteres)').Trim()
if($account -notmatch '^[0-9a-fA-F]{32}$'){throw 'Account ID invalido'}
$access=(Read-Host 'RadioDJ Download - Access Key ID').Trim()
if(-not $access){throw 'Access Key ID vazio'}
$secret=Read-Host 'RadioDJ Download - Secret Access Key (oculto)' -AsSecureString
if($secret.Length -eq 0){throw 'Secret Access Key vazio'}
$cred=New-Object System.Management.Automation.PSCredential ($access,$secret)
$secure=Join-Path $root 'r2-download-credential.xml'
$meta=Join-Path $root 'r2-download-account.txt'
$cred | Export-Clixml -LiteralPath $secure
[System.IO.File]::WriteAllText($meta, $account, [System.Text.UTF8Encoding]::new($false))
# Garantir que a conversao é legível pelo utilizador atual antes de terminar.
$check=Import-Clixml -LiteralPath $secure
if($check -isnot [pscredential] -or $check.UserName -ne $access){
    throw 'Verificacao da credencial cifrada falhou'
}
Write-Host 'SUCESSO: dados protegidos para este utilizador Windows. Nenhum valor secreto foi apresentado.'
Write-Host 'IMPORTANTE: apagar manualmente o ficheiro antigo velvetverse-r2-config.ps1 apos testar a rececao.'
