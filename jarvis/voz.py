"""Modulo de voz do Jarvis: fala (TTS) e escuta (STT).

A fala usa duas camadas:
1. Edge TTS (vozes neurais em pt-BR, soam naturais - precisa de internet).
2. pyttsx3 (voz offline do Windows) como reserva automatica.

Foi desenhado para degradar com elegancia: se o microfone ou as
bibliotecas de audio nao estiverem disponiveis, o Jarvis continua
funcionando apenas por texto.
"""

from __future__ import annotations

import asyncio
import os
import tempfile

# ---------------------------------------------------------------------------
# CONFIGURACAO DA VOZ  -- mude aqui para personalizar.
# Vozes pt-BR disponiveis no Edge TTS:
#   pt-BR-FranciscaNeural  (feminina, natural)
#   pt-BR-AntonioNeural    (masculina)
#   pt-BR-ThalitaMultilingualNeural (feminina, multilingue)
# VELOCIDADE: ex. "+0%", "+10%", "-10%".  TOM (pitch): ex. "+0Hz", "+20Hz".
# ---------------------------------------------------------------------------
VOZ_EDGE = "pt-BR-FranciscaNeural"
VELOCIDADE = "+8%"
TOM = "+0Hz"

# ---------------------------------------------------------------------------
# MICROFONE
# Deixe None para usar o microfone padrao do Windows. Se o padrao nao captar
# som, rode:  python -m jarvis.voz   (lista os microfones) e coloque aqui o
# numero (indice) do microfone certo. Ex: MICROFONE_INDICE = 1
# ---------------------------------------------------------------------------
MICROFONE_INDICE = None


def listar_microfones() -> None:
    """Imprime os microfones disponiveis com seus indices."""
    import speech_recognition as sr

    print("Microfones disponiveis (use o numero em MICROFONE_INDICE):")
    for i, nome in enumerate(sr.Microphone.list_microphone_names()):
        print(f"  [{i}] {nome}")


class Falador:
    """Converte texto em fala. Tenta Edge TTS; se falhar, usa pyttsx3."""

    def __init__(self) -> None:
        self._edge_ok = False
        self._engine = None
        self._preparar_edge()
        self._preparar_pyttsx3()

    # ---- Edge TTS (motor principal) --------------------------------------
    def _preparar_edge(self) -> None:
        try:
            import edge_tts  # noqa: F401

            self._edge_ok = True
        except Exception as exc:  # pragma: no cover
            print(f"[voz] Edge TTS indisponivel ({exc}). Usando voz offline.")
            self._edge_ok = False

    def _falar_edge(self, texto: str) -> bool:
        """Gera o audio com Edge TTS e toca. Retorna True se deu certo."""
        try:
            import edge_tts

            caminho = os.path.join(tempfile.gettempdir(), "jovem_aprendiz_fala.mp3")

            async def _gerar() -> None:
                com = edge_tts.Communicate(
                    texto, VOZ_EDGE, rate=VELOCIDADE, pitch=TOM
                )
                await com.save(caminho)

            asyncio.run(_gerar())
            self._tocar(caminho)
            return True
        except Exception as exc:
            print(f"[voz] Falha no Edge TTS ({exc}). Caindo para voz offline.")
            return False

    @staticmethod
    def _tocar(caminho_mp3: str) -> None:
        """Toca o MP3 de forma sincrona usando o Windows Media Player (SAPI)."""
        import subprocess

        # Usa o player nativo do Windows via PowerShell, aguardando terminar.
        ps = (
            "Add-Type -AssemblyName presentationCore; "
            "$p = New-Object System.Windows.Media.MediaPlayer; "
            f"$p.Open([uri]'{caminho_mp3}'); "
            "Start-Sleep -Milliseconds 300; "
            "$p.Play(); "
            "while ($p.NaturalDuration.HasTimeSpan -eq $false) "
            "{ Start-Sleep -Milliseconds 50 }; "
            "Start-Sleep -Seconds $p.NaturalDuration.TimeSpan.TotalSeconds; "
            "$p.Close()"
        )
        subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps],
            check=False,
            capture_output=True,
        )

    # ---- pyttsx3 (reserva offline) ---------------------------------------
    def _preparar_pyttsx3(self) -> None:
        try:
            import pyttsx3

            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", 180)
            self._configurar_voz_pt()
        except Exception as exc:  # pragma: no cover
            self._engine = None
            if not self._edge_ok:
                print(f"[voz] TTS indisponivel, usando apenas texto. Motivo: {exc}")

    def _configurar_voz_pt(self) -> None:
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

    def _falar_offline(self, texto: str) -> None:
        if self._engine is None:
            return
        try:
            self._engine.say(texto)
            self._engine.runAndWait()
        except Exception as exc:  # pragma: no cover
            print(f"[voz] Falha ao falar: {exc}")

    # ---- API publica ------------------------------------------------------
    def falar(self, texto: str) -> None:
        print(f"Jovem Aprendiz: {texto}")
        if self._edge_ok and self._falar_edge(texto):
            return
        self._falar_offline(texto)


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
            # Usa o microfone escolhido no config, ou o padrao do Windows.
            if MICROFONE_INDICE is not None:
                self._microfone = sr.Microphone(device_index=MICROFONE_INDICE)
                print(f"[voz] Usando microfone indice {MICROFONE_INDICE}.")
            else:
                self._microfone = sr.Microphone()
            # Calibra o ruido de fundo uma vez.
            with self._microfone as fonte:
                self._reconhecedor.adjust_for_ambient_noise(fonte, duration=0.6)
            # Garante um minimo de sensibilidade (evita nao captar fala baixa).
            if self._reconhecedor.energy_threshold < 300:
                self._reconhecedor.energy_threshold = 300
            # Reajusta sozinho conforme o ambiente muda.
            self._reconhecedor.dynamic_energy_threshold = True
            self.disponivel = True
        except Exception as exc:  # pragma: no cover - depende do ambiente
            print(f"[voz] Microfone indisponivel, usando entrada por texto. Motivo: {exc}")
            print("[voz] Dica: rode  python -m jarvis.voz  para ver os microfones.")
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


if __name__ == "__main__":
    # Util: "python -m jarvis.voz" lista os microfones para voce descobrir
    # qual indice colocar em MICROFONE_INDICE.
    listar_microfones()
