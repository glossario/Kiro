"""Cerebro do Jarvis: interpreta o comando e escolhe a habilidade.

Nesta Etapa 1 a interpretacao e por palavras-chave (regras simples).
Na Etapa 2 vamos plugar uma LLM aqui para entender comandos livres.
"""

from __future__ import annotations

from typing import Callable

from . import habilidades


# Cada regra: (lista de gatilhos, funcao que trata o comando).
# A ordem importa - a primeira regra que casar e usada.
_REGRAS: list[tuple[tuple[str, ...], Callable[[str], str]]] = [
    (("que horas", "horas sao", "hora agora"), habilidades.dizer_hora),
    (("que dia", "data de hoje", "dia de hoje"), habilidades.dizer_data),
    (("pesquisar", "pesquise", "buscar", "busque", "procurar", "procure"),
     habilidades.pesquisar_web),
    (("wikipedia", "quem e", "quem foi", "o que e", "me fale sobre"),
     habilidades.wikipedia_resumo),
    (("criar pasta", "crie pasta"), habilidades.criar_pasta),
    (("abrir site", "abrir youtube", "abrir google", "abrir gmail",
      "abrir github", "abrir whatsapp", "youtube", "gmail", "whatsapp"),
     habilidades.abrir_site),
    (("abrir", "abre", "abra"), habilidades.abrir_programa),
]


def interpretar(comando: str) -> str:
    """Recebe o texto do comando e devolve a resposta do Jarvis."""
    comando = (comando or "").lower().strip()
    if not comando:
        return "Nao entendi. Pode repetir?"

    for gatilhos, acao in _REGRAS:
        if any(g in comando for g in gatilhos):
            return acao(comando)

    return (
        "Ainda nao sei fazer isso. Em breve vou aprender com uma "
        "inteligencia artificial. Por enquanto tente: que horas sao, "
        "abrir chrome, pesquisar <algo>, ou criar pasta <nome>."
    )
