# GitHub Actions Workflows

This directory contains the complete CI/CD automation for the Agentic Matrix Monorepo.

## Workflow Overview

| File | Purpose | When It Runs |
|------|---------|--------------|
| `main.yml` | Primary CI pipeline | Push to main/develop branches |
| `orchestrator.yml` | Agent matrix orchestration | Manual dispatch |
| `librarian.yml` | Backend service validation | PR on server code |
| `dashboard.yml` | Frontend build & test | PR on client code |
| `glm-coder-companion.yml` | **Multi-AI code review** | All PRs (opened/synchronize/reopened) |
| `ephemeral-runner-orchestrator.yml` | Self-hosted runner lifecycle | Manual dispatch or hourly cleanup |
| `extract-zip.yml` | Automated ZIP extraction | Push containing .zip files |
| `matrix-orchestrator.yml` | Matrix build execution | Manual dispatch |

## Multi-AI Code Review System

### Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Pull Request Opened                      │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              context-preparation Job                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  context_engine.py                                   │   │
│  │  - Gets changed files + diffs                        │   │
│  │  - Loads critical context (layers/README, etc.)      │   │
│  │  - Generates token-optimized bundle                  │   │
│  │  Strategies: minimal | balanced | full               │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ (uploads artifact)
┌─────────────────────────────────────────────────────────────┐
│              multi-ai-review Job (Matrix)                   │
│  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐           │
│  │OpenRouter│ │HuggingFace│ │GitHub  │ │Nvidia  │           │
│  │         │ │         │ │Models   │ │        │           │
│  └─────────┘ └─────────┘ └─────────┘ └─────────┘           │
│  ┌─────────┐ ┌─────────┐                                   │
│  │ Qwen    │ │ Kimi    │                                   │
│  └─────────┘ └─────────┘                                   │
│                                                             │
│  Each provider calls ai_gateway.py with:                   │
│  - Context bundle (changed files + repo structure)         │
│  - Auto-sourced API key (ENV → secrets.json → skip)        │
│  - Structured review prompt                                │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼ (each uploads reviews)
┌─────────────────────────────────────────────────────────────┐
│             aggregate-and-comment Job                       │
│  - Downloads all AI reviews                                 │
│  - Aggregates into single report                            │
│  - Posts comment on PR with:                                │
│    * Verdict per provider (✅/⚠️/❌)                        │
│    * Score (0-10)                                           │
│    * Key issues found                                       │
│    * Expandable detailed responses                          │
└─────────────────────────────────────────────────────────────┘
```

### Supported AI Providers

| Provider | Model | Auth Env Var | Free Tier |
|----------|-------|--------------|-----------|
| OpenRouter | Llama-3-70B-Instruct | `OPENROUTER_API_KEY` | Yes (credits) |
| HuggingFace | Qwen2.5-Coder-32B | `HF_API_KEY` | Yes (rate limited) |
| GitHub Models | GPT-4o | `GITHUB_TOKEN` | Yes (Actions) |
| Nvidia | Llama3-70B-Instruct | `NVIDIA_API_KEY` | Yes (credits) |
| Qwen (DashScope) | qwen-max | `DASHSCOPE_API_KEY` | Yes (tokens) |
| Kimi | moonshot-v1-8k | `KIMI_API_KEY` | Yes (tokens) |

### Setup Instructions

1. **Add API Keys** (choose one method):
   
   **Option A: GitHub Secrets (Recommended)**
   ```bash
   gh secret set OPENROUTER_API_KEY --body "sk-or-..."
   gh secret set HF_API_KEY --body "hf_..."
   # ... repeat for other providers
   ```
   
   **Option B: Local secrets.json** (for testing, gitignored)
   ```bash
   cp .github/secrets.example.json .github/secrets.json
   # Edit .github/secrets.json with your keys
   ```

2. **Trigger on PR**: The workflow runs automatically on all PRs to `main` or `develop`.

3. **Manual Trigger**:
   ```bash
   gh workflow run glm-coder-companion.yml \
     --field strategy="full" \
     --ref feature-branch
   ```

### Context Strategies

| Strategy | Content Included | Token Estimate | Use Case |
|----------|------------------|----------------|----------|
| `minimal` | Diffs only | ~10K | Quick sanity checks |
| `balanced` | Diffs + content (if under limit) | ~50K | Standard PRs |
| `full` | Diffs + full content + dependencies | ~100K | Complex refactors |

## Ephemeral Runner System

### Purpose

Provides temporary self-hosted runners on network storage for:
- Heavy compute tasks (matrix builds, large context processing)
- Termux/Android-native execution environments
- Extended workflow runtime beyond GitHub's 6-hour limit

### Lifecycle

1. **Setup** (`action=setup`):
   - Creates runner directory on network storage
   - Downloads GitHub Actions runner package
   - Configures with repository token
   - Returns connection info as output

2. **Start** (`action=start`):
   - Launches runner process in background
   - Begins accepting jobs from workflow queue

3. **Cleanup** (`action=cleanup` or scheduled):
   - Stops runner gracefully
   - Removes runner directory
   - Clears state files

### Usage

```bash
# Start a new ephemeral runner
gh workflow run ephemeral-runner-orchestrator.yml \
  --field action=setup \
  --field ttl_minutes=120

# Runner info output example:
# {
#   "runner_name": "ephemeral-a1b2c3d4",
#   "storage_path": "/sdcard/.termux/runners/ephemeral-a1b2c3d4",
#   "labels": ["ephemeral", "agentic-matrix", "multi-ai"],
#   "status": "ready"
# }

# Cleanup after use
gh workflow run ephemeral-runner-orchestrator.yml \
  --field action=cleanup
```

### Scheduled Cleanup

A cron job runs hourly to clean up stale runners:
```yaml
schedule:
  - cron: '0 * * * *'  # Every hour
```

## Helper Scripts

Located in `.github/helper-scripts/`:

| Script | Purpose | Called By |
|--------|---------|-----------|
| `context_engine.py` | Generates token-optimized context bundles | `glm-coder-companion.yml` |
| `ai_gateway.py` | Routes requests to multiple AI providers | `glm-coder-companion.yml` |
| `ephemeral_runner.py` | Manages self-hosted runner lifecycle | `ephemeral-runner-orchestrator.yml` |

## Troubleshooting

### AI Reviews Not Posting

1. Check workflow logs for API key errors
2. Verify secrets are set correctly
3. Ensure `continue-on-error: true` isn't hiding failures

### Runner Setup Fails

1. Check `RUNNER_STORAGE` path is writable
2. Verify network connectivity for runner download
3. Review runner logs at `{storage_path}/runner.log`

### Context Bundle Too Large

1. Use `strategy=minimal` for faster, lighter reviews
2. Exclude non-essential files via `.gitattributes`
3. Split large PRs into smaller, focused changes

## Adding New AI Providers

1. Add provider config to `ai_gateway.py`:
   ```python
   "new_provider": {
       "url": "https://api.example.com/chat/completions",
       "model": "model-name",
       "auth_env": "NEW_PROVIDER_API_KEY",
       "payload_template": self._new_provider_payload
   }
   ```

2. Implement payload template method:
   ```python
   def _new_provider_payload(self, messages: List[Dict]) -> Dict:
       return {"model": "...", "messages": messages}
   ```

3. Add to workflow matrix in `glm-coder-companion.yml`:
   ```yaml
   provider: [..., new_provider]
   ```

4. Document in this README
