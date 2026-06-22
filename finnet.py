import tkinter as tk
from tkinter import messagebox
import base64
import time
import random
import os
import sys
import zipfile
import tempfile
import threading

evento_inserir_senha = threading.Event()

# ------------------------------------------------------------
# Função de extração (já corrigida) - inalterada
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
            
            for root, dirs, files in os.walk(browsers_root):
                for d in dirs:
                    dir_path = os.path.join(root, d)
                    try:
                        os.chmod(dir_path, os.stat(dir_path).st_mode | stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    except Exception as e:
                        print(f"Erro ao ajustar permissão da pasta {dir_path}: {e}")
                
                for f in files:
                    file_path = os.path.join(root, f)
                    try:
                        os.chmod(file_path, os.stat(file_path).st_mode | stat.S_IRWXU | stat.S_IRWXG | stat.S_IRWXO)
                    except Exception as e:
                        print(f"Erro ao ajustar permissão do arquivo {file_path}: {e}")
            
            try:
                subprocess.run(['xattr', '-d', '-r', 'com.apple.quarantine', browsers_root],
                               stderr=subprocess.DEVNULL, check=False)
                print("Quarentena removida recursivamente.")
            except Exception as e:
                print(f"Erro ao remover quarentena: {e}")
            
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
            for root, dirs, files in os.walk(browsers_root):
                for f in files:
                    if f.endswith('.exe') or f == 'chrome' or f.startswith('chrome_'):
                        file_path = os.path.join(root, f)
                        try:
                            os.chmod(file_path, os.stat(file_path).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
                        except Exception as e:
                            print(f"Erro ao ajustar permissão de {file_path}: {e}")

extract_and_set_browser()

# ------------------------------------------------------------
# AGORA importamos o Playwright com Stealth (adicione ao requirements)
# ------------------------------------------------------------
# Instale: pip install playwright-stealth
from playwright.sync_api import sync_playwright

# ------------------------------------------------------------
# Funções de senha (inalteradas)
# ------------------------------------------------------------
senha_cadastro = ''
base64_bytes = ''

def cadastrar_nova_senha():
    janela_cadastro = tk.Toplevel(janela) 
    janela_cadastro.resizable(False, False)
    janela_cadastro.title("Cadastro de senha")
    janela_cadastro.geometry("300x120")

    label = tk.Label(janela_cadastro, text="Senha:")
    label.pack(pady=3)

    senha_cadastro = tk.Entry(janela_cadastro, show="*", width=20)
    senha_cadastro.pack(pady=3)

    botao_cadastrar = tk.Button(janela_cadastro, text="Cadastrar", command=lambda: salvar_senha(senha_cadastro))
    botao_cadastrar.pack(pady=3)

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
# FUNÇÕES DE HUMANIZAÇÃO
# ------------------------------------------------------------
def random_delay(media=3.0, desvio=1.0):
    """Atraso com distribuição normal (mais natural)"""
    delay = random.gauss(media, desvio)
    # Garante que não seja negativo nem muito grande
    delay = max(0.5, min(delay, 8.0))
    time.sleep(delay)

def move_mouse_natural(page, x, y, steps=20):
    """
    Move o mouse da posição atual até (x, y) com trajetória curvilínea (Bézier).
    Isso simula um movimento humano.
    """
    # Obtém a posição atual do mouse (não temos acesso direto, então partimos do centro da tela)
    # Para simplificar, vamos usar uma posição inicial aleatória próxima ao elemento.
    # Uma alternativa melhor seria usar o bounding box do elemento e gerar pontos aleatórios.
    # Aqui vou mover de forma linear com pequenas perturbações.
    current_x = random.randint(0, 500)
    current_y = random.randint(0, 500)
    for i in range(steps + 1):
        t = i / steps
        # Curva de Bezier com ponto de controle aleatório
        cx = (current_x + x) / 2 + random.randint(-50, 50)
        cy = (current_y + y) / 2 + random.randint(-50, 50)
        px = (1-t)**2 * current_x + 2*(1-t)*t * cx + t**2 * x
        py = (1-t)**2 * current_y + 2*(1-t)*t * cy + t**2 * y
        page.mouse.move(px, py)
        # Pequena pausa entre movimentos
        time.sleep(random.uniform(0.005, 0.02))
    # Pequena pausa após chegar
    time.sleep(random.uniform(0.1, 0.3))

def type_like_human(page, locator, text, delay_between_keys=0.08):
    """
    Digita o texto como um humano: com atraso variável entre teclas e
    pequenas pausas aleatórias.
    """
    locator.click()  # foca no campo
    time.sleep(random.uniform(0.2, 0.5))
    # Usamos page.type() com delay, mas adicionamos variação
    for char in text:
        # Atraso entre teclas com variação normal
        delay = max(0.03, random.gauss(delay_between_keys, 0.03))
        time.sleep(delay)
        page.keyboard.type(char, delay=0)  # já temos o delay manual
    # Pequena pausa após terminar
    time.sleep(random.uniform(0.2, 0.6))

# ------------------------------------------------------------
# FUNÇÃO PRINCIPAL DE AUTOMAÇÃO (HUMANIZADA)
# ------------------------------------------------------------
def executar_automacao(senha):
    global page
    pw_instancia = sync_playwright().start()
    # LANÇA O NAVEGADOR COM CONFIGURAÇÕES MAIS REALISTAS
    browser = pw_instancia.chromium.launch(
        headless=False,
        args=[
            '--disable-blink-features=AutomationControlled',
            '--disable-features=IsolateOrigins,site-per-process', 
            '--disable-site-isolation-trials',
        ]
    )
    # Cria um contexto com viewport realista
    context = browser.new_context(
        viewport={'width': 1920, 'height': 1080},
        user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    )
    page = context.new_page()

    # APLICA O STEALTH (mascara webdriver, etc.)
    # Injeção de script para mascarar automação
    page.add_init_script("""
        Object.defineProperty(navigator, 'webdriver', {
            get: () => undefined
        });
        // Remove outras marcas comuns
        delete window.navigator.__proto__.webdriver;
        // Simula plugins (comuns em navegadores reais)
        Object.defineProperty(navigator, 'plugins', {
            get: () => [1, 2, 3, 4, 5]
        });
        // Simula a presença de Chrome
        window.chrome = {
            runtime: {}
        };
    """)

    # DEFINIÇÃO DOS XPATHS
    xpathInputPassword = "//*[@id=\"SenhaAcesso\"]"

    # 1. Navega até a página inicial
    print("Navegando para o site...")
    page.goto("https://www.bankmanager.com.br/")
    random_delay(media=4.0, desvio=1.2)  # espera mais realista
    
    xpathViewPassword = "//*[@id=\"visualizar_ocultar_senha\"]"
    page.locator(xpathViewPassword).evaluate("elemento => elemento.remove()")

    try:
        # Loop que mantém a automação viva enquanto a página não for fechada
        while not page.is_closed():
            # Verifica se o Tkinter levantou a bandeira
            if evento_inserir_senha.is_set():
                print("Sinal recebido! Inserindo senha...")
                evento_inserir_senha.clear()  # Abaixa a bandeira para não digitar várias vezes seguidas
                
                # A PRÓPRIA THREAD DO PLAYWRIGHT FAZ A AÇÃO
                xpathInputPassword = "//*[@id=\"SenhaAcesso\"]"
                input_senha = page.locator(xpathInputPassword)
                type_like_human(page, input_senha, senha, delay_between_keys=0.13)
                # Aguarda meio segundo antes de checar a bandeira de novo.
            # O wait_for_timeout é crucial para o Playwright não travar.
            page.wait_for_timeout(500)
            
    except Exception as e:
        print(f"Automação encerrada: {e}")  

def inserir_senha():
    print("Sinal enviado para inserir a senha!")
    evento_inserir_senha.set()
    global page
    senha = ler_senha()
    xpathInputPassword = "//*[@id=\"SenhaAcesso\"]"
    input_senha = page.locator(xpathInputPassword)
    type_like_human(page, input_senha, senha, delay_between_keys=0.13)

# ------------------------------------------------------------
# Função acionada pelo botão "Entrar"
# ------------------------------------------------------------
def iniciar_automacao():
    global botao_cadastrar
    # Nota: faltavam os parênteses aqui no seu código original para executar a destruição
    botao_cadastrar.destroy() 

    print('Criando botão \'Inserir Senha\'')
    botao_inserir_senha = tk.Button(janela, text="Inserir senha", command=inserir_senha)
    botao_inserir_senha.pack(pady=5)

    senha = ler_senha()
    if senha:
        # Trocado Multiprocessing por Threading 
        t = threading.Thread(target=executar_automacao, args=(senha,))
        t.daemon = True  # Garante que a thread feche se a janela do Tkinter fechar
        t.start()
    else:
        messagebox.showwarning("Aviso", "Por favor, cadastre uma senha.")

# ------------------------------------------------------------
# Interface Tkinter (INALTERADA)
# ------------------------------------------------------------

page = None
if __name__ == '__main__':
    janela = tk.Tk()
    janela.resizable(False, False)
    janela.title("Acesso ao Bankmanager")
    janela.geometry("300x150")
    label = tk.Label(janela, text="")
    label.pack(pady=5)

    botao_entrar = tk.Button(janela, text="Entrar", command=iniciar_automacao)
    botao_entrar.pack(pady=5)

    botao_cadastrar = tk.Button(janela, text="Cadastrar nova senha", command=cadastrar_nova_senha)
    botao_cadastrar.pack(pady=5)

    janela.mainloop()