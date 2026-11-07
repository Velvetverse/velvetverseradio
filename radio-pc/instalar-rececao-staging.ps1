# CRIA UMA TAREFA WINDOWS DESATIVADA; nunca instala evento RadioDJ.
# Executar no Windows apenas depois de verificar o acesso privado ao R2.
# Esta tarefa apenas descarrega MP3s para staging (sem os emitir).
$ErrorActionPreference='Stop'
$name='VelvetVerse Noticias - Rececao Staging'
$script=(Resolve-Path (Join-Path $PSScriptRoot 'receber-noticias-staging.ps1')).Path
$exe=(Get-Command powershell.exe -ErrorAction Stop).Source
$action=New-ScheduledTaskAction -Execute $exe -Argument ('-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "'+$script+'"')
$trigger=New-ScheduledTaskTrigger -Weekly -DaysOfWeek Sunday -At '11:30AM'
$settings=New-ScheduledTaskSettingsSet -StartWhenAvailable -ExecutionTimeLimit (New-TimeSpan -Minutes 15) -MultipleInstances IgnoreNew
$principal=New-ScheduledTaskPrincipal -UserId ([Security.Principal.WindowsIdentity]::GetCurrent().Name) -LogonType Interactive -RunLevel LeastPrivilege
Register-ScheduledTask -TaskName $name -Action $action -Trigger $trigger -Settings $settings -Principal $principal -Force | Out-Null
Disable-ScheduledTask -TaskName $name | Out-Null
Write-Host "Tarefa criada DESATIVADA: $name (domingo 11:30, hora local do Windows)"
Write-Host 'NAO ativa-la antes de confirmar fuso America/Toronto, credenciais, rececao e aprovacao editorial.'
Write-Host 'O RadioDJ nao foi alterado.'
