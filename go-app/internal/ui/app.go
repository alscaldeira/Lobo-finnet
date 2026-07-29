// Package ui reproduces the original Tkinter window: a small dialog with
// "Entrar", "Cadastrar nova senha" and, once a session starts, "Inserir
// senha".
package ui

import (
	"fmt"

	"fyne.io/fyne/v2"
	"fyne.io/fyne/v2/app"
	"fyne.io/fyne/v2/container"
	"fyne.io/fyne/v2/dialog"
	"fyne.io/fyne/v2/widget"

	"finnet/internal/browser"
	"finnet/internal/crypto"
)

type App struct {
	fyneApp fyne.App
	window  fyne.Window
	vault   *crypto.Vault

	session *browser.Session
}

func New(vault *crypto.Vault) *App {
	fyneApp := app.NewWithID("br.com.finnet.bankmanager")
	window := fyneApp.NewWindow("Acesso ao Bankmanager")
	window.Resize(fyne.NewSize(300, 150))
	window.SetFixedSize(true)

	return &App{fyneApp: fyneApp, window: window, vault: vault}
}

func (a *App) Run() {
	a.showMainScreen()
	a.window.ShowAndRun()
}

func (a *App) showMainScreen() {
	entrarBtn := widget.NewButton("Entrar", nil)
	cadastrarBtn := widget.NewButton("Cadastrar nova senha", func() {
		a.showRegisterDialog()
	})
	entrarBtn.OnTapped = func() {
		a.onEntrar()
	}

	a.window.SetContent(container.NewVBox(
		widget.NewLabel(""),
		entrarBtn,
		cadastrarBtn,
	))
}

// onEntrar mirrors iniciar_automacao(): loads the stored password, replaces
// the screen with the "Inserir senha" button, and starts the browser
// session in the background.
func (a *App) onEntrar() {
	password, err := a.vault.Load()
	if err != nil {
		dialog.ShowError(fmt.Errorf("por favor, cadastre uma senha"), a.window)
		return
	}

	inserirBtn := widget.NewButton("Inserir senha", nil)
	inserirBtn.Disable()
	inserirBtn.OnTapped = func() {
		a.onInserirSenha(password)
	}
	a.window.SetContent(container.NewVBox(widget.NewLabel(""), inserirBtn))

	go func() {
		execPath, err := browser.Bootstrap()
		if err != nil {
			fyne.Do(func() { dialog.ShowError(err, a.window) })
			return
		}

		session, err := browser.StartSession(execPath)
		if err != nil {
			fyne.Do(func() { dialog.ShowError(err, a.window) })
			return
		}

		a.session = session
		fyne.Do(func() { inserirBtn.Enable() })
	}()
}

// onInserirSenha mirrors inserir_senha(): fills the password field on the
// already-open page. No mouse/keyboard humanization is applied.
func (a *App) onInserirSenha(password string) {
	if a.session == nil {
		return
	}
	go func() {
		if err := a.session.FillPassword(password); err != nil {
			fyne.Do(func() { dialog.ShowError(err, a.window) })
		}
	}()
}

// showRegisterDialog mirrors cadastrar_nova_senha() + salvar_senha().
func (a *App) showRegisterDialog() {
	entry := widget.NewPasswordEntry()
	formItem := widget.NewFormItem("Senha:", entry)

	dialog.ShowForm("Cadastro de senha", "Cadastrar", "Cancelar",
		[]*widget.FormItem{formItem},
		func(confirmed bool) {
			if !confirmed {
				return
			}
			if err := a.vault.Save(entry.Text); err != nil {
				dialog.ShowError(err, a.window)
				return
			}
			dialog.ShowInformation("Sucesso", "Senha cadastrada com sucesso!", a.window)
		}, a.window)
}
