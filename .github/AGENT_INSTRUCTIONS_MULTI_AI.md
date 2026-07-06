# AGENT INSTRUCTIONS: Multi-AI Code Review System

## MANDATORY FILE INGESTION
Before executing any code review, you **MUST** read and process:
1. `.github/context-bundle.json` - Contains changed files, diffs, and critical context
2. `layers/README.md` - Layered architecture overview
3. `.github/AGENT_INSTRUCTIONS.md` - This file (meta-instructions)
4. `layers/matrix-config/matrix.yml` - Matrix execution configuration
5. `layers/matrix-config/agent-index.json` - Registered agent capabilities

**DO NOT** proceed without ingesting the context bundle. It contains the complete PR diff and repository state.

---

## REVIEW CRITERIA

### 1. Correctness Analysis
- Verify logic matches intended behavior from diff comments
- Check for off-by-one errors, null pointer risks, type mismatches
- Validate async/await patterns and error handling
- Ensure matrix combinations are computed correctly (cartesian product)

### 2. Security Audit
- **API Key Handling**: Never log or expose keys; use environment variables only
- **Path Traversal**: Validate all file paths against repo root
- **Injection Risks**: Sanitize user inputs in scripts (bash, Python, SQL)
- **Permission Scope**: GitHub token permissions should be minimal (read vs write)

### 3. Architecture Compliance
- **Layer Boundaries**: Changes must respect layer isolation (skill-protocol ≠ state-engine)
- **Bridge Patterns**: Cross-layer communication must use defined bridges (HTTP IPC, stdio)
- **Anti-Drift**: New code must align with existing patterns in `references/` directories
- **State Lock**: No actions outside validated phases (bootstrap → matrix → index → run → persist)

### 4. Performance Checks
- **Token Optimization**: Context bundles must stay under 100K chars (use strategies)
- **Parallel Efficiency**: Matrix jobs should maximize parallelization without resource contention
- **Cache Utilization**: Check for redundant computations that could be cached

### 5. Standards Compliance
- Follow existing code style (Python: black/ruff, TypeScript: eslint/prettier)
- YAML files must pass schema validation
- Commit messages follow conventional commits if auto-generated

---

## OUTPUT FORMAT

Return analysis as JSON:
```json
{
  "verdict": "PASS|FAIL|CONDITIONAL",
  "score": 0-10,
  "issues": [
    {
      "severity": "critical|high|medium|low",
      "category": "correctness|security|architecture|performance",
      "file": "path/to/file.py",
      "line": 42,
      "description": "Clear description of issue",
      "suggestion": "Recommended fix"
    }
  ],
  "positive_findings": ["List of good practices observed"],
  "drift_detected": false,
  "token_usage_estimate": 45000
}
```

---

## ANTI-FLAIL ENFORCEMENT

- **Reject Duplicates**: If same issue already reported by another AI, add confidence score instead of repeating
- **Context Awareness**: Reference specific lines from the context bundle, not generic advice
- **Actionable Feedback**: Every issue must have a concrete suggestion or code snippet
- **No Hallucination**: Do not invent APIs, functions, or patterns not present in the codebase

---

## PROVIDER-SPECIFIC OPTIMIZATIONS

### OpenRouter
- Use system prompt for role definition
- Leverage multiple model fallbacks

### HuggingFace
- Format as simple text prompt if chat API fails
- Specify max_new_tokens to prevent truncation

### GitHub Models
- Include Accept header for proper response format
- Use temperature 0.2 for deterministic reviews

### Nvidia
- Optimize for Llama3 instruction format
- Keep prompts concise due to token limits

### Qwen/Kimi
- Use native message format
- Include explicit JSON output instructions

---

## FALLBACK BEHAVIOR

If API calls fail:
1. Retry once with exponential backoff (2s, 4s)
2. If still failing, return structured error:
   ```json
   {"status": "failed", "error": "Connection timeout", "retry_after": 60}
   ```
3. Never block the PR workflow due to AI failures (`continue-on-error: true`)

---

## SELF-HOSTED RUNNER INTEGRATION

When ephemeral runners are available:
1. Detect runner via `RUNNER_STORAGE` environment variable
2. Offload heavy context processing to runner
3. Stream results back to main workflow
4. Cleanup runner after TTL expires

Runner labels to check: `ephemeral`, `termux`, `agentic-matrix`, `multi-ai`

---

## CONTINUOUS IMPROVEMENT

After each review cycle:
1. Log metrics to `.github/review-metrics.jsonl`
2. Update provider success rates
3. Adjust token strategies based on actual usage
4. Refine prompt templates for better accuracy

Metrics to track:
- Provider uptime percentage
- Average review time per provider
- Issue detection rate (false positives/negatives)
- Token efficiency ratio
