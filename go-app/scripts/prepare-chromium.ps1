# Downloads Chrome for Testing (portable) from Google's official CDN and
# packages it into internal/browser/assets/chromium/windows-amd64/chromium.zip
# to be embedded in the binary via go:embed.

$ErrorActionPreference = "Stop"
$ProgressPreference = "SilentlyContinue"

$VersionsJsonUrl = "https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json"
$CftPlatform = "win64"
$OSArch = "windows-amd64"

$AssetsDir = Join-Path $PSScriptRoot "..\internal\browser\assets\chromium"
$TempDir = Join-Path $env:TEMP ("finnet_chrome_" + [guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $TempDir -Force | Out-Null

try {
    Write-Host "Fetching Chrome for Testing stable version..."
    $VersionsJson = Invoke-RestMethod -Uri $VersionsJsonUrl -UseBasicParsing

    $Download = $VersionsJson.channels.Stable.downloads.chrome | Where-Object { $_.platform -eq $CftPlatform } | Select-Object -First 1
    if (-not $Download) {
        Write-Error "Could not find download URL for platform $CftPlatform"
        exit 1
    }
    $DownloadUrl = $Download.url

    Write-Host "Downloading from: $DownloadUrl"
    $ZipPath = Join-Path $TempDir "chrome.zip"
    Invoke-WebRequest -Uri $DownloadUrl -OutFile $ZipPath -UseBasicParsing

    $ExtractPath = Join-Path $TempDir "extracted"
    New-Item -ItemType Directory -Path $ExtractPath -Force | Out-Null
    Expand-Archive -Path $ZipPath -DestinationPath $ExtractPath -Force

    $ChromeDir = Get-ChildItem -Path $ExtractPath -Directory -Filter "chrome-*" | Select-Object -First 1
    if (-not $ChromeDir) {
        Write-Error "chrome-* folder not found after extraction"
        exit 1
    }

    $TargetDir = Join-Path $AssetsDir $OSArch
    New-Item -ItemType Directory -Path $TargetDir -Force | Out-Null

    Write-Host "Packaging for $OSArch..."
    $ChromiumZip = Join-Path $TargetDir "chromium.zip"
    if (Test-Path $ChromiumZip) {
        Remove-Item $ChromiumZip -Force
    }
    Compress-Archive -Path (Join-Path $ChromeDir.FullName "*") -DestinationPath $ChromiumZip -CompressionLevel Optimal

    $SizeMB = [Math]::Round((Get-Item $ChromiumZip).Length / 1MB, 1)
    Write-Host "Done: $ChromiumZip - $SizeMB MB"
}
finally {
    Remove-Item -Recurse -Force $TempDir -ErrorAction SilentlyContinue
}
