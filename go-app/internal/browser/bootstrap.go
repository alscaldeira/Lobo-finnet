package browser

import (
	"archive/zip"
	"bytes"
	"embed"
	"fmt"
	"io"
	"os"
	"path/filepath"
	"runtime"
)

//go:embed all:assets/chromium
var embeddedAssets embed.FS

const embeddedRoot = "assets/chromium"

// NOTE: Chromium binaries (.zip files) are not committed to git due to size
// constraints (>100MB). They may be provided in assets/chromium/{os}-{arch}/
// for offline deployments, but if absent, the system falls back to Chrome/Edge
// already installed on the machine. This keeps deployments flexible and the
// repo size manageable.

// binaryRelPath maps GOOS-GOARCH to the executable's path inside its
// platform's packaged Chromium zip (see assets/chromium/README.md).
var binaryRelPath = map[string]string{
	"darwin-arm64":  "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
	"darwin-amd64":  "Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing",
	"windows-amd64": "chrome.exe",
	"linux-amd64":   "chrome",
}

// Bootstrap extracts the Chromium build embedded for the current OS/arch
// into a temp directory and returns its executable path. If no build was
// embedded for this platform, it returns an empty path so the caller falls
// back to a Chrome/Edge already installed on the machine.
func Bootstrap() (string, error) {
	platformKey := fmt.Sprintf("%s-%s", runtime.GOOS, runtime.GOARCH)
	relBinary, ok := binaryRelPath[platformKey]
	if !ok {
		return "", nil
	}

	zipEmbeddedPath := filepath.ToSlash(filepath.Join(embeddedRoot, platformKey, "chromium.zip"))
	zipData, err := embeddedAssets.ReadFile(zipEmbeddedPath)
	if err != nil {
		// Nada embutido para esta plataforma: usa o Chrome/Edge instalado.
		return "", nil
	}

	extractDir := filepath.Join(os.TempDir(), "finnet_browser_v1", platformKey)
	destBinary := filepath.Join(extractDir, filepath.FromSlash(relBinary))

	if _, err := os.Stat(destBinary); err == nil {
		return destBinary, nil
	}

	if err := os.MkdirAll(extractDir, 0o755); err != nil {
		return "", fmt.Errorf("criando diretório de extração: %w", err)
	}

	if err := extractZip(zipData, extractDir); err != nil {
		return "", fmt.Errorf("extraindo Chromium: %w", err)
	}

	if err := applyExecutablePermissions(extractDir); err != nil {
		return "", err
	}

	if _, err := os.Stat(destBinary); err != nil {
		return "", fmt.Errorf("binário do Chromium não encontrado após extração: %w", err)
	}

	return destBinary, nil
}

// extractZip extracts a zip archive to destDir, preserving symlinks (needed
// for the .app bundle structure on macOS) and original file modes.
func extractZip(zipData []byte, destDir string) error {
	reader, err := zip.NewReader(bytes.NewReader(zipData), int64(len(zipData)))
	if err != nil {
		return err
	}

	for _, entry := range reader.File {
		targetPath := filepath.Join(destDir, filepath.FromSlash(entry.Name))

		if entry.FileInfo().IsDir() {
			if err := os.MkdirAll(targetPath, 0o755); err != nil {
				return err
			}
			continue
		}

		if err := os.MkdirAll(filepath.Dir(targetPath), 0o755); err != nil {
			return err
		}

		rc, err := entry.Open()
		if err != nil {
			return err
		}

		if entry.Mode()&os.ModeSymlink != 0 {
			linkTarget, readErr := io.ReadAll(rc)
			rc.Close()
			if readErr != nil {
				return readErr
			}
			_ = os.Remove(targetPath)
			if err := os.Symlink(string(linkTarget), targetPath); err != nil {
				return err
			}
			continue
		}

		out, err := os.OpenFile(targetPath, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0o755)
		if err != nil {
			rc.Close()
			return err
		}
		_, copyErr := io.Copy(out, rc)
		rc.Close()
		out.Close()
		if copyErr != nil {
			return copyErr
		}
	}

	return nil
}
