# SubBot Admin Panel - Angular Frontend

Professional Angular SPA for managing Telegram subscription bot.

## Quick Start

```bash
# Install dependencies
npm install

# Development server
npm start

# Build for production
npm run build:prod
```

## Architecture

### Directory Structure

```
src/
├── app/
│   ├── core/
│   │   ├── services/       # Auth, API, Notifications
│   │   ├── guards/         # Route protection
│   │   ├── interceptors/   # HTTP interceptors (JWT)
│   │   ├── models/         # TypeScript interfaces
│   │   └── core.module.ts
│   ├── features/
│   │   ├── auth/           # Login, logout
│   │   ├── dashboard/      # Stats, analytics
│   │   ├── channels/       # Channel management
│   │   ├── users/          # User management
│   │   ├── payments/       # Transactions
│   │   └── broadcasts/     # Message broadcasting
│   ├── shared/             # Common components, pipes
│   ├── app-routing.module.ts
│   ├── app.module.ts
│   └── app.component.ts
├── environments/           # Environment config
├── assets/                 # Images, i18n
└── index.html
```

### Core Services

- **AuthService** - JWT token management, login/logout
- **ApiService** - REST API client with typed endpoints
- **NotificationService** - Toast notifications

### Security

- **AuthGuard** - Protects routes, requires authentication
- **AuthInterceptor** - Injects JWT token, handles 401 refresh

## Features

- ✅ JWT-based authentication
- ✅ Automatic token refresh
- ✅ CRUD operations for all resources
- ✅ Real-time dashboard with charts
- ✅ Uzbek language (i18n)
- ✅ Responsive Bootstrap 5 design
- ✅ Toast notifications

## API Integration

Communicates with Django REST API at `/api/v1/`:

- Authentication: `/auth/token/`, `/auth/token/refresh/`
- Resources: `/users/`, `/channels/`, `/subscriptions/`, `/transactions/`, `/broadcasts/`
- Dashboard: `/dashboard/stats/`

## Technologies

- **Angular 18** - Frontend framework
- **TypeScript 5.3** - Typed JavaScript
- **Bootstrap 5** - CSS framework
- **ng-bootstrap** - Bootstrap components for Angular
- **RxJS** - Reactive programming
- **ngx-toastr** - Notifications
- **ngx-translate** - Internationalization
- **Chart.js** - Charts & analytics

## Development

```bash
# Format code
npm run format

# Run tests
npm test

# Lint
npm run lint
```

## Production Build

```bash
# Build optimized bundle
npm run build:prod

# Output directory
dist/auto-contact-bot-frontend/
```

## Environment Configuration

Update `src/environments/environment.prod.ts`:

```typescript
export const environment = {
  production: true,
  apiUrl: 'https://yourdomain.com/api/v1',
  baseUrl: 'https://yourdomain.com',
};
```

## Docker

```dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build:prod

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

## Documentation

See [FRONTEND_SETUP.md](./FRONTEND_SETUP.md) for detailed setup guide.

---

**Status:** Phase 2 - Core infrastructure ready  
**Next:** Implement feature modules (auth, dashboard, resources)
