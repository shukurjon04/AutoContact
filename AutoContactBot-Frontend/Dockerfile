# Multi-stage build for Angular frontend
FROM node:20-alpine as builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci

# Copy source code
COPY . .

# Build production bundle
RUN npm run build:prod

# Production stage - Nginx
FROM nginx:alpine

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Copy built application from builder
COPY --from=builder /app/dist/auto-contact-bot-frontend /usr/share/nginx/html

# Create non-root user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

# Set permissions
RUN chown -R appuser:appgroup /usr/share/nginx/html /var/cache/nginx /var/log/nginx

USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://localhost/index.html || exit 1

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
