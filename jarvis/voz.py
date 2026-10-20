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
# Duas formas de escolher (nesta ordem de prioridade):
#  1. MICROFONE_NOME: parte do nome do microfone (ex: "headset", "intel").
#     E o jeito recomendado, pois nao quebra quando os indices mudam ao
#     conectar/desconectar dispositivos.
#  2. MICROFONE_INDICE: numero fixo (use so se precisar). Deixe None para
#     usar o padrao do Windows.
# Rode  python -m jarvis.voz  para ver os nomes/indices disponiveis.
# ---------------------------------------------------------------------------
MICROFONE_NOME = "headset"   # ex: "headset", "intel", ou None
MICROFONE_INDICE = None


def _achar_indice_por_nome(trecho: str):
    """Devolve o indice do primeiro microfone cujo nome contem `trecho`."""
    import speech_recognition as sr

    trecho = trecho.lower()
    for i, nome in enumerate(sr.Microphone.list_microphone_names()):
        if trecho in (nome or "").lower():
            return i
    return None


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
        self.motor = None  # "sounddevice" ou "pyaudio"
        self._sr = None
        self._reconhecedor = None
        self._microfone = None       # usado no modo pyaudio
        self._sd_indice = None       # usado no modo sounddevice
        self._sd_fs = 16000

        # 1) Tenta o motor sounddevice (WASAPI compartilhado, mais robusto
        #    e nao da o erro 'NoneType close' que o PyAudio da pelo .bat).
        if self._tentar_sounddevice():
            self.disponivel = True
            self.motor = "sounddevice"
            return

        # 2) Reserva: PyAudio via speech_recognition.
        try:
            import speech_recognition as sr

            self._sr = sr
            self._reconhecedor = sr.Recognizer()
            self._abrir_microfone(sr)
            self.motor = "pyaudio"
        except Exception as exc:  # pragma: no cover - depende do ambiente
            print(f"[voz] Microfone indisponivel, usando entrada por texto. Motivo: {exc}")
            if "close" in str(exc) or "NoneType" in str(exc):
                print("[voz] Isso costuma acontecer quando OUTRO programa esta "
                      "usando o microfone (ex: Microsoft Teams, Zoom, Meet, "
                      "Discord ou uma chamada no navegador).")
                print("[voz] FECHE esses programas e abra o Jovem Aprendiz de novo.")
            print("[voz] Dica: rode  python -m jarvis.voz  para ver os microfones.")
            self.disponivel = False

    # ---- Motor sounddevice (principal) -----------------------------------
    def _tentar_sounddevice(self) -> bool:
        """Abre o microfone via sounddevice. Retorna True se funcionar."""
        try:
            import sounddevice as sd
            import speech_recognition as sr  # usado so para reconhecer depois

            self._sr = sr
            self._reconhecedor = sr.Recognizer()

            indice = self._achar_indice_sd(sd)
            # Grava um instante para validar que o dispositivo abre mesmo.
            sd.check_input_settings(device=indice, samplerate=self._sd_fs,
                                    channels=1)
            self._sd_indice = indice
            nome = sd.query_devices(indice)["name"] if indice is not None else "padrao"
            print(f"[voz] Microfone pronto (sounddevice): {nome}")
            return True
        except Exception as exc:
            print(f"[voz] sounddevice indisponivel ({exc}). Tentando PyAudio...")
            return False

    @staticmethod
    def _achar_indice_sd(sd):
        """Acha o indice (no sounddevice) do microfone pelo MICROFONE_NOME."""
        if not MICROFONE_NOME:
            return None
        alvo = MICROFONE_NOME.lower()
        for i, dev in enumerate(sd.query_devices()):
            if dev["max_input_channels"] > 0 and alvo in dev["name"].lower():
                return i
        return None

    def _ouvir_sounddevice(self) -> str | None:
        """Grava do microfone via sounddevice e reconhece com o Google.

        Grava enquanto detecta voz (ate ~2s de silencio) com limite de 8s.
        """
        import sounddevice as sd
        import numpy as np

        fs = self._sd_fs
        print("[voz] Ouvindo...")
        try:
            # Grava um bloco fixo de ate 8 segundos.
            duracao = 8
            buffer = sd.rec(int(duracao * fs), samplerate=fs, channels=1,
                            dtype="int16", device=self._sd_indice)
            sd.wait()
        except Exception as exc:
            print(f"[voz] Erro ao gravar: {exc}")
            return None

        audio = np.asarray(buffer).flatten()
        if int(np.abs(audio).max()) < 500:
            # Praticamente silencio: nada dito.
            return None

        # Converte para AudioData do speech_recognition e reconhece.
        try:
            dados = audio.tobytes()
            audio_sr = self._sr.AudioData(dados, fs, 2)  # 2 bytes = int16
            texto = self._reconhecedor.recognize_google(audio_sr, language="pt-BR")
            print(f"Voce (voz): {texto}")
            return texto.lower()
        except self._sr.UnknownValueError:
            print("[voz] Nao entendi o audio.")
            return None
        except Exception as exc:
            print(f"[voz] Erro ao reconhecer: {exc}")
            return None

    def _candidatos(self, sr) -> list:
        """Lista de indices a tentar, em ordem de preferencia.

        Tenta todos os indices que batem com MICROFONE_NOME, depois o
        MICROFONE_INDICE, e por fim o padrao do Windows (None).
        """
        indices: list = []
        nomes = sr.Microphone.list_microphone_names()
        if MICROFONE_NOME:
            alvo = MICROFONE_NOME.lower()
            indices += [i for i, n in enumerate(nomes) if alvo in (n or "").lower()]
        if MICROFONE_INDICE is not None and MICROFONE_INDICE not in indices:
            indices.append(MICROFONE_INDICE)
        indices.append(None)  # microfone padrao do Windows (ultimo recurso)
        return indices

    def _abrir_microfone(self, sr) -> None:
        """Tenta abrir e calibrar cada candidato ate um funcionar."""
        nomes = sr.Microphone.list_microphone_names()
        ultimo_erro = ""
        for indice in self._candidatos(sr):
            try:
                mic = (sr.Microphone(device_index=indice)
                       if indice is not None else sr.Microphone())
                with mic as fonte:
                    self._reconhecedor.adjust_for_ambient_noise(fonte, duration=0.6)
                # Deu certo: guarda e configura a sensibilidade.
                self._microfone = mic
                if self._reconhecedor.energy_threshold < 300:
                    self._reconhecedor.energy_threshold = 300
                self._reconhecedor.dynamic_energy_threshold = True
                self.disponivel = True
                etiqueta = (f"[{indice}] {nomes[indice]}"
                            if indice is not None else "padrao do Windows")
                print(f"[voz] Microfone pronto: {etiqueta}")
                return
            except Exception as exc:
                ultimo_erro = str(exc)
                rotulo = indice if indice is not None else "padrao"
                print(f"[voz] Microfone {rotulo} nao abriu ({exc}). Tentando o proximo...")
        # Nenhum candidato funcionou.
        raise RuntimeError(ultimo_erro or "nenhum microfone disponivel")

    def ouvir(self) -> str | None:
        """Escuta uma frase e devolve o texto reconhecido (ou None)."""
        if not self.disponivel:
            return None
        if self.motor == "sounddevice":
            return self._ouvir_sounddevice()
        # Motor PyAudio (reserva).
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
