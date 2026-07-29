package browser

import (
	"context"
	"fmt"

	"github.com/chromedp/chromedp"
)

const (
	targetURL              = "https://www.bankmanager.com.br/"
	passwordFieldSelector  = `#SenhaAcesso`
	togglePasswordSelector = `#visualizar_ocultar_senha`
)

// Session wraps a chromedp browser context pointed at the login page.
// No anti-automation evasion is applied: the field is filled directly,
// with no webdriver masking or humanized mouse/typing simulation.
type Session struct {
	ctx    context.Context
	cancel context.CancelFunc
}

// StartSession launches the browser (using execPath if non-empty, otherwise
// the system's installed Chrome/Edge) and navigates to the login page.
func StartSession(execPath string) (*Session, error) {
	opts := append([]chromedp.ExecAllocatorOption{}, chromedp.DefaultExecAllocatorOptions[:]...)
	// A automação precisa de uma janela visível (o funcionário confere a
	// tela antes de clicar em "Inserir senha"), então desligamos o modo
	// headless que o chromedp liga por padrão.
	opts = append(opts, chromedp.Flag("headless", false))
	if execPath != "" {
		opts = append(opts, chromedp.ExecPath(execPath))
	}

	allocCtx, allocCancel := chromedp.NewExecAllocator(context.Background(), opts...)
	ctx, ctxCancel := chromedp.NewContext(allocCtx)

	cancel := func() {
		ctxCancel()
		allocCancel()
	}

	if err := chromedp.Run(ctx,
		chromedp.Navigate(targetURL),
		chromedp.WaitVisible(passwordFieldSelector, chromedp.ByID),
		removeElement(togglePasswordSelector),
	); err != nil {
		cancel()
		return nil, fmt.Errorf("abrindo sessão: %w", err)
	}

	return &Session{ctx: ctx, cancel: cancel}, nil
}

func removeElement(selector string) chromedp.Action {
	js := fmt.Sprintf(`(() => { const el = document.querySelector(%q); if (el) el.remove(); })()`, selector)
	return chromedp.Evaluate(js, nil)
}

// FillPassword sets the password field's value directly, with no attempt to
// mimic human typing or evade bot detection.
func (s *Session) FillPassword(password string) error {
	return chromedp.Run(s.ctx,
		chromedp.WaitVisible(passwordFieldSelector, chromedp.ByID),
		chromedp.SetValue(passwordFieldSelector, password, chromedp.ByID),
	)
}

// Done returns a channel that closes when the browser session ends
// (window closed by the user or Close called).
func (s *Session) Done() <-chan struct{} {
	return s.ctx.Done()
}

func (s *Session) Close() {
	s.cancel()
}
