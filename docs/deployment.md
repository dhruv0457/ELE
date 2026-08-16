# ELE Agent Deployment Guide

## Prerequisites

- GitHub account (for CI/CD and releases)
- Oracle Cloud Free Tier account
- Cloudflare account (Pages + DNS)
- Supabase account
- Telegram Bot (via @BotFather)

---

## 1. Supabase Setup

### Create Project
1. Go to https://supabase.com → New Project
2. Choose free tier, set region close to Oracle (e.g., `us-east-1`)
3. Save: **Project URL**, **Anon Key**, **Service Role Key**

### Database Schema
Run in Supabase SQL Editor:
```sql
-- Users (extends auth.users)
create table public.profiles (
  id uuid references auth.users on delete cascade primary key,
  email text,
  tier text default 'free',  -- free, pro, team
  api_key_hash text,         -- platform API key hash
  credits_remaining integer default 100,
  credits_reset_at timestamptz default now(),
  telegram_id bigint unique, -- for whitelist
  settings jsonb default '{}',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Sessions
create table public.sessions (
  id uuid default gen_random_uuid() primary key,
  user_id uuid references public.profiles(id) on delete cascade,
  title text,
  messages jsonb default '[]',
  metadata jsonb default '{}',
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Audit Log (append-only)
create table public.audit_log (
  id bigserial primary key,
  user_id uuid references public.profiles(id) on delete set null,
  action text not null,
  details jsonb,
  ip_address inet,
  created_at timestamptz default now()
);

-- Plugins
create table public.plugins (
  id uuid default gen_random_uuid() primary key,
  name text not null,
  version text not null,
  manifest jsonb not null,
  author_id uuid references public.profiles(id),
  rating numeric(3,2) default 0,
  downloads integer default 0,
  is_approved boolean default false,
  created_at timestamptz default now()
);

-- RLS Policies
alter table public.profiles enable row level security;
alter table public.sessions enable row level security;
alter table public.audit_log enable row level security;

create policy "Users see own profile" on public.profiles
  for select using (auth.uid() = id);

create policy "Users manage own sessions" on public.sessions
  for all using (auth.uid() = user_id);

create policy "Users see own audit" on public.audit_log
  for select using (auth.uid() = user_id);
```

### Auth Providers
Enable in Supabase Auth:
- Email (magic link)
- Google OAuth (add credentials)

---

## 2. Oracle Cloud Free Tier

### Create Instance
1. Oracle Cloud → Compute → Instances → Create Instance
2. Shape: `VM.Standard.A1.Flex` (4 OCPU, 24GB RAM - ARM)
3. Image: Canonical Ubuntu 22.04
4. SSH Keys: Add your public key
5. Network: Allow ports 22, 80, 443, 8000

### Server Setup
```bash
# Connect
ssh ubuntu@<public_ip>

# Install dependencies
sudo apt update && sudo apt install -y \
  python3.11 python3.11-venv python3.11-dev \
  nodejs npm postgresql-client redis-tools \
  nginx certbot python3-certbot-nginx \
  git curl wget unzip rustc cargo

# Python virtual env
python3.11 -m venv /opt/ele-venv
source /opt/ele-venv/bin/activate
pip install --upgrade pip

# Clone repo
cd /opt
git clone https://github.com/yourusername/ele-agent.git
cd ele-agent/backend
pip install -r requirements.txt

# Environment
cp .env.example .env
# Edit .env with your keys
```

### Systemd Service
```ini
# /etc/systemd/system/ele-api.service
[Unit]
Description=ELE Agent API
After=network.target

[Service]
Type=exec
User=ubuntu
WorkingDirectory=/opt/ele-agent/backend
Environment=PATH=/opt/ele-venv/bin
ExecStart=/opt/ele-venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ele-api
```

### Nginx Reverse Proxy
```nginx
# /etc/nginx/sites-available/ele
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
        proxy_send_timeout 300s;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/ele /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
sudo certbot --nginx -d api.yourdomain.com
```

### Oracle Functions (Telegram Webhook)
```bash
# Install Fn CLI
curl -LSs https://raw.githubusercontent.com/fnproject/cli/master/install | sh

# Deploy webhook function
cd /opt/ele-agent/backend
fn deploy --app ele --local
```

---

## 3. Cloudflare Pages (Web Frontend)

### Connect Repository
1. Cloudflare Dashboard → Pages → Create a project
2. Connect to GitHub → Select `ele-agent` repo
3. Build settings:
   - **Framework**: Next.js
   - **Build command**: `cd web && npm run build`
   - **Output directory**: `web/out`
   - **Root directory**: `/`
4. Environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://api.yourdomain.com
   NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
   NEXT_PUBLIC_SUPABASE_ANON_KEY=your-anon-key
   ```

### Custom Domain
1. Pages → Custom domains → Add `app.yourdomain.com`
2. DNS: CNAME `app` → `<project>.pages.dev`

---

## 4. GitHub Actions CI/CD

### Secrets (Repository → Settings → Secrets)
```
SUPABASE_URL
SUPABASE_ANON_KEY
SUPABASE_SERVICE_ROLE_KEY
ORACLE_SSH_KEY
ORACLE_HOST
ORACLE_USER
TELEGRAM_BOT_TOKEN
TELEGRAM_WEBHOOK_SECRET
```

### Workflows

#### CI (`.github/workflows/ci.yml`)
```yaml
name: CI
on: [push, pull_request]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: {python-version: '3.11'}
      - run: cd backend && pip install -r requirements.txt && pip install -r requirements-dev.txt
      - run: cd backend && python -m pytest tests/ -v
      - run: cd backend && python -m ruff check .
      - run: cd backend && python -m mypy .
  
  frontend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: {node-version: '20'}
      - run: cd web && npm ci && npm run build && npm run lint
  
  desktop:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: {node-version: '20'}
      - run: cd desktop && npm ci && npm run build
```

#### Deploy (`.github/workflows/deploy.yml`)
```yaml
name: Deploy
on:
  release:
    types: [published]
jobs:
  backend:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Deploy to Oracle
        uses: appleboy/ssh-action@v1
        with:
          host: ${{ secrets.ORACLE_HOST }}
          username: ${{ secrets.ORACLE_USER }}
          key: ${{ secrets.ORACLE_SSH_KEY }}
          script: |
            cd /opt/ele-agent
            git pull
            cd backend
            /opt/ele-venv/bin/pip install -r requirements.txt
            sudo systemctl restart ele-api
  
  desktop:
    runs-on: windows-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: {node-version: '20'}
      - run: cd desktop && npm ci && npm run build && npm run package
      - uses: softprops/action-gh-release@v1
        with:
          files: desktop/dist/*.exe
```

---

## 5. Telegram Bot

### Create Bot
1. Message @BotFather → `/newbot`
2. Name: `ELE Agent`, Username: `your_ele_bot`
3. Save **Bot Token**

### Set Webhook
```bash
curl -X POST "https://api.telegram.org/bot<TOKEN>/setWebhook" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://api.yourdomain.com/api/v1/telegram/webhook", "secret_token": "<WEBHOOK_SECRET>"}'
```

### Configure Whitelist
In Supabase `profiles` table, set `telegram_id` for authorized users.

---

## 6. Desktop App Distribution

### Code Signing (Optional but Recommended)
```bash
# Windows - self-signed for testing
New-SelfSignedCertificate -Type CodeSigning -Subject "CN=ELE Agent" -CertStoreLocation "Cert:\CurrentUser\My" -KeyUsage DigitalSignature -FriendlyName "ELE Agent"
```

### electron-builder Config (`desktop/build/config.js`)
```js
module.exports = {
  appId: 'com.ele.agent',
  productName: 'ELE Agent',
  copyright: 'MIT License',
  directories: { output: 'dist' },
  files: ['src/**/*', 'package.json', '!**/node_modules/**/*'],
  win: {
    target: ['nsis', 'portable'],
    icon: 'build/icon.ico',
    signtoolOptions: { certificateFile: 'cert.p12', certificatePassword: process.env.CERT_PASSWORD }
  },
  nsis: {
    oneClick: false,
    allowToChangeInstallationDirectory: true,
    createDesktopShortcut: true,
    createStartMenuShortcut: true
  },
  publish: {
    provider: 'github',
    owner: 'yourusername',
    repo: 'ele-agent'
  }
}
```

---

## 7. Local Development

### Backend
```bash
cd backend
cp .env.example .env
# Edit .env
source ../.venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

### Web
```bash
cd web
npm install
npm run dev
# http://localhost:3000
```

### Desktop
```bash
cd desktop
npm install
npm run dev
```

### CLI
```bash
cd cli
pip install -e .
ele --help
```

---

## 8. Monitoring & Logs

### Log Locations
- **Backend**: `journalctl -u ele-api -f`
- **Nginx**: `/var/log/nginx/access.log`, `/var/log/nginx/error.log`
- **Application**: Structured JSON logs to stdout (captured by systemd)

### Health Checks
- `GET /health` → `{status: "ok", version: "1.0.0", uptime: 3600}`
- `GET /health/ready` → Checks DB, Redis, LLM connectivity

### Sentry (Optional)
```python
# backend/app/main.py
import sentry_sdk
sentry_sdk.init(dsn=os.getenv("SENTRY_DSN"), traces_sample_rate=0.1)
```

---

## 9. Backup & Recovery

### Supabase
- Automatic daily backups (7-day retention on free tier)
- Manual: `pg_dump` via Supabase CLI

### Application Data
- Local user data: `~/.ele-agent/` (user responsibility)
- Plugin data: `~/.ele-agent/plugins/`

### Disaster Recovery
1. Redeploy backend from GitHub
2. Restore Supabase from backup
3. Update DNS if needed
4. Users re-authenticate (sessions preserved in Supabase)