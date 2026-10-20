"""Habilidades (skills) do Jarvis - as acoes que ele sabe executar.

Cada habilidade recebe o texto do comando do usuario e devolve uma
string com a resposta a ser falada/exibida.
"""

from __future__ import annotations

import datetime
import os
import subprocess
import urllib.request
import webbrowser
from urllib.parse import quote_plus


# ---------------------------------------------------------------------------
# Data e hora
# ---------------------------------------------------------------------------
_MESES = [
    "janeiro", "fevereiro", "marco", "abril", "maio", "junho",
    "julho", "agosto", "setembro", "outubro", "novembro", "dezembro",
]


def dizer_hora(_: str) -> str:
    agora = datetime.datetime.now()
    return f"Agora sao {agora.hour} horas e {agora.minute:02d} minutos."


def dizer_data(_: str) -> str:
    hoje = datetime.date.today()
    return f"Hoje e dia {hoje.day} de {_MESES[hoje.month - 1]} de {hoje.year}."


# ---------------------------------------------------------------------------
# Abrir programas do Windows
# ---------------------------------------------------------------------------
# Mapeia palavras-chave para o executavel/comando que abre o programa.
_PROGRAMAS = {
    "bloco de notas": "notepad.exe",
    "notepad": "notepad.exe",
    "calculadora": "calc.exe",
    "paint": "mspaint.exe",
    "explorador": "explorer.exe",
    "navegador": "start chrome",
    "chrome": "start chrome",
    "edge": "start msedge",
    "cmd": "start cmd",
    "terminal": "start cmd",
}


def abrir_programa(comando: str) -> str:
    for chave, executavel in _PROGRAMAS.items():
        if chave in comando:
            try:
                # shell=True para resolver comandos como "start chrome".
                subprocess.Popen(executavel, shell=True)
                return f"Abrindo {chave}."
            except Exception as exc:
                return f"Nao consegui abrir {chave}. Erro: {exc}"
    return "Nao sei qual programa voce quer abrir."


# ---------------------------------------------------------------------------
# Web: abrir sites e pesquisar
# ---------------------------------------------------------------------------
_SITES = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "github": "https://github.com",
    "whatsapp": "https://web.whatsapp.com",
}


def abrir_site(comando: str) -> str:
    for nome, url in _SITES.items():
        if nome in comando:
            webbrowser.open(url)
            return f"Abrindo {nome}."
    return "Nao conheco esse site."


def pesquisar_web(comando: str) -> str:
    termo = comando
    for gatilho in ("pesquisar", "pesquise", "buscar", "busque", "procurar", "procure"):
        termo = termo.replace(gatilho, "")
    termo = termo.strip()
    if not termo:
        return "O que voce quer pesquisar?"
    webbrowser.open(f"https://www.google.com/search?q={quote_plus(termo)}")
    return f"Pesquisando por {termo}."


# ---------------------------------------------------------------------------
# Wikipedia
# ---------------------------------------------------------------------------
def wikipedia_resumo(comando: str) -> str:
    termo = comando
    for gatilho in ("wikipedia", "quem e", "quem foi", "o que e", "me fale sobre"):
        termo = termo.replace(gatilho, "")
    termo = termo.strip()
    if not termo:
        return "Sobre o que voce quer saber?"
    try:
        import wikipedia

        wikipedia.set_lang("pt")
        resumo = wikipedia.summary(termo, sentences=2)
        return resumo
    except Exception as exc:
        return f"Nao encontrei nada sobre {termo}. ({exc})"


# ---------------------------------------------------------------------------
# Arquivos e pastas
# ---------------------------------------------------------------------------
def criar_pasta(comando: str) -> str:
    nome = comando.replace("criar pasta", "").replace("crie pasta", "").strip()
    if not nome:
        return "Qual o nome da pasta?"
    try:
        destino = os.path.join(os.path.expanduser("~"), "Desktop", nome)
        os.makedirs(destino, exist_ok=True)
        return f"Pasta {nome} criada na area de trabalho."
    except Exception as exc:
        return f"Nao consegui criar a pasta. Erro: {exc}"


# ---------------------------------------------------------------------------
# Tocar musica no YouTube
# ---------------------------------------------------------------------------
def tocar_musica(comando: str) -> str:
    termo = comando
    for gatilho in ("tocar musica", "toque musica", "tocar", "toque",
                    "coloca", "colocar", "poe", "por"):
        termo = termo.replace(gatilho, "")
    termo = termo.strip()
    if not termo:
        return "Qual musica voce quer ouvir?"
    # Abre a busca do YouTube ja com reproducao automatica do 1o resultado.
    url = f"https://www.youtube.com/results?search_query={quote_plus(termo)}"
    webbrowser.open(url)
    return f"Tocando {termo} no YouTube."


# ---------------------------------------------------------------------------
# Previsao do tempo (via wttr.in - gratis, sem chave de API)
# ---------------------------------------------------------------------------
def previsao_tempo(comando: str) -> str:
    cidade = comando
    for gatilho in ("previsao do tempo", "como esta o tempo",
                    "como ta o tempo", "tempo em", "clima em",
                    "temperatura em", "tempo", "clima", "temperatura"):
        cidade = cidade.replace(gatilho, "")
    cidade = cidade.replace(" em ", " ").strip()
    if not cidade:
        cidade = "Sao Paulo"
    try:
        # Formato enxuto: "Cidade: condicao +temperatura"
        url = (
            "https://wttr.in/"
            + quote_plus(cidade)
            + "?format=%l:+%C+%t&lang=pt&m"
        )
        req = urllib.request.Request(url, headers={"User-Agent": "curl/8"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            texto = resp.read().decode("utf-8", errors="ignore").strip()
        # Traduz alguns termos comuns que a wttr costuma devolver em ingles.
        traducoes = {
            "Sunny": "ensolarado", "Clear": "ceu limpo",
            "Partly cloudy": "parcialmente nublado", "Cloudy": "nublado",
            "Overcast": "encoberto", "Mist": "neblina", "Fog": "nevoeiro",
            "Light rain": "chuva leve", "Rain": "chuva",
            "Heavy rain": "chuva forte", "Patchy rain nearby": "chuva isolada",
            "Light drizzle": "garoa", "Thundery outbreaks possible": "risco de trovoadas",
        }
        for en, pt in traducoes.items():
            texto = texto.replace(en, pt)
        return f"O tempo agora: {texto}."
    except Exception as exc:
        return f"Nao consegui ver o tempo de {cidade} agora. ({exc})"


# ---------------------------------------------------------------------------
# Controle de volume (simula teclas de midia do Windows)
# ---------------------------------------------------------------------------
def _enviar_tecla_volume(codigo: int, vezes: int = 1) -> None:
    """Dispara teclas virtuais de volume via Windows API (user32)."""
    import ctypes

    for _ in range(vezes):
        ctypes.windll.user32.keybd_event(codigo, 0, 0, 0)  # key down
        ctypes.windll.user32.keybd_event(codigo, 0, 2, 0)  # key up


def controlar_volume(comando: str) -> str:
    # Codigos de tecla virtual do Windows.
    VK_VOLUME_MUTE = 0xAD
    VK_VOLUME_DOWN = 0xAE
    VK_VOLUME_UP = 0xAF
    try:
        if "mudo" in comando or "silenciar" in comando or "mutar" in comando:
            _enviar_tecla_volume(VK_VOLUME_MUTE)
            return "Som no mudo."
        if any(p in comando for p in ("aumentar", "aumenta", "subir", "mais alto", "mais volume")):
            _enviar_tecla_volume(VK_VOLUME_UP, vezes=5)
            return "Aumentando o volume."
        if any(p in comando for p in ("diminuir", "diminui", "abaixar", "abaixa", "mais baixo", "menos volume")):
            _enviar_tecla_volume(VK_VOLUME_DOWN, vezes=5)
            return "Diminuindo o volume."
        return "Quer que eu aumente, diminua ou coloque no mudo?"
    except Exception as exc:
        return f"Nao consegui controlar o volume. ({exc})"


# ---------------------------------------------------------------------------
# Controle do sistema: bloquear tela e tirar print
# ---------------------------------------------------------------------------
def bloquear_tela(_: str) -> str:
    try:
        import ctypes

        ctypes.windll.user32.LockWorkStation()
        return "Bloqueando a tela."
    except Exception as exc:
        return f"Nao consegui bloquear a tela. ({exc})"


def tirar_print(_: str) -> str:
    try:
        destino = os.path.join(
            os.path.expanduser("~"),
            "Pictures",
            f"print_{datetime.datetime.now():%Y%m%d_%H%M%S}.png",
        )
        os.makedirs(os.path.dirname(destino), exist_ok=True)
        # Usa PowerShell + .NET para capturar a tela inteira.
        ps = (
            "Add-Type -AssemblyName System.Windows.Forms,System.Drawing; "
            "$b=[System.Windows.Forms.SystemInformation]::VirtualScreen; "
            "$bmp=New-Object System.Drawing.Bitmap($b.Width,$b.Height); "
            "$g=[System.Drawing.Graphics]::FromImage($bmp); "
            "$g.CopyFromScreen($b.Location,[System.Drawing.Point]::Empty,$b.Size); "
            f"$bmp.Save('{destino}'); $g.Dispose(); $bmp.Dispose()"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            check=True,
            capture_output=True,
        )
        return "Print salvo na pasta Imagens."
    except Exception as exc:
        return f"Nao consegui tirar o print. ({exc})"
