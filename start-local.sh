#!/bin/bash
# Start ELE Agent locally for development

set -e

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;90m'
NC='\033[0m'

BACKEND_ONLY=false
WEB_ONLY=false
DESKTOP_ONLY=false
SKIP_INSTALL=false

for arg in "$@"; do
    case $arg in
        --backend-only) BACKEND_ONLY=true ;;
        --web-only) WEB_ONLY=true ;;
        --desktop-only) DESKTOP_ONLY=true ;;
        --skip-install) SKIP_INSTALL=true ;;
    esac
done

header() { echo -e "\n${CYAN}=== $1 ===${NC}"; }
success() { echo -e "${GREEN}✓ $1${NC}"; }
error() { echo -e "${RED}✗ $1${NC}"; }
info() { echo -e "${GRAY}  $1${NC}"; }
warn() { echo -e "${YELLOW}⚠ $1${NC}"; }

# Check prerequisites
header "Checking Prerequisites"

if ! command -v python3 &> /dev/null; then
    error "Python 3.11+ not found"
    exit 1
fi
success "Python: $(python3 --version)"

if ! command -v node &> /dev/null; then
    error "Node.js 20+ not found"
    exit 1
fi
success "Node.js: $(node --version)"
success "npm: $(npm --version)"

# Check .env
ENV_FILE="$ROOT_DIR/.env"
if [ ! -f "$ENV_FILE" ]; then
    warn ".env file not found. Creating from template..."
    cp "$ROOT_DIR/.env.example" "$ENV_FILE"
    warn "Please edit .env with your API keys before continuing!"
    echo "Required: SUPABASE_URL, SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY"
    read -p "Press Enter after editing .env to continue..."
fi

# Install dependencies
if [ "$SKIP_INSTALL" = false ]; then
    header "Installing Dependencies"

    if [ "$WEB_ONLY" = false ] && [ "$DESKTOP_ONLY" = false ]; then
        info "Installing backend dependencies..."
        cd "$ROOT_DIR/backend"
        if [ ! -d ".venv" ]; then
            python3 -m venv .venv
        fi
        source .venv/bin/activate
        pip install -r requirements.txt -q
        pip install -r requirements-dev.txt -q
        success "Backend dependencies installed"
    fi

    if [ "$BACKEND_ONLY" = false ] && [ "$DESKTOP_ONLY" = false ]; then
        info "Installing web dependencies..."
        cd "$ROOT_DIR/web"
        npm install
        success "Web dependencies installed"
    fi

    if [ "$BACKEND_ONLY" = false ] && [ "$WEB_ONLY" = false ]; then
        info "Installing desktop dependencies..."
        cd "$ROOT_DIR/desktop"
        npm install
        success "Desktop dependencies installed"
    fi

    info "Installing CLI..."
    cd "$ROOT_DIR/cli"
    pip install -e . -q
    success "CLI installed"
fi

cd "$ROOT_DIR"

# Start services
header "Starting Services"
PIDS=()

if [ "$WEB_ONLY" = false ] && [ "$DESKTOP_ONLY" = false ]; then
    info "Starting Backend (FastAPI) on http://localhost:8000..."
    cd "$ROOT_DIR/backend"
    source .venv/bin/activate
    uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
    PIDS+=($BACKEND_PID)
    sleep 3
    success "Backend started (PID: $BACKEND_PID)"
fi

if [ "$BACKEND_ONLY" = false ] && [ "$DESKTOP_ONLY" = false ]; then
    info "Starting Web (Next.js) on http://localhost:3000..."
    cd "$ROOT_DIR/web"
    npm run dev &
    WEB_PID=$!
    PIDS+=($WEB_PID)
    sleep 3
    success "Web started (PID: $WEB_PID)"
fi

if [ "$BACKEND_ONLY" = false ] && [ "$WEB_ONLY" = false ]; then
    info "Starting Desktop (Electron)..."
    cd "$ROOT_DIR/desktop"
    npm run dev &
    DESKTOP_PID=$!
    PIDS+=($DESKTOP_PID)
    success "Desktop started (PID: $DESKTOP_PID)"
fi

header "All Services Running"
echo -e "${GREEN}Backend API:  http://localhost:8000${NC}"
echo -e "${GREEN}API Docs:     http://localhost:8000/docs${NC}"
echo -e "${GREEN}Web App:      http://localhost:3000${NC}"
echo -e "${GREEN}Desktop:      Electron window should open${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop all services...${NC}"

# Cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}Stopping services...${NC}"
    for pid in "${PIDS[@]}"; do
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null
        fi
    done
    success "All services stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait
wait