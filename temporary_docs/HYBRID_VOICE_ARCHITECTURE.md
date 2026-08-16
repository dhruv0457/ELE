# Hybrid Voice Architecture - Online/Offline Voice Engines

## Overview

The voice system must work **seamlessly both online and offline** with automatic fallback. The user wants maximum efficiency in both modes.

---

## Architecture: Dual-Engine with Auto-Fallback

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

---

## STT (Speech-to-Text) Engines

### Online: Whisper API (Primary)
```python
# backend/app/voice/stt_whisper.py
class WhisperSTT:
    """OpenAI Whisper API - High accuracy, multi-language"""
    
    def __init__(self, api_key: str, model: str = "whisper-1"):
        self.client = AsyncOpenAI(api_key=api_key)
        self.model = model
    
    async def transcribe(self, audio_bytes: bytes, language: str = "en") -> str:
        # Convert to proper format (webm/mp4/mpeg/mpga/m4a/wav)
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

**Pros**: Best accuracy, handles accents/noise, multi-language, no local model
**Cons**: Needs internet, API cost (~$0.006/min), latency ~500ms

### Offline: Vosk (Fallback)
```python
# backend/app/voice/stt_vosk.py
class VoskSTT:
    """Vosk - Offline, fast, decent accuracy"""
    
    def __init__(self, model_path: str = "~/.ele-agent/vosk-model"):
        self.model = Model(model_path)
        self.recognizer = KaldiRecognizer(self.model, 16000)
    
    async def transcribe(self, audio_bytes: bytes) -> str:
        # Vosk expects 16kHz mono PCM
        pcm_audio = self._convert_to_pcm16k(audio_bytes)
        
        if self.recognizer.AcceptWaveform(pcm_audio):
            result = json.loads(self.recognizer.Result())
            return result.get("text", "")
        else:
            # Partial result
            partial = json.loads(self.recognizer.PartialResult())
            return partial.get("partial", "")
```

**Model Sizes** (download to `~/.ele-agent/vosk-model/`):
| Model | Size | Speed | Accuracy | Best For |
|-------|------|-------|----------|----------|
| `vosk-model-small-en-us-0.15` | 40 MB | Fastest | Good | Real-time, low CPU |
| `vosk-model-en-us-0.22` | 1.8 GB | Medium | Better | Balanced |
| `vosk-model-en-us-0.42` | 2.5 GB | Slower | Best | High accuracy needs |

**Recommendation**: Start with **small model (40 MB)** for speed, upgrade if accuracy insufficient.

---

## TTS (Text-to-Speech) Engines

### Online: Edge-TTS (Primary)
```python
# backend/app/voice/tts_edge.py
class EdgeTTS:
    """Microsoft Edge TTS - Free, high quality, many voices"""
    
    VOICES = {
        "jarvis": "en-GB-RyanNeural",      # British male (Jarvis-like)
        "female": "en-US-AriaNeural",      # US female
        "system": "en-US-GuyNeural",       # US male
        "indian": "en-IN-NeerjaNeural",    # Indian female
        "australian": "en-AU-NatashaNeural", # Australian female
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
```

**Pros**: Free, 400+ voices, natural prosody, SSML support, streaming
**Cons**: Needs internet, Microsoft dependency

### Offline Option 1: pyttsx3 (System TTS)
```python
# backend/app/voice/tts_pyttsx3.py
class Pyttsx3TTS:
    """System TTS - Uses OS voices (SAPI5/NTTS/Espeak)"""
    
    def __init__(self, voice_id: str = None, speed: int = 200):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', speed)
        if voice_id:
            self.engine.setProperty('voice', voice_id)
    
    def synthesize(self, text: str) -> bytes:
        # Save to bytes via temp file
        with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
            self.engine.save_to_file(text, f.name)
            self.engine.runAndWait()
            with open(f.name, 'rb') as audio:
                return audio.read()
```

**Pros**: Zero deps, uses system voices, works everywhere
**Cons**: Robotic quality, limited voice control, blocking

### Offline Option 2: Coqui TTS (Voice Cloning)
```python
# backend/app/voice/tts_coqui.py
class CoquiTTS:
    """Coqui TTS - High quality, voice cloning"""
    
    def __init__(self, model_name: str = "tts_models/en/ljspeech/tacotron2-DDC"):
        self.tts = TTS(model_name).to("cpu")  # or "cuda"
    
    def synthesize(self, text: str, speaker_wav: str = None) -> bytes:
        # If speaker_wav provided, use voice cloning
        if speaker_wav:
            audio = self.tts.tts(text=text, speaker_wav=speaker_wav, language="en")
        else:
            audio = self.tts.tts(text=text)
        return self._array_to_wav_bytes(audio)
```

**Pros**: Best offline quality, voice cloning (30s sample), many models
**Cons**: Heavy (1-2GB models), slower, needs GPU for speed

---

## Voice Manager - Auto-Fallback Logic

```python
# backend/app/voice/manager.py
class VoiceManager:
    """Manages STT/TTS with online/offline auto-fallback"""
    
    def __init__(self, config: VoiceConfig):
        self.config = config
        self.online = True
        self._init_engines()
    
    def _init_engines(self):
        # STT Engines (priority order)
        self.stt_engines = []
        
        # Online: Whisper API
        if config.openai_api_key:
            self.stt_engines.append(("whisper_api", WhisperSTT(config.openai_api_key)))
        
        # Offline: Vosk
        if config.vosk_model_path:
            self.stt_engines.append(("vosk", VoskSTT(config.vosk_model_path)))
        
        # TTS Engines (priority order)
        self.tts_engines = []
        
        # Online: Edge-TTS
        self.tts_engines.append(("edge", EdgeTTS(config.voice, config.speed)))
        
        # Offline: pyttsx3 (always available)
        self.tts_engines.append(("pyttsx3", Pyttsx3TTS()))
        
        # Offline: Coqui (if model exists)
        if config.coqui_model_path:
            self.tts_engines.append(("coqui", CoquiTTS(config.coqui_model_path)))
    
    async def check_connectivity(self) -> bool:
        """Check if online engines can be reached"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("https://api.openai.com", timeout=2) as resp:
                    return resp.status < 500
        except:
            return False
    
    async def transcribe(self, audio: bytes) -> STTResult:
        """Try engines in priority order with fallback"""
        online = await self.check_connectivity()
        
        for name, engine in self.stt_engines:
            if not online and name == "whisper_api":
                continue  # Skip online when offline
            try:
                text = await engine.transcribe(audio)
                return STTResult(text=text, engine=name, online=online)
            except Exception as e:
                logger.warning(f"STT {name} failed: {e}")
                continue
        
        return STTResult(text="", engine="none", error="All engines failed")
    
    async def synthesize(self, text: str) -> TTSResult:
        """Try engines in priority order with fallback"""
        online = await self.check_connectivity()
        
        for name, engine in self.tts_engines:
            if not online and name == "edge":
                continue  # Skip online when offline
            try:
                audio = await engine.synthesize(text)
                return TTSResult(audio=audio, engine=name, online=online)
            except Exception as e:
                logger.warning(f"TTS {name} failed: {e}")
                continue
        
        return TTSResult(audio=b"", engine="none", error="All engines failed")
```

---

## VAD (Voice Activity Detection)

### For Continuous Listening in Autonomous Mode

```python
# backend/app/voice/vad.py
class VADManager:
    """Voice Activity Detection for always-on listening"""
    
    def __init__(self, engine: str = "silero", aggressiveness: int = 3):
        self.engine = engine
        self.aggressiveness = aggressiveness
        self._init_vad()
    
    def _init_vad(self):
        if self.engine == "webrtcvad":
            import webrtcvad
            self.vad = webrtcvad.Vad(self.aggressiveness)
        elif self.engine == "silero":
            import torch
            self.model, _ = torch.hub.load(
                repo_or_dir='snakers4/silero-vad',
                model='silero_vad',
                force_reload=False
            )
    
    def is_speech(self, audio_chunk: bytes, sample_rate: int = 16000) -> bool:
        """Return True if speech detected in chunk"""
        if self.engine == "webrtcvad":
            return self.vad.is_speech(audio_chunk, sample_rate)
        elif self.engine == "silero":
            # Silero expects float32 tensor
            tensor = torch.frombuffer(audio_chunk, dtype=torch.int16).float() / 32768.0
            return self.model(tensor, sample_rate).item() > 0.5
    
    async def stream_vad(self, audio_stream: AsyncIterator[bytes]) -> AsyncIterator[bytes]:
        """Yield speech segments from continuous audio stream"""
        buffer = bytearray()
        in_speech = False
        silence_chunks = 0
        
        async for chunk in audio_stream:
            if self.is_speech(chunk):
                buffer.extend(chunk)
                in_speech = True
                silence_chunks = 0
            elif in_speech:
                buffer.extend(chunk)
                silence_chunks += 1
                # End of utterance: 0.5s silence (32 chunks at 16kHz, 20ms each)
                if silence_chunks >= 32:
                    yield bytes(buffer)
                    buffer = bytearray()
                    in_speech = False
                    silence_chunks = 0
```

### VAD Engine Comparison

| Engine | Accuracy | Speed | Dependencies | Best For |
|--------|----------|-------|--------------|----------|
| `webrtcvad` | Good | Very fast | Pure Python (C ext) | Real-time, low CPU |
| `silero-vad` | Excellent | Fast | PyTorch + ONNX | Best accuracy, noise robustness |

**Recommendation**: **Silero VAD** - better accuracy for continuous listening, handles background noise well. Pre-export to ONNX for no-PyTorch runtime.

---

## Configuration (TOML)

```toml
[voice]
# Engine Selection
stt_priority = ["whisper_api", "vosk"]      # Try order
tts_priority = ["edge", "coqui", "pyttsx3"] # Try order
auto_fallback = true                         # Auto-switch on failure

# Online Engines
[voice.online]
whisper_model = "whisper-1"                  # or "whisper-large-v3"
whisper_language = "en"
edge_voice = "en-GB-RyanNeural"              # Jarvis
edge_speed = 1.0

# Offline Engines
[voice.offline]
# Vosk STT
vosk_model_path = "~/.ele-agent/vosk-model/vosk-model-small-en-us-0.15"
vosk_sample_rate = 16000

# pyttsx3 TTS
pyttsx3_voice_id = ""                        # Empty = system default
pyttsx3_speed = 200                          # Words per minute

# Coqui TTS (Voice Cloning)
coqui_model = "tts_models/en/ljspeech/tacotron2-DDC"
coqui_clone_path = "~/.ele-agent/voice/cloned/my_voice.wav"

# VAD
[voice.vad]
engine = "silero"                            # "webrtcvad" or "silero"
aggressiveness = 3                           # 0-3 (webrtcvad only)
silence_timeout_ms = 500                     # End of utterance
min_speech_ms = 100                          # Minimum speech duration

# Wake Word (Optional in Autonomous Mode)
[voice.wake_word]
enabled = false                              # VAD replaces wake word in auto mode
engine = "porcupine"
keyword = "hey ellie"
sensitivity = 0.5
```

---

## CLI Integration - Voice Pipeline

```
┌────────────────────────────────────────────────────────────────────┐
                    AUTONOMOUS MODE VOICE PIPELINE
└────────────────────────────────────────────────────────────────────┘

Microphone (16kHz mono)
       │
       ▼
┌──────────────────┐
│   Audio Capture  │  ← sounddevice / pyaudio (non-blocking)
│   (callback)     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│   VAD Processor  │  ← Silero VAD (ONNX)
│   (streaming)    │
└────────┬─────────┘
         │ Speech segment detected
         ▼
┌──────────────────┐
│  Voice Manager   │  ← Auto-selects STT engine
│  (STT)           │
└────────┬─────────┘
         │ Transcribed text
         ▼
┌──────────────────┐
│   Agent Core     │  ← Process command, execute tools
│   (LangGraph)    │
└────────┬─────────┘
         │ Response text
         ▼
┌──────────────────┐
│  Voice Manager   │  ← Auto-selects TTS engine
│  (TTS)           │
└────────┬─────────┘
         │ Audio bytes
         ▼
┌──────────────────┐
│  Audio Playback  │  ← sounddevice (non-blocking)
│  (streaming)     │
└──────────────────┘
         │
         ▼
   Ellie speaks + text sync panel updates
```

---

## Directory Structure for Voice Models

```
~/.ele-agent/
├── voice/
│   ├── vosk-model/
│   │   └── vosk-model-small-en-us-0.15/    # 40 MB
│   ├── coqui/
│   │   ├── tts_models--en--ljspeech--tacotron2-DDC/
│   │   └── cloned/
│   │       └── my_voice.wav                 # 30s sample for cloning
│   └── silero-vad/
│       └── silero_vad.onnx                  # Exported ONNX model
```

---

## Installation Commands

```bash
# Online engines (always needed)
pip install openai edge-tts

# Offline engines
pip install vosk pyttsx3

# VAD
pip install silero-vad onnxruntime  # For Silero ONNX
# OR
pip install webrtcvad               # For WebRTC VAD

# Coqui (optional, for voice cloning)
pip install coqui-tts

# Audio I/O
pip install sounddevice numpy

# Download Vosk model
mkdir -p ~/.ele-agent/voice/vosk-model
cd ~/.ele-agent/voice/vosk-model
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip

# Export Silero VAD to ONNX (one-time)
python -c "
import torch
model, _ = torch.hub.load('snakers4/silero-vad', 'silero_vad')
torch.onnx.export(model, torch.randn(1, 512), 'silero_vad.onnx', opset_version=13)
"
```

---

## Questions to Resolve

1. **VAD Engine**: Silero (ONNX) or WebRTC VAD? (Silero recommended for accuracy)
2. **Offline TTS Primary**: pyttsx3 (lightweight) or Coqui (quality)? 
3. **Vosk Model Size**: Small (40MB) or Medium (1.8GB)?
4. **Coqui Voice Cloning**: Set up now or later?
5. **Audio Backend**: `sounddevice` (cross-platform) or `pyaudio`?
6. **Streaming TTS**: Chunk audio playback as it generates (lower latency)?