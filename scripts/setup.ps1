param(
    [switch]$Dev,
    [switch]$GDrive
)

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "=== FIAP Class Recorder | Setup Windows ===" -ForegroundColor Cyan
Write-Host ""

if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python não encontrado no PATH." -ForegroundColor Red
    Write-Host "Instale o Python 3.10+ e marque a opção de adicionar ao PATH." -ForegroundColor Yellow
    exit 1
}

if (-not (Get-Command ffmpeg -ErrorAction SilentlyContinue)) {
    Write-Host "FFmpeg não encontrado no PATH." -ForegroundColor Yellow
    Write-Host "O projeto até instala o ambiente, mas a gravação só funcionará após configurar o FFmpeg." -ForegroundColor Yellow
}

if (-not (Test-Path ".venv")) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Green
    python -m venv .venv
} else {
    Write-Host "Ambiente virtual .venv já existe." -ForegroundColor DarkYellow
}

Write-Host "Ativando ambiente virtual..." -ForegroundColor Green
& .\.venv\Scripts\Activate.ps1

Write-Host "Atualizando pip..." -ForegroundColor Green
python -m pip install --upgrade pip

if ($Dev) {
    Write-Host "Instalando dependências de desenvolvimento..." -ForegroundColor Green
    pip install -e ".[dev]"
}
elseif ($GDrive) {
    Write-Host "Instalando runtime com Google Drive..." -ForegroundColor Green
    pip install -e ".[gdrive]"
}
else {
    Write-Host "Instalando runtime básico..." -ForegroundColor Green
    pip install -e .
}

if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host ".env criado a partir de .env.example" -ForegroundColor Green
    } else {
        Write-Host ".env.example não encontrado. Crie manualmente o .env." -ForegroundColor Yellow
    }
} else {
    Write-Host ".env já existe." -ForegroundColor DarkYellow
}

Write-Host ""
Write-Host "Setup concluído." -ForegroundColor Cyan
Write-Host ""
Write-Host "Próximos passos:" -ForegroundColor White
Write-Host "1. Ajuste o arquivo .env" -ForegroundColor Gray
Write-Host "2. Verifique se o FFmpeg está no PATH" -ForegroundColor Gray
Write-Host "3. Teste as janelas com: fiap-recorder --list-windows" -ForegroundColor Gray
Write-Host "4. Rode a gravação com: fiap-recorder" -ForegroundColor Gray
Write-Host ""
