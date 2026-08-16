"""Voice Manager - Hybrid STT/TTS with Auto-Fallback"""
import os
import asyncio
import aiohttp
import structlog
from typing import Optional, List, Tuple, Any
from dataclasses import dataclass

logger = structlog.get_logger()


@dataclass
class STTResult:
    text: str
    engine: str
    online: bool
    error: Optional[str] = None


@dataclass
class TTSResult:
    audio: bytes
    engine: str
    online: bool
    error: Optional[str] = None


class WhisperSTT:
    """OpenAI Whisper API"""

    def __init__(self, api_key: str, model: str = "whisper-1"):
        self.api_key = api_key
        self.model = model

    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> str:
        import io
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=self.api_key)

        file = io.BytesIO(audio_bytes)
        file.name = "audio.webm"

        response = await client.audio.transcriptions.create(
            model=self.model,
            file=file,
            language=language,
            response_format="text",
            temperature=0.2,
        )
        return response.strip()


class VoskSTT:
    """Vosk Offline STT"""

    def __init__(self, model_path: str = "~/.ele-agent/vosk-model"):
        self.model_path = os.path.expanduser(model_path)

    async def transcribe(self, audio_bytes: bytes) -> str:
        # Run in thread pool since Vosk is blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self._transcribe_sync, audio_bytes)

    def _transcribe_sync(self, audio_bytes: bytes) -> str:
        try:
            from vosk import Model, KaldiRecognizer
            model = Model(self.model_path)
            rec = KaldiRecognizer(model, 16000)

            # Convert to 16kHz mono PCM if needed
            # For now assume input is already correct format
            if rec.AcceptWaveform(audio_bytes):
                import json
                result = json.loads(rec.Result())
                return result.get("text", "")
            else:
                import json
                partial = json.loads(rec.PartialResult())
                return partial.get("partial", "")
        except Exception as e:
            logger.error("vosk_error", error=str(e))
            return ""


class EdgeTTS:
    """Microsoft Edge TTS"""

    VOICES = {
        "jarvis": "en-GB-RyanNeural",
        "female": "en-US-AriaNeural",
        "system": "en-US-GuyNeural",
    }

    def __init__(self, voice: str = "jarvis", speed: float = 1.0):
        self.voice = self.VOICES.get(voice, voice)
        self.speed = speed

    async def synthesize(self, text: str) -> bytes:
        import edge_tts
        communicate = edge_tts.Communicate(text, self.voice, rate=f"{int((self.speed-1)*100)}%")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data

    async def stream_synthesize(self, text: str):
        import edge_tts
        communicate = edge_tts.Communicate(text, self.voice, rate=f"{int((self.speed-1)*100)}%")
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]


class Pyttsx3TTS:
    """System TTS (offline fallback)"""

    def __init__(self, voice_id: str = None, speed: int = 200):
        self.voice_id = voice_id
        self.speed = speed

    def synthesize(self, text: str) -> bytes:
        import pyttsx3
        import tempfile

        engine = pyttsx3.init()
        engine.setProperty('rate', self.speed)
        if self.voice_id:
            engine.setProperty('voice', self.voice_id)

        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            engine.save_to_file(text, f.name)
            engine.runAndWait()
            with open(f.name, 'rb') as audio:
                return audio.read()


class CoquiTTS:
    """Coqui TTS (offline, high quality)"""

    def __init__(self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC", clone_path: str = None):
        self.model_name = model_name
        self.clone_path = clone_path
        self._tts = None

    def _get_tts(self):
        if self._tts is None:
            from TTS.api import TTS
            self._tts = TTS(self.model_name).to("cpu")
        return self._tts

    def synthesize(self, text: str) -> bytes:
        import tempfile
        import numpy as np
        import scipy.io.wavfile as wavfile

        tts = self._get_tts()
        if self.clone_path:
            audio = tts.tts(text=text, speaker_wav=self.clone_path, language="en")
        else:
            audio = tts.tts(text=text)

        # Convert to WAV bytes
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            wavfile.write(f.name, 22050, np.array(audio))
            with open(f.name, 'rb') as audio_file:
                return audio_file.read()


class VoiceManager:
    """Manages STT/TTS with auto-fallback"""

    def __init__(self, config: Any):
        self.config = config
        self._init_engines()

    def _init_engines(self):
        # STT Engines (priority order)
        self.stt_engines: List[Tuple[str, Any]] = []

        if self.config.get("openai_api_key"):
            self.stt_engines.append(("whisper_api", WhisperSTT(self.config["openai_api_key"])))

        vosk_path = self.config.get("vosk_model_path", "~/.ele-agent/vosk-model")
        self.stt_engines.append(("vosk", VoskSTT(vosk_path)))

        # TTS Engines (priority order)
        self.tts_engines: List[Tuple[str, Any]] = []

        self.tts_engines.append(("edge", EdgeTTS(
            self.config.get("voice", "jarvis"),
            self.config.get("speed", 1.0)
        )))

        coqui_path = self.config.get("coqui_model_path")
        if coqui_path:
            self.tts_engines.append(("coqui", CoquiTTS(
                self.config.get("coqui_model", "tts_models/en/ljspeech/tacotron2-DDC"),
                self.config.get("coqui_clone_path")
            )))

        self.tts_engines.append(("pyttsx3", Pyttsx3TTS()))

    async def check_connectivity(self) -> bool:
        """Check if online engines are reachable"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.openai.com", timeout=aiohttp.ClientTimeout(total=2)) as resp:
                    return resp.status < 500
        except:
            return False

    async def transcribe(self, audio: bytes, language: str = "en") -> STTResult:
        online = await self.check_connectivity()

        for name, engine in self.stt_engines:
            if not online and name == "whisper_api":
                continue
            try:
                if hasattr(engine, 'transcribe'):
                    text = await engine.transcribe(audio, language)
                else:
                    text = await engine.transcribe(audio)
                return STTResult(text=text, engine=name, online=online)
            except Exception as e:
                logger.warning(f"STT {name} failed", error=str(e))
                continue

        return STTResult(text="", engine="none", online=online, error="All engines failed")

    async def synthesize(self, text: str, stream: bool = False) -> TTSResult:
        online = await self.check_connectivity()

        for name, engine in self.tts_engines:
            if not online and name == "edge":
                continue
            try:
                if stream and name == "edge":
                    # Return async generator for streaming
                    return TTSResult(
                        audio=b"",
                        engine=name,
                        online=online,
                        stream=engine.stream_synthesize(text)
                    )
                if hasattr(engine, 'synthesize'):
                    import asyncio
                    if asyncio.iscoroutinefunction(engine.synthesize):
                        audio = await engine.synthesize(text)
                    else:
                        import asyncio
                        audio = await asyncio.get_event_loop().run_in_executor(None, engine.synthesize, text)
                else:
                    audio = await asyncio.get_event_loop().run_in_executor(None, engine.synthesize, text)
                return TTSResult(audio=audio, engine=name, online=online)
            except Exception as e:
                logger.warning(f"TTS {name} failed", error=str(e))
                continue

        return TTSResult(audio=b"", engine="none", online=online, error="All engines failed")