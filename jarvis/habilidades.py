"""Habilidades (skills) do Jarvis - as acoes que ele sabe executar.

Cada habilidade recebe o texto do comando do usuario e devolve uma
string com a resposta a ser falada/exibida.
"""

from __future__ import annotations

import datetime
import os
import subprocess
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
