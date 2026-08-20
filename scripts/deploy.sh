#!/usr/bin/env bash
# ==============================================================================
# ELE Agent - Production Deployment Automation Script (Linux/macOS)
# ==============================================================================
set -euo pipefail

BOLD='\033[1m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${CYAN}${BOLD}"
echo "================================================================="
echo "   ELE AGENT — Production Stack Deployment"
echo "================================================================="
echo -e "${NC}"

# Check Docker & Docker Compose
if ! command -v docker &> /dev/null; then
    echo -e "${RED}[✗] Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo -e "${RED}[✗] Docker Compose v2 is required.${NC}"
    exit 1
fi

echo -e "${GREEN}[✓] Docker and Docker Compose detected.${NC}"

# Ensure .env file exists
if [ ! -f ".env" ]; then
    if [ -f ".env.example" ]; then
        echo -e "${YELLOW}[!] .env file not found. Creating from .env.example...${NC}"
        cp .env.example .env
        echo -e "${YELLOW}[!] Please edit .env with your production API keys and JWT secret before running in production.${NC}"
    else
        echo -e "${RED}[✗] .env.example not found!${NC}"
        exit 1
    fi
fi

# Build and start the production stack
echo -e "${CYAN}[+] Building production container images...${NC}"
docker compose build --pull

echo -e "${CYAN}[+] Starting ELE Agent production stack...${NC}"
docker compose up -d

# Wait for backend healthcheck
echo -e "${CYAN}[+] Waiting for backend healthcheck to report healthy...${NC}"
for i in {1..30}; do
    if curl -s -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}${BOLD}[✓] ELE Backend is healthy!${NC}"
        break
    fi
    echo -n "."
    sleep 2
done

echo ""
echo -e "${GREEN}${BOLD}=================================================================${NC}"
echo -e "${GREEN}${BOLD}   🚀 ELE Agent Production Stack is Live!${NC}"
echo -e "${GREEN}${BOLD}=================================================================${NC}"
echo -e "   • Web Dashboard:   ${CYAN}http://localhost:3000${NC}"
echo -e "   • Backend API:     ${CYAN}http://localhost:8000${NC}"
echo -e "   • API Docs:        ${CYAN}http://localhost:8000/docs${NC}"
echo -e "   • Health Check:    ${CYAN}http://localhost:8000/health${NC}"
echo ""
echo -e "To view logs:         ${YELLOW}docker compose logs -f${NC}"
echo -e "To stop the stack:    ${YELLOW}docker compose down${NC}"
