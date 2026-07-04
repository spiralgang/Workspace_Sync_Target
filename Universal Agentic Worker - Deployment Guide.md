# Universal Agentic Worker - Deployment Guide

## Overview

This package contains four deployment options for the Universal Agentic Worker:

1. **Android APK** - Native Android application
2. **Progressive Web App (PWA)** - Chrome/browser-based
3. **Web RCI** - Remote Command Interface dashboard
4. **CLI Launcher** - Terminal-based command-line interface

All options run the same core agentic worker with multi-turn LLM interactions and comprehensive tool execution.

---

## Option 1: Android APK

### Prerequisites
- Docker (recommended) or local Android SDK
- 2GB+ disk space
- Java 11+

### Build Instructions

#### Using Docker (Alpine Linux aarch64)

```bash
cd /home/ubuntu/universal_agentic_worker_apk
docker build -t universal-agentic-worker-apk:latest .
docker run --rm -v $(pwd)/output:/output universal-agentic-worker-apk:latest
```

#### Local Build (without Docker)

```bash
cd /home/ubuntu/universal_agentic_worker_apk
chmod +x build.sh
./build.sh
```

### Installation

1. Transfer the APK to your Android device
2. Enable "Unknown Sources" in Settings > Security
3. Open the APK file and tap "Install"
4. Launch "Universal Agentic Worker" from your app drawer

### Configuration

- Set your LLM provider API keys in the Settings panel
- Configure agent parameters (ID, mode, prompt, model)
- Toggle dry-run mode for safe testing

---

## Option 2: Progressive Web App (PWA)

### Prerequisites
- Node.js 16+ and npm/pnpm
- Modern web browser (Chrome, Firefox, Edge, Safari)

### Build Instructions

```bash
cd /home/ubuntu/universal_agentic_worker_pwa
npm install  # or: pnpm install
npm run build
```

### Deployment

#### Local Development

```bash
npm run dev
```

Open `http://localhost:3000` in your browser.

#### Production Deployment

```bash
# Build for production
npm run build

# Serve with HTTP server
npm run serve
```

Or deploy the `dist/` folder to any static hosting service:
- Vercel
- Netlify
- GitHub Pages
- AWS S3 + CloudFront
- Firebase Hosting

### Installation as App

1. Open the PWA in Chrome/Edge
2. Click the "Install" button in the address bar
3. Or: Menu > "Install app"
4. The app will be added to your home screen/app drawer

### Features

- Offline support via Service Worker
- Installable as standalone app
- Responsive design (mobile, tablet, desktop)
- Terminal emulator for command execution
- Real-time agent status monitoring

---

## Option 3: Web RCI (Remote Command Interface)

### Prerequisites
- Python 3.8+
- FastAPI and dependencies

### Installation

```bash
cd /home/ubuntu/universal_agentic_worker_rci
pip3 install -r requirements.txt
```

### Running the Server

```bash
python3 app/main.py
```

The server will start on `http://localhost:8000`

### Accessing the Dashboard

1. Open `http://localhost:8000` in your browser
2. Configure agent parameters in the left panel
3. Click "Start" to begin the agent
4. Use the terminal to execute commands

### Remote Access

To access from another machine:

```bash
# On the server machine, expose to all interfaces
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000

# Access from remote machine
# http://<server-ip>:8000
```

### Deployment

#### Docker Deployment

```bash
cd /home/ubuntu/universal_agentic_worker_rci
docker build -t universal-agentic-worker-rci:latest .
docker run -p 8000:8000 universal-agentic-worker-rci:latest
```

#### Cloud Deployment

- **Heroku**: `git push heroku main`
- **Railway**: Connect GitHub repo
- **Render**: Create new Web Service
- **AWS EC2**: Run on Ubuntu instance
- **DigitalOcean**: Deploy to Droplet

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/` | GET | Dashboard UI |
| `/api/agent/start` | POST | Start agent with config |
| `/api/agent/stop` | POST | Stop running agent |
| `/api/terminal/execute` | POST | Execute shell command |
| `/api/agent/status` | GET | Get agent status |
| `/api/agents` | GET | List all active agents |

---

## Option 4: CLI Launcher (Terminal)

### Prerequisites
- Python 3.8+
- Bash shell (Linux/macOS) or PowerShell (Windows)

### Installation

```bash
cd /home/ubuntu/universal_agentic_worker
chmod +x launcher.sh
```

### Usage

#### Interactive Mode (Default)

```bash
./launcher.sh
```

#### One-Shot Mode

```bash
./launcher.sh --mode one-shot --prompt "Your task here"
```

#### Daemon Mode

```bash
./launcher.sh --mode daemon --llm-provider ollama
```

#### With Custom Configuration

```bash
./launcher.sh \
  --agent-id my_agent \
  --mode interactive \
  --llm-provider openai \
  --llm-model gpt-4o \
  --dry-run
```

### Help

```bash
./launcher.sh --help
```

---

## Configuration & Environment Variables

### Setting API Keys

#### Option 1: Environment Variables

```bash
export OPENAI_API_KEY="sk-..."
export GEMINI_API_KEY="..."
export OLLAMA_BASE_URL="http://localhost:11434"
```

#### Option 2: .env File

Create `.env` in the project root:

```dotenv
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o
AGENT_DRY_RUN=True
```

#### Option 3: Web UI Settings

- **PWA**: Settings panel (stored in localStorage)
- **Web RCI**: Settings modal
- **Android**: Settings screen
- **CLI**: Environment variables

### Supported LLM Providers

| Provider | Config | Notes |
|----------|--------|-------|
| OpenAI | `openai` | Requires API key |
| Google Gemini | `gemini` | Requires API key |
| GitHub Copilot | `copilot` | Conceptual integration |
| Ollama | `ollama` | Local LLM, no API key needed |

---

## Troubleshooting

### Python Dependencies Issues

```bash
pip3 install --upgrade pip
pip3 install -r requirements.txt --force-reinstall
```

### Port Already in Use

```bash
# Find process using port 8000
lsof -i :8000

# Kill process
kill -9 <PID>

# Or use different port
python3 app/main.py --port 9000
```

### LLM Provider Connection Issues

- **OpenAI**: Verify API key is valid and has credits
- **Gemini**: Check API key and enable Generative AI API
- **Ollama**: Ensure Ollama is running (`ollama serve`)
- **Copilot**: Verify GitHub authentication

### Agent Not Starting

1. Check logs: `tail -f ~/.universal_agent/trail.log`
2. Verify LLM provider is configured
3. Test with `--dry-run` mode first
4. Check file permissions in working directory

---

## Security Considerations

### Dry-Run Mode

Always test with `--dry-run` enabled first. This prevents:
- Accidental file deletion
- Unintended system modifications
- Unauthorized API calls

### API Key Management

- Never commit `.env` files to version control
- Use environment variables or secure vaults
- Rotate keys regularly
- Use service accounts with minimal permissions

### Network Security

- Deploy Web RCI behind a firewall
- Use HTTPS for remote access
- Implement authentication/authorization
- Run in isolated environments for untrusted prompts

### File System Access

- Restrict agent to specific directories
- Use read-only mode when possible
- Monitor file operations in logs
- Implement file access policies

---

## Performance Optimization

### Caching

The agent uses intelligent caching to reduce API costs:
- LLM response caching (configurable TTL)
- Tool execution result caching
- Hash-based deduplication

### Parallel Execution

- Multiple tools execute in parallel
- Configurable worker pool size
- Automatic load balancing

### Resource Management

- Memory-efficient streaming
- Configurable timeout values
- Background garbage collection

---

## Monitoring & Logging

### Log Locations

| Component | Log File |
|-----------|----------|
| Agent | `~/.universal_agent/trail.log` |
| Web RCI | stdout/stderr |
| PWA | Browser console |
| Android | Logcat |

### Log Format

All logs use JSON-lines format for easy parsing:

```json
{"timestamp": "2024-01-15T10:30:00Z", "level": "INFO", "message": "Agent started"}
{"timestamp": "2024-01-15T10:30:01Z", "level": "DEBUG", "tool": "file_read", "status": "success"}
```

### Monitoring Commands

```bash
# Watch agent logs in real-time
tail -f ~/.universal_agent/trail.log

# Filter by level
grep '"level": "ERROR"' ~/.universal_agent/trail.log

# Count events
grep '"tool":' ~/.universal_agent/trail.log | wc -l
```

---

## Support & Documentation

- **README**: `/home/ubuntu/universal_agentic_worker/README.md`
- **Architecture**: `/home/ubuntu/universal_agentic_worker_architecture.md`
- **API Reference**: See Web RCI section above
- **Examples**: See each deployment option's directory

---

## License

MIT License - See LICENSE file for details

---

**Last Updated**: January 2024
**Version**: 1.0.0
