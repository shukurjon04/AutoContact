# 🚀 Angular Frontend Setup — Phase 2 Part 1

## ✅ Yaratilgan Fayl va Modullar

### Configuration Files
- `package.json` — Dependencies va scripts
- `angular.json` — Angular build configuration
- `tsconfig.json` — TypeScript compiler options
- `tsconfig.app.json` — App-specific TypeScript config
- `tsconfig.spec.json` — Test TypeScript config
- `.gitignore` — Git ignore patterns
- `README.md` — Project overview

### Environment Configuration
- `src/environments/environment.ts` — Development environment
- `src/environments/environment.prod.ts` — Production environment

### Core Module Infrastructure
- `src/app/core/models/index.ts` — 12+ TypeScript interfaces/models
- `src/app/core/services/auth.service.ts` — JWT authentication
- `src/app/core/services/api.service.ts` — REST API client (40+ endpoints)
- `src/app/core/services/notification.service.ts` — Toast notifications
- `src/app/core/services/index.ts` — Service exports
- `src/app/core/interceptors/auth.interceptor.ts` — JWT injection + error handling
- `src/app/core/guards/auth.guard.ts` — Route protection
- `src/app/core/core.module.ts` — Core module provider setup

### Application Files
- `src/app/app.module.ts` — Root module with imports
- `src/app/app-routing.module.ts` — Lazy-loaded route configuration
- `src/app/app.component.ts` — Root component
- `src/app/app.component.html` — Router outlet
- `src/app/app.component.scss` — Global styles

### Shared Module
- `src/app/shared/shared.module.ts` — Common imports/exports

### Styling
- `src/styles.scss` — Global styles with Bootstrap integration

### Entry Point
- `src/main.ts` — Application bootstrap
- `src/index.html` — HTML entry point

### Directory Structure (Placeholder)
```
src/app/features/
├── auth/                    # Login/logout
├── dashboard/               # Home, analytics
├── channels/                # Channel CRUD
├── users/                   # User management
├── payments/                # Transaction approval
└── broadcasts/              # Broadcasting
```

## 🔑 Key Components Implemented

### 1. **Authentication System**
- **AuthService**: Login, logout, token management, auto-refresh
- **AuthInterceptor**: JWT token injection, 401 handling
- **AuthGuard**: Route protection
- **Features**:
  - ✅ Login with username/password
  - ✅ Store tokens in localStorage
  - ✅ Automatic token refresh (7-day lifecycle)
  - ✅ Logout on 401 Unauthorized

### 2. **REST API Client**
- **ApiService**: Typed HTTP methods for all resources
- **40+ Endpoints** implemented:
  - Users: list, get, update, delete, block/unblock
  - Channels: CRUD + deactivate
  - Tariffs: CRUD
  - Subscriptions: CRUD + extend/cancel
  - Transactions: list, approve, reject, stats
  - Broadcasts: CRUD + launch + recipients
  - Dashboard: stats endpoint
  - Settings: payment settings management

### 3. **Models & Types**
```typescript
- User
- TelegramUser
- Channel, Tariff
- Subscription
- Transaction
- Broadcast
- DashboardStats
- PaymentSettings
- PaginatedResponse<T>
```

### 4. **Notification System**
- **NotificationService**: Toast notifications (success, error, warning, info)
- **Integration**: ngx-toastr for UI
- **Localization**: Uzbek labels built-in

### 5. **Internationalization (i18n)**
- **ngx-translate** configured
- **Default**: Uzbek language
- **Structure**: Ready for additional languages

## 📁 Project Structure

```
AutoContactBot-Frontend/
├── src/
│   ├── app/
│   │   ├── core/                      # Singleton services
│   │   │   ├── guards/
│   │   │   ├── interceptors/
│   │   │   ├── models/
│   │   │   ├── services/
│   │   │   └── core.module.ts
│   │   ├── features/                  # Lazy-loaded modules
│   │   │   ├── auth/
│   │   │   ├── dashboard/
│   │   │   ├── channels/
│   │   │   ├── users/
│   │   │   ├── payments/
│   │   │   └── broadcasts/
│   │   ├── shared/                    # Common components
│   │   ├── app-routing.module.ts
│   │   ├── app.module.ts
│   │   └── app.component.*
│   ├── environments/                  # Environment configs
│   ├── assets/                        # Images, translations
│   ├── main.ts                        # Entry point
│   ├── index.html
│   └── styles.scss                    # Global styles
├── angular.json                       # Build config
├── package.json                       # Dependencies
├── tsconfig.json                      # TypeScript config
├── README.md                          # Project readme
└── FRONTEND_SETUP.md                  # This file
```

## 🔧 Technologies Stack

### Frontend Framework
- **Angular 18** — Modern web framework
- **TypeScript 5.3** — Type-safe JavaScript

### UI & Styling
- **Bootstrap 5** — CSS framework
- **ng-bootstrap** — Bootstrap components
- **SCSS** — Stylesheets

### HTTP & State
- **RxJS 7.8** — Reactive programming
- **HttpClient** — API communication

### Features
- **Chart.js + ng2-charts** — Data visualization
- **ngx-toastr** — Notifications
- **ngx-translate** — Internationalization
- **date-fns** — Date utilities

## 📦 Installation

```bash
# Install dependencies
npm install

# Verify installation
npm list

# Check versions
node -v   # Should be v20+
npm -v    # Should be 10+
```

## 🚀 Development Server

```bash
# Start dev server
npm start

# Open browser
# http://localhost:4200

# Server will auto-reload on file changes
```

## 🏗️ Production Build

```bash
# Build optimized bundle
npm run build:prod

# Output location
# dist/auto-contact-bot-frontend/

# Bundle is production-ready for deployment
```

## 🔒 Security Features

### Authentication
- ✅ JWT tokens (not session-based)
- ✅ Access token: 1 hour
- ✅ Refresh token: 7 days
- ✅ Automatic token refresh on 401

### HTTP Security
- ✅ AuthInterceptor injects Bearer token
- ✅ Error handling for 401/403/5xx errors
- ✅ CORS pre-configured in backend

### Route Protection
- ✅ AuthGuard checks authentication
- ✅ Redirects to login if needed
- ✅ Preserves return URL after login

## 🌐 API Integration

### Base URL Configuration
```typescript
// Development
apiUrl: 'http://localhost:8000/api/v1'

// Production
apiUrl: 'https://api.yourdomain.com/api/v1'
```

### Request Flow
```
1. Component calls ApiService.getUsers()
   ↓
2. ApiService makes HTTP GET request
   ↓
3. AuthInterceptor adds Authorization: Bearer token
   ↓
4. Request sent to /api/v1/users/
   ↓
5. Backend validates JWT and returns data
   ↓
6. Response returned to component
   ↓
7. Component updates view with data
```

## 📚 Routing Architecture

### Lazy Loading
```typescript
{
  path: 'channels',
  loadChildren: () => import('./features/channels/channels.module')
    .then(m => m.ChannelsModule),
  canActivate: [AuthGuard]
}
```

### Protected Routes
- `/:authenticated-only` — All feature routes protected
- `/auth/login` — Public route
- `/` → `/dashboard` — Default redirect

## 🎨 UI Components

### Bootstrap Components Available
- Navbar, Sidebar
- Cards, Buttons
- Forms (input, select, textarea)
- Tables (responsive)
- Modals, Offcanvas
- Badges, Alerts
- Pagination
- Progress bars
- Spinners

### Custom Components (To Build)
- Login form
- Dashboard cards
- User table
- Channel list
- Transaction approval dialog
- Broadcast form
- File upload component

## 🧪 Testing (Ready to Configure)

```bash
# Run unit tests
npm test

# Run with coverage
ng test --code-coverage

# Run e2e tests (after setup)
npm run e2e
```

## 📝 Language Support

### Current
- ✅ Uzbek (uz) - Default
- ✅ Structure ready for English, Russian, etc.

### i18n Setup
```typescript
// Set language
this.translate.use('uz');

// In templates
{{ 'key' | translate }}
```

## 🚢 Deployment

### Docker Build
```dockerfile
docker build -t subbot-frontend:latest .
docker run -p 80:80 subbot-frontend:latest
```

### Nginx Configuration
```nginx
server {
    listen 80;
    root /usr/share/nginx/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
}
```

### Environment Variables
```bash
# .env (frontend)
ANGULAR_APP_API_URL=https://api.yourdomain.com/api/v1
ANGULAR_APP_BASE_URL=https://yourdomain.com
```

## 🔄 Feature Module Pattern

Each feature module follows this structure:

```
feature/
├── pages/
│   ├── list/
│   └── detail/
├── components/
│   ├── form/
│   └── table/
├── services/
│   └── feature.service.ts
├── feature-routing.module.ts
└── feature.module.ts
```

## 📊 State Management (Optional)

For complex state, NgRx can be added:

```bash
npm install @ngrx/store @ngrx/effects
```

```typescript
store/
├── auth/
│   ├── auth.actions.ts
│   ├── auth.reducer.ts
│   ├── auth.effects.ts
│   └── auth.selectors.ts
├── dashboard/
└── ...
```

## 🐛 Debugging

### Chrome DevTools
1. Open Developer Tools (F12)
2. Go to Sources tab
3. Set breakpoints in TypeScript
4. Use Network tab to monitor API calls

### Angular DevTools
```bash
npm install -g @angular/devtools
# Or browser extension
```

## 📖 Next Steps (Phase 2 Part 2)

1. **Implement Auth Module**
   - Login page component
   - Logout functionality
   - Password change

2. **Build Dashboard Module**
   - Statistics cards
   - Charts (revenue, subscribers)
   - Activity feed

3. **Create Resource Modules**
   - Channels: CRUD, tariff management
   - Users: List, detail, block/unblock
   - Transactions: Approve/reject workflow
   - Broadcasts: Create, launch, track

4. **Polish UI**
   - Responsive design
   - Loading states
   - Error boundaries
   - Empty states
   - Dark mode (optional)

5. **Add i18n**
   - Translate all UI strings
   - Add language switcher
   - Support Uzbek, English, Russian

## 🎯 Checklist

- [x] Project structure created
- [x] Core module (services, guards, interceptors) implemented
- [x] API service with 40+ endpoints
- [x] Authentication flow
- [x] Route protection
- [x] Models/types defined
- [x] Bootstrap & ng-bootstrap configured
- [x] i18n structure ready
- [ ] Feature modules implemented (auth, dashboard, etc.)
- [ ] Components built (forms, tables, cards)
- [ ] Testing added
- [ ] Production build tested
- [ ] Docker image built
- [ ] Deployed to staging/production

---

**Status:** ✅ Phase 2 Part 1 Complete - Core Infrastructure Ready  
**Next:** Phase 2 Part 2 - Feature Modules Implementation  
**Date:** 2026-07-13
