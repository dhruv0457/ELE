# Voice Integration Specification

## Overview

Hybrid voice architecture supporting **both online and offline** operation with automatic fallback. Two modes:

1. **Chat Mode**: Push-to-talk + wake word ("Hey Ellie")
2. **Autonomous Mode**: Continuous listening (VAD) + streaming TTS

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      Voice Manager                               │
│  (Detects connectivity, selects engine, handles fallback)       │
└─────────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┴───────────────┐
              ▼                               ▼
    ┌─────────────────────┐         ┌─────────────────────┐
    │   ONLINE ENGINES    │         │   OFFLINE ENGINES   │
    │  (Primary when      │         │  (Fallback/Primary  │
    │   connected)        │         │   when offline)     │
    └─────────────────────┘         └─────────────────────┘
              │                               │
    ┌─────────┴─────────┐           ┌─────────┴─────────┐
    ▼                   ▼           ▼                   ▼
┌─────────┐         ┌─────────┐ ┌─────────┐         ┌─────────┐
│  STT:   │         │  TTS:   │ │  STT:   │         │  TTS:   │
│ Whisper │         │ Edge-   │ │ Vosk    │         │ pyttsx3 │
│ API     │         │ TTS     │ │         │         │         │
└─────────┘         └─────────┘ └─────────┘         └─────────┘
                                               │
                                               ▼
                                        ┌─────────┐
                                        │  TTS:   │
                                        │ Coqui   │
                                        │ (clone) │
                                        └─────────┘
```

## STT (Speech-to-Text)

### Online: Whisper API (Primary)
```python
# backend/app/voice/stt_whisper.py
class WhisperSTT:
    def __init__(self, api_key: str, model: str = "whisper-1"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> str:
        file = BytesIO(audio_bytes)
        file.name = "audio.webm"
        
        response = await self.client.audio.transcriptions.create(
            model=self.model,
            file=file,
            language=language,
            response_format="text",
            temperature=0.2
        )
        return response.strip()
```
- **Model**: `whisper-1` (or `whisper-large-v3` via API)
- **Cost**: ~$0.006/minute
- **Latency**: ~500ms
- **Languages**: 99+

### Offline: Vosk (Fallback)
```python
# backend/app/voice/stt_vosk.py
class VoskSTT:
    def __init__(self, model_path: str = "~/.ele-agent/voice/vosk-model"):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
    
    async def transcribe(self, audio_bytes: bytes) -> str:
        pcm_audio = self._convert_to_pcm16k(audio_bytes)
        
        if self.recognizer.AcceptWaveform(pcm_audio):
            result = json.loads(self.recognizer.Result())
            return result.get("text", "")
        else:
            partial = json.loads(self.recognizer.PartialResult())
            return partial.get("partial", "")
```

**Model**: `vosk-model-en-us-0.22` (1.8 GB, Medium)
- **Accuracy**: Good for commands/dictation
- **Speed**: Real-time on CPU
- **Languages**: 20+

## TTS (Text-to-Speech)

### Online: Edge-TTS (Primary)
```python
# backend/app/voice/tts_edge.py
class EdgeTTS:
    VOICES = {
        "jarvis": "en-GB-RyanNeural",      # British male (Jarvis-like)
        "female": "en-US-AriaNeural",
        "system": "en-US-GuyNeural",
    }
    
    def __init__(self, voice: str = "jarvis", speed: float = 1.0):
        self.voice = self.VOICES.get(voice, voice)
        self.speed = speed
    
    async def synthesize(self, text: str) -> bytes:
        communicate = edge_tts.Communicate(text, self.voice, rate=f"{int((self.speed-1)*100)}%")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        return audio_data
    
    async def stream_synthesize(self, text: str) -> AsyncGenerator[bytes, None]:
        """Stream audio chunks for lower latency"""
        communicate = edge_tts.Communicate(text, self.voice)
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                yield chunk["data"]
```
- **Voices**: 400+ voices, 140+ languages
- **Quality**: Excellent, natural prosody
- **Streaming**: Chunked playback support
- **Cost**: Free

### Offline: Coqui TTS (Primary Offline)
```python
# backend/app/voice/tts_coqui.py
class CoquiTTS:
    def __init__(self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC", clone_path: str = None):
        self.tts = TTS(model_name).to("cpu")
        self.clone_path = clone_path
    
    def synthesize(self, text: str) -> bytes:
        if self.clone_path:
            audio = self.tts.tts(text=text, speaker_wav=self.clone_path, language="en")
        else:
            audio = self.tts.tts(text=text)
        return self._array_to_wav_bytes(audio)
    
    def stream_synthesize(self, text: str) -> Generator[bytes, None, None]:
        # Coqui doesn't natively stream, chunk the output
        audio = self.synthesize(text)
        for chunk in self._chunk_wav(audio, chunk_size=4096):
            yield chunk
```
- **Models**: Tacotron2, VITS, FastSpeech2
- **Voice Cloning**: 30s sample → custom voice
- **Quality**: High (near-online)
- **Size**: 1-2 GB models

### Offline: pyttsx3 (Ultimate Fallback)
```python
# backend/app/voice/tts_pyttsx3.py
class Pyttsx3TTS:
    def __init__(self, voice_id: str = None, speed: int = 200):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', speed)
        if voice_id:
            self.engine.setProperty('voice', voice_id)
    
    def synthesize(self, text: str) -> bytes:
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            self.engine.save_to_file(text, f.name)
            self.engine.runAndWait()
            with open(f.name, 'rb') as audio:
                return audio.read()
```
- **Voices**: System voices (SAPI5, NSSpeech, espeak)
- **Quality**: Robotic
- **Dependencies**: None (stdlib)
- **Always works**: Ultimate fallback

## VAD (Voice Activity Detection)

### Silero VAD (ONNX)
```python
# backend/app/voice/vad.py
import onnxruntime as ort

class SileroVAD:
    def __init__(self, model_path: str = "~/.ele-agent/voice/silero-vad/silero_vad.onnx"):
        self.session = ort.InferenceSession(model_path)
        self.sample_rate = 16000
        self.window_size = 512  # 32ms at 16kHz
    
    def is_speech(self, audio_chunk: bytes) -> bool:
        # Convert to float32 tensor
        import numpy as np
        audio = np.frombuffer(audio_chunk, dtype=np.int16).astype(np.float32) / 32768.0
        
        # Pad/truncate to window_size
        if len(audio) < self.window_size:
            audio = np.pad(audio, (0, self.window_size - len(audio)))
        else:
            audio = audio[:self.window_size]
        
        # Run inference
        input_tensor = audio.reshape(1, 1, -1)
        prob = self.session.run(None, {"input": input_tensor})[0][0][0]
        
        return prob > 0.5
    
    async def stream_vad(self, audio_stream: AsyncIterator[bytes]) -> AsyncIterator[bytes]:
        """Yield speech segments from continuous audio stream"""
        buffer = bytearray()
        in_speech = False
        silence_chunks = 0
        SILENCE_THRESHOLD = 16  # 0.5s at 32ms chunks
        
        async for chunk in audio_stream:
            if self.is_speech(chunk):
                buffer.extend(chunk)
                in_speech = True
                silence_chunks = 0
            elif in_speech:
                buffer.extend(chunk)
                silence_chunks += 1
                if silence_chunks >= SILENCE_THRESHOLD:
                    yield bytes(buffer)
                    buffer = bytearray()
                    in_speech = False
                    silence_chunks = 0
```

## Voice Manager (Auto-Fallback)

```python
# backend/app/voice/manager.py
class VoiceManager:
    def __init__(self, config: VoiceConfig):
        self.config = config
        self._init_engines()
    
    def _init_engines(self):
        # STT priority order
        self.stt_engines = []
        if self.config.openai_api_key:
            self.stt_engines.append(("whisper_api", WhisperSTT(self.config.openai_api_key)))
        self.stt_engines.append(("vosk", VoskSTT(self.config.vosk_model_path)))
        
        # TTS priority order
        self.tts_engines = []
        self.tts_engines.append(("edge", EdgeTTS(self.config.voice, self.config.speed)))
        if self.config.coqui_model_path:
            self.tts_engines.append(("coqui", CoquiTTS(self.config.coqui_model_path, self.config.coqui_clone_path)))
        self.tts_engines.append(("pyttsx3", Pyttsx3TTS()))
    
    async def check_connectivity(self) -> bool:
        """Check if online engines reachable"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.openai.com", timeout=aiohttp.ClientTimeout(total=2)) as resp:
                    return resp.status < 500
        except:
            return False
    
    async def transcribe(self, audio: bytes) -> STTResult:
        online = await self.check_connectivity()
        
        for name, engine in self.stt_engines:
            if not online and name == "whisper_api":
                continue
            try:
                text = await engine.transcribe(audio)
                return STTResult(text=text, engine=name, online=online)
            except Exception as e:
                logger.warning(f"STT {name} failed: {e}")
                continue
        
        return STTResult(text="", engine="none", error="All engines failed")
    
    async def synthesize(self, text: str, stream: bool = False) -> TTSResult:
        online = await self.check_connectivity()
        
        for name, engine in self.tts_engines:
            if not online and name == "edge":
                continue
            try:
                if stream and hasattr(engine, 'stream_synthesize'):
                    return TTSResult(engine=name, online=online, stream=engine.stream_synthesize(text))
                audio = await engine.synthesize(text) if asyncio.iscoroutinefunction(engine.synthesize) else engine.synthesize(text)
                return TTSResult(audio=audio, engine=name, online=online)
            except Exception as e:
                logger.warning(f"TTS {name} failed: {e}")
                continue
        
        return TTSResult(audio=b"", engine="none", error="All engines failed")
```

## Wake Word (Porcupine)

```python
# backend/app/voice/wake_word.py
import pvporcupine

class PorcupineWakeWord:
    def __init__(self, access_key: str, keyword: str = "hey ellie", sensitivity: float = 0.5):
        self.handle = pvporcupine.create(
            access_key=access_key,
            keywords=[keyword],
            sensitivities=[sensitivity]
        )
    
    def process(self, pcm: bytes) -> bool:
        """Return True if wake word detected"""
        import struct
        pcm_unpacked = struct.unpack_from("h" * self.handle.frame_length, pcm)
        return self.handle.process(pcm_unpacked) >= 0
    
    async def listen(self, audio_stream: AsyncIterator[bytes]) -> AsyncIterator[None]:
        """Yield when wake word detected"""
        async for chunk in audio_stream:
            if self.process(chunk):
                yield
```

## CLI Audio Pipeline

```
┌────────────────────────────────────────────────────────────────────┐
                    AUTONOMOUS MODE VOICE PIPELINE
└────────────────────────────────────────────────────────────────────┘

Microphone (16kHz mono, 32ms chunks)
       │
       ▼
┌──────────────────┐
│   sounddevice    │  ← PortAudio, async callback
│   InputStream    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   Silero VAD     │  ← ONNX Runtime
│   (streaming)    │
└────────┬─────────┘
         │ Speech segment
         ▼
┌──────────────────┐
│  Voice Manager   │  ← Auto-selects STT
│  (STT)           │
└────────┬─────────┘
         │ Text
         ▼
┌──────────────────┐
│   Agent Core     │  ← Process, execute tools
│   (LangGraph)    │
└────────┬─────────┘
         │ Response text
         ▼
┌──────────────────┐
│  Voice Manager   │  ← Auto-selects TTS
│  (TTS streaming) │
└────────┬─────────┘
         │ Audio chunks
         ▼
┌──────────────────┐
│   sounddevice    │  ← OutputStream, non-blocking
│   OutputStream   │
└──────────────────┘
         │
         ▼
   Ellie speaks + conversation panel updates
```

### Chat Mode Pipeline (Push-to-Talk)
```
Mic button pressed → Record → Wake word check → STT → Agent → TTS → Playback
                              ↑
                        Porcupine (always listening in background)
```

## Configuration

```toml
[voice]
stt_priority = ["whisper_api", "vosk"]
tts_priority = ["edge", "coqui", "pyttsx3"]
auto_fallback = true

[voice.online]
whisper_model = "whisper-1"
whisper_language = "en"
edge_voice = "en-GB-RyanNeural"
edge_speed = 1.0

[voice.offline]
vosk_model_path = "~/.ele-agent/voice/vosk-model/vosk-model-en-us-0.22"
vosk_sample_rate = 16000

pyttsx3_voice_id = ""
pyttsx3_speed = 200

coqui_model = "tts_models/en/ljspeech/tacotron2-DDC"
coqui_clone_path = "~/.ele-agent/voice/cloned/my_voice.wav"

[voice.vad]
engine = "silero"
silence_timeout_ms = 500
min_speech_ms = 100

[voice.wake_word]
enabled = true
engine = "porcupine"
keyword = "hey ellie"
sensitivity = 0.5
```

## Model Downloads

```bash
# Vosk Medium (1.8 GB)
mkdir -p ~/.ele-agent/voice/vosk-model
cd ~/.ele-agent/voice/vosk-model
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip

# Silero VAD ONNX
mkdir -p ~/.ele-agent/voice/silero-vad
cd ~/.ele-agent/voice/silero-vad
python -c "
import torch
model, _ = torch.hub.load('snakers4/silero-vad', 'silero_vad')
torch.onnx.export(model, torch.randn(1, 512), 'silero_vad.onnx', opset_version=13)
"

# Coqui TTS Model
mkdir -p ~/.ele-agent/voice/coqui
# Downloaded automatically on first use

# Porcupine keyword file (.ppn)
# Download from Picovoice Console after creating "Hey Ellie" keyword
```

## Installation

```bash
# Online engines
pip install openai edge-tts

# Offline engines
pip install vosk pyttsx3 coqui-tts

# VAD
pip install onnxruntime

# Audio I/O
pip install sounddevice numpy

# Wake word
pip install pvporcupine

# Porcupine keyword file from Picovoice Console
```

## Interrupt Handling (Autonomous Mode)

```python
# When user speaks during TTS playback
class InterruptManager:
    def __init__(self, vad: SileroVAD, tts_player: AudioPlayer):
        self.vad = vad
        self.tts_player = tts_player
        self.interrupted = False
    
    async def monitor_interrupt(self, mic_stream: AsyncIterator[bytes]):
        async for chunk in mic_stream:
            if self.tts_player.is_playing and self.vad.is_speech(chunk):
                # User started speaking during TTS
                self.tts_player.stop()  # Immediate stop
                self.interrupted = True
                return chunk  # Return first speech chunk for STT
```

## Ellie Avatar Sync

```python
# TUI updates during voice pipeline
class VoiceState:
    def __init__(self):
        self.state = "idle"  # idle, listening, thinking, working, speaking, error
        self.transcript = ""
        self.partial = ""
    
    async def on_listening(self):
        self.state = "listening"
        self.partial = ""
        ellie_avatar.set_state("listening")
    
    async def on_partial_stt(self, text: str):
        self.partial = text
        conversation_panel.update_partial(text)
    
    async def on_final_stt(self, text: str):
        self.transcript = text
        self.partial = ""
        conversation_panel.add_user_message(text)
        ellie_avatar.set_state("thinking")
    
    async def on_thinking(self, thought: str):
        conversation_panel.add_thought(thought)
    
    async def on_tool_start(self, tool: str):
        ellie_avatar.set_state("working")
        execution_stream.add_tool_call(tool)
    
    async def on_tts_start(self, text: str):
        self.state = "speaking"
        ellie_avatar.set_state("speaking")
        conversation_panel.add_agent_message(text)
    
    async def on_tts_chunk(self, chunk: bytes):
        audio_player.play_chunk(chunk)
    
    async def on_tts_end(self):
        self.state = "listening"
        ellie_avatar.set_state("listening")
```