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
        # O zip está dentro da subpasta 'data'
        zip_path = os.path.join(sys._MEIPASS, 'data', 'browsers.zip')
        
        # Depuração: lista o conteúdo da pasta data
        data_dir = os.path.join(sys._MEIPASS, 'data')
        if os.path.exists(data_dir):
            print(f"Conteúdo de {data_dir}:")
            for item in os.listdir(data_dir):
                print(f"  {item}")
        else:
            print(f"Pasta {data_dir} não encontrada!")
        
        # Tenta abrir o zip
        try:
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.testzip()  # verifica integridade
        except Exception as e:
            raise RuntimeError(f"Erro ao abrir {zip_path}: {e}")
        
        # Pasta de extração (no temp)
        extract_dir = os.path.join(tempfile.gettempdir(), 'playwright_browsers')
        if not os.path.exists(extract_dir):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            print(f"Extraído para {extract_dir}")
        else:
            print(f"Usando extração existente em {extract_dir}")
        
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = extract_dir
        print(f"PLAYWRIGHT_BROWSERS_PATH definido como {extract_dir}")

# Executa a extração
extract_and_set_browser()

from playwright.sync_api import sync_playwright

senha_cadastro = ''
base64_bytes = ''

def iniciar_automacao():
    senha = ler_senha()
    if senha:

        # Detecta se o script está rodando a partir de um executável compilado (.frozen)
        if getattr(sys, 'frozen', False):
            # Encontra a pasta temporária onde o executável descompactou os arquivos
            bundle_dir = sys._MEIPASS
            # Aponta o driver do Playwright para buscar os navegadores embutidos dentro dela
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = os.path.join(bundle_dir, "playwright", "driver", "package", ".local-browsers")
        else:
            # Se rodar direto via terminal (em desenvolvimento), mantém o padrão local
            os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "0"
            
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