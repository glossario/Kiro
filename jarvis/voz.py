"""Modulo de voz do Jarvis: fala (TTS) e escuta (STT).

Foi desenhado para degradar com elegancia: se o microfone ou as
bibliotecas de audio nao estiverem disponiveis, o Jarvis continua
funcionando apenas por texto.
"""

from __future__ import annotations


class Falador:
    """Converte texto em fala usando pyttsx3 (offline)."""

    def __init__(self) -> None:
        self._engine = None
        try:
            import pyttsx3

            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", 180)
            self._configurar_voz_pt()
        except Exception as exc:  # pragma: no cover - depende do ambiente
            print(f"[voz] TTS indisponivel, usando apenas texto. Motivo: {exc}")
            self._engine = None

    def _configurar_voz_pt(self) -> None:
        """Tenta escolher uma voz em portugues, se existir no sistema."""
        if self._engine is None:
            return
        try:
            for voz in self._engine.getProperty("voices"):
                nome = (voz.name or "").lower()
                idiomas = " ".join(
                    str(x).lower() for x in getattr(voz, "languages", [])
                )
                if "portug" in nome or "brazil" in nome or "pt" in idiomas:
                    self._engine.setProperty("voice", voz.id)
                    break
        except Exception:
            pass

    def falar(self, texto: str) -> None:
        print(f"Jovem Aprendiz: {texto}")
        if self._engine is None:
            return
        try:
            self._engine.say(texto)
            self._engine.runAndWait()
        except Exception as exc:  # pragma: no cover
            print(f"[voz] Falha ao falar: {exc}")


class Ouvinte:
    """Converte fala em texto usando SpeechRecognition + microfone.

    Se o microfone nao estiver disponivel, `disponivel` fica False e o
    programa deve usar entrada por texto.
    """

    def __init__(self) -> None:
        self.disponivel = False
        self._sr = None
        self._reconhecedor = None
        self._microfone = None
        try:
            import speech_recognition as sr

            self._sr = sr
            self._reconhecedor = sr.Recognizer()
            self._microfone = sr.Microphone()
            # Calibra o ruido de fundo uma vez.
            with self._microfone as fonte:
                self._reconhecedor.adjust_for_ambient_noise(fonte, duration=0.5)
            self.disponivel = True
        except Exception as exc:  # pragma: no cover - depende do ambiente
            print(f"[voz] Microfone indisponivel, usando entrada por texto. Motivo: {exc}")
            self.disponivel = False

    def ouvir(self) -> str | None:
        """Escuta uma frase e devolve o texto reconhecido (ou None)."""
        if not self.disponivel:
            return None
        try:
            with self._microfone as fonte:
                print("[voz] Ouvindo...")
                audio = self._reconhecedor.listen(fonte, timeout=6, phrase_time_limit=8)
            texto = self._reconhecedor.recognize_google(audio, language="pt-BR")
            print(f"Voce (voz): {texto}")
            return texto.lower()
        except self._sr.WaitTimeoutError:
            return None
        except self._sr.UnknownValueError:
            print("[voz] Nao entendi o audio.")
            return None
        except Exception as exc:
            print(f"[voz] Erro ao reconhecer: {exc}")
            return None
