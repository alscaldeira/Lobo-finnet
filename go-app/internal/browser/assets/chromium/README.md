Coloque aqui um `chromium.zip` por plataforma, contendo a build portátil do
Chromium (a mesma baixada pelo Playwright em `~/Library/Caches/ms-playwright/
chromium-<rev>/chrome-<plat>`), no formato:

```
assets/chromium/darwin-arm64/chromium.zip
assets/chromium/darwin-amd64/chromium.zip
assets/chromium/windows-amd64/chromium.zip
assets/chromium/linux-amd64/chromium.zip
```

O caminho do binário dentro do zip para cada plataforma está mapeado em
`binaryRelPath` (bootstrap.go). No macOS, o zip precisa ser criado com um
comando que preserve symlinks (o `.app` do Chromium depende disso), por
exemplo a partir da pasta `chrome-mac-arm64`:

```bash
cd chrome-mac-arm64 && zip -ry -X /caminho/para/darwin-arm64/chromium.zip .
```

O zip é embutido no executável final via `go:embed` e extraído em tempo de
execução para uma pasta temporária (equivalente ao `browsers.zip` da versão
Python), preservando symlinks e permissões de execução. Se nenhum zip estiver
presente para o SO/arquitetura atual, `Bootstrap()` retorna vazio e a
automação usa o Chrome/Edge já instalado na máquina do usuário.
