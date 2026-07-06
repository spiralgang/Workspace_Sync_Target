
import os
import hashlib
import json
import time
import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional, Callable

# --- Configuration (Environment Variable Driven) ---
# Analogous to Deep SSnaHke's env vars
AGENT_MODEL = os.getenv("AGENT_MODEL", "gemini-pro") # Placeholder, will use sandbox's LLM
AGENT_INTERVAL = int(os.getenv("AGENT_INTERVAL", "5")) # seconds
AGENT_TOOL_JOBS = int(os.getenv("AGENT_TOOL_JOBS", str(os.cpu_count() or 2)))
AGENT_CACHE_TTL = int(os.getenv("AGENT_CACHE_TTL", str(3600 * 24))) # 24 hours
AGENT_DRY_RUN = os.getenv("AGENT_DRY_RUN", "1") == "1"
AGENT_STATE_DIR = os.getenv("AGENT_STATE_DIR", os.path.expanduser("~/.agentic_worker"))
AGENT_LOG_LEVEL = os.getenv("AGENT_LOG_LEVEL", "INFO").upper()

# Ensure state directory exists
os.makedirs(AGENT_STATE_DIR, exist_ok=True)

# --- Logging Setup ---
# Analogous to Deep SSnaHke's TRAIL log
LOG_FILE = os.path.join(AGENT_STATE_DIR, "trail.log")

logging.basicConfig(
    level=AGENT_LOG_LEVEL,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class StateManager:
    """Manages persistent state for the agent, analogous to SSnaHke's STATE_DIR and index files."""
    def __init__(self, state_file: str):
        self.state_file = state_file
        self.state: Dict[str, Any] = self._load_state()

    def _load_state(self) -> Dict[str, Any]:
        if os.path.exists(self.state_file):
            try:
                with open(self.state_file, 'r') as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode state file {self.state_file}: {e}. Starting with empty state.")
                return {}
        return {}

    def save_state(self):
        os.makedirs(os.path.dirname(self.state_file), exist_ok=True)
        with open(self.state_file, 'w') as f:
            json.dump(self.state, f, indent=2)
        logger.info(json.dumps({"event": "state_saved", "file": self.state_file}))

    def get(self, key: str, default: Any = None) -> Any:
        return self.state.get(key, default)

    def set(self, key: str, value: Any):
        self.state[key] = value

class CacheManager:
    """Manages hash-based caching for LLM responses and tool results, analogous to SSnaHke's cache.tsv."""
    def __init__(self, cache_file: str, ttl: int = AGENT_CACHE_TTL):
        self.cache_file = cache_file
        self.ttl = ttl
        self.cache: Dict[str, Any] = self._load_cache()

    def _load_cache(self) -> Dict[str, Any]:
        if os.path.exists(self.cache_file):
            try:
                with open(self.cache_file, 'r') as f:
                    cache_data = json.load(f)
                    # Filter out expired entries
                    current_time = time.time()
                    active_cache = {
                        k: v for k, v in cache_data.items()
                        if current_time - v.get("timestamp", 0) < self.ttl
                    }
                    if len(cache_data) != len(active_cache):
                        logger.info(json.dumps({"event": "cache_pruned", "expired_entries": len(cache_data) - len(active_cache)}))
                    return active_cache
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode cache file {self.cache_file}: {e}. Starting with empty cache.")
                return {}
        return {}

    def _generate_key(self, data: Any) -> str:
        # Use a consistent, sorted JSON representation for hashing
        serialized_data = json.dumps(data, sort_keys=True).encode('utf-8')
        return hashlib.sha256(serialized_data).hexdigest()

    def get(self, data: Any) -> Optional[Any]:
        key = self._generate_key(data)
        entry = self.cache.get(key)
        if entry and (time.time() - entry.get("timestamp", 0) < self.ttl):
            logger.debug(json.dumps({"event": "cache_hit", "key": key}))
            return entry["value"]
        logger.debug(json.dumps({"event": "cache_miss", "key": key}))
        return None

    def set(self, data: Any, value: Any):
        key = self._generate_key(data)
        self.cache[key] = {"value": value, "timestamp": time.time()}
        self._save_cache()
        logger.debug(json.dumps({"event": "cache_set", "key": key}))

    def _save_cache(self):
        os.makedirs(os.path.dirname(self.cache_file), exist_ok=True)
        with open(self.cache_file, 'w') as f:
            json.dump(self.cache, f, indent=2)

class ToolDispatcher:
    """Dispatches tool calls in parallel, analogous to SSnaHke's xargs -P."""
    def __init__(self, tools: Dict[str, Callable], max_workers: int = AGENT_TOOL_JOBS, cache_manager: Optional[CacheManager] = None):
        self.tools = tools
        self.executor = ThreadPoolExecutor(max_workers=max_workers)
        self.cache_manager = cache_manager

    def _execute_tool(self, tool_name: str, tool_args: Dict[str, Any]) -> Dict[str, Any]:
        start_time = time.time()
        tool_func = self.tools.get(tool_name)
        if not tool_func:
            error_msg = f"Tool '{tool_name}' not found."
            logger.error(json.dumps({"event": "tool_error", "tool_name": tool_name, "error": error_msg}))
            return {"tool_name": tool_name, "tool_args": tool_args, "error": error_msg, "duration": time.time() - start_time}

        # Check cache before execution
        cache_key_data = {"tool_name": tool_name, "tool_args": tool_args}
        if self.cache_manager:
            cached_result = self.cache_manager.get(cache_key_data)
            if cached_result is not None:
                logger.info(json.dumps({"event": "tool_cache_hit", "tool_name": tool_name, "duration": time.time() - start_time}))
                return {"tool_name": tool_name, "tool_args": tool_args, "result": cached_result, "duration": time.time() - start_time}

        if AGENT_DRY_RUN:
            logger.info(json.dumps({"event": "tool_dry_run", "tool_name": tool_name, "tool_args": tool_args}))
            return {"tool_name": tool_name, "tool_args": tool_args, "result": f"Dry run: Would execute {tool_name} with {tool_args}", "duration": time.time() - start_time}

        try:
            result = tool_func(**tool_args)
            if self.cache_manager:
                self.cache_manager.set(cache_key_data, result)
            logger.info(json.dumps({"event": "tool_executed", "tool_name": tool_name, "duration": time.time() - start_time}))
            return {"tool_name": tool_name, "tool_args": tool_args, "result": result, "duration": time.time() - start_time}
        except Exception as e:
            error_msg = f"Error executing tool '{tool_name}': {e}"
            logger.error(json.dumps({"event": "tool_error", "tool_name": tool_name, "error": error_msg, "duration": time.time() - start_time}))
            return {"tool_name": tool_name, "tool_args": tool_args, "error": error_msg, "duration": time.time() - start_time}

    def dispatch(self, tool_calls: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        futures = [self.executor.submit(self._execute_tool, tc["function"]["name"], tc["function"]["arguments"]) for tc in tool_calls]
        results = []
        for future in as_completed(futures):
            results.append(future.result())
        return results

class LLMClient:
    """Handles LLM interactions, including tool call parsing and response generation."""
    def __init__(self, api_key: str, base_url: str, model: str = AGENT_MODEL):
        # This assumes an OpenAI-compatible API. In a real scenario, you'd import from `openai`
        # and configure it. For sandbox, we'll simulate or use a direct call if available.
        self.api_key = api_key
        self.base_url = base_url
        self.model = model
        logger.info(json.dumps({"event": "llm_client_init", "model": self.model, "base_url": self.base_url}))

    def _call_llm_api(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        # Simulate LLM call for now. In a real scenario, this would be an API call.
        # Example: from openai import OpenAI; client = OpenAI(api_key=self.api_key, base_url=self.base_url)
        # response = client.chat.completions.create(...)
        logger.warning(json.dumps({"event": "llm_api_mock", "message": "LLM API call is mocked. Replace with actual API integration." }))
        time.sleep(1) # Simulate network latency

        # Mock response for demonstration
        if any("tool_calls" in m for m in messages):
            # If there were tool calls, assume the LLM responds with a final answer
            return {
                "choices": [{
                    "message": {"role": "assistant", "content": "Based on the tool results, I have completed the task."}
                }],
                "usage": {"prompt_tokens": 50, "completion_tokens": 20}
            }
        else:
            # Simulate a tool call request from the LLM
            return {
                "choices": [{
                    "message": {
                        "role": "assistant",
                        "content": "I need to use a tool.",
                        "tool_calls": [{
                            "id": "call_123",
                            "type": "function",
                            "function": {"name": "example_tool", "arguments": "{\"query\": \"test data\"}"}
                        }]
                    }
                }],
                "usage": {"prompt_tokens": 30, "completion_tokens": 30}
            }

    def chat(self, messages: List[Dict[str, Any]], tools: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        start_time = time.time()
        response = self._call_llm_api(messages, tools)
        end_time = time.time()
        duration = end_time - start_time
        prompt_tokens = response.get("usage", {}).get("prompt_tokens", 0)
        completion_tokens = response.get("usage", {}).get("completion_tokens", 0)
        total_tokens = prompt_tokens + completion_tokens

        logger.info(json.dumps({
            "event": "llm_call",
            "model": self.model,
            "duration": duration,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "total_tokens": total_tokens
        }))
        return response

class AgentLoop:
    """Main agent loop for multi-turn LLM interactions with tool execution."""
    def __init__(self,
                 agent_name: str,
                 llm_client: LLMClient,
                 tools: Dict[str, Callable],
                 state_manager: StateManager,
                 cache_manager: CacheManager,
                 interval: int = AGENT_INTERVAL,
                 dry_run: bool = AGENT_DRY_RUN,
                 max_turns: int = 10
                ):
        self.agent_name = agent_name
        self.llm_client = llm_client
        self.tools = tools
        self.state_manager = state_manager
        self.cache_manager = cache_manager
        self.interval = interval
        self.dry_run = dry_run
        self.max_turns = max_turns
        self.tool_dispatcher = ToolDispatcher(tools, cache_manager=cache_manager)

        self.messages: List[Dict[str, Any]] = self.state_manager.get("conversation_history", [])
        if not self.messages:
            self.messages.append({"role": "system", "content": f"You are {self.agent_name}, an AI assistant."})

        logger.info(json.dumps({"event": "agent_init", "agent_name": agent_name, "dry_run": dry_run}))

    def _process_llm_response(self, response: Dict[str, Any]) -> bool:
        message = response["choices"][0]["message"]
        self.messages.append(message)

        if message.get("tool_calls"):
            tool_calls = message["tool_calls"]
            logger.info(json.dumps({"event": "tool_calls_received", "count": len(tool_calls)}))
            tool_results = self.tool_dispatcher.dispatch(tool_calls)

            for result in tool_results:
                self.messages.append({
                    "tool_call_id": result["tool_name"], # In real API, this would be tool_call_id from LLM
                    "role": "tool",
                    "name": result["tool_name"],
                    "content": json.dumps(result.get("result") or result.get("error"))
                })
            return False # Continue for another LLM turn to process tool results
        else:
            logger.info(json.dumps({"event": "final_llm_response", "content": message["content"]}))
            return True # Task completed or no more tool calls

    def run_once(self) -> str:
        """Executes a single turn of the agent loop."""
        logger.info(json.dumps({"event": "run_once_start", "turn_count": len(self.messages)}))
        current_messages_for_hash = [m for m in self.messages if m["role"] != "tool"] # Don't hash tool results for LLM input
        llm_input_hash = self.cache_manager.get(current_messages_for_hash)

        llm_response = None
        if llm_input_hash:
            llm_response = llm_input_hash # Cache hit
            logger.info(json.dumps({"event": "llm_cache_hit"}))
        else:
            llm_response = self.llm_client.chat(self.messages, tools=list(self.tools.keys())) # Pass tool names for LLM to know
            self.cache_manager.set(current_messages_for_hash, llm_response)

        is_complete = self._process_llm_response(llm_response)
        self.state_manager.set("conversation_history", self.messages)
        self.state_manager.save_state()
        logger.info(json.dumps({"event": "run_once_end", "is_complete": is_complete}))
        return self.messages[-1]["content"]

    def run_daemon(self):
        """Runs the agent in a continuous loop."""
        logger.info(json.dumps({"event": "daemon_start", "interval": self.interval}))
        try:
            while True:
                self.run_once()
                time.sleep(self.interval)
        except KeyboardInterrupt:
            logger.info(json.dumps({"event": "daemon_shutdown", "reason": "KeyboardInterrupt"}))
        except Exception as e:
            logger.error(json.dumps({"event": "daemon_error", "error": str(e)}))
        finally:
            self.state_manager.save_state()

    def run_interactive(self):
        """Runs the agent in an interactive REPL mode."""
        logger.info(json.dumps({"event": "interactive_start"}))
        print(f"\nAgent '{self.agent_name}' in interactive mode. Type 'exit' to quit.\n")
        try:
            while True:
                user_input = input("You: ")
                if user_input.lower() == 'exit':
                    break
                self.messages.append({"role": "user", "content": user_input})
                final_response_content = self.run_once()
                print(f"Agent: {final_response_content}")
                if "Based on the tool results, I have completed the task." in final_response_content: # Heuristic for mock completion
                    print("Agent indicates task completion.")
                    break
        except KeyboardInterrupt:
            logger.info(json.dumps({"event": "interactive_shutdown", "reason": "KeyboardInterrupt"}))
        except Exception as e:
            logger.error(json.dumps({"event": "interactive_error", "error": str(e)}))
        finally:
            self.state_manager.save_state()

# --- Example Tool (for demonstration) ---
def example_tool(query: str) -> Dict[str, Any]:
    """An example tool that processes a query."""
    logger.info(json.dumps({"event": "example_tool_called", "query": query}))
    return {"status": "success", "processed_query": query.upper(), "timestamp": datetime.now().isoformat()}

# --- Main Execution Block ---
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Agentic AI Worker inspired by Deep SSnaHke.")
    parser.add_argument("--once", action="store_true", help="Run a single turn and exit.")
    parser.add_argument("--daemon", action="store_true", help="Run in daemon mode (continuous loop).")
    parser.add_argument("--interactive", action="store_true", help="Run in interactive REPL mode.")
    parser.add_argument("--dry-run", action="store_true", help="Enable dry run mode for tools.")
    parser.add_argument("--agent-name", type=str, default="DeepSSnaHkeAgent", help="Name of the agent.")
    parser.add_argument("--model", type=str, default=AGENT_MODEL, help="LLM model to use.")
    parser.add_argument("--interval", type=int, default=AGENT_INTERVAL, help="Interval for daemon mode in seconds.")
    parser.add_argument("--cache-ttl", type=int, default=AGENT_CACHE_TTL, help="Cache TTL in seconds.")
    parser.add_argument("--log-level", type=str, default=AGENT_LOG_LEVEL, help="Logging level (DEBUG, INFO, WARNING, ERROR).")

    args = parser.parse_args()

    # Override env vars with CLI args if provided
    if args.dry_run: os.environ["AGENT_DRY_RUN"] = "1"
    if args.model: os.environ["AGENT_MODEL"] = args.model
    if args.interval: os.environ["AGENT_INTERVAL"] = str(args.interval)
    if args.cache_ttl: os.environ["AGENT_CACHE_TTL"] = str(args.cache_ttl)
    if args.log_level: os.environ["AGENT_LOG_LEVEL"] = args.log_level

    # Re-configure logging if level changed via CLI
    if AGENT_LOG_LEVEL != os.getenv("AGENT_LOG_LEVEL"): # Check if it was overridden
        for handler in logger.handlers[:]: # Remove existing handlers
            logger.removeHandler(handler)
        logging.basicConfig(
            level=os.getenv("AGENT_LOG_LEVEL", "INFO").upper(),
            format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": %(message)s}',
            datefmt='%Y-%m-%d %H:%M:%S',
            handlers=[
                logging.FileHandler(LOG_FILE),
                logging.StreamHandler()
            ]
        )

    # Initialize components
    state_manager = StateManager(os.path.join(AGENT_STATE_DIR, "state.json"))
    cache_manager = CacheManager(os.path.join(AGENT_STATE_DIR, "cache.json"))
    llm_client = LLMClient(api_key="mock_api_key", base_url="mock_base_url", model=args.model)

    # Register tools
    available_tools = {"example_tool": example_tool}

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
        agent_loop.run_once()
    elif args.daemon:
        agent_loop.run_daemon()
    elif args.interactive:
        agent_loop.run_interactive()
    else:
        print("Please specify a run mode: --once, --daemon, or --interactive.")

