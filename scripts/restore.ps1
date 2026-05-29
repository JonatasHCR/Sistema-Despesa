param(
  [Parameter(Mandatory=$true, HelpMessage="Caminho para o arquivo .sql de backup")]
  [string]$BackupFile
)

$fullPath = Resolve-Path $BackupFile -ErrorAction Stop

Write-Host ""
Write-Host "Arquivo : $fullPath"
Write-Host "Banco   : $env:POSTGRES_DB"
Write-Host ""
Write-Host "ATENCAO: os dados atuais serao substituidos. Continuar? (s/N): " -NoNewline
$confirm = Read-Host

if ($confirm -ne 's') {
  Write-Host "Cancelado."
  exit 0
}

Write-Host "Restaurando..."
Get-Content $fullPath | docker compose exec -T db psql -U $env:POSTGRES_USER $env:POSTGRES_DB

if ($LASTEXITCODE -eq 0) {
  Write-Host "Restore concluido com sucesso."
} else {
  Write-Host "ERRO: restore falhou (codigo $LASTEXITCODE)."
  exit $LASTEXITCODE
}
