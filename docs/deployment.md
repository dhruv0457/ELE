# 🚀 ELE Agent Production Deployment Guide

This guide details how to deploy **ELE Agent** in a production environment with maximum security, high availability, monitoring, and automated scaling.

---

## 🏗️ Architecture Overview

ELE Agent production deployment consists of:
1. **AI Agent Backend (FastAPI + Uvicorn)**: Asynchronous REST and WebSocket API running on port `8000`.
2. **Web Dashboard (Next.js + Nginx)**: High-performance web frontend running on port `3000` (or `80`/`443`).
3. **Database**: Persistent SQLite (single-instance) or PostgreSQL (multi-tenant/distributed cluster).
4. **Cache & Broker (Optional)**: Redis 7 for high-speed rate-limiting and asynchronous task distribution.
5. **AI Inference Mesh**: Direct integrations with NVIDIA NIM, Google Gemini, OpenAI, Groq, Anthropic, and local Ollama.

---

## 📦 Option 1: Docker Compose (Recommended)

### 1. Prerequisites
- Docker Engine `>= 24.0`
- Docker Compose v2 `>= 2.20`
- Minimum 2 CPU cores, 4 GB RAM

### 2. Setup Environment
Clone the repository and prepare your environment variables:
```bash
git clone https://github.com/your-org/ele.git
cd ele
cp .env.example .env
```

Edit `.env` and provide your production credentials:
```ini
APP_ENV=production
DEBUG=false
JWT_SECRET_KEY=use_a_secure_random_64_character_string
NVIDIA_API_KEY=your_nvidia_nim_api_key
GEMINI_API_KEY=your_gemini_api_key
```

### 3. Deploy
Launch the complete container stack:
```bash
# Linux / macOS
./scripts/deploy.sh

# Windows PowerShell
.\scripts\deploy.ps1

# Or standard Docker Compose command
docker compose up -d --build
```

### 4. Verify Health
```bash
curl -f http://localhost:8000/health
```

---

## 🌐 Option 2: Nginx Reverse Proxy with SSL (HTTPS)

For domain deployment (e.g. `https://ele.yourdomain.com`), use Nginx with Let's Encrypt SSL.

### Sample Nginx Server Block:
```nginx
server {
    listen 80;
    server_name ele.yourdomain.com;
    return 301 https://$host$request_uri;
}

server {
    listen 443 ssl http2;
    server_name ele.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/ele.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/ele.yourdomain.com/privkey.pem;

    # Security Headers
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;

    # Frontend Dashboard
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API & WebSocket Streaming
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## ☁️ Option 3: Cloud Container Platforms

### AWS ECS / Fargate
1. Push images to Amazon ECR (`docker tag ele-backend:latest <account>.dkr.ecr.<region>.amazonaws.com/ele-backend:latest`).
2. Create ECS Task Definition specifying `backend` and `web` containers.
3. Configure AWS Application Load Balancer (ALB) targeting container ports.

### GCP Cloud Run
Deploy backend as a scalable service:
```bash
gcloud run deploy ele-backend \
  --image gcr.io/your-project/ele-backend:latest \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars APP_ENV=production,DEBUG=false
```

---

## 🛠️ Management & Monitoring

| Action | Command |
| :--- | :--- |
| **Check service status** | `docker compose ps` |
| **View live logs** | `docker compose logs -f` |
| **Restart backend** | `docker compose restart backend` |
| **Update to latest code** | `git pull && docker compose up -d --build` |
| **Check health endpoint** | `curl -i http://localhost:8000/health` |
| **Run diagnostics** | `python scripts/verify-production.py` |