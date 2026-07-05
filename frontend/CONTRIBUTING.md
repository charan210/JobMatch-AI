# Contributing to ARAS Frontend

Thank you for contributing to the AI Recruitment System! To maintain code quality and architectural integrity, please adhere strictly to the following guidelines.

## Project Structure
We utilize a **Feature-Based Architecture**. All logic related to a specific domain (e.g., `auth`, `candidates`) belongs exclusively in its respective `src/features/<domain>` folder. 

## Coding Conventions
- Use **TypeScript** for everything. No `.js` or `.jsx` files.
- Prefer **Functional Components** and React Hooks over class components.
- Use explicit return types on major components and hooks.
- Strictly adhere to `interface` for object shapes instead of `type`.

## Feature Module Rules
1. **Isolation**: A feature must NEVER import from another feature's folder. If code is needed by multiple features, promote it to `src/shared/`.
2. **Internal Structure**: Every feature should typically contain `api/`, `components/`, `hooks/`, `pages/`, `schemas/`, and `types/`.

## Shared Component Rules
- Place all reusable, presentation-only components in `src/shared/components/`.
- Use atomic design principles (`ui/` for buttons/inputs, `feedback/` for loading/errors, `navigation/` for menus).
- Do not inject business logic or API calls directly into shared UI components.

## Routing Conventions
- Global routing is configured exclusively in `src/routes/AppRouter.tsx`.
- Use `<ProtectedRoute>` to guard authenticated domains.
- Use `<PublicRoute>` to explicitly bounce authenticated users away from public pages (like `/login`).

## Service Layer Rules
- Do NOT use Axios directly in components.
- All HTTP requests must go through the pre-configured `apiClient.ts` (which handles interceptors and timeouts).
- `TokenManager` (`tokenManager.ts`) is the *single source of truth* for `localStorage`. Components and Hooks must never call `localStorage.getItem()` directly.

## Authentication Architecture
- Managed natively by `AuthContext`.
- Registration requires `name`, `email`, and `password`.
- Passwords are never logged.
- Login provides standard JWTs. 

## Commit Message Convention
We use conventional commits:
- `feat:` for new features
- `fix:` for bug fixes
- `refactor:` for code changes that neither fix a bug nor add a feature
- `docs:` for documentation updates
- `chore:` for tooling or infrastructure changes

## Lint and Build Requirements
Before committing, you **MUST** ensure:
1. `npm run lint` yields **zero warnings or errors**.
2. `npm run build` completes successfully.
3. No file-level `eslint-disable` rules are used unless fundamentally required (which must be explicitly documented and approved).
