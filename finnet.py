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

import stat
import glob

def extract_and_set_browser():
    if getattr(sys, 'frozen', False):
        zip_path = os.path.join(sys._MEIPASS, 'data', 'browsers.zip')
        extract_dir = os.path.join(tempfile.gettempdir(), 'playwright_browsers')
        
        # Extrai apenas se a pasta não existir
        if not os.path.exists(extract_dir):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            print(f"Extraído para {extract_dir}")
        else:
            print(f"Usando extração existente em {extract_dir}")
        
        # Localiza a pasta raiz que contém as subpastas dos navegadores
        contents = os.listdir(extract_dir)
        if len(contents) == 1 and os.path.isdir(os.path.join(extract_dir, contents[0])):
            browsers_root = os.path.join(extract_dir, contents[0])
        else:
            browsers_root = extract_dir
        
        # Define a variável de ambiente
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_root
        print(f"PLAYWRIGHT_BROWSERS_PATH definido como {browsers_root}")
        
        # ---- CORREÇÃO DE PERMISSÕES (especialmente no macOS) ----
        # Procura pelo executável do Chromium dentro da árvore
        # Padrão para macOS: .../chromium-*/chrome-mac-*/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing
        # Padrão para Linux/Windows: .../chromium-*/chrome (ou chrome.exe)
        
        # 1. Tenta encontrar o executável do macOS
        chrome_pattern_mac = os.path.join(
            browsers_root, 
            'chromium-*', 
            'chrome-mac-*', 
            'Google Chrome for Testing.app', 
            'Contents', 
            'MacOS', 
            'Google Chrome for Testing'
        )
        executaveis = glob.glob(chrome_pattern_mac)
        
        # 2. Se não achou, tenta o padrão Linux (chrome)
        if not executaveis:
            chrome_pattern_linux = os.path.join(browsers_root, 'chromium-*', 'chrome')
            executaveis = glob.glob(chrome_pattern_linux)
        
        # 3. Se ainda não achou, tenta Windows (chrome.exe)
        if not executaveis:
            chrome_pattern_win = os.path.join(browsers_root, 'chromium-*', 'chrome.exe')
            executaveis = glob.glob(chrome_pattern_win)
        
        # Aplica permissão de execução em todos os encontrados
        for exe in executaveis:
            try:
                # Adiciona permissão de execução para usuário, grupo e outros
                os.chmod(exe, os.stat(exe).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                print(f"Permissão de execução adicionada: {exe}")
                
                # (Opcional) Remove atributo de quarentena do macOS (se houver)
                if sys.platform == 'darwin':
                    import subprocess
                    subprocess.run(['xattr', '-d', 'com.apple.quarantine', exe], 
                                   stderr=subprocess.DEVNULL, check=False)
            except Exception as e:
                print(f"Erro ao ajustar permissões para {exe}: {e}")
        
        # Lista o conteúdo da pasta para depuração
        print("Conteúdo da pasta de navegadores:")
        for item in os.listdir(browsers_root):
            print(f"  {item}")

# Chama a extração antes de qualquer importação do Playwright
extract_and_set_browser()

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