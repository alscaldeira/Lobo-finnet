package browser

import (
	"os"
	"os/exec"
	"path/filepath"
	"runtime"
)

// candidatePaths lists, per OS, the well-known install locations of
// Chromium-based browsers, in order of preference. chromedp's own
// detection only checks Chrome/Chromium on macOS, so we extend it to also
// find Edge and Brave — common on machines where Chrome isn't installed.
func candidatePaths() []string {
	switch runtime.GOOS {
	case "darwin":
		return []string{
			"/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
			"/Applications/Chromium.app/Contents/MacOS/Chromium",
			"/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
			"/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
		}
	case "windows":
		userProfile := os.Getenv("USERPROFILE")
		return []string{
			`C:\Program Files\Google\Chrome\Application\chrome.exe`,
			`C:\Program Files (x86)\Google\Chrome\Application\chrome.exe`,
			filepath.Join(userProfile, `AppData\Local\Google\Chrome\Application\chrome.exe`),
			`C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe`,
			`C:\Program Files\Microsoft\Edge\Application\msedge.exe`,
			`C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe`,
			filepath.Join(userProfile, `AppData\Local\BraveSoftware\Brave-Browser\Application\brave.exe`),
		}
	default: // linux
		return []string{
			"google-chrome",
			"google-chrome-stable",
			"chromium",
			"chromium-browser",
			"microsoft-edge",
			"brave-browser",
		}
	}
}

// detectSystemBrowser returns the path to an installed Chromium-based
// browser (Chrome, Edge, Brave or Chromium), or "" if none was found.
func detectSystemBrowser() string {
	for _, path := range candidatePaths() {
		if filepath.IsAbs(path) {
			if info, err := os.Stat(path); err == nil && !info.IsDir() {
				return path
			}
			continue
		}
		if found, err := exec.LookPath(path); err == nil {
			return found
		}
	}
	return ""
}
