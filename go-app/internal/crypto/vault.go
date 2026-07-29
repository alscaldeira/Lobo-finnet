// Package crypto stores the operator password encrypted at rest, replacing
// the reversible Base64 "encoding" used by the original Python vault.
package crypto

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/base64"
	"errors"
	"fmt"
	"os"
	"path/filepath"
)

const (
	keyFileName  = "finnet.key"
	vaultFileName = "pass.key"
	keySize      = 32 // AES-256
)

var ErrNoPassword = errors.New("nenhuma senha cadastrada")

// Vault reads/writes the encrypted password file alongside a locally
// generated master key. Both files live in dir.
type Vault struct {
	dir string
}

func NewVault(dir string) *Vault {
	return &Vault{dir: dir}
}

func (v *Vault) keyPath() string   { return filepath.Join(v.dir, keyFileName) }
func (v *Vault) vaultPath() string { return filepath.Join(v.dir, vaultFileName) }

// loadOrCreateKey returns the AES key, generating and persisting a new
// random one on first use. The key file is written with 0600 permissions.
func (v *Vault) loadOrCreateKey() ([]byte, error) {
	data, err := os.ReadFile(v.keyPath())
	if err == nil {
		key, decErr := base64.StdEncoding.DecodeString(string(data))
		if decErr != nil || len(key) != keySize {
			return nil, fmt.Errorf("arquivo de chave corrompido: %w", decErr)
		}
		return key, nil
	}
	if !os.IsNotExist(err) {
		return nil, err
	}

	key := make([]byte, keySize)
	if _, err := rand.Read(key); err != nil {
		return nil, fmt.Errorf("gerando chave: %w", err)
	}
	encoded := base64.StdEncoding.EncodeToString(key)
	if err := os.WriteFile(v.keyPath(), []byte(encoded), 0o600); err != nil {
		return nil, fmt.Errorf("salvando chave: %w", err)
	}
	return key, nil
}

// Save encrypts and persists the password with AES-256-GCM.
func (v *Vault) Save(password string) error {
	key, err := v.loadOrCreateKey()
	if err != nil {
		return err
	}

	block, err := aes.NewCipher(key)
	if err != nil {
		return err
	}
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return err
	}

	nonce := make([]byte, gcm.NonceSize())
	if _, err := rand.Read(nonce); err != nil {
		return err
	}

	ciphertext := gcm.Seal(nonce, nonce, []byte(password), nil)
	encoded := base64.StdEncoding.EncodeToString(ciphertext)
	return os.WriteFile(v.vaultPath(), []byte(encoded), 0o600)
}

// Load decrypts and returns the stored password.
func (v *Vault) Load() (string, error) {
	data, err := os.ReadFile(v.vaultPath())
	if err != nil {
		if os.IsNotExist(err) {
			return "", ErrNoPassword
		}
		return "", err
	}

	key, err := v.loadOrCreateKey()
	if err != nil {
		return "", err
	}

	ciphertext, err := base64.StdEncoding.DecodeString(string(data))
	if err != nil {
		return "", fmt.Errorf("senha corrompida: %w", err)
	}

	block, err := aes.NewCipher(key)
	if err != nil {
		return "", err
	}
	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return "", err
	}

	nonceSize := gcm.NonceSize()
	if len(ciphertext) < nonceSize {
		return "", errors.New("senha corrompida: dados insuficientes")
	}
	nonce, encrypted := ciphertext[:nonceSize], ciphertext[nonceSize:]

	plaintext, err := gcm.Open(nil, nonce, encrypted, nil)
	if err != nil {
		return "", fmt.Errorf("senha corrompida: %w", err)
	}
	return string(plaintext), nil
}
