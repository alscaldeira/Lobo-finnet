import os
import sys

# 1. CORREÇÃO CRÍTICA: Previne o crash do --noconsole redirecionando saídas
if sys.stdout is None:
    sys.stdout = open(os.devnull, 'w')
if sys.stderr is None:
    sys.stderr = open(os.devnull, 'w')

import tkinter as tk
from tkinter import messagebox
import base64
from playwright.sync_api import sync_playwright
import time
import random

def iniciar_automacao():
    senha = ler_senha()
    if not senha:
        messagebox.showwarning("Aviso", "Por favor, cadastre uma senha.")
        return

    # Oculta a janela principal do Tkinter para não parecer que "travou"
    janela.withdraw() 
    
    try:
        # Configuração de caminhos baseada no Sistema Operacional
        if getattr(sys, 'frozen', False):
            if sys.platform == 'darwin':
                # No Mac, o browser NÃO está embutido (evita quebra de codesign no Actions)
                # Removemos a variável para o Playwright usar a pasta padrão do usuário (~/Library/Caches)
                if "PLAYWRIGHT_BROWSERS_PATH" in os.environ:
                    del os.environ["PLAYWRIGHT_BROWSERS_PATH"]
            else:
                # Windows e Linux usam o browser embutido normalmente dentro do .exe
                bundle_dir = sys._MEIPASS
                os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(bundle_dir, "playwright", "driver", "package", ".local-browsers")
        else:
            # Ambiente de desenvolvimento local
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"
            
        with sync_playwright() as p:
            try:
                browser = p.chromium.launch(headless=False)
            except Exception as erro_launch:
                # Se o browser não for encontrado (comum na primeira execução no Mac)
                if "Executable doesn't exist" in str(erro_launch) and sys.platform == 'darwin':
                    # Exibe um aviso rápido para o usuário não achar que o app quebrou
                    messagebox.showinfo("Instalação", "Configurando dependências do sistema para o primeiro uso (Mac). Aguarde alguns instantes...")
                    
                    # Invoca o instalador interno do Playwright de forma programática
                    from playwright.cli.main import main as playwright_cli
                    old_argv = sys.argv
                    sys.argv = ["playwright", "install", "chromium"]
                    try:
                        playwright_cli()
                    except SystemExit:
                        pass  # O CLI do playwright força um sys.exit(0) ao terminar a instalação
                    sys.argv = old_argv
                    
                    # Tenta abrir novamente agora que está instalado
                    browser = p.chromium.launch(headless=False)
                else:
                    raise erro_launch

            page = browser.new_page()

            xpathBtnGoToLoginPage = "//*[@id=\"menu-1-7cfb9e9\"]/li[5]/a"
            xpathInputPassword = "//*[@id=\"SenhaAcesso\"]"
            xpathViewPassword = "//*[@id=\"visualizar_ocultar_senha\"]"

            page.goto("https://www.bankmanager.com.br/")
            time.sleep(random.randint(3, 6))
            page.locator(xpathBtnGoToLoginPage).click()
            time.sleep(random.randint(3, 6))
            
            page.locator(xpathViewPassword).evaluate("elemento => elemento.remove()")
            time.sleep(random.randint(1, 3))
            page.locator(xpathInputPassword).fill(senha)

            # Aguarda o usuário fechar o navegador
            page.wait_for_event("close", timeout=0)

    except Exception as e:
        messagebox.showerror("Erro", f"Ocorreu um erro na automação:\n{str(e)}")
    finally:
        # Traz a janela principal de volta após o fechamento do navegador
        janela.deiconify()

##########
#
# Senhas
#
##########

def cadastrar_nova_senha():
    # 2. CORREÇÃO TKINTER: Janelas filhas devem usar Toplevel, não Tk()
    janela_cadastro = tk.Toplevel(janela)
    janela_cadastro.title("Cadastro de senha")
    janela_cadastro.geometry("300x200")
    
    # Faz com que a janela filha bloqueie a interação com a janela mãe enquanto estiver aberta
    janela_cadastro.grab_set() 

    label = tk.Label(janela_cadastro, text="Senha:")
    label.pack(pady=10)

    input_senha = tk.Entry(janela_cadastro, show="*", width=20)
    input_senha.pack(pady=5)
    
    def confirmar_cadastro():
        salvar_senha(input_senha.get())
        janela_cadastro.destroy() # Fecha a janela filha após salvar

    botao_salvar = tk.Button(janela_cadastro, text="Cadastrar nova senha", command=confirmar_cadastro)
    botao_salvar.pack(pady=10)

def salvar_senha(senha):
    if not senha:
        messagebox.showwarning("Aviso", "A senha não pode ser vazia.")
        return
        
    string_base64 = codificar(senha)

    with open("pass.key", "w", encoding="utf-8") as arquivo:
        arquivo.write(string_base64)
    
    messagebox.showinfo("Sucesso", "Senha cadastrada com sucesso!")

def codificar(texto):
    string_bytes = texto.encode('utf-8')
    base64_bytes = base64.b64encode(string_bytes)
    return base64_bytes.decode('utf-8')

def ler_senha():
    try:
        with open("pass.key", "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read().strip()
            if not conteudo:
                return None
            return decodificar(conteudo)
    except FileNotFoundError:
        return None

def decodificar(texto_base64):
    try:
        bytes_base64 = texto_base64.encode('utf-8')
        bytes_originais = base64.b64decode(bytes_base64)
        return bytes_originais.decode('utf-8')
    except Exception:
        messagebox.showwarning("Aviso", "Senha corrompida! Por favor, cadastre uma nova senha.")
        return None

# ==========================================
# Configuração da Janela Principal
# ==========================================
janela = tk.Tk()
janela.title("Acesso ao Bankmanager")
janela.geometry("300x200")

label_titulo = tk.Label(janela, text="Controle de Acesso")
label_titulo.pack(pady=10)

botao_entrar = tk.Button(janela, text="Entrar", command=iniciar_automacao, width=20)
botao_entrar.pack(pady=10)

# Corrigido o nome da variável que estava sobrescrevendo botao_entrar
botao_cadastrar = tk.Button(janela, text="Cadastrar nova senha", command=cadastrar_nova_senha, width=20)
botao_cadastrar.pack(pady=10)

# Mantém a janela aberta
janela.mainloop()