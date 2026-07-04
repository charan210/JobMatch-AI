# AI Recruitment Automation System (ARAS)

> An AI-powered recruitment platform that automates resume screening, candidate ranking, skill gap analysis, and recruitment intelligence using Explainable AI (XAI), semantic search, and Large Language Models.

---

## Project Status

**Current Phase:** Core AI & Async Pipeline Development

**Version:** v0.2.0

**Development Status:**

- ✅ Project Foundation
- ✅ Backend Architecture
- ✅ Database Models
- ✅ Authentication & User Management
- ✅ Resume Upload API
- ✅ Async Job Architecture (Celery + Redis)
- ✅ Resume Parsing Pipeline (AI Engine)
- ✅ PostgreSQL + pgvector Integration
- ✅ AI Services (Summaries, Skill Gap, Interviews)
- ✅ End-to-End API Validation

---

# Features

## Current (Implemented)

- FastAPI Backend Foundation
- PostgreSQL Database + pgvector
- SQLAlchemy ORM & Alembic Migrations
- Repository & Clean Architecture
- Authentication & User Management
- Resume Upload API
- Async Job Architecture (Celery + Redis)
- Modular AI Engine (Resume Parsing Pipeline)
- AI Candidate Summaries (Gemini API)
- Skill Gap Analysis Engine
- Interview Question Generation
- Docker Support
- GitHub Actions CI
- Comprehensive Project Documentation

## Planned (Frontend Focus)

- React + TypeScript Frontend
- Job Description Analysis UI
- Semantic Candidate Matching UI
- AI Candidate Ranking Dashboard
- Explainable AI (XAI) Visualizations
- Recruiter Dashboard
- Analytics & Reports

---

# Technology Stack

## Backend

- Python 3.12+
- FastAPI
- SQLAlchemy
- Alembic
- PostgreSQL + pgvector
- Pydantic
- Celery
- Redis

## Frontend

- React
- TypeScript
- Vite

## AI

- Sentence Transformers
- Gemini API
- PyMuPDF
- pdfplumber

## DevOps

- Docker
- Docker Compose
- GitHub Actions

---

# Repository Structure

```text
AI-Recruitment-System/
│
├── ai_engine/          # Modular AI services and parsing pipeline
├── backend/            # FastAPI backend, Celery workers, and async jobs
├── frontend/           # React + TypeScript UI
├── deployment/         # Docker Compose and deployment configs
├── docs/               # Project specifications and architecture
├── tests/              # E2E and integration tests
│
├── CONTRIBUTING.md
├── Makefile
└── README.md
```

---

# Documentation

## Requirements

- Project Vision
- Software Requirements Specification (SRS)
- User Stories
- Use Cases
- Competitor Analysis

## Architecture

- High Level Design
- Low Level Design
- Database Design
- API Specification
- UI/UX Design
- AI Model Design
- Async Job Architecture
- Data Governance

## Project Management

- Project Roadmap
- Risk Assessment
- AI Validation Plan

## Validation

- PROJECT_IMPLEMENTATION_STATUS.md
- AUDIT_CHECKLIST.md

---

# Getting Started

## Clone Repository

```bash
git clone https://github.com/nikhil-0123/AI-Recruitment-System.git
cd AI-Recruitment-System
```

---

## Backend

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

pip install -r requirements.txt
pip install -e ../ai_engine
```

Run FastAPI Server:

```bash
uvicorn app.main:app --reload
```

Run Celery Worker:

```bash
# Linux/macOS
celery -A app.tasks.celery_app worker -Q default,ai --loglevel=info

# Windows
celery -A app.tasks.celery_app worker -P solo -Q default,ai --loglevel=info
```

---

## Frontend

```bash
cd frontend

npm install

npm run dev
```

---

## Docker

```bash
docker compose -f deployment/docker-compose.yml up --build
```

---

# Architecture

```text
Frontend
      │
      ▼
FastAPI API Layer  <───> Redis (Message Broker)
      │                     │
      ▼                     ▼
Services              Celery Workers
      │                     │
      ▼                     ▼
Repositories          AI Engine (Resume Parsing)
      │
      ▼
PostgreSQL + pgvector
```

---

# Development Workflow

```text
main
│
develop
│
feature/*
│
fix/*
```

Follow the guidelines in **CONTRIBUTING.md**.

---

# Testing

Backend

```bash
cd backend
pytest
ruff check .
mypy .
```

---

# Development Phase

Current focus is transitioning to the Frontend (Phase 5). The backend async processing integration (Celery), AI pipeline, and API validation are now fully completed and stabilized.

---

# Roadmap

- ✅ Phase 1 – Foundation
- ✅ Phase 2 – Verification
- ✅ Phase 3 – Core APIs & Async Pipeline
- ✅ Phase 4 – AI Services Integration
- 🔄 Phase 5 – Frontend Features
- ⏳ Phase 6 – Production Deployment

---

## License

This project is currently under active development.

Copyright © 2026 Nikhil Chaugule. All rights reserved.

No license has been granted at this stage.
Licensing terms will be finalized before the first public release.

---

# Author

**Nikhil Chaugule**

Bachelor of Engineering (Artificial Intelligence & Data Science)

Savitribai Phule Pune University

---

## Acknowledgements

This project is being developed as a production-oriented AI Recruitment Automation System with a strong emphasis on software engineering best practices, explainable AI, and scalable architecture.
