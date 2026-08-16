# API Key Management (BYOK Flow)

## Overview

ELE Agent uses a **Bring Your Own Key (BYOK)** model where users provide their own API keys for LLM providers. Platform keys serve as fallback for users without their own keys.

## Key Priority

```
1. User-provided keys (stored encrypted in Age keyring)
2. Platform keys (from .env, for credits system)
3. No key → Error / Local-only mode
```

## Storage

| Key Type | Storage | Encryption |
|----------|---------|------------|
| User keys | Age-encrypted keyring | Hardware-bound (TPM/Windows Hello) |
| Platform keys | `.env` file | None (file permissions) |
| Supabase keys | `.env` file | None |

## CLI Interface

### First-Run Wizard (API Keys Screen)

```
┌─────────────────────────────────────────────────────────────┐
│  API Keys (All Providers)                    Step 2 of 5    │
├─────────────────────────────────────────────────────────────┤
│  Provide your API keys for each provider. Keys are stored   │
│  securely using hardware-bound encryption.                  │
│                                                             │
│  ┌─ Google Gemini ──────────────────────────────────────┐  │
│  │  [AIzaSy...________________________]  [Test] [Clear]  │  │
│  │  Get key: https://makersuite.google.com/app/apikey    │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─ Groq ────────────────────────────────────────────────┐  │
│  │  [gsk_...____________________________]  [Test] [Clear]  │  │
│  │  Get key: https://console.groq.com/keys               │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─ NVIDIA NIM ──────────────────────────────────────────┐  │
│  │  [nvapi-...___________________________]  [Test] [Clear]  │  │
│  │  Get key: https://build.nvidia.com/explore/discover   │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─ Anthropic Claude ────────────────────────────────────┐  │
│  │  [sk-ant-...__________________________]  [Test] [Clear]  │  │
│  │  Get key: https://console.anthropic.com/settings/keys │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─ OpenAI ──────────────────────────────────────────────┐  │
│  │  [sk-...______________________________]  [Test] [Clear]  │  │
│  │  Get key: https://platform.openai.com/api-keys        │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  [Skip All]                                    [Continue]   │
└─────────────────────────────────────────────────────────────┘
```

### Settings → API Keys (Post-Setup)

```
┌─────────────────────────────────────────────────────────────┐
│  Settings → API Keys                                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─ Google Gemini ──────────────────────────────────────┐  │
│  │  Status: ✓ Configured (gemini-1.5-pro)               │  │
│  │  Key: ••••••••••••••••••••••••••••••••••••••••      │  │
│  │  [Test] [Update] [Remove]                            │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─ Groq ────────────────────────────────────────────────┐  │
│  │  Status: ✓ Configured (llama-3.1-70b)                │  │
│  │  Key: ••••••••••••••••••••••••••••••••••••••••      │  │
│  │  [Test] [Update] [Remove]                            │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─ NVIDIA NIM ──────────────────────────────────────────┐  │
│  │  Status: ✗ Not configured                            │  │
│  │  [Add Key]                                            │  │
│  └───────────────────────────────────────────────────────┘  │
│                                                             │
│  Platform Credits: 847 / 1000  [Upgrade]                   │
└─────────────────────────────────────────────────────────────┘
```

## Key Testing

```python
# backend/app/routes/settings.py
async def test_api_key(provider: str, key: str) -> TestResult:
    """Test if API key is valid by making a minimal request"""
    client = get_llm_client(provider, key)
    try:
        # Minimal test request
        response = await client.complete(
            prompt="Reply with 'OK'",
            model=DEFAULT_MODELS[provider],
            max_tokens=5
        )
        return TestResult(success=True, latency=response.latency)
    except Exception as e:
        return TestResult(success=False, error=str(e))
```

## Encryption (Age + Hardware KDF)

```python
# backend/app/auth/keyring.py
import age
import os

class KeyManager:
    def __init__(self):
        self.keyring_path = os.path.expanduser("~/.ele-agent/keyring.age")
        self._identity = self._get_hardware_identity()
    
    def _get_hardware_identity(self) -> age.Identity:
        # Windows: Use DPAPI/Windows Hello
        # Linux: Use secret-service (libsecret)
        # macOS: Use Keychain
        pass
    
    def encrypt_key(self, provider: str, key: str) -> bytes:
        recipient = age.Recipient(self._identity.public_key())
        encrypted = age.encrypt(key.encode(), [recipient])
        return encrypted
    
    def decrypt_key(self, provider: str, encrypted: bytes) -> str:
        identity = age.Identity(self._identity.private_key())
        decrypted = age.decrypt(encrypted, [identity])
        return decrypted.decode()
    
    def store_key(self, provider: str, key: str):
        encrypted = self.encrypt_key(provider, key)
        # Store in keyring file (one per provider)
        path = f"{self.keyring_path}.{provider}"
        with open(path, "wb") as f:
            f.write(encrypted)
    
    def get_key(self, provider: str) -> Optional[str]:
        path = f"{self.keyring_path}.{provider}"
        if not os.path.exists(path):
            return None
        with open(path, "rb") as f:
            encrypted = f.read()
        return self.decrypt_key(provider, encrypted)
```

## Platform Credits System

```python
# backend/app/routes/settings.py
class CreditManager:
    TIERS = {
        "free": {"daily": 100, "rpm": 30},
        "pro": {"daily": 1000, "rpm": 120},
        "team": {"daily": 5000, "rpm": 300}
    }
    
    async def get_credits(self, user_id: str) -> CreditInfo:
        # Check user tier from Supabase/profile
        tier = await self.get_user_tier(user_id)
        limit = self.TIERS[tier]["daily"]
        
        # Get today's usage from Redis/SQLite
        used = await self.get_daily_usage(user_id)
        
        return CreditInfo(
            tier=tier,
            limit=limit,
            used=used,
            remaining=max(0, limit - used),
            reset_at=next_midnight()
        )
    
    async def consume(self, user_id: str, tokens: int) -> bool:
        if await self.get_credits(user_id).remaining >= tokens:
            await self.increment_usage(user_id, tokens)
            return True
        return False
```

## Backend Key Resolution

```python
# backend/app/agents/llm_clients.py
class KeyResolver:
    def __init__(self, key_manager: KeyManager, platform_keys: PlatformKeys):
        self.key_manager = key_manager
        self.platform_keys = platform_keys
    
    async def get_key(self, user_id: str, provider: str) -> Optional[str]:
        # 1. Try user's BYOK key
        user_key = self.key_manager.get_key(user_id, provider)
        if user_key:
            return user_key
        
        # 2. Fall back to platform key
        platform_key = getattr(self.platform_keys, f"{provider.upper()}_API_KEY")
        if platform_key:
            return platform_key
        
        return None
    
    async def get_available_providers(self, user_id: str) -> List[Provider]:
        available = []
        for provider in ALL_PROVIDERS:
            key = await self.get_key(user_id, provider)
            if key:
                available.append(Provider(provider, key))
        return available
```

## CLI Commands

```bash
# Key management
ele keys list                    # List configured providers
ele keys add gemini              # Interactive add
ele keys test gemini             # Test key validity
ele keys remove gemini           # Remove key
ele keys credits                 # Show platform credits
```

## Security Notes

- Keys never logged (masked in all outputs)
- Keys encrypted at rest with hardware-bound key
- Keys only decrypted in memory during LLM calls
- Platform keys in `.env` - ensure file permissions 600
- No keys transmitted to marketplace/telemetry