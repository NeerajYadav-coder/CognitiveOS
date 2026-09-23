# CognitiveOS Development Standards

This document outlines the core engineering principles, development standards, and architectural decisions for the CognitiveOS project.

## Engineering Principles

1.  **Strict Modularity**: Each component and engine must have a single, well-defined responsibility.
2.  **Clean Architecture**: Separation of concerns is paramount. The interface (Next.js, extension) must be completely decoupled from the cognitive logic (Python FastAPI backend).
3.  **Pipelines over Monoliths**: Complex cognitive tasks must be broken down into discrete pipeline stages (Intent, Mode, Ambiguity, Vocabulary, Thought, Synthesis).
4.  **Schema-First Design**: Define all data models using Pydantic (Python) and Zod/TypeScript interfaces (Frontend).
5.  **Reusable Engines**: Engines should be stateless and reusable across different pipelines.

## Monorepo Architecture

The project is structured as a `pnpm` workspace using `turbo` for task orchestration.

### Directory Structure

*   `apps/`: Applications (Next.js web, Plasmo extension, FastAPI API).
*   `packages/`: Shared libraries, configuration, and distinct cognitive engines.
*   `docs/`: Project documentation.
*   `infrastructure/`: Deployment configurations (Docker, CI/CD).

## Backend Standards (Python/FastAPI)

*   **Typing**: Strict type hinting is mandatory. Use `mypy` for validation.
*   **Validation**: Use Pydantic V2 for all incoming and outgoing data structures.
*   **Logging**: Use structured JSON logging provided in `src.utils.logger`.
*   **Error Handling**: Raise subclasses of `CognitiveError` for known failure modes. Use the global exception handlers provided in `src.utils.exceptions`.
*   **Orchestration**: Direct LLM calls should be managed through orchestration pipelines, not directly inside routing logic.

## Frontend Standards (TypeScript/React)

*   **Styling**: Use TailwindCSS. Avoid custom CSS files unless strictly necessary.
*   **State Management**: Use React Context for UI state, and React Query or SWR for remote data fetching.
*   **Typing**: Strict TypeScript is mandatory. Avoid `any` at all costs.
*   **Shared Components**: Build robust, accessible components in the `@cognitive-os/ui` package.

## Dependency Management Strategy

*   **Node**: All node packages should be managed via `pnpm` at the root workspace level. Version conflicts must be resolved in `pnpm-workspace.yaml`.
*   **Python**: Dependencies are managed via `requirements.txt` (or equivalent `poetry`/`pipenv` if migrated later). Use isolated virtual environments for development.

## Environment Management Strategy

*   Do not commit `.env` files.
*   Use `.env.example` to document required environment variables.
*   In local development, use a local `.env` file loaded by Next.js and FastAPI respectively.
*   In production, environment variables should be injected via Docker/Kubernetes secrets.

## Docker and Infrastructure

*   Use `docker-compose.yml` for local orchestration (Postgres, Redis, API, Web).
*   Production Dockerfiles should use multi-stage builds to minimize image sizes.
*   All images must run as non-root users in production.

## Linting and Formatting

*   **JavaScript/TypeScript**: ESLint and Prettier are configured globally via `@cognitiveos/eslint-config`.
*   **Python**: Use `ruff` for fast linting and formatting.

## API Base Architecture

*   RESTful principles apply for synchronous operations.
*   WebSockets or Server-Sent Events (SSE) should be used for streaming cognitive pipeline results.
*   All endpoints must include rate limiting and appropriate authentication/authorization layers.
