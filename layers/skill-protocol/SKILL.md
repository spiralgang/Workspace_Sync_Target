---
name: agentic-worker
description: Build production-grade agentic AI workers with persistent state, hash-based caching, parallel tool execution, and daemon/interactive modes. Use for creating robust multi-turn LLM agents, automating complex workflows, or developing self-managing AI services inspired by the Deep SSnaHke pattern and Google ADK 2.0 principles.
---

# Agentic Worker Skill

This skill provides the framework and guidance for constructing powerful, self-managing AI agents capable of complex, multi-turn interactions with Large Language Models (LLMs) and external tools. It integrates principles of persistence, caching, and parallel processing, drawing inspiration from the robust design of the Deep SSnaHke bash script and the advanced patterns found in Google ADK 2.0.

## Quick Start: Build Your First Agentic Worker

Follow these steps to quickly set up and run a new agentic worker:

1.  **Initialize a new worker project**: Use the `init_worker.py` script to scaffold a new worker directory.
    ```bash
    python /home/ubuntu/skills/agentic-worker/scripts/init_worker.py my_first_agent
    ```
    This creates `my_first_agent/my_first_agent_worker.py` and a `reports/` directory.

2.  **Customize your worker**: Navigate into the `my_first_agent` directory and edit `my_first_agent_worker.py`.
    -   **Define your tools**: Add or modify Python functions that your agent can call (e.g., `search_knowledge_base`, `create_report`). Ensure they are JSON-serializable.
    -   **Configure LLM access**: Replace `"YOUR_OPENAI_API_KEY"` and `"YOUR_OPENAI_API_BASE"` with your actual LLM API credentials. For sandbox testing, the `LLMClient` is mocked.

3.  **Run your agent**: Execute your worker in one of the available modes:
    -   **One-shot**: Perform a single turn and exit.
        ```bash
        python my_first_agent_worker.py --once
        ```
    -   **Daemon**: Run continuously in the background (e.g., for scheduled tasks).
        ```bash
        python my_first_agent_worker.py --daemon
        ```
    -   **Interactive**: Engage with your agent in a REPL-like interface.
        ```bash
        python my_first_agent_worker.py --interactive
        ```
    -   **Dry Run**: Simulate tool execution without actual side effects (recommended for testing).
        ```bash
        python my_first_agent_worker.py --once --dry-run
        ```

## Core Architectural Concepts

The `agentic-worker` framework is built upon several key components that provide persistence, efficiency, and robustness:

-   **Persistent State**: The `StateManager` ensures that your agent remembers its conversation history and internal state across runs, enabling long-running, context-aware interactions.
-   **Hash-Based Caching**: The `CacheManager` intelligently stores LLM responses and tool results, preventing redundant computations and API calls, leading to faster and more cost-effective operations.
-   **Parallel Tool Execution**: The `ToolDispatcher` executes multiple tool calls concurrently, significantly speeding up workflows that involve several external actions.
-   **Daemon & Interactive Modes**: The `AgentLoop` supports continuous background operation (daemon) and direct user interaction (interactive REPL), adapting to various deployment scenarios.

For a detailed breakdown of the architecture and how it translates the Deep SSnaHke pattern to LLM agents, refer to [references/architecture.md](references/architecture.md).

## Advanced Patterns and Integrations

This skill is designed to be extensible and can incorporate advanced agentic patterns:

-   **Google ADK 2.0 Inspiration**: Learn how concepts like Graph Workflows, Collaborative Multi-Agent Workflows, and advanced Session/Memory management from Google ADK 2.0 can be applied or adapted within this framework. See [references/adk-patterns.md](references/adk-patterns.md).
-   **Robust Tooling**: Understand best practices for tool registration, parallel dispatch, result caching, error handling, and the critical role of dry-run gates for safe development. See [references/tool-execution.md](references/tool-execution.md).

## Skill File Structure

The `agentic-worker` skill is organized as follows:

```
agentic-worker/
├── SKILL.md
├── scripts/
│   ├── agentic_worker.py      # Core Python implementation of the agent framework
│   └── init_worker.py         # Script to scaffold new agent projects
├── references/
│   ├── architecture.md        # Detailed explanation of the agent\'s architecture
│   ├── adk-patterns.md        # Google ADK 2.0 patterns for advanced agent design
│   └── tool-execution.md      # Guide to defining, dispatching, and managing tools
└── templates/
    └── worker_template.py     # Boilerplate for new agentic worker instances
```

This modular structure allows for easy customization and extension of your agentic workers. Each component is designed to be independent yet integrated, providing a flexible and powerful foundation for your AI automation needs.
