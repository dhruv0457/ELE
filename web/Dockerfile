# ==============================================================================
# ELE Agent Web Dashboard - Production Multi-Stage Dockerfile
# ==============================================================================

# --- Stage 1: Build Next.js Application ---
FROM node:20-alpine AS builder

WORKDIR /app

# Install build tools if necessary
RUN apk add --no-cache libc6-compat

# Copy package dependencies
COPY package.json package-lock.json ./
RUN npm ci

# Copy source files
COPY . .

# Set build-time environment arguments
ARG NEXT_PUBLIC_API_URL=""
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
    NEXT_TELEMETRY_DISABLED=1 \
    NODE_ENV=production

# Build static export
RUN npm run build

# --- Stage 2: Production Nginx Server ---
FROM nginx:alpine AS runner

WORKDIR /usr/share/nginx/html

# Remove default nginx static assets
RUN rm -rf ./*

# Copy static assets from builder stage
COPY --from=builder /app/out ./

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Security and cache settings
RUN chmod -R 755 /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost:80/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
