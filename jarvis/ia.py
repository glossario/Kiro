"""Integracao com a LLM gratuita Google Gemini (biblioteca google-genai).

Le a chave do arquivo .env (GEMINI_API_KEY). Se a chave nao estiver
configurada ou a biblioteca falhar, a IA fica indisponivel e o Jarvis
continua funcionando so com os comandos por palavra-chave.
"""

from __future__ import annotations

import os
import time

_MODELO = "gemini-flash-latest"

_INSTRUCAO_SISTEMA = (
    "Voce e o Jarvis, um assistente pessoal brasileiro. "
    "Responda SEMPRE em portugues do Brasil, de forma curta, clara e direta "
    "(no maximo 2 ou 3 frases, pois a resposta sera falada em voz alta). "
    "Seja amigavel e objetivo. Evite listas longas e simbolos que soam mal "
    "quando lidos em voz alta."
)


class CerebroIA:
    """Mantem uma conversa com o Gemini (com memoria do chat)."""

    def __init__(self) -> None:
        self.disponivel = False
        self._cliente = None  # precisa ficar vivo enquanto o chat existir
        self._chat = None
        self._carregar()

    def _carregar(self) -> None:
        try:
            from dotenv import load_dotenv

            load_dotenv()  # le o arquivo .env da raiz do projeto
            chave = os.getenv("GEMINI_API_KEY", "").strip()
            if not chave or chave == "COLE_SUA_CHAVE_AQUI":
                print("[ia] GEMINI_API_KEY nao configurada no .env. "
                      "IA desativada; usando so comandos por palavra-chave.")
                return

            from google import genai
            from google.genai import types

            self._cliente = genai.Client(api_key=chave)
            self._chat = self._cliente.chats.create(
                model=_MODELO,
                config=types.GenerateContentConfig(
                    system_instruction=_INSTRUCAO_SISTEMA,
                ),
            )
            self.disponivel = True
            print("[ia] Gemini conectado. Jarvis agora entende comandos livres.")
        except Exception as exc:  # pragma: no cover - depende do ambiente/rede
            print(f"[ia] Nao foi possivel iniciar a IA: {exc}")
            self.disponivel = False

    def responder(self, pergunta: str) -> str:
        """Envia a pergunta ao Gemini e devolve a resposta em texto.

        Faz algumas tentativas em caso de sobrecarga temporaria (erro 503),
        que e comum no plano gratuito.
        """
        if not self.disponivel or self._chat is None:
            return "Minha inteligencia nao esta ativa agora."

        ultimo_erro = ""
        for tentativa in range(3):
            try:
                resposta = self._chat.send_message(pergunta)
                texto = (resposta.text or "").strip()
                return texto or "Nao consegui pensar em uma resposta."
            except Exception as exc:
                ultimo_erro = str(exc)
                # 503/UNAVAILABLE/overloaded: vale tentar de novo.
                temporario = any(
                    s in ultimo_erro.lower()
                    for s in ("503", "unavailable", "overloaded", "high demand")
                )
                if temporario and tentativa < 2:
                    time.sleep(1.5 * (tentativa + 1))
                    continue
                break

        return f"Tive um problema ao pensar: {ultimo_erro}"
