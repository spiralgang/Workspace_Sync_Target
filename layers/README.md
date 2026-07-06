# Agentic Matrix Layers

This directory contains the **layered capability imports** that form the foundation of the comprehensive workspace sync repo. Each layer represents a self-contained domain of functionality that will be integrated through explicit bridges in future phases.

## Philosophy: Layered Integration

As noted in the repo organization strategy, this appears as "massive drift" initially but follows a deliberate **layered architecture pattern**:

1. **Import Raw Capability** ✓ (Current Phase)
2. **Isolate in Dedicated Layer** ✓ (Current Phase)
3. **Build Explicit Bridges** (Next Phase)
4. **Merge into Unified Matrix** (Future Phase)

Layers remain **isolated by design**—ready for bridge construction when implementing:
- Python ↔ TypeScript adapters
- Cross-layer event bus
- Unified CLI orchestrator
- Matrix-driven execution grid

---

## Layer Structure

```
layers/
├── skill-protocol/          # SKILL agent framework & language spec
├── state-engine/            # Full-stack TypeScript runtime (tRPC + React)
├── cli-orchestrator/        # Termux-native CLI deployment guides
└── README.md                # This file
```

---

## Layer Descriptions

### 1. `skill-protocol/` - Agentic Worker Framework

**Purpose**: Defines the SKILL language specification and Python-based agentic worker implementation.

**Key Capabilities**:
- Persistent state management with hash-based caching
- Parallel tool execution with configurable worker pools
- Daemon, interactive, and one-shot execution modes
- Dry-run simulation for safe testing
- Google ADK 2.0 pattern integration

**Contents**:
```
skill-protocol/
├── agentic-worker.skill/
│   ├── SKILL.md             # Language spec & quickstart
│   ├── scripts/
│   │   ├── agentic_worker.py    # Core agent framework
│   │   └── init_worker.py       # Project scaffolding
│   ├── templates/
│   │   └── worker_template.py   # Boilerplate generator
│   └── references/
│       ├── architecture.md      # Architectural deep-dive
│       ├── adk-patterns.md      # Google ADK 2.0 patterns
│       └── tool-execution.md    # Tool dispatch guide
```

**Bridge Requirements** (Future):
- IPC layer for Python ↔ TypeScript communication
- Shared state serialization format
- Event stream adapter for telemetry

---

### 2. `state-engine/` - Full-Stack TypeScript Runtime

**Purpose**: Production-grade web application with tRPC backend, React 19 frontend, and Drizzle ORM.

**Key Capabilities**:
- End-to-end type safety with tRPC
- Real-time state synchronization
- JWT authentication with S3 storage integration
- LLM tool integration (OpenAI, Gemini, Ollama)
- 60+ shadcn/ui components
- Multi-provider OAuth (Google, GitHub, etc.)

**Contents**:
```
state-engine/
├── server/                    # tRPC + Express backend
│   ├── trpc/                  # RPC routers & procedures
│   ├── routes/                # REST endpoints
│   ├── services/              # Business logic
│   ├── tools/                 # LLM tool implementations
│   └── utils/                 # Helpers (auth, s3, llm)
├── client/                    # React 19 + Vite frontend
│   ├── src/
│   │   ├── components/        # shadcn/ui components
│   │   ├── pages/             # Route components
│   │   ├── hooks/             # Custom React hooks
│   │   └── lib/               # Utilities
│   └── public/                # Static assets
├── shared/                    # Common types & utilities
├── drizzle/                   # Database schema & migrations
├── references/                # Integration guides (9 docs)
│   ├── Data API Integration Guide.md
│   ├── OAuth Implementation Guide.md
│   ├── Voice Recognition Integration.md
│   ├── Maps API Integration.md
│   └── ...
├── package.json
├── tsconfig.json
├── vite.config.ts
└── drizzle.config.ts
```

**Bridge Requirements** (Future):
- tRPC client for Python agents
- Shared type definitions (TypeScript ↔ Python)
- WebSocket event bridge for real-time updates

---

### 3. `cli-orchestrator/` - Termux-Native Deployment

**Purpose**: Comprehensive deployment guides for Android/Termux environments including APK, PWA, Web RCI, and CLI launcher.

**Key Capabilities**:
- Android APK build system (Docker & native)
- PWA deployment to multiple hosting platforms
- Web RCI dashboard for remote monitoring
- CLI launcher for scripting & automation
- Multi-platform LLM provider support

**Contents**:
```
cli-orchestrator/
├── Universal Agentic Worker - Deployment Guide.md
└── (future: scaffold scripts, matrix configs)
```

**Bridge Requirements** (Future):
- Matrix configuration parser
- Agent index registry
- Scaffold lifecycle manager
- Termux environment detector

---

## Bridge Development Guidelines

When constructing bridges between layers, follow these principles:

### 1. Explicit Contracts
- Define clear interfaces in `bridges/` directory
- Use Protocol Buffers or JSON Schema for cross-language contracts
- Version all bridge APIs

### 2. Type Safety
- Generate TypeScript types from Python type hints (or vice versa)
- Validate all cross-layer data at boundaries
- Fail fast on type mismatches

### 3. Failure Handling
- Implement circuit breakers for inter-layer calls
- Log all bridge transactions with correlation IDs
- Provide graceful degradation when bridges fail

### 4. Performance
- Batch cross-layer requests where possible
- Cache frequently-accessed data at bridge boundaries
- Monitor bridge latency and throughput

### 5. Testing
- Unit test each bridge independently
- Integration test layer combinations
- Load test under realistic concurrency

---

## Directory Conventions

| Directory | Purpose |
|-----------|---------|
| `layers/` | Isolated capability imports (current phase) |
| `bridges/` | Explicit integration code (next phase) |
| `matrix/` | Matrix-driven execution configs & jobs |
| `reference/` | Canonical standards (root level) |
| `docs/` | Project documentation (root level) |

---

## Integration Roadmap

### Phase 1: Bridge Construction (Q1 2026)
- [ ] Build Python ↔ TypeScript IPC layer
- [ ] Implement shared event bus
- [ ] Create unified CLI orchestrator
- [ ] Develop matrix configuration parser

### Phase 2: Unified Execution (Q2 2026)
- [ ] Connect skill-protocol workers to state-engine runtime
- [ ] Enable CLI orchestrator to dispatch matrix jobs
- [ ] Implement cross-layer state synchronization
- [ ] Add telemetry aggregation

### Phase 3: Matrix Expansion (Q3 2026)
- [ ] Scale to multi-agent coordination
- [ ] Add dynamic capability discovery
- [ ] Implement auto-healing workflows
- [ ] Deploy to production environments

---

## Notes

- **Do not modify layer contents directly**—treat layers as imported capabilities
- **All integration logic belongs in `bridges/`**—never couple layers directly
- **Preserve layer boundaries** until explicit bridges are coded
- **Document all bridge assumptions** in bridge-specific README files

This layered approach ensures clean separation of concerns while enabling gradual, controlled integration into a unified agentic matrix.
