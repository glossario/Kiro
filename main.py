"""Ponto de entrada do Jarvis.

Fluxo:
1. Jarvis cumprimenta.
2. Tenta usar o microfone. Se nao houver, cai para entrada por texto.
3. A cada comando, o cerebro interpreta e o Jarvis responde (falando).
4. Diga/escreva "sair" (ou "tchau") para encerrar.
"""

from __future__ import annotations

from jarvis.cerebro import interpretar
from jarvis.voz import Falador, Ouvinte

_PALAVRAS_SAIR = {"sair", "tchau", "encerrar", "fechar jarvis", "adeus"}


def obter_comando(ouvinte: Ouvinte) -> str:
    """Pega um comando por voz (se disponivel) ou por texto."""
    if ouvinte.disponivel:
        texto = ouvinte.ouvir()
        if texto:
            return texto
        # Se nao reconheceu a voz, oferece o teclado como alternativa.
        return input("Voce (digite, ou Enter para falar de novo): ").lower().strip()
    return input("Voce: ").lower().strip()


def main() -> None:
    falador = Falador()
    ouvinte = Ouvinte()

    if ouvinte.disponivel:
        falador.falar("Ola! Eu sou o Jarvis. Estou te ouvindo. Diga um comando.")
    else:
        falador.falar("Ola! Eu sou o Jarvis. O microfone nao esta disponivel, "
                      "entao vamos por texto. Digite um comando.")

    while True:
        comando = obter_comando(ouvinte)
        if not comando:
            continue
        if any(p in comando for p in _PALAVRAS_SAIR):
            falador.falar("Ate logo!")
            break
        resposta = interpretar(comando)
        falador.falar(resposta)


if __name__ == "__main__":
    main()
