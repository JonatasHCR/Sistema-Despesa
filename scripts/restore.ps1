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
# ON_ERROR_STOP e --single-transaction andam juntos: sem eles o psql segue
# depois de cada erro e sai com codigo 0 tendo aplicado so parte do arquivo.
# Um restore assim, de um backup antigo, inseriu uma segunda linha em
# alembic_version (dois heads na mesma linhagem) e derrubou o backend.
Get-Content -Raw $fullPath | docker compose exec -T db psql `
  --set ON_ERROR_STOP=1 --single-transaction `
  -U $env:POSTGRES_USER -d $env:POSTGRES_DB

if ($LASTEXITCODE -eq 0) {
  Write-Host "Restore concluido com sucesso."
} else {
  Write-Host "ERRO: restore falhou (codigo $LASTEXITCODE)."
  exit $LASTEXITCODE
}
