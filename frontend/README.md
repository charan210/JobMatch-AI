# ARAS (AI Recruitment System) - Frontend

This is the frontend application for the AI Recruitment System (ARAS), built with React, Vite, TypeScript, and TailwindCSS.

## Architecture Overview

The application strictly adheres to a **Feature-Driven Clean Architecture**:
- **Features**: Highly cohesive, decoupled modules (e.g., `auth`, `jobs`, `candidates`, `resumes`). Features do not import from other features.
- **Shared Infrastructure**: Centralized UI components, layouts, hooks, API clients, and routing utilities.
- **Routing**: Client-side routing managed by React Router.
- **State**: Server-state handled by React Query (future implementation). Auth state handled natively via React Context.
- **Design System**: A shared atomic design system utilizing TailwindCSS and Lucide Icons.

## Folder Structure

```
src/
├── features/          # Self-contained feature modules
│   ├── auth/          # Authentication flows
│   ├── dashboard/     # Dashboard shell
│   ├── jobs/          # Job management
│   ├── candidates/    # Candidate tracking
│   └── resumes/       # AI resume parsing
├── shared/            # Shared infrastructure
│   ├── components/    # Atomic UI (buttons, inputs, cards)
│   ├── hooks/         # Reusable custom hooks
│   ├── layouts/       # Route layouts (DashboardLayout, AuthLayout)
│   ├── lib/           # Third-party instance wrappers (React Query)
│   ├── services/      # Axios instance, Token Management
│   ├── types/         # Global types
│   └── utils/         # Helper functions (cn)
└── routes/            # Global App Router
```

## Environment Variables

Copy `.env.example` to `.env.development` or `.env.production` before starting:

```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
VITE_APP_NAME="ARAS - AI Recruitment"
VITE_ENV=development
VITE_API_TIMEOUT=30000
```

## Development Setup

1. **Install Dependencies**: `npm install`
2. **Start Dev Server**: `npm run dev`
3. **Build**: `npm run build`
4. **Lint**: `npm run lint`

## Authentication Flow

Authentication is deeply integrated into the frontend shell:
- **Registration**: Routes to backend `POST /api/v1/auth/register`. Payload strictly mandates `name`, `email`, and `password`.
- **Login**: Acquires `access_token` and `refresh_token`. Tokens are persisted safely using the singleton `TokenManager`.
- **Axios Interceptor**: `apiClient.ts` intercepts all requests, appending `Authorization: Bearer <token>`. 
- **Session Persistence**: On hard refresh, `AuthContext` asynchronously rehydrates by pinging `/api/v1/users/me`. If a `401 Unauthorized` is encountered, tokens are purged locally and the user is redirected safely to `/login`.

## Frontend Commands

- `npm run dev`: Boot local Vite server.
- `npm run build`: Compile TypeScript and bundle via Vite.
- `npm run lint`: Run ESLint statically against all files.
