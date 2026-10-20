"""Utilitario para descobrir qual microfone capta a sua voz.

Como usar:
    .\.venv\Scripts\python.exe testar_microfone.py

Ele testa os microfones reais, um de cada vez. Em cada teste, FALE por
3 segundos. Ele mostra o nivel de som captado e tenta reconhecer o que
voce disse. O microfone com nivel ALTO e que reconhecer sua fala e o
certo - anote o indice e coloque em MICROFONE_INDICE no arquivo
jarvis/voz.py.
"""

from __future__ import annotations

import speech_recognition as sr

# Testamos apenas alguns indices representativos (os 3 microfones reais,
# em sua primeira ocorrencia). Ajuste se quiser testar outros.
INDICES_PARA_TESTAR = [1, 2, 3]


def testar(indice: int) -> None:
    nomes = sr.Microphone.list_microphone_names()
    if indice >= len(nomes):
        print(f"[{indice}] (nao existe)")
        return
    nome = nomes[indice]
    print("\n" + "=" * 60)
    print(f"Testando microfone [{indice}]: {nome}")
    print("FALE AGORA por 3 segundos...")
    r = sr.Recognizer()
    try:
        with sr.Microphone(device_index=indice) as fonte:
            r.adjust_for_ambient_noise(fonte, duration=0.4)
            audio = r.listen(fonte, timeout=4, phrase_time_limit=3)
        nivel = max(audio.frame_data) if audio.frame_data else 0
        print(f"  Som captado: {len(audio.frame_data)} bytes")
        try:
            texto = r.recognize_google(audio, language="pt-BR")
            print(f"  >>> RECONHECEU: '{texto}'  <-- ESTE MICROFONE FUNCIONA!")
        except sr.UnknownValueError:
            print("  Captou algo, mas nao reconheceu palavras.")
    except sr.WaitTimeoutError:
        print("  Nada captado (microfone mudo ou sem sinal).")
    except Exception as exc:
        print(f"  Erro: {exc}")


def main() -> None:
    print("Vamos descobrir qual microfone capta a sua voz.")
    print("Em cada teste, fale normalmente por 3 segundos.")
    for indice in INDICES_PARA_TESTAR:
        input(f"\nPressione ENTER para testar o microfone [{indice}]...")
        testar(indice)
    print("\n" + "=" * 60)
    print("Pronto! Pegue o indice que RECONHECEU sua fala e coloque em")
    print("MICROFONE_INDICE no topo de jarvis/voz.py")


if __name__ == "__main__":
    main()
