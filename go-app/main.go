package main

import (
	"log"
	"os"

	"finnet/internal/crypto"
	"finnet/internal/ui"
)

func main() {
	execDir, err := os.Getwd()
	if err != nil {
		log.Fatalf("não foi possível determinar o diretório de trabalho: %v", err)
	}

	vault := crypto.NewVault(execDir)
	app := ui.New(vault)
	app.Run()
}
