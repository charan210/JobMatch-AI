# Contributing to ARAS

Welcome to the AI Recruitment Automation System (ARAS).

This document defines the development workflow, coding standards, Git strategy, and review process for all contributors.

---

# Project Goals

- Maintain a clean and scalable architecture.
- Follow the approved project documentation.
- Keep the codebase production-ready.
- Prevent architectural drift.
- Ensure all changes are tested before merging.

---

# Development Workflow

Development follows the approved roadmap.

Current Development Phase:

- Frontend Features Integration
- Candidate Dashboard
- Recruiter Dashboard

Focus on transitioning from backend processing to frontend user interfaces.

---

# Git Workflow

## Main Branches

```
main
```

Production-ready releases only.

```
develop
```

Active development.

---

## Feature Branches

Use:

```
feature/<feature-name>
```

Examples

```
feature/authentication

feature/resume-upload

feature/database-models
```

---

## Bug Fixes

```
fix/<issue-name>
```

Example

```
fix/login-validation
```

---

## Refactoring

```
refactor/celery-tasks

refactor/api-endpoints
```

---

## Documentation

```
docs/api-update

docs/database-design
```

---

# Commit Message Convention

Use Conventional Commits.

Examples

```
feat(auth): implement JWT authentication

fix(database): resolve migration issue

docs(api): update authentication endpoints

test(ranking): add repository tests

refactor(service): simplify ranking service

chore(ci): update GitHub workflow
```

---

# Pull Request Rules

Every Pull Request must:

- Build successfully.
- Pass all tests.
- Follow project architecture.
- Update documentation if required.
- Avoid unrelated changes.

---

# Coding Standards

## Python

- Python 3.12+
- Follow PEP 8
- Use type hints
- Use docstrings for public APIs
- Prefer dependency injection
- Keep business logic inside services
- Avoid duplicate code

---

## FastAPI

- Thin API routes
- Business logic inside services
- Database access through repositories
- Validation using Pydantic schemas

---

## Database

- UUID primary keys
- Alembic migrations only
- No direct schema modifications
- Use SQLAlchemy ORM

---

## Frontend

- React + TypeScript
- Functional components
- Reusable UI components
- Avoid inline styles
- Follow ESLint rules

### Feature Module Rules
1. **Isolation**: A feature must NEVER import from another feature's folder. If code is needed by multiple features, promote it to `src/shared/`.
2. **Internal Structure**: Every feature should typically contain `api/`, `components/`, `hooks/`, `pages/`, `schemas/`, and `types/`.

### Shared Component Rules
- Place all reusable, presentation-only components in `src/shared/components/`.
- Use atomic design principles (`ui/` for buttons/inputs, `feedback/` for loading/errors, `navigation/` for menus).
- Do not inject business logic or API calls directly into shared UI components.

### Routing Conventions
- Global routing is configured exclusively in `src/routes/AppRouter.tsx`.
- Use `<ProtectedRoute>` to guard authenticated domains.
- Use `<PublicRoute>` to explicitly bounce authenticated users away from public pages (like `/login`).

### Service Layer Rules
- Do NOT use Axios directly in components.
- All HTTP requests must go through the pre-configured `apiClient.ts` (which handles interceptors and timeouts).
- `TokenManager` (`tokenManager.ts`) is the *single source of truth* for `localStorage`. Components and Hooks must never call `localStorage.getItem()` directly.

---

# Testing

Every feature should include appropriate tests.

Minimum requirements:

- Unit tests
- Integration tests (when applicable)

Tests must pass before merging.

---

# Documentation

When changing architecture or APIs, update the relevant documentation.

Examples:

- SRS
- API Specification
- Database Design
- HLD
- LLD

Implementation should remain consistent with the approved documents.

---

# Code Review Checklist

Before requesting review:

- Code builds successfully.
- Tests pass.
- No unnecessary files.
- No commented-out code.
- No secrets or API keys.
- Documentation updated if needed.
- Imports organized.
- Linting completed.

---

# Security

Never commit:

- `.env`
- API keys
- Passwords
- Tokens
- Database credentials

Use `.env.example` for configuration templates.

---

# AI Development Guidelines

AI assistants (Antigravity, Codex, Copilot, ChatGPT, etc.) must:

- Follow the project architecture.
- Avoid introducing unnecessary dependencies.
- Respect existing folder structure.
- Avoid modifying unrelated files.
- Explain architectural changes before implementation.

---

# Branch Protection

Only merge into `main` after:

- Documentation verified
- Tests passing
- Code review completed
- Audit checklist approved

---

# Architecture Principles

- Clean Architecture
- SOLID Principles
- Repository Pattern
- Service Layer Pattern
- Dependency Injection
- Modular Monolith (Version 1)

---

# Current Status

Completed

✔ Project Foundation
✔ Backend Architecture
✔ Database Layer
✔ Authentication & User Management
✔ Core APIs
✔ Async Processing Pipeline
✔ AI Services (Skill Gap, Gemini Summaries, Interviews)
✔ End-to-End Validation
✔ Frontend Integration & Foundation
✔ UI/UX Design System Implementation
✔ Authentication & Routing Components

Current focus:

• Jobs & Candidates Modules
• React Query Data Fetching
• AI Resume UI Integration

---
