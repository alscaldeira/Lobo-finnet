#!/bin/bash
# Baixa Chrome for Testing (portátil) da CDN oficial do Google e empacota
# em internal/browser/assets/chromium/{os}-{arch}/chromium.zip para ser
# embutido no binário via go:embed.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
ASSETS_DIR="$REPO_ROOT/internal/browser/assets/chromium"

VERSIONS_JSON_URL="https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"

# Arquitetura alvo: pode ser passada como $1 (arm64|amd64) para permitir
# cross-compile no CI (ex: macos-latest é arm64, mas também compilamos
# para amd64). Sem argumento, usa a arquitetura do host atual.
TARGET_ARCH="${1:-$(uname -m)}"
case "$TARGET_ARCH" in
  arm64) TARGET_ARCH="arm64" ;;
  amd64|x86_64) TARGET_ARCH="amd64" ;;
  *) echo "Arquitetura não suportada: $TARGET_ARCH" >&2; exit 1 ;;
esac

if [[ "$OSTYPE" == "darwin"* ]]; then
  if [[ "$TARGET_ARCH" == "arm64" ]]; then
    CFT_PLATFORM="mac-arm64"
    OS_ARCH="darwin-arm64"
  else
    CFT_PLATFORM="mac-x64"
    OS_ARCH="darwin-amd64"
  fi
else
  echo "Este script é para macOS. Use prepare-chromium.ps1 no Windows." >&2
  exit 1
fi

echo "Consultando versão estável do Chrome for Testing..."
curl -sS "$VERSIONS_JSON_URL" -o /tmp/cft-versions.json

DOWNLOAD_URL=$(python3 -c "
import json
d = json.load(open('/tmp/cft-versions.json'))
downloads = d['channels']['Stable']['downloads']['chrome']
for entry in downloads:
    if entry['platform'] == '$CFT_PLATFORM':
        print(entry['url'])
        break
")

if [ -z "$DOWNLOAD_URL" ]; then
  echo "Não foi possível encontrar a URL de download para $CFT_PLATFORM" >&2
  exit 1
fi

echo "Baixando de: $DOWNLOAD_URL"

TEMP_DIR=$(mktemp -d)
trap 'rm -rf "$TEMP_DIR"' EXIT

curl -# -L "$DOWNLOAD_URL" -o "$TEMP_DIR/chrome.zip"

mkdir -p "$TEMP_DIR/extracted"
unzip -q "$TEMP_DIR/chrome.zip" -d "$TEMP_DIR/extracted"

CHROME_DIR=$(find "$TEMP_DIR/extracted" -maxdepth 1 -type d -name "chrome-*" | head -1)
if [ -z "$CHROME_DIR" ]; then
  echo "Erro: pasta chrome-* não encontrada após extração" >&2
  exit 1
fi

mkdir -p "$ASSETS_DIR/$OS_ARCH"

echo "Compactando para $OS_ARCH (preservando symlinks)..."
(cd "$CHROME_DIR" && zip -ry -X "$ASSETS_DIR/$OS_ARCH/chromium.zip" . -x ".DS_Store" > /dev/null)

echo "✓ Criado $ASSETS_DIR/$OS_ARCH/chromium.zip ($(du -sh "$ASSETS_DIR/$OS_ARCH/chromium.zip" | cut -f1))"
