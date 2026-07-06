# Multipolar Agentic Web Platform

[![GitHub License](https://img.shields.io/github/license/webmachinelearning/webmcp)](LICENSE)
[![GitHub Issues](https://img.shields.io/github/issues/webmachinelearning/webmcp)](https://github.com/webmachinelearning/webmcp/issues)
[![W3C Community Group](https://img.shields.io/badge/W3C-Community%20Group-blue)](https://webmachinelearning.github.io/community/#join)

A stateful, persistent, and efficient compute plane architecture implementing a sophisticated MLOps workflow built on a **multi-polar strategy** that separates concerns into distinct **control**, **compute**, and **storage** planes.

This monorepo consolidates multi-platform clients, shared libraries, backend services, and AI models into a unified structure, streamlining development for collaborative, human-in-the-loop workflows based on the [WebMCP proposal](docs/proposal.md).

## TL;DR

This is a production-grade monorepo for building agentic AI systems with:
- **Three Planes**: Control (orchestration), Compute (execution), Storage (persistence)
- **Layered Architecture**: Isolated capability imports (`layers/`) with explicit bridge integration (future phase)
- **Matrix Execution**: Cartesian product build grid with agent registry and anti-flail enforcement
- **Multi-Platform Support**: Android, desktop (x86-64), CLI tools, PWA, and Web RCI
- **Shared Libraries**: UI components, API clients, AI logic, MCP protocol, state management
- **Backend Services**: API gateway, AI inference, job scheduler, workspace orchestrator, IAM
- **Professional Standards**: Security-first design, traceable AI operations, auditable codebase

Quick start: Review the [Reference Vault](#the-reference-vault), explore the [Layers](#layered-architecture), check the [Matrix Config](#matrix-execution-system), clone the repo, install dependencies, and run `docker-compose up` for backend services.

## The Reference Vault: Our Single Source of Truth

Before contributing, familiarize yourself with the canonical standards in `/reference`:

| Document | Purpose |
|----------|---------|
| [`Minimum_Professionalism_Standards.md`](reference/Minimum_Professionalism_Standards.md) | Code quality, documentation, version control standards |
| [`Minimum_Security_Standards.md`](reference/Minimum_Security_Standards.md) | Secure coding practices (OWASP-aligned) |
| [`AI_Minimum_Operational_Guidelines.md`](reference/AI_Minimum_Operational_Guidelines.md) | AI agent operational and ethical guidelines |

These are **non-negotiable baseline standards**. All contributions must adhere to these principles.

## Features

### Core Architecture
- **Multipolar Design**: Separation of control, compute, and storage planes for clean architectural boundaries
- **Persistent State Management**: Hash-based caching, state snapshots, and trail logging for reproducibility
- **Parallel Tool Execution**: Concurrent dispatch with configurable worker pools and load balancing
- **Daemon & Interactive Modes**: Support for background operation and REPL-style interaction

### WebMCP Integration
- **Client-Side Tool Registration**: Expose JavaScript functions as AI-agent-callable tools
- **Natural Language Descriptions**: Tools include schemas and descriptions for agent understanding
- **Permission Mediation**: Browser-mediated tool calls with user consent flows
- **Human-in-the-Loop**: Seamless interleaving of agent actions and human input

### Deployment Options
| Option | Type | Use Case |
|--------|------|----------|
| **Android APK** | Native mobile | On-device agent execution |
| **PWA** | Progressive Web App | Browser-based with offline support |
| **Web RCI** | Remote Command Interface | Dashboard for monitoring and control |
| **CLI Launcher** | Terminal-based | Scripting and automation |

### Layered Architecture

The repo uses a **layered capability import** strategy to manage complexity and enable gradual integration:

| Layer | Purpose | Contents |
|-------|---------|----------|
| **`skill-protocol/`** | SKILL agent framework | Python workers, state management, ADK patterns |
| **`state-engine/`** | Full-stack TypeScript runtime | tRPC backend, React 19 frontend, Drizzle ORM |
| **`cli-orchestrator/`** | Termux-native deployment | APK/PWA/RCI guides, matrix configs |

**Integration Philosophy**: Layers remain isolated until explicit bridges are constructed in the `bridges/` directory. See [layers/README.md](layers/README.md) for the complete integration roadmap.

### Matrix Execution System

The matrix-driven execution system enables parallel, multi-dimensional builds:

- **Cartesian Product Grid**: Combines SDK × ABI × build type × optimization × environment
- **Agent Registry**: Live index of 6 specialist agents with capability mapping
- **Anti-Flail Enforcement**: Rejects duplicate capabilities and unregistered agents
- **State Persistence**: Preserves cache hashes and performance scores across runs

Configuration files:
- [`matrix/config/matrix.yml`](matrix/config/matrix.yml) - Build grid definition
- [`matrix/config/agent-index.json`](matrix/config/agent-index.json) - Agent registry

### Supported LLM Providers
- OpenAI (GPT-4o, etc.)
- Google Gemini
- Ollama (local models)
- GitHub Copilot (conceptual integration)

## GitHub Actions & CI/CD

The repository includes comprehensive workflows for automated testing, matrix execution, and AI-assisted code review:

| Workflow | Purpose | Triggers |
|----------|---------|----------|
| [`main.yml`](.github/workflows/main.yml) | Primary CI pipeline | Push to main/develop |
| [`orchestrator.yml`](.github/workflows/orchestrator.yml) | Agent matrix orchestration | Manual dispatch |
| [`librarian.yml`](.github/workflows/librarian.yml) | Backend service validation | PR on server code |
| [`dashboard.yml`](.github/workflows/dashboard.yml) | Frontend build & test | PR on client code |
| [`glm-coder-companion.yml`](.github/workflows/glm-coder-companion.yml) | **Multi-AI code review** (6+ providers) | All PRs |
| [`ephemeral-runner-orchestrator.yml`](.github/workflows/ephemeral-runner-orchestrator.yml) | Self-hosted runner lifecycle | Manual/scheduled |

### Multi-AI Code Review System

The `glm-coder-companion.yml` workflow provides comprehensive PR analysis using multiple free-tier AI endpoints:

**Supported Providers**: OpenRouter, HuggingFace, GitHub Models, Nvidia, Qwen, Kimi

**Features**:
- **Context Engine**: Generates token-optimized bundles (minimal/balanced/full strategies)
- **Auto Key Sourcing**: Attempts ENV → Secrets file → Skip (no manual config needed)
- **Parallel Execution**: All providers run simultaneously for diverse perspectives
- **Aggregated Comments**: Consolidated report posted as PR comment with verdicts and scores

**Setup**: Add API keys to repository secrets or `.github/secrets.json` (gitignored):
```bash
# Example secrets.json structure
{
  "OPENROUTER_API_KEY": "sk-or-...",
  "HF_API_KEY": "hf_...",
  "NVIDIA_API_KEY": "nvapi-...",
  "DASHSCOPE_API_KEY": "sk-...",
  "KIMI_API_KEY": "..."
}
```

### Ephemeral Self-Hosted Runners

For heavy workloads, the system supports temporary runners on network storage:

```bash
# Trigger runner setup via workflow dispatch
gh workflow run ephemeral-runner-orchestrator.yml --field action=setup

# Runner will be available for 60 minutes (configurable TTL)
# Labels: ephemeral, agentic-matrix, multi-ai, termux
```

Runners are automatically cleaned up after TTL expiration or via scheduled cleanup job.

## Directory Structure

```
/
├── .github/                    # GitHub configurations (workflows, templates)
├── bridges/                    # Cross-layer integration code (future phase)
├── content/                    # Assets (images, screenshots)
├── dashboard/                  # Web dashboard / RCI interface
├── docs/                       # Documentation
│   ├── adr/                    # Architecture Decision Records
│   ├── architecture/           # Architecture diagrams and specs
│   ├── guides/                 # User and developer guides
│   ├── proposal.md             # WebMCP API proposal (canonical)
│   └── service-workers.md      # PWA service worker documentation
├── layers/                     # Layered capability imports
│   ├── skill-protocol/         # SKILL agent framework & language spec
│   ├── state-engine/           # Full-stack TypeScript runtime (tRPC + React)
│   ├── cli-orchestrator/       # Termux-native deployment guides
│   └── README.md               # Layer integration roadmap
├── libs/                       # Shared libraries
│   ├── auth-client/            # Authentication client library
│   ├── common-utils/           # Cross-cutting utilities
│   ├── data-models/            # Shared data types and schemas
│   ├── mcp-protocol/           # Model Context Protocol implementation
│   ├── standards-enforcement/  # Security and quality enforcement tools
│   ├── state-management/       # Persistent state and caching
│   └── ui-components/          # Reusable UI components
├── matrix/                     # Matrix-driven execution system
│   ├── config/                 # Matrix & agent configurations
│   │   ├── matrix.yml          # Cartesian product build grid
│   │   └── agent-index.json    # Live agent registry
│   └── jobs/                   # Job execution artifacts
├── planes/                     # Architectural planes
│   ├── compute/                # Execution plane (workers, runners)
│   ├── control/                # Orchestration plane (schedulers, coordinators)
│   └── storage/                # Persistence plane (databases, caches)
├── reference/                  # The Reference Vault (canonical standards)
├── references/                 # Integration guides & external references
├── sdks/                       # SDK packages
│   ├── honcho-sdk/             # Orchestration SDK
│   ├── services-api-client/    # Backend API client
│   └── storage-sdk/            # Storage abstraction layer
├── services/                   # Backend services
│   ├── ai-inference-proxy/     # LLM proxy and routing
│   ├── api-gateway/            # API routing and security
│   ├── artifact-manager/       # Build artifact management
│   ├── iam/                    # Identity and access management
│   ├── job-scheduler/          # Distributed job scheduling
│   ├── state-snapshotter/      # State persistence service
│   └── workspace-orchestrator/ # Workspace lifecycle management
├── specs/                      # Technical specifications
├── tools/                      # Developer tooling
│   ├── build-system/           # Build configuration and scripts
│   ├── cli-scripts/            # CLI utilities
│   └── codegen/                # Code generation tools
├── CODEOWNERS                  # Code ownership assignments
├── CONTRIBUTING.md             # Contribution guidelines (W3C CG)
├── LICENSE                     # MIT License
├── README.md                   # This file
└── w3c.json                    # W3C repository metadata
```

## Setup Instructions

### Prerequisites
- **Node.js 16+** and npm/pnpm (for frontend/libs)
- **Python 3.8+** (for backend/services)
- **Docker** (recommended for containerized deployment)
- **Java 11+** (for Android builds)

### 1. Clone the Repository
```bash
git clone https://github.com/webmachinelearning/webmcp.git
cd webmcp
```

### 2. Install Dependencies

**JavaScript/TypeScript (libs, apps, dashboard):**
```bash
npm install
# or
pnpm install
```

**Python (services, tools):**
```bash
cd services/api-gateway
pip install -r requirements.txt
# Repeat for each service directory
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:
```dotenv
# LLM Provider Configuration
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Optional: Local models
OLLAMA_BASE_URL=http://localhost:11434

# Agent Configuration
AGENT_DRY_RUN=True
AGENT_MODE=interactive
```

### 4. Run Backend Services

**Using Docker (Recommended):**
```bash
docker-compose up
```

**Manual Startup:**
```bash
# Start API Gateway
cd services/api-gateway && python main.py

# Start AI Inference Proxy
cd services/ai-inference-proxy && python main.py

# Start Job Scheduler
cd services/job-scheduler && python main.py
```

### 5. Launch Frontend

**Development Mode:**
```bash
cd dashboard
npm run dev
```

Open `http://localhost:3000` in your browser.

**Production Build:**
```bash
npm run build
npm run serve
```

### 6. Deploy Agentic Worker

See the [Universal Agentic Worker - Deployment Guide](./Universal%20Agentic%20Worker%20-%20Deployment%20Guide.md) for detailed instructions on:
- Building the Android APK
- Deploying the PWA
- Running the Web RCI dashboard
- Using the CLI launcher

## Contributing

### W3C Community Group Participation

This repository is governed by the [W3C Community License Agreement (CLA)](https://www.w3.org/community/about/agreements/cla/). To make substantive contributions:

1. **Join the W3C Web Machine Learning Community Group**: [Sign up here](https://webmachinelearning.github.io/community/#join)
2. **Review the Reference Vault**: Understand our professionalism, security, and AI operational standards
3. **Follow Professional Standards**: Adhere to inline documentation, citation, and commit message requirements

### Contribution Workflow

1. **Fork the repository** and create a feature branch
2. **Implement changes** following the [Minimum Professionalism Standards](reference/Minimum_Professionalism_Standards.md)
3. **Add inline rationale** for non-trivial decisions (show your work)
4. **Cite sources** at end of files (external standards, libraries, articles)
5. **Write tests** and ensure CI passes
6. **Submit a pull request** using the [PR template](.github/PULL_REQUEST_TEMPLATE.md)

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):
```
feat: add hash-based caching to state manager
fix: resolve path traversal vulnerability in artifact manager
docs: update security standards with OWASP references
refactor: extract permission logic to auth-client library
```

### Code Review

All PRs require review from [CODEOWNERS](CODEOWNERS). Reviewers will check:
- Adherence to Reference Vault standards
- Proper inline documentation and citations
- Security best practices (input validation, secrets management)
- AI operational guidelines (traceability, fail-safe design)

## Architecture Overview

### The Three Planes

**Control Plane** (`planes/control/`):
- Orchestrates agent workflows
- Manages job scheduling and resource allocation
- Handles permissions and consent flows

**Compute Plane** (`planes/compute/`):
- Executes tool calls and LLM interactions
- Runs parallel workers with configurable concurrency
- Implements caching and deduplication

**Storage Plane** (`planes/storage/`):
- Persists agent state and conversation history
- Manages hash-based caches
- Provides snapshot and recovery capabilities

### Data Flow

```
User Input → Control Plane (Orchestrator)
              ↓
         Compute Plane (Tool Execution + LLM Calls)
              ↓
         Storage Plane (State Persistence)
              ↓
         Response → User
```

### Security Model

- **Input Validation**: All external inputs validated against allowlists (OWASP)
- **Path Traversal Protection**: No direct concatenation of user input into file paths
- **Secrets Management**: API keys stored in environment variables or secure vaults
- **Dependency Scanning**: Automated vulnerability detection (Dependabot, Snyk)
- **Least Privilege**: Agents operate with minimal required permissions

## Monitoring & Logging

### Log Locations
- Matrix Execution: `layers/matrix-config/logs/matrix-execution.log`
- Agent Telemetry: `~/.termux/agent-state/telemetry.json`
- AI Reviews: `.github/ai-reviews.json` (generated by CI)

### Multi-AI Code Review

This repo features a **Multi-AI Code Review System** that automatically analyzes pull requests using multiple LLM providers simultaneously.

#### How It Works

1. **Context Engine** (`.github/scripts/context_engine.py`): Generates token-optimized bundles containing:
   - Changed files with full diffs
   - Critical context (scaffold, agent-index, matrix config)
   - Repository structure summary

2. **Universal AI Gateway** (`.github/scripts/ai_gateway.py`): Routes reviews to 6+ providers:
   - OpenRouter (Llama-3-70B)
   - HuggingFace (Qwen2.5-Coder-32B)
   - GitHub Models (GPT-4o)
   - Nvidia (Llama3-70B)
   - Qwen/DashScope
   - Kimi/Moonshot

3. **Auto-Auth**: Sources API keys from GitHub Secrets or `.github/secrets.json`

#### Configuration

Add your API keys to repository secrets or create `.github/secrets.json`:
```bash
cp .github/secrets.example.json .github/secrets.json
# Edit with your keys (gitignored)
```

#### Manual Trigger
```bash
gh workflow run glm-coder-companion.yml --field strategy=full
```

See [`.github/AGENT_INSTRUCTIONS.md`](.github/AGENT_INSTRUCTIONS.md) for full details.

### Log Format

| Component | Log Location |
|-----------|--------------|
| Agent Trail | `~/.universal_agent/trail.log` |
| Backend Services | stdout/stderr (Docker logs) |
| Web Dashboard | Browser console |
| Android App | Logcat |

### Log Format

JSON-lines format for easy parsing:
```json
{"timestamp": "2025-01-15T10:30:00Z", "level": "INFO", "message": "Agent started"}
{"timestamp": "2025-01-15T10:30:01Z", "level": "DEBUG", "tool": "file_read", "status": "success"}
```

### Real-Time Monitoring

```bash
# Watch agent logs
tail -f ~/.universal_agent/trail.log

# Filter errors
grep '"level": "ERROR"' ~/.universal_agent/trail.log

# Docker logs
docker-compose logs -f
```

## Troubleshooting

### Common Issues

**Port Already in Use:**
```bash
lsof -i :8000
kill -9 <PID>
```

**LLM Connection Failures:**
- Verify API keys are valid and have credits
- For Ollama: ensure `ollama serve` is running
- Check network connectivity and firewall rules

**Dependency Issues:**
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

**Agent Not Starting:**
1. Check trail logs: `tail -f ~/.universal_agent/trail.log`
2. Test with `--dry-run` mode first
3. Verify LLM provider configuration
4. Check file permissions in working directory

## Acknowledgments

This project builds upon:
- **[WebMCP Proposal](https://github.com/webmachinelearning/webmcp)** by Brandon Walderman, Andrew Nolan (Microsoft), David Bokan, Khushal Sagar, Hannah Van Opstal (Google)
- **[MCP-B](https://github.com/MiguelsPizza/WebMCP)** for browser extension patterns
- **[Model Context Protocol](https://modelcontextprotocol.io/)** for server-side tool integration
- **[Deep SSnaHke Pattern](./SKILL.md)** for agentic worker architecture
- **[Google ADK 2.0](./SKILL.md)** for advanced multi-agent workflow patterns

## Related Projects

| Project | Description | Status |
|---------|-------------|--------|
| **WebMCP (Original)** | JS API for web tools to AI agents | Proposal stage (Aug 2025) |
| **MCP-B** | Browser extension with tab/extension transports | Maintained community fork |
| **MCP Protocol** | Backend AI-tool integration standard | Active (next release Nov 2025) |
| **Bright Data Web MCP** | Real-time web data for ChatGPT | Recent (Nov 2025) |

## License

MIT License - see [LICENSE](LICENSE) for details.

---

**Last Updated**: November 2025  
**Version**: 1.0.0  
**Governance**: W3C Web Machine Learning Community Group
