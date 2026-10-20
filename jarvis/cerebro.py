"""Cerebro do Jarvis: interpreta o comando e escolhe o que fazer.

Estrategia hibrida:
1. Primeiro tenta casar com os comandos por palavra-chave (rapido, offline,
   acoes concretas no computador).
2. Se nenhum comando casar, envia a frase para a LLM (Gemini), que responde
   livremente em portugues. Se a IA nao estiver disponivel, mostra uma
   mensagem de ajuda.
"""

from __future__ import annotations

from typing import Callable

from . import habilidades
from .ia import CerebroIA


# Cada regra: (lista de gatilhos, funcao que trata o comando).
# A ordem importa - a primeira regra que casar e usada.
# A ORDEM IMPORTA: a primeira regra que casar e usada. Regras mais
# especificas devem vir antes das mais genericas.
_REGRAS: list[tuple[tuple[str, ...], Callable[[str], str]]] = [
    (("que horas", "horas sao", "hora agora"), habilidades.dizer_hora),
    (("que dia", "data de hoje", "dia de hoje"), habilidades.dizer_data),

    # Controle de volume: vem ANTES de "tocar musica" porque "mudo/volume"
    # sao intencoes especificas (ex: "coloca no mudo" nao e tocar musica).
    (("volume", "aumentar som", "diminuir som", "mudo", "silenciar",
      "mutar", "mais alto", "mais baixo"),
     habilidades.controlar_volume),

    # Tocar musica: vem ANTES de "abrir youtube"/"youtube" para nao conflitar.
    (("tocar musica", "toque musica", "tocar ", "toque ", "coloca ",
      "colocar ", "poe ", "por "),
     habilidades.tocar_musica),

    # Previsao do tempo.
    (("previsao do tempo", "como esta o tempo", "como ta o tempo",
      "tempo em", "clima em", "temperatura em", "clima", "temperatura"),
     habilidades.previsao_tempo),

    # Controle do sistema.
    (("bloquear tela", "bloquear o computador", "travar tela", "trancar tela"),
     habilidades.bloquear_tela),
    (("tirar print", "tira print", "captura de tela", "capturar tela",
      "screenshot", "printar"),
     habilidades.tirar_print),

    (("pesquisar", "pesquise", "buscar", "busque", "procurar", "procure"),
     habilidades.pesquisar_web),
    # So aciona a Wikipedia quando o usuario pede explicitamente "wikipedia".
    # Perguntas gerais de conhecimento ("o que e", "quem foi", "explique")
    # agora vao para a IA, que responde melhor.
    (("wikipedia",), habilidades.wikipedia_resumo),
    (("criar pasta", "crie pasta"), habilidades.criar_pasta),
    (("abrir site", "abrir youtube", "abrir google", "abrir gmail",
      "abrir github", "abrir whatsapp", "youtube", "gmail", "whatsapp"),
     habilidades.abrir_site),
    (("abrir", "abre", "abra"), habilidades.abrir_programa),
]


class Cerebro:
    """Interpreta comandos combinando regras fixas e a IA."""

    def __init__(self) -> None:
        self.ia = CerebroIA()

    def interpretar(self, comando: str) -> str:
        comando = (comando or "").lower().strip()
        if not comando:
            return "Nao entendi. Pode repetir?"

        # 1) Comandos concretos por palavra-chave.
        for gatilhos, acao in _REGRAS:
            if any(g in comando for g in gatilhos):
                return acao(comando)

        # 2) Caiu aqui: deixa a IA responder livremente.
        if self.ia.disponivel:
            return self.ia.responder(comando)

        return (
            "Ainda nao sei fazer isso e minha inteligencia nao esta ativa. "
            "Configure a chave do Gemini no arquivo .env, ou tente: que horas "
            "sao, abrir chrome, pesquisar <algo>, ou criar pasta <nome>."
        )
