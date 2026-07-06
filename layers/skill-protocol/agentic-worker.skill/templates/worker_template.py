
import os
import argparse
from datetime import datetime
from typing import Dict, Any

# Import the core agentic worker components
from scripts.agentic_worker import AgentLoop, StateManager, CacheManager, LLMClient, logger

# --- Define Custom Tools for this Worker ---
# These are the functions your agent can call. They should be self-contained
# and perform a specific action, returning a JSON-serializable result.

def search_knowledge_base(query: str) -> Dict[str, Any]:
    """Searches a hypothetical internal knowledge base for information related to the query.

    Args:
        query: The search term or question.

    Returns:
        A dictionary containing the search results or an error message.
    """
    logger.info(f"Searching knowledge base for: {query}")
    # Simulate a search operation
    if "agentic worker" in query.lower():
        return {"status": "success", "results": ["Found document on agentic worker design patterns.", "Article about persistent state in AI agents."], "query": query}
    else:
        return {"status": "not_found", "message": f"No results for 
{query}
", "query": query}

def create_report(title: str, content: str) -> Dict[str, Any]:
    """Creates a new report with the given title and content.

    Args:
        title: The title of the report.
        content: The main body content of the report.

    Returns:
        A dictionary indicating the success or failure of the report creation.
    """
    logger.info(f"Creating report titled: 
{title}
")
    # In a real scenario, this would write to a file, database, or external system.
    report_filename = f"reports/{title.replace(' ', '_').lower()}_{datetime.now().strftime('%Y%m%d%H%M%S')}.txt"
    os.makedirs("reports", exist_ok=True)
    with open(report_filename, "w") as f:
        f.write(f"Title: {title}\n\n{content}")
    return {"status": "success", "message": f"Report 
{title}
 created at 
{report_filename}
"}

# --- Main Execution Block for the {{PROJECT_NAME}} Worker ---
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="{{PROJECT_NAME}} Agentic AI Worker.")
    parser.add_argument("--once", action="store_true", help="Run a single turn and exit.")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode (continuous loop).")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive REPL mode.")
    parser.add_argument("--dry-run", action="store_true", help="Enable dry run mode for tools.")
    parser.add_argument("--agent-name", type=str, default="{{PROJECT_NAME}}Agent", help="Name of the agent.")
    parser.add_argument("--model", type=str, default=os.getenv("AGENT_MODEL", "gemini-pro"), help="LLM model to use.")
    parser.add_argument("--interval", type=int, default=int(os.getenv("AGENT_INTERVAL", "5")), help="Interval for daemon mode in seconds.")
    parser.add_argument("--cache-ttl", type=int, default=int(os.getenv("AGENT_CACHE_TTL", str(3600 * 24))), help="Cache TTL in seconds.")
    parser.add_argument("--log-level", type=str, default=os.getenv("AGENT_LOG_LEVEL", "INFO").upper(), help="Logging level (DEBUG, INFO, WARNING, ERROR).")

    args = parser.parse_args()

    # Set environment variables based on CLI args for consistent configuration
    if args.dry_run: os.environ["AGENT_DRY_RUN"] = "1"
    os.environ["AGENT_MODEL"] = args.model
    os.environ["AGENT_INTERVAL"] = str(args.interval)
    os.environ["AGENT_CACHE_TTL"] = str(args.cache_ttl)
    os.environ["AGENT_LOG_LEVEL"] = args.log_level

    # Initialize core components
    # The state and cache files will be stored in ~/.agentic_worker/ by default
    state_manager = StateManager(os.path.join(os.getenv("AGENT_STATE_DIR", os.path.expanduser("~/.agentic_worker")), "{{PROJECT_NAME}}_state.json"))
    cache_manager = CacheManager(os.path.join(os.getenv("AGENT_STATE_DIR", os.path.expanduser("~/.agentic_worker")), "{{PROJECT_NAME}}_cache.json"))

    # IMPORTANT: Replace "mock_api_key" and "mock_base_url" with actual credentials
    # For sandbox environment, the LLMClient in agentic_worker.py is mocked.
    # In a real application, you would configure it to use a live LLM API.
    llm_client = LLMClient(api_key="YOUR_OPENAI_API_KEY", base_url="YOUR_OPENAI_API_BASE", model=args.model)

    # Register all tools this specific agent can use
    available_tools = {
        "search_knowledge_base": search_knowledge_base,
        "create_report": create_report,
        # Add more tools here as needed for your agent's capabilities
    }

    # Instantiate and run the AgentLoop
    agent_loop = AgentLoop(
        agent_name=args.agent_name,
        llm_client=llm_client,
        tools=available_tools,
        state_manager=state_manager,
        cache_manager=cache_manager,
        interval=args.interval,
        dry_run=args.dry_run
    )

    if args.once:
        print(f"Running 
{args.agent_name}
 for a single turn...")
        agent_loop.run_once()
    elif args.daemon:
        print(f"Running 
{args.agent_name}
 in daemon mode (interval: 
{args.interval}
 seconds). Press Ctrl+C to stop.")
        agent_loop.run_daemon()
    elif args.interactive:
        agent_loop.run_interactive()
    else:
        print("Please specify a run mode: --once, --daemon, or --interactive.")
        parser.print_help()

