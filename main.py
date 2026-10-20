"""Ponto de entrada do Jovem Aprendiz.

Fluxo com palavra de ativacao (modo voz):
1. Ele cumprimenta e fica "dormindo", ouvindo em silencio.
2. Quando voce diz a palavra de ativacao ("Ei Jovem"), ele acorda.
3. Acordado, atende seus comandos normalmente.
4. Apos um tempo sem comandos, ele volta a dormir (precisa chamar de novo).
5. Diga "sair" / "tchau" para encerrar de vez.

No modo texto (sem microfone) nao e preciso a palavra de ativacao: basta
digitar o comando. "Ei Jovem" como prefixo e aceito, mas opcional.
"""

from __future__ import annotations

from jarvis.cerebro import Cerebro
from jarvis.voz import Falador, Ouvinte

# Palavra(s) de ativacao. Incluimos variacoes porque o reconhecimento de voz
# as vezes transcreve diferente ("ei jovem", "e jovem", "a jovem"...).
PALAVRAS_ATIVACAO = ("ei jovem", "e jovem", "ei, jovem", "a jovem", "hey jovem")

# Depois de acordar, ele atende ate este numero de comandos seguidos antes de
# voltar a dormir (sem precisar dizer "Ei Jovem" a cada frase).
COMANDOS_ANTES_DE_DORMIR = 5

_PALAVRAS_SAIR = {"sair", "tchau", "encerrar", "fechar", "adeus"}


def _tem_ativacao(texto: str) -> bool:
    return any(p in texto for p in PALAVRAS_ATIVACAO)


def _remover_ativacao(texto: str) -> str:
    """Tira a palavra de ativacao do inicio, deixando so o comando."""
    for p in PALAVRAS_ATIVACAO:
        if p in texto:
            texto = texto.replace(p, "", 1)
    return texto.strip(" ,.!?")


def _e_saida(texto: str) -> bool:
    return any(p in texto for p in _PALAVRAS_SAIR)


def _loop_voz(falador: Falador, ouvinte: Ouvinte, cerebro: Cerebro) -> None:
    falador.falar(
        "Ola! Eu sou o Jovem Aprendiz. "
        "Quando precisar de mim, diga: Ei Jovem."
    )
    dormindo = True
    restantes = 0

    while True:
        texto = ouvinte.ouvir()
        if not texto:
            continue

        if _e_saida(texto):
            falador.falar("Ate logo!")
            return

        if dormindo:
            # So reage se ouvir a palavra de ativacao.
            if _tem_ativacao(texto):
                dormindo = False
                restantes = COMANDOS_ANTES_DE_DORMIR
                comando = _remover_ativacao(texto)
                if comando:
                    # Ex: "ei jovem que horas sao" -> ja executa o comando.
                    falador.falar(cerebro.interpretar(comando))
                    restantes -= 1
                else:
                    falador.falar("Oi! Pode falar.")
            # Se nao houve ativacao, ignora em silencio (continua dormindo).
            continue

        # Acordado: atende o comando (removendo ativacao se vier junto).
        comando = _remover_ativacao(texto) if _tem_ativacao(texto) else texto
        falador.falar(cerebro.interpretar(comando))
        restantes -= 1
        if restantes <= 0:
            dormindo = True
            falador.falar("Vou descansar. Quando precisar, diga: Ei Jovem.")


def _loop_texto(falador: Falador, cerebro: Cerebro) -> None:
    falador.falar(
        "Ola! Eu sou o Jovem Aprendiz. O microfone nao esta disponivel, "
        "entao vamos por texto. Digite um comando."
    )
    while True:
        texto = input("Voce: ").lower().strip()
        if not texto:
            continue
        if _e_saida(texto):
            falador.falar("Ate logo!")
            return
        # No modo texto a palavra de ativacao e opcional.
        comando = _remover_ativacao(texto) if _tem_ativacao(texto) else texto
        falador.falar(cerebro.interpretar(comando))


def main() -> None:
    falador = Falador()
    ouvinte = Ouvinte()
    cerebro = Cerebro()

    if ouvinte.disponivel:
        _loop_voz(falador, ouvinte, cerebro)
    else:
        _loop_texto(falador, cerebro)


if __name__ == "__main__":
    main()
