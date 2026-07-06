# Tool Execution in Agentic Worker

This document details the mechanisms for defining, dispatching, and managing tool execution within the `agentic-worker` framework. Effective tool integration is crucial for extending the agent's capabilities beyond its core LLM reasoning.

## 1. Tool Registration

Tools are essentially Python functions that the agent can call. They are registered with the `ToolDispatcher` during the agent's initialization.

- **Mechanism**: Tools are provided as a dictionary where keys are the tool names (strings) and values are the callable Python functions.
- **Example (from `agentic_worker.py`)**:

```python
def example_tool(query: str) -> Dict[str, Any]:
    """An example tool that processes a query."""
    # ... implementation ...
    return {"status": "success", "processed_query": query.upper()}

# ... later in main execution block ...
available_tools = {"example_tool": example_tool}
# ... passed to AgentLoop and ToolDispatcher ...
```

- **Best Practices for Tool Definition**:
    - **Clear Docstrings**: Each tool function should have a clear docstring explaining its purpose, parameters, and expected return value. This helps the LLM understand when and how to use the tool.
    - **Type Hinting**: Use Python type hints for parameters and return values to improve clarity and enable static analysis.
    - **JSON-serializable I/O**: Tool arguments and return values should be easily serializable to and from JSON, as this is how LLMs typically interact with tools.

## 2. Parallel Dispatch Mechanics

The `ToolDispatcher` is responsible for executing tool calls, leveraging concurrency to improve efficiency.

- **`ToolDispatcher` Class**: Initializes with a dictionary of registered tools and a `max_workers` parameter for its `ThreadPoolExecutor`.
- **`dispatch` Method**: Takes a list of tool calls (as parsed from the LLM's response) and submits each to the `ThreadPoolExecutor`.
- **Concurrency**: Uses `concurrent.futures.ThreadPoolExecutor` to run multiple tool functions in parallel. The `as_completed` function is used to collect results as they become available, rather than waiting for all tools to finish.
- **Configurable Parallelism**: The `AGENT_TOOL_JOBS` environment variable (defaulting to CPU count) controls the maximum number of concurrent tool executions, analogous to Deep SSnaHke's `HASH_JOBS`.

## 3. Result Caching

To avoid redundant computations and API calls, the `ToolDispatcher` integrates with the `CacheManager`.

- **Cache Key**: A unique hash is generated based on the tool name and its arguments.
- **Cache Lookup**: Before executing a tool, the `ToolDispatcher` checks the `CacheManager` for a pre-computed result using the generated key.
- **Cache Write**: If a tool executes successfully and its result is not in the cache, the result is stored in the `CacheManager` with its associated TTL.
- **Benefits**: Reduces latency, saves computational resources, and can lower costs for API-based tools.

## 4. Error Handling and Retry Logic

Robust error handling is critical for agent stability.

- **Individual Tool Errors**: Each tool execution is wrapped in a `try-except` block within the `_execute_tool` method. If an error occurs, it's caught, logged, and returned as part of the tool result, allowing the agent to continue processing other tools.
- **Logging**: Errors are logged with `logger.error`, providing detailed context including the tool name and the exception message.
- **Retry Logic (Future Enhancement)**: While not explicitly implemented in the current `agentic_worker.py`, a common pattern for production agents is to add retry logic (e.g., with exponential backoff) for transient tool errors. This would typically be implemented within the `_execute_tool` method or by a wrapper around tool calls.

## 5. Action Confirmation (Dry-Run Gate)

The `agentic-worker` includes a `dry_run` mechanism to prevent unintended side effects during development or sensitive operations.

- **`AGENT_DRY_RUN` Flag**: Controlled by an environment variable, this flag (defaulting to `True`) determines whether tools perform their actual actions or merely log their intent.
- **`ToolDispatcher` Integration**: When `AGENT_DRY_RUN` is `True`, the `_execute_tool` method logs what *would* have been executed instead of calling the actual tool function.
- **Safety**: Provides a crucial safety net, allowing developers to test agent workflows and tool interactions without modifying external systems or incurring costs from real API calls. This is analogous to Deep SSnaHke's `DRY_RUN` variable for file pruning.
