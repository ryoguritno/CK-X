# Study Companion — Design Spec

**Date:** 2026-03-29
**Author:** agungtguritno
**Goal:** A Telegram bot that delivers daily task notifications, tracks step-level progress, and provides AI mentoring (explain/hint/quiz) for the DevOps certification roadmap.

---

## Context

This system runs alongside `ck-x-simulator`. It reads the existing roadmap plan at `docs/superpowers/plans/2026-03-29-devops-certification-roadmap.md` and turns it into a daily accountability + mentoring tool.

**User:** Junior DevOps, studying at Pace A (5–7h/week), targeting LFCS → CKA → CKAD → CKS → ICA → CNPE.

---

## Architecture

A new `study-companion` Docker service added to the existing `docker-compose.yml`. Four internal components communicating within a single Python process:

| Component | Responsibility |
|-----------|---------------|
| **Bot handler** | Receives Telegram messages, routes to the right feature |
| **Scheduler** | Fires morning (07:00) + evening conditional (19:00) |
| **State manager** | SQLite — persists tasks, steps, sessions |
| **Mentor** | Calls Ollama HTTP API with roadmap context |

**Ollama** runs on the host machine (not containerized — too RAM-heavy). The bot reaches it via `http://host.docker.internal:11434`.

**Roadmap parsing:** On first startup, the bot parses the roadmap markdown and seeds the SQLite database with all tasks and steps. Subsequent startups detect existing state and skip re-seeding.

---

## Ollama Setup

### Installation

```bash
curl -fsSL https://ollama.com/install.sh | sh
systemctl status ollama   # verify running
```

### Model Selection

| Model | RAM needed | Verdict |
|-------|-----------|---------|
| `llama3.1:8b` | ~6GB | **Recommended** — best technical reasoning |
| `mistral:7b` | ~5GB | Good fallback, faster responses |
| `llama3.2:3b` | ~2GB | Use if RAM < 8GB available |

```bash
ollama pull llama3.1:8b
# Verify before wiring into bot:
ollama run llama3.1:8b "explain kubernetes NetworkPolicy in 3 sentences"
```

### Mentoring Integration

Each mode injects the user's current task + step into every Ollama call:

| Mode | Prompt shape |
|------|-------------|
| `/explain <topic>` | "You are a DevOps mentor. The student is on Phase X, Task Y (title). Explain `<topic>` concisely in under 200 words, using analogies from Linux/Kubernetes." |
| `/hint` | "The student is stuck on step Z of Task Y. Give a directional hint — do NOT give the answer. Maximum 3 sentences." |
| `/quiz` | "Generate 1 multiple-choice question about `<current task topic>`. Show options A/B/C/D. Wait for the student's answer before revealing the correct one." |

**Docker → host Ollama bridge:**
```yaml
extra_hosts:
  - "host.docker.internal:host-gateway"
```

---

## Data Model

SQLite database at `study-companion/data/state.db`. Seeded from roadmap markdown on first run.

### `tasks`

| column | type | notes |
|--------|------|-------|
| `id` | INTEGER PK | matches Task N from roadmap |
| `title` | TEXT | e.g. "Task 3: Networking Fundamentals" |
| `phase` | INTEGER | 1, 2, or 3 |
| `status` | TEXT | `pending` / `in_progress` / `completed` |
| `started_at` | TIMESTAMP | set when first step completed |
| `completed_at` | TIMESTAMP | set when all steps completed |

### `steps`

| column | type | notes |
|--------|------|-------|
| `id` | INTEGER PK | |
| `task_id` | INTEGER FK → tasks.id | |
| `content` | TEXT | step description from markdown |
| `status` | TEXT | `pending` / `completed` / `skipped` |
| `completed_at` | TIMESTAMP | nullable |

### `sessions`

| column | type | notes |
|--------|------|-------|
| `id` | INTEGER PK | |
| `date` | DATE | |
| `started_at` | TIMESTAMP | set by `/session start` |
| `ended_at` | TIMESTAMP | set by `/session end` |
| `duration_minutes` | INTEGER | calculated on end |
| `task_id` | INTEGER FK → tasks.id | active task at session start |
| `notes` | TEXT | optional free-text from `/session end [notes]` |

---

## Telegram Commands

| Command | Behavior |
|---------|----------|
| `/today` | Shows current task title + all pending steps |
| `/done` | Marks next pending step complete, shows what's next |
| `/progress` | Overall % complete, current phase, total sessions, streak |
| `/session start` | Logs session start timestamp |
| `/session end [notes]` | Logs end, calculates duration, saves notes |
| `/explain <topic>` | Ollama explain mode with current task context |
| `/hint` | Ollama hint for current pending step |
| `/quiz` | Ollama quiz on current task topic |
| `/skip [reason]` | Skips current step, logs reason, moves to next |

---

## Daily Notification Flow

**07:00 — Morning notification:**
```
Good morning! 🌅

Today's task: Task 3 — Networking Fundamentals (Week 5 of LFCS)

Your next step:
▸ Step 2: Understand iptables (this IS Kubernetes networking)

Type /hint if you need a nudge. Type /session start when you begin.
```

**19:00 check — no progress recorded today:**
```
Hey — no progress logged today. No pressure, but your next step is:

▸ Step 2: Understand iptables

Even 15 minutes counts. Type /session start to begin.
```

**19:00 check — progress recorded today:**
```
Nice work today — you completed 2 step(s).

Current task: Task 3 — Networking Fundamentals
Progress: 3/6 steps done

See you tomorrow. 💪
```

---

## Project Structure

```
study-companion/
├── Dockerfile
├── requirements.txt
├── config.yaml                  # Ollama model, timezone, notification times
├── .env                         # TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID (not committed)
├── data/                        # volume-mounted, persists state.db
│   └── state.db
├── roadmap/
│   └── parser.py                # Parses roadmap markdown → seeds DB on first run
├── bot/
│   ├── main.py                  # Entry point, wires everything together
│   ├── handlers.py              # Telegram command handlers
│   ├── scheduler.py             # APScheduler: 07:00 send + 19:00 conditional check
│   └── mentor.py                # Ollama HTTP calls, prompt templates per mode
└── state/
    └── manager.py               # SQLite CRUD — tasks, steps, sessions
```

---

## Configuration

**`config.yaml`** (committed, no secrets):
```yaml
ollama:
  host: http://host.docker.internal:11434
  model: llama3.1:8b
  timeout_seconds: 60

notifications:
  morning_time: "07:00"
  evening_time: "19:00"
  timezone: "Asia/Jakarta"

roadmap:
  plan_file: /app/docs/superpowers/plans/2026-03-29-devops-certification-roadmap.md
```

**`.env`** (never committed):
```
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

---

## docker-compose.yml Addition

```yaml
study-companion:
  build:
    context: ./study-companion
  volumes:
    - ./study-companion/data:/app/data
    - ./docs:/app/docs:ro
  env_file:
    - ./study-companion/.env
  extra_hosts:
    - "host.docker.internal:host-gateway"
  restart: unless-stopped
  networks:
    - ckx-network
```

---

## Python Dependencies

```
python-telegram-bot==20.7
apscheduler==3.10.4
httpx==0.27.0
pyyaml==6.0.1
```

No ORM — raw `sqlite3` (stdlib). No async overhead for DB calls.

---

## Error Handling

| Scenario | Behavior |
|----------|----------|
| Ollama unreachable | Bot replies: "Mentor offline — Ollama not reachable. Check `systemctl status ollama` on host." |
| No active task | Bot replies: "No active task found. Check `/progress` to see your roadmap state." |
| Telegram token invalid | Service fails at startup with clear error log, does not crash silently |
| Roadmap already seeded | Parser detects existing rows in `tasks` table, skips re-seeding |

---

## Out of Scope

- Multi-user support (single Telegram chat ID only)
- Web dashboard
- Automatic grading of practice lab results
- Pushing progress to external services (GitHub, Notion, etc.)
