# Gera o despesa-agent.exe (rode na máquina de desenvolvimento, com Python 3.11+).
# Uso: powershell -ExecutionPolicy Bypass -File build.ps1

python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt pyinstaller

.\.venv\Scripts\pyinstaller.exe --onefile --noconsole `
  --collect-all win11toast `
  --name despesa-agent agent.py

Write-Host ""
Write-Host "Pronto: dist\despesa-agent.exe"
Write-Host "Copie o .exe + config.json para a pasta de instalacao em cada maquina."
