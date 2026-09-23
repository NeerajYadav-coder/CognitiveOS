# CognitiveOS

> **An Operating Layer Between Human Cognition and Artificial Intelligence**  
> *Created by NJ 5.0 (`CreatedBYNJ5.0`)*

CognitiveOS is not a prompt enhancer. It is a **cognitive infrastructure system** — a modular, extensible platform that helps humans discover intent, structure thinking, navigate concepts, and communicate effectively with AI.

---

## Core Philosophy

We are building:
- **NOT** an AI wrapper
- **NOT** a prompt enhancer
- **BUT** a cognitive infrastructure system

The browser extension is only the first interface. The real product is the **Cognitive Engine** architecture.

---

## System Architecture

```
Human Thought
    ↓
Extension / Web Interface
    ↓
API Gateway
    ↓
Cognitive Processing Pipeline
    ├── Intent Engine
    ├── Cognitive Mode Detector
    ├── Ambiguity Analyzer
    ├── Vocabulary Expansion Engine
    ├── Thought Structuring Engine
    ├── Prompt Synthesis Engine
    └── Reflection Engine
    ↓
LLM Interaction Layer
    ↓
Final Cognitive Output
    ↓
User Feedback & Learning Loop
```

---

## Human-AI Interaction & Cognitive Alignment Research

A fundamental breakdown in contemporary human-AI systems is the **semantic misalignment and cognitive friction** between what humans intuitively conceptualize and what AI model architectures expect. Humans think non-linearly, associatively, and with tacit context; LLMs operate on token distributions, structured instructions, and explicit constraints.

CognitiveOS addresses this chasm not by adding superficial prompt wrappers, but by providing an **adaptive cognitive mediator**:
- **Ambiguity Detection & Gentle Clarification**: Distinguishes between fertile exploration and vague confusion, guiding without railroading.
- **Mental Model Frameworks**: Formats ambiguous thoughts into proven frameworks (First Principles, Dialectical Synthesis, Inversion, MECE, Tree of Thoughts, SCQA).
- **Domain Precision & Terminology Bridging**: Dynamically elevates vocabulary to graduate or domain-expert level when discussing technical concepts.
- **Longitudinal Cognitive Profile**: Models user expertise level, verbosity, and reasoning style across sessions.
- **Metacognitive Reflection**: Analyzes past prompts and interactions to help humans become clearer, more disciplined thinkers over time.

---

## Cognitive Engine Architecture

CognitiveOS implements 15 specialized, composable cognitive engines within the FastAPI processing pipeline:

1. **Cognitive Orchestrator**: Heuristic & graph-based pipeline routing engine.
2. **Intent Extraction Engine**: Primary/secondary goal discovery, domain taxonomy, depth classification.
3. **Cognitive Mode Detector**: 10-dimensional thought style classifier (Analytical, Exploratory, Socratic, etc.).
4. **Ambiguity Analysis Engine**: Clarity scoring, vagueness detection, and targeted clarification questions.
5. **Vocabulary Expansion Engine**: Semantic elevation and domain-specific lexicon injection.
6. **Thought Structuring Engine**: Multi-framework restructuring (First Principles, Inversion, Dialectic, etc.).
7. **Prompt Synthesis Engine**: Assembles structured inputs into hyper-effective LLM prompts.
8. **Semantic Knowledge Graph**: Concept node extraction and relational entity mapping.
9. **Cognitive Memory & Profile Engine**: Persistent memory and user intellectual preference modeling.
10. **Metacognitive Reflection Engine**: Prompt evolution tracking and communication insights.
11. **Cognitive Governance Engine**: Alignment, safety boundaries, and constraint enforcement.
12. **Deep Research Engine**: Automated thought exploration and concept branching.
13. **Cognitive Operating System (COS)**: Unified state machine and session orchestrator.
14. **Cognitive Evolution Engine**: Longitudinal adaptation and drift prevention.
15. **Collaborative Cognition Engine**: Multi-agent shared reasoning workflows.

---

## Monorepo Structure

```
CognitiveOS/
├── apps/
│   ├── api/             # FastAPI Python backend (15 Cognitive Engines, SQLAlchemy, Pydantic)
│   ├── web/             # Next.js 15 Web Application (Tailwind CSS, Zustand, Framer Motion)
│   └── extension/       # Plasmo Chrome Extension (MV3, Shadow DOM overlay, React)
│
├── packages/
│   ├── shared-types/    # Shared TypeScript types for contracts & data models
│   ├── ui/              # Shared design system components (Card, Badge, Button, cn)
│   ├── tsconfig/        # Shared TypeScript configurations
│   └── eslint-config/   # Shared linting configs
│
├── infrastructure/      # Docker, Docker Compose, PostgreSQL + pgvector, Redis
├── docs/                # Architectural RFCs and cognitive specs
├── tests/               # End-to-end and integration suites
└── scripts/             # Development, seeding, and migration utilities
```

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **Web Dashboard** | Next.js 15 (App Router) + React 19 + TailwindCSS + Framer Motion |
| **Browser Extension**| Plasmo Framework (Chrome MV3) + React + Isolated Shadow DOM |
| **Cognitive Backend**| FastAPI (Python 3.12) + Pydantic v2 + SQLAlchemy 2.0 (Asyncpg) |
| **LLM Inference** | OpenAI SDK (Supports OpenAI, Groq, Ollama, vLLM via base URL) |
| **Storage & Cache** | PostgreSQL (with pgvector) + Redis |
| **Monorepo Tooling** | Turborepo + pnpm workspaces |

---

## Getting Started

### Prerequisites
- Node.js >= 20
- pnpm >= 9
- Python >= 3.11
- Docker & Docker Compose (optional for local Postgres/Redis)

### Installation

```bash
# Clone the repository
git clone https://github.com/<your-username>/CognitiveOS.git
cd CognitiveOS

# Install Node monorepo dependencies
pnpm install

# Setup Python environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r apps/api/requirements.txt

# Configure environment variables
cp .env.example .env
# Edit .env with your LLM key (Groq, OpenAI, etc.)
```

### Running in Development

```bash
# Start all apps concurrently (Turborepo)
pnpm dev

# Or run individual services:
pnpm dev:web        # Web dashboard on http://localhost:3000
pnpm dev:api        # FastAPI backend on http://localhost:8000
pnpm dev:extension  # Plasmo Chrome MV3 extension
```

### Running Tests

```bash
# Run backend cognitive engine test suite (49 unit tests)
PYTHONPATH=apps/api .venv/bin/pytest apps/api/tests

# Run workspace type-checking
pnpm type-check

# Run web production build
pnpm --filter @cognitive-os/web build
```

---

## Roadmap & Next Stages

```
Phase 1: Cognitive Core & Extension MVP [COMPLETED]
   └── 15 Cognitive Engines • Next.js 15 Dashboard • Plasmo Chrome MV3 • Test Suite

Phase 2: Multi-Modal & Ambient Ingestion [CURRENT STAGE]
   ├── Real-time voice stream ingestion with spoken thought ambiguity scoring
   ├── Spatial mind-mapping & canvas reasoning (concept graph visualizer)
   └── Dynamic browser context anchors (DOM-aware prompt grounding)

Phase 3: Dialectical Co-Reasoning & Agent Feedback Loops [UPCOMING]
   ├── Socratic stress-testing agents (pre-mortem analysis, devil's advocate)
   ├── Multi-agent collaborative consensus before dispatching to primary LLMs
   └── Automated prompt drift prevention and cognitive schema evolution

Phase 4: Metacognitive Health & Longitudinal Growth Tracking
   ├── Cognitive bias detection (confirmation bias, premature convergence, framing traps)
   ├── Clarity trajectory score tracking and conceptual vocabulary growth
   └── Personalized cognitive style fine-tuning (analytical, exploratory, strategic)

Phase 5: Native OS & IDE Ambient Integration
   ├── Desktop system tray companion (macOS / Linux / Windows)
   ├── VS Code / Cursor IDE extension for software architecture reasoning
   └── Privacy-first local LLM inference routing (Ollama, vLLM, Llama 3)
```

---

## License

MIT © CognitiveOS Contributors — *CreatedBYNJ5.0*
