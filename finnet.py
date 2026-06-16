import tkinter as tk
from tkinter import messagebox
import base64
import time
import random
import os
import sys
import zipfile
import tempfile
import stat
import glob
import multiprocessing          # <--- NOVO

# ------------------------------------------------------------
# Função de extração (já corrigida)
# ------------------------------------------------------------
def extract_and_set_browser():
    if getattr(sys, 'frozen', False):
        zip_path = os.path.join(sys._MEIPASS, 'data', 'browsers.zip')
        extract_dir = os.path.join(tempfile.gettempdir(), 'playwright_browsers')
        
        if not os.path.exists(extract_dir):
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            print(f"Extraído para {extract_dir}")
        else:
            print(f"Usando extração existente em {extract_dir}")
        
        contents = os.listdir(extract_dir)
        if len(contents) == 1 and os.path.isdir(os.path.join(extract_dir, contents[0])):
            browsers_root = os.path.join(extract_dir, contents[0])
        else:
            browsers_root = extract_dir
        
        os.environ['PLAYWRIGHT_BROWSERS_PATH'] = browsers_root
        print(f"PLAYWRIGHT_BROWSERS_PATH definido como {browsers_root}")
        
        # ---- CORREÇÃO DE PERMISSÕES ----
        if sys.platform == 'darwin':
            import subprocess
            import stat
            
            # 1. Dar permissão de execução para TODOS os arquivos e pastas (recursivamente)
            for root, dirs, files in os.walk(browsers_root):
                # Pastas: permissão de leitura/escrita/execução
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    try:
                        os.chmod(dir_path, os.stat(dir_path).st_mode | stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    except Exception as e:
                        print(f"Erro ao ajustar permissão da pasta {dir_path}: {e}")
                
                # Arquivos: permissão de leitura/escrita/execução (todos)
                for f in files:
                    file_path = os.path.join(root, f)
                    try:
                        os.chmod(file_path, os.stat(file_path).st_mode | stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    except Exception as e:
                        print(f"Erro ao ajustar permissão do arquivo {file_path}: {e}")
            
            # 2. Remover quarentena de toda a árvore (recursivamente)
            try:
                subprocess.run(['xattr', '-d', '-r', 'com.apple.quarantine', browsers_root],
                               stderr=subprocess.DEVNULL, check=False)
                print("Quarentena removida recursivamente.")
            except Exception as e:
                print(f"Erro ao remover quarentena: {e}")
            
            # 3. Verificação adicional: localiza o crashpad_handler e dá permissão explicitamente
            crashpad_pattern = os.path.join(browsers_root, '**', 'chrome_crashpad_handler')
            import glob
            for handler in glob.glob(crashpad_pattern, recursive=True):
                try:
                    os.chmod(handler, os.stat(handler).st_mode | stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    print(f"Permissão explicitamente concedida ao handler: {handler}")
                except Exception as e:
                    print(f"Erro ao ajustar permissão do handler {handler}: {e}")
            
            print("Permissões de execução aplicadas a todos os arquivos e pastas.")
        else:
            # Linux/Windows: apenas executáveis relevantes
            for root, dirs, files in os.walk(browsers_root):
                for f in files:
                    if f.endswith('.exe') or f == 'chrome' or f.startswith('chrome_'):
                        file_path = os.path.join(root, f)
                        try:
                            os.chmod(file_path, os.stat(file_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                        except Exception as e:
                            print(f"Erro ao ajustar permissão de {file_path}: {e}")

# Executa a extração ANTES de importar o Playwright
extract_and_set_browser()

# Agora importa o Playwright (apenas uma vez)
from playwright.sync_api import sync_playwright

# ------------------------------------------------------------
# Funções de senha (inalteradas)
# ------------------------------------------------------------
senha_cadastro = ''
base64_bytes = ''

def cadastrar_nova_senha():
    janela_cadastro = tk.Toplevel(janela) 
    janela_cadastro.title("Cadastro de senha")
    janela_cadastro.geometry("300x200")
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
    return base64_bytes.decode('utf-8')

def ler_senha():
    try:
        with open("pass.key", "r", encoding="utf-8") as arquivo:
            return decodificar(arquivo.read())
    except FileNotFoundError:
        print("File pass.key not found.")
        return None

def decodificar(str):
    try:
        bytes_base64 = str.encode('utf-8')
        bytes_originais = base64.b64decode(bytes_base64)
        return bytes_originais.decode('utf-8')
    except Exception:
        messagebox.showwarning("Aviso", "Senha corrompida! Por favor, cadastre uma nova senha.")
        return None

# ------------------------------------------------------------
# NOVA FUNÇÃO: executa a automação em um processo separado
# ------------------------------------------------------------
def executar_automacao(senha):
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

# ------------------------------------------------------------
# Função acionada pelo botão "Entrar"
# ------------------------------------------------------------
def iniciar_automacao():
    senha = ler_senha()
    if senha:
        executar_automacao(senha)
        # Cria um processo filho para executar a automação
        # p = multiprocessing.Process(target=executar_automacao, args=(senha,))
        # p.start()
        # Não faz p.join() para não travar a interface
    else:
        messagebox.showwarning("Aviso", "Por favor, cadastre uma senha.")

# ------------------------------------------------------------
# Interface Tkinter (INALTERADA)
# ------------------------------------------------------------
janela = tk.Tk()
janela.title("Acesso ao Bankmanager")
janela.geometry("300x200")
label = tk.Label(janela, text="")
label.pack(pady=10)
botao_entrar = tk.Button(janela, text="Entrar", command=iniciar_automacao)
botao_entrar.pack(pady=10)
botao_cadastrar = tk.Button(janela, text="Cadastrar nova senha", command=cadastrar_nova_senha)
botao_cadastrar.pack(pady=10)
janela.mainloop()