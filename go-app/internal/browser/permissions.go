package browser

import (
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
)

// applyExecutablePermissions mirrors the original Python bootstrap's
// `chmod -R 755` (+ `xattr -cr` on macOS, to clear Gatekeeper quarantine)
// applied to the whole extracted Chromium tree.
func applyExecutablePermissions(root string) error {
	err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.Mode()&os.ModeSymlink != 0 {
			return nil
		}
		return os.Chmod(path, 0o755)
	})
	if err != nil {
		return err
	}

	if runtime.GOOS == "darwin" {
		_ = exec.Command("xattr", "-cr", root).Run()
	}
	return nil
}
