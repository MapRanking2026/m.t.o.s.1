# MTOS Technical Architecture

This workspace uses the canonical implementation blueprint in `docs/mtos-architecture.md`.

## Stack

- Frontend: React, Vite, TypeScript, Tailwind CSS, React Router, TanStack Query, Zustand, shadcn/ui patterns
- Backend: FastAPI, Python, Pydantic, async-first service boundaries
- Database: Supabase PostgreSQL, Supabase Auth, Row Level Security
- Infrastructure: Docker, GitHub Actions, environment-driven configuration

## Architectural Priorities

- Tenant isolation and ownership enforcement
- Unified client intelligence before downstream AI workflows
- Prompt-driven AI behavior
- Observable background jobs and approvals
- Production-safe security and auditability

## Build Basis

- Product source of truth: `docs/mtos-prd.md`
- Architecture source of truth: `docs/mtos-architecture.md`
- Delivery source of truth: `docs/mtos-build-plan.md`
