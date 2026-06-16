import tkinter as tk
from tkinter import messagebox
import base64
import time
import random

import os
import sys

import sys
import os
import zipfile
import tempfile

def extract_and_set_browser():
    if getattr(sys, 'frozen', False):
        # Caminho do zip dentro do pacote
        zip_path = os.path.join(sys._MEIPASS, 'data', 'browsers.zip')
        
        # Pasta onde será extraído (usando tempfile)
        extract_dir = os.path.join(tempfile.gettempdir(), 'playwright_browsers')
        
        # Extrai apenas se ainda não existir
        if not os.path.exists(extract_dir):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            print(f"Extraído para {extract_dir}")
        else:
            print(f"Usando extração existente em {extract_dir}")
        
        # Descobre qual é a pasta raiz que contém os navegadores
        # O zip contém uma pasta 'playwright-browsers' que por sua vez contém 'chromium-*'
        contents = os.listdir(extract_dir)
        # Se houver apenas uma pasta e ela não for vazia, provavelmente é a que queremos
        if len(contents) == 1 and os.path.isdir(os.path.join(extract_dir, contents[0])):
            browsers_root = os.path.join(extract_dir, contents[0])
        else:
            browsers_root = extract_dir
        
        # Define a variável de ambiente para o Playwright
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_root
        print(f"PLAYWRIGHT_BROWSERS_PATH definido como {browsers_root}")
        
        # Verifica se o navegador realmente existe no caminho
        possible_chromium = os.path.join(browsers_root, 'chromium-*')  # wildcard, mas só para debug
        # Lista o conteúdo para confirmação
        print("Conteúdo da pasta de navegadores:")
        for item in os.listdir(browsers_root):
            print(f"  {item}")

# Executa a extração e configuração ANTES de qualquer importação do Playwright
extract_and_set_browser()

# Agora você pode importar o Playwright e usá-lo normalmente
from playwright.sync_api import sync_playwright

from playwright.sync_api import sync_playwright

senha_cadastro = ''
base64_bytes = ''

def iniciar_automacao():
    senha = ler_senha()
    if senha:
            
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False)
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

            page.wait_for_event("close", timeout=0)

    else:
        messagebox.showwarning("Aviso", "Por favor, cadastre uma senha.")

##########
#
# Senhas
#
##########

def cadastrar_nova_senha():
    janela = tk.Tk()
    janela.title("Cadastro de senha")
    janela.geometry("300x200")

    label = tk.Label(janela, text="Senha:")
    label.pack(pady=10)

    senha_cadastro = tk.Entry(janela, show="*", width=20)
    senha_cadastro.pack(pady=5)
    
    botao_entrar = tk.Button(janela, text="Cadastrar nova senha", command=lambda: salvar_senha(senha_cadastro))
    botao_entrar.pack(pady=10)

def salvar_senha(senha):
    string_base64 = codificar(senha.get())

    with open("pass.key", "w", encoding="utf-8") as arquivo:
        arquivo.write(string_base64)
    
    messagebox.showinfo("Sucesso", "Senha cadastrada com sucesso!")

def codificar(str):
    string_bytes = str.encode('utf-8')
    base64_bytes = base64.b64encode(string_bytes)
    string_base64 = base64_bytes.decode('utf-8')
    return string_base64

def ler_senha():
    try:
        with open("pass.key", "r", encoding="utf-8") as arquivo:
            return decodificar(arquivo.read())
    except FileNotFoundError:
        return None

def decodificar(str):
    try:
        bytes_base64 = str.encode('utf-8')
        bytes_originais = base64.b64decode(bytes_base64)
        string_original = bytes_originais.decode('utf-8')
        return string_original
    except Exception:
        messagebox.showwarning("Aviso", "Senha corrompida! Por favor, cadastre uma nova senha.")
        return None
    

# Configuração da Janela
janela = tk.Tk()
janela.title("Acesso ao Bankmanager")
janela.geometry("300x200")

# Rótulo (Label)
label = tk.Label(janela, text="")
label.pack(pady=10)

# Botão entrar
botao_entrar = tk.Button(janela, text="Entrar", command=iniciar_automacao)
botao_entrar.pack(pady=10)

# Botão criar senha
botao_entrar = tk.Button(janela, text="Cadastrar nova senha", command=cadastrar_nova_senha)
botao_entrar.pack(pady=10)

# Mantém a janela aberta
janela.mainloop()