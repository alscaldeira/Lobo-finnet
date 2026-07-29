# PowerShell script to download and package Chrome for Testing (Windows)

param(
    [string]$ChromeVersion = "130.0.6723.58"
)

$ErrorActionPreference = "Stop"

# Detectar arquitetura
if ([Environment]::Is64BitOperatingSystem) {
    $Platform = "win64"
    $OSArch = "windows-amd64"
} else {
    Write-Error "32-bit Windows is not supported"
    exit 1
}

Write-Host "Downloading Chrome for Testing ($Platform)..."

$DownloadUrl = "https://googlechromelabs.github.io/chrome-for-testing/download/win64/$ChromeVersion"
$AssetsDir = Join-Path $PSScriptRoot "..\internal\browser\assets\chromium"
$TempDir = New-Item -ItemType Directory -Path (Join-Path $env:TEMP "finnet_chrome_$$")

try {
    Write-Host "Downloading from: $DownloadUrl"
    $ZipPath = Join-Path $TempDir "chrome.zip"

    # Download usando ProgressPreference (sem barra de progresso verbosa)
    $ProgressPreference = 'SilentlyContinue'
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $ZipPath -UseBasicParsing
    $ProgressPreference = 'Continue'

    # Extrair
    $ExtractPath = Join-Path $TempDir "extracted"
    New-Item -ItemType Directory -Path $ExtractPath -Force | Out-Null
    Expand-Archive -Path $ZipPath -DestinationPath $ExtractPath -Force

    # Encontrar pasta chrome-win64
    $ChromeDir = Get-ChildItem -Path $ExtractPath -Directory -Filter "chrome-*" | Select-Object -First 1
    if (-not $ChromeDir) {
        Write-Error "Could not find extracted chrome directory"
        exit 1
    }

    # Criar diretório de assets
    $TargetDir = Join-Path $AssetsDir $OSArch
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null

    # Compactar
    Write-Host "Creating chromium.zip for $OSArch..."
    $ChromiumZip = Join-Path $TargetDir "chromium.zip"
    Compress-Archive -Path (Join-Path $ChromeDir.FullName "*") -DestinationPath $ChromiumZip -Force

    $Size = (Get-Item $ChromiumZip).Length / 1MB
    Write-Host "✓ Created $ChromiumZip ($([Math]::Round($Size, 1)) MB)"
}
finally {
    # Cleanup
    Remove-Item -Recurse -Force $TempDir
}
