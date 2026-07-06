# Deep SSnaHke Agentic Duplicate Hunter — Project TODO

## Phase 1: Database Schema & Backend Procedures

- [ ] Create database schema: scans, scan_configs, duplicate_groups, duplicate_files, trail_logs, cache_entries, agent_state
- [ ] Implement tRPC procedures: scan.create, scan.start, scan.stop, scan.pause, scan.getStatus
- [ ] Implement tRPC procedures: config.get, config.update, config.getDefaults
- [ ] Implement tRPC procedures: duplicates.list, duplicates.getGroup, duplicates.markIgnored
- [ ] Implement tRPC procedures: duplicates.quarantine, duplicates.delete (with dry-run gate)
- [ ] Implement tRPC procedures: history.getLogs, history.search, history.filter
- [ ] Implement tRPC procedures: cache.getStats, cache.clear
- [ ] Implement tRPC procedures: agent.getState, agent.getConversation
- [ ] Implement tRPC procedures: llm.analyzeGroup, llm.chat (scoped to scan context)
- [ ] Integrate agentic worker backend loop with real-time progress streaming
- [ ] Set up WebSocket or Server-Sent Events (SSE) for real-time progress updates

## Phase 2: Cyberpunk UI Theme & Dashboard Layout

- [ ] Define cyberpunk color palette (deep black, neon pink, electric cyan) in Tailwind/CSS variables
- [ ] Create global cyberpunk styling with neon glow effects and geometric borders
- [ ] Implement DashboardLayout with sidebar navigation covering all sections
- [ ] Design HUD-style corner brackets and technical line elements
- [ ] Create responsive mobile-first layout
- [ ] Set up navigation routes for all major sections

## Phase 3: Feature Pages Implementation

- [ ] Dashboard home: live scan status, summary stats, recent activity feed
- [ ] Scan configuration panel: directory paths, hash algorithm, TOOL_JOBS, cache TTL, dry-run toggle, prune strategy
- [ ] Duplicate groups viewer: paginated table with file paths, sizes, last-modified, recommended keep file
- [ ] Per-group action controls: quarantine, delete, mark ignored (all with dry-run confirmations)
- [ ] Scan history log viewer: searchable, filterable JSON-lines log
- [ ] Cache management panel: view stats, hit/miss ratio, TTL settings, clear cache button
- [ ] Agent state inspector: view conversation history, active tool calls, pending actions
- [ ] LLM chat interface: scoped to scan result context

## Phase 4: Real-Time Integration & Advanced Features

- [ ] Implement real-time progress streaming from agentic worker
- [ ] Build dry-run confirmation dialog component
- [ ] Integrate LLM analysis for duplicate groups
- [ ] Implement LLM chat interface for Q&A about scan results
- [ ] Add start/stop/pause scan controls
- [ ] Implement cache hit/miss tracking and display
- [ ] Add search and filter to trail log viewer

## Phase 5: Testing & Delivery

- [ ] Test all tRPC procedures with vitest
- [ ] Test agentic worker integration and real-time streaming
- [ ] Test UI responsiveness on mobile and desktop
- [ ] Verify cyberpunk styling consistency across all pages
- [ ] Test dry-run confirmations and destructive actions
- [ ] Test LLM chat and analysis features
- [ ] Create initial checkpoint
- [ ] Deliver to user with demo walkthrough

