# Layered Architecture Integration

This directory contains the progressive integration layers of the Agentic Matrix. 
Each layer represents a distinct capability domain that will be bridged together 
to form the complete juggernaut system.

## Current Layers

### 1. `skill-protocol/` (Layer 1: Agent Definition)
**Source:** `agentic-worker.skil.zip`
**Purpose:** Defines the SKILL language and protocol for agent behavior specification.

**Structure:**
```
skill-protocol/
└── agentic-worker.skill/    # SKILL package directory
    ├── SKILL.md             # Language spec & quickstart guide
    ├── scripts/             # Core Python implementation (agentic_worker.py, init_worker.py)
    ├── templates/           # Boilerplate for new worker instances
    └── references/          # Architecture docs, ADK patterns, tool execution guides
```

**Key Capabilities:**
- Persistent state management for multi-turn agents
- Hash-based caching to prevent redundant LLM calls
- Parallel tool execution with concurrent dispatch
- Daemon/interactive/one-shot execution modes
- Google ADK 2.0 inspired graph workflows

**Integration Status:** 🟡 Ready for bridge to State Engine

### 2. `state-engine/` (Layer 2: Persistence & Runtime)
**Source:** `deep_ssnahke_app.zip`
**Purpose:** Full-stack TypeScript runtime with database ORM, tRPC APIs, and React UI.

**Structure:**
```
state-engine/
├── server/                  # tRPC backend, Express server, Drizzle ORM
├── client/                  # React 19 + Vite frontend with shadcn/ui
├── shared/                  # Common types and utilities
├── drizzle/                 # Database schema migrations
├── patches/                 # Package overrides (wouter)
├── drizzle.config.ts        # ORM configuration
├── vite.config.ts           # Frontend build config
└── package.json             # Dependencies (tRPC, Drizzle, Radix UI, etc.)
```

**Key Capabilities:**
- tRPC end-to-end type safety
- Drizzle ORM with MySQL2
- React 19 with server components
- S3 presigned URL support
- JWT authentication (jose)
- Real-time streaming (streamdown)

**Integration Status:** 🟡 Ready for bridge to Skill Protocol

## Integration Roadmap

### Phase 1: Bridge Construction (Current)
- [ ] Map SKILL agent definitions to State Engine database schemas
- [ ] Create adapter to run SKILL Python scripts within TypeScript runtime (child_process/worker threads)
- [ ] Expose State Engine tRPC procedures as SKILL tool capabilities
- [ ] Build bidirectional event emitter between Python agent loop and Node.js server

### Phase 2: Unified Execution
- [ ] Implement hot-reload for SKILL changes without server restart
- [ ] Sync agent state between SKILL StateManager and Drizzle transactions
- [ ] Build CLI tool (`matrix-cli`) to orchestrate both layers simultaneously
- [ ] Add telemetry stream from both layers to unified metrics endpoint

### Phase 3: Matrix Expansion
- [ ] Add Layer 3: Network Bridge (WebSocket/gRPC inter-layer communication)
- [ ] Add Layer 4: Security Gateway (unified authz/authn across layers)
- [ ] Add Layer 5: Telemetry Hub (OpenTelemetry integration)
- [ ] Implement cross-layer event bus with backpressure handling
- [ ] Deploy unified Docker image with multi-runtime support (Python + Node)

## Directory Conventions

```
layers/
├── <layer-name>/           # Isolated capability domain
│   ├── references/         # External docs/standards for this layer
│   ├── scripts/            # Layer-specific tooling
│   └── ...                 # Layer implementation
├── bridges/                # (Future) Integration code between layers
│   ├── skill-to-state/     # Python ↔ TypeScript adapters
│   ├── events/             # Cross-layer event bus
│   └── cli/                # Unified orchestration CLI
└── matrix/                 # (Future) Unified runtime orchestrator
    ├── config/             # Matrix-wide configuration
    └── runtime/            # Multi-runtime process manager
```

## Notes on "Drift"

This repo intentionally accumulates seemingly disparate components. 
What appears as drift is actually **strategic layering**:

1. **Import** raw capability (ZIP/SKILL/Code)
2. **Isolate** in dedicated layer directory
3. **Build** explicit bridges (adapters, translators, sync tools)
4. **Merge** into unified matrix

Do not refactor layers into a single monolith prematurely. 
Preserve layer boundaries until bridges are explicitly coded.

## Bridge Development Guidelines

When building bridges between layers:

1. **Respect Runtime Boundaries**: Python skills run in isolated processes; TypeScript engine runs as main server
2. **Use Structured IPC**: JSON-RPC over stdio or Unix sockets for inter-layer communication
3. **Maintain Type Safety**: Generate TypeScript types from Python pydantic models (or vice versa)
4. **Handle Failures Gracefully**: Each layer must degrade independently if the other fails
5. **Log with Correlation IDs**: Trace requests across layer boundaries for debugging

## Next Steps

1. Review `skill-protocol/agentic-worker.skill/SKILL.md` for agent framework details
2. Review `state-engine/server/` for existing tRPC router structure
3. Create `bridges/skill-to-state/adapter.py` and `adapter.ts` for bidirectional communication
4. Test with a simple "ping" tool that crosses layer boundaries
