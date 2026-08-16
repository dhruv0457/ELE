# ELE Agent API Specification

## Base URL
- **Production**: `https://api.ele-agent.dev/api/v1`
- **Development**: `http://localhost:8000/api/v1`

## Authentication

### JWT (Supabase)
```
Authorization: Bearer <supabase_access_token>
```

### API Key (Platform Credits)
```
X-API-Key: ele_<key_id>_<secret>
```

### API Key (BYOK - User Provided)
```
X-OpenAI-Key: sk-...
X-Gemini-Key: AI...
X-OpenClaw-Key: oc_...
```

## Rate Limits

| Tier | Requests/min | Concurrent | Credits/day |
|------|--------------|------------|-------------|
| Free (BYOK) | 60 | 5 | N/A (user keys) |
| Free (Platform) | 30 | 3 | 100 |
| Pro | 120 | 10 | 1000 |
| Team | 300 | 20 | 5000 |

Headers returned:
```
X-RateLimit-Limit: 60
X-RateLimit-Remaining: 45
X-RateLimit-Reset: 1699900800
```

## REST Endpoints

### Chat

#### Send Message (Non-streaming)
```
POST /chat
Content-Type: application/json

{
  "message": "Open Chrome and go to github.com",
  "interface": "web",           // "web" | "telegram" | "cli" | "desktop"
  "session_id": "uuid",         // optional, for conversation continuity
  "model_preference": "auto",   // "auto" | "openai" | "gemini" | "local" | "openclaw"
  "tools_allowed": ["file", "browser", "shell"],
  "stream": false
}
```

Response:
```json
{
  "session_id": "uuid",
  "response": "I've opened Chrome and navigated to GitHub.",
  "thoughts": [
    "Step 1: Launching Chrome via AppLauncher",
    "Step 2: Navigating to github.com via Browser tool"
  ],
  "screenshots": ["base64..."],
  "tools_used": ["app_launcher", "browser"],
  "duration_ms": 2340,
  "model_used": "gemini"
}
```

#### Stream Chat (WebSocket)
```
WS /ws/chat?session_id=<uuid>&token=<jwt>
```

Client → Server:
```json
{"type": "message", "content": "Create a Python file", "tools": ["file"]}
```

Server → Client (streaming):
```json
{"type": "thought", "content": "Planning: create file with Python template"}
{"type": "tool_start", "tool": "file", "args": {"path": "main.py", "content": "..."}}
{"type": "tool_result", "tool": "file", "success": true, "output": "Created main.py"}
{"type": "screenshot", "data": "base64..."}
{"type": "progress", "current": 1, "total": 2, "step": "Writing file"}
{"type": "final", "content": "Created main.py with basic structure", "session_id": "uuid"}
```

### Sessions

```
GET /sessions                    # List user sessions
GET /sessions/{id}               # Get session with full history
DELETE /sessions/{id}            # Delete session
PATCH /sessions/{id}             # Update session (title, pinned)
```

### Plugins

```
GET /plugins                     # List installed plugins
GET /plugins/marketplace         # Browse marketplace (with filters)
POST /plugins/install            # Install plugin (manifest URL or upload)
DELETE /plugins/{id}             # Uninstall plugin
POST /plugins/{id}/enable        # Enable plugin
POST /plugins/{id}/disable       # Disable plugin
GET /plugins/{id}/manifest       # Get plugin manifest
```

### Voice

```
POST /voice/stt                  # Speech-to-text (multipart audio)
POST /voice/tts                  # Text-to-speech (returns audio)
GET /voice/voices                # List available voices
POST /voice/wake-word/toggle     # Enable/disable wake word
```

### Settings

```
GET /settings                    # Get all settings
PATCH /settings                  # Update settings
GET /settings/api-keys           # List configured API keys (masked)
POST /settings/api-keys          # Add/update API key
DELETE /settings/api-keys/{provider}  # Remove API key
```

### Telegram

```
POST /telegram/webhook           # Telegram webhook endpoint (internal)
GET /telegram/status             # Bot status
POST /telegram/send              # Send message to user (admin only)
```

### Admin (requires admin role)

```
GET /admin/users                 # List users with pagination
GET /admin/users/{id}            # User details (cloud data only)
GET /admin/analytics             # Usage analytics
POST /admin/broadcast            # Broadcast message to users
GET /admin/system/health         # System health check
```

## WebSocket Events

### Client → Server
| Event | Payload | Description |
|-------|---------|-------------|
| `message` | `{content, tools, model}` | Send chat message |
| `interrupt` | `{}` | Stop current agent execution |
| `confirm` | `{action_id, approved}` | Respond to confirmation prompt |
| `ping` | `{}` | Keepalive |

### Server → Client
| Event | Payload | Description |
|-------|---------|-------------|
| `thought` | `{content, node}` | Agent thinking step |
| `tool_start` | `{tool, args}` | Tool execution started |
| `tool_result` | `{tool, success, output, error}` | Tool completed |
| `screenshot` | `{data, timestamp}` | Screen capture |
| `progress` | `{current, total, step}` | Progress update |
| `confirmation_required` | `{action_id, action, description, risk_level}` | Needs user approval |
| `final` | `{content, session_id, metadata}` | Final response |
| `error` | `{code, message, recoverable}` | Error occurred |
| `pong` | `{}` | Keepalive response |

## Error Codes

| Code | HTTP | Description |
|------|------|-------------|
| `AUTH_REQUIRED` | 401 | Missing or invalid authentication |
| `RATE_LIMITED` | 429 | Rate limit exceeded |
| `QUOTA_EXCEEDED` | 402 | Credit quota exceeded |
| `INVALID_REQUEST` | 400 | Malformed request |
| `SESSION_NOT_FOUND` | 404 | Session doesn't exist |
| `PLUGIN_ERROR` | 500 | Plugin execution failed |
| `TOOL_ERROR` | 500 | System tool failed |
| `LLM_ERROR` | 502 | LLM provider error |
| `OFFLINE_MODE` | 503 | Feature unavailable offline |

## OpenAPI Spec

Full OpenAPI 3.1 spec available at `/openapi.json` (served by FastAPI).

Generated from code using `fastapi.openapi.utils.get_openapi()`.