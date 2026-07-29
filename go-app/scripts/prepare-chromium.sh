#!/bin/bash
# Baixa Chrome for Testing (portátil) para a plataforma atual e empacota em zip

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ASSETS_DIR="$REPO_ROOT/internal/browser/assets/chromium"

# Detectar plataforma
if [[ "$OSTYPE" == "darwin"* ]]; then
  if [[ "$(uname -m)" == "arm64" ]]; then
    PLATFORM="mac-arm64"
    OS_ARCH="darwin-arm64"
  else
    PLATFORM="mac-x64"
    OS_ARCH="darwin-amd64"
  fi
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
  PLATFORM="win64"
  OS_ARCH="windows-amd64"
else
  echo "Platform not supported for Chromium embedding"
  exit 1
fi

echo "Downloading Chrome for Testing ($PLATFORM)..."

# Versão fixa do Chrome for Testing (você pode atualizar isso)
CHROME_VERSION="130.0.6723.58"
DOWNLOAD_URL="https://googlechromelabs.github.io/chrome-for-testing/download/linux/amd64/${CHROME_VERSION}"

# Para macOS e Windows, ajustar URL
if [[ "$OSTYPE" == "darwin"* ]]; then
  DOWNLOAD_URL="https://googlechromelabs.github.io/chrome-for-testing/download/mac/${PLATFORM}/${CHROME_VERSION}"
elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "win32" ]]; then
  DOWNLOAD_URL="https://googlechromelabs.github.io/chrome-for-testing/download/win64/${CHROME_VERSION}"
fi

TEMP_DIR=$(mktemp -d)
trap "rm -rf $TEMP_DIR" EXIT

echo "Downloading from: $DOWNLOAD_URL"
curl -# -L "$DOWNLOAD_URL" -o "$TEMP_DIR/chrome.zip"

# Extrair
mkdir -p "$TEMP_DIR/extracted"
unzip -q "$TEMP_DIR/chrome.zip" -d "$TEMP_DIR/extracted"

# Encontrar a pasta chrome-mac-arm64, chrome-win64, etc
CHROME_DIR=$(find "$TEMP_DIR/extracted" -maxdepth 1 -type d -name "chrome-*" | head -1)
if [ -z "$CHROME_DIR" ]; then
  echo "Error: Could not find extracted chrome directory"
  exit 1
fi

# Criar diretório de assets
mkdir -p "$ASSETS_DIR/$OS_ARCH"

# Compactar (preservando symlinks no macOS)
echo "Creating chromium.zip for $OS_ARCH..."
cd "$CHROME_DIR"
if [[ "$OSTYPE" == "darwin"* ]]; then
  zip -ry -X "$ASSETS_DIR/$OS_ARCH/chromium.zip" . -x ".DS_Store" > /dev/null
else
  # Windows: usar PowerShell Compress-Archive
  powershell -Command "Compress-Archive -Path * -DestinationPath '$ASSETS_DIR/$OS_ARCH/chromium.zip' -Force" 2>/dev/null || {
    # Fallback para zip se PowerShell falhar
    zip -r -X "$ASSETS_DIR/$OS_ARCH/chromium.zip" . -x ".DS_Store"
  }
fi

echo "✓ Created $ASSETS_DIR/$OS_ARCH/chromium.zip ($(du -sh "$ASSETS_DIR/$OS_ARCH/chromium.zip" | cut -f1))"
