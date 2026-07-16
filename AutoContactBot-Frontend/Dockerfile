# Multi-stage build for Angular frontend
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --legacy-peer-deps

# Copy source code
COPY . .

# Build production bundle
RUN npm run build:prod

# Production stage - Nginx
FROM nginx:alpine

# Copy nginx configuration template
COPY nginx.conf.template /etc/nginx/templates/default.conf.template

# Copy built application from builder
COPY --from=builder /app/dist/auto-contact-bot-frontend /usr/share/nginx/html

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/index.html || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
