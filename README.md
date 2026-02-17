# TodoBot - Telegram Task Manager

A production-ready todo list bot with smart reminders. Built with Django, Aiogram, and Celery. Main AI agent to use was Claude, good context window, not much hallucinations, great choice for fast prototyping.

## Features

- **Task Management**: CRUD operations with categories
- **Smart Reminders**: 6-level escalation system (daily → urgent → final)
- **Natural Language**: "tomorrow at 3pm", "in 2 hours", etc.
- **Telegram Bot**: Full FSM-based dialog flow
- **America/Adak Timezone**: Tech task requirement

## Architecture

SOLID principles throughout, or at least following some principles (for the sake of clear and rapid development).

```
apps/tasks/
├── models.py           # Domain entities (Task, Category)
├── services/           # Business logic layer
│   ├── task_service.py
│   ├── reminder_service.py
│   └── notification_service.py
├── formatters/         # Presentation logic
└── notifications/      # Infrastructure (Telegram, etc)

bot/
├── handlers/           # Telegram handlers
├── dialogs/            # FSM conversation flows
├── keyboards/          # Inline keyboards
└── formatters/         # Message formatting
```

## Quick Start

### Prerequisites
- Docker & Docker Compose
- Telegram Bot Token (talk to [@BotFather](https://t.me/botfather))

### Setup

1. **Clone and configure**:
```bash
git clone <repo>
cd todobot
cp .env.example .env
```

2. **Edit `.env` file** - add your bot token:
```bash
# Required changes:
BOT_TOKEN=your-actual-telegram-bot-token
SECRET_KEY=some-random-secret-key  # generate one

# Everything else can stay default for local dev
```

3. **Start everything**:
```bash
docker-compose up -d
```

This will:
- Spin up PostgreSQL, Redis, Django, Celery worker, Celery beat, and the bot
- Run migrations automatically
- Start the bot and connect to Telegram

4. **Check if it's running**:
```bash
docker-compose ps  # should show 6 containers running
docker-compose logs bot  # check bot logs
```

Look for: `"Bot started successfully"` in bot logs

5. **Test it**: Open Telegram and send `/start` to your bot

### Stop/Restart

```bash
# Stop everything
docker-compose down

# Restart everything
docker-compose up -d

# Rebuild after code changes
docker-compose up -d --build

# View logs
docker-compose logs -f  # all services
docker-compose logs -f bot  # just bot
docker-compose logs -f celery_worker  # just celery worker
```

### Troubleshooting

**Bot won't start?**
- Check BOT_TOKEN in `.env` is correct
- Look at logs: `docker-compose logs bot`

**Database errors?**
- Containers might've started out of order (shouldn't happen with healthchecks)
- Try: `docker-compose restart web`

**Reminders not working?**
- Check celery_beat is running: `docker-compose ps celery_beat`
- Check logs: `docker-compose logs celery_beat celery_worker`

**Need to reset everything?**
```bash
docker-compose down -v  # removes volumes (all data!)
docker-compose up -d
```

## Development

### Run migrations:
```bash
docker-compose exec web python manage.py migrate
```

### Create superuser:
```bash
docker-compose exec web python manage.py createsuperuser
```

### Access Django admin:
```
http://localhost:8000/admin
```

### Run Celery locally:
```bash
# Worker
celery -A config worker --loglevel=info

# Beat scheduler
celery -A config beat --loglevel=info
```

## 📊 Smart Reminders System

Tasks get reminders based on time-to-deadline:

| Time Left | Level | Frequency |
|-----------|-------|-----------|
| 5+ days | Daily | Every 24h |
| 2-5 days | Half-day | Every 12h |
| 1-2 days | Quarter-day | Every 6h |
| < 1 day | Urgent | Every 2h |
| < 2 hours | Final | Every 30min |
| Past due | Overdue | Once |

## Bot Commands

- `/start` - Start the bot
- `/help` - Show help
- Add Task - Create new task (with FSM dialog)
- My Tasks - View all tasks
- Categories - Manage categories

## Database

Uses ULID for primary keys instead of UUID. Tech-task requirement
- Sortable by creation time
- Shorter string representation
- Better database performance

## Timezone Handling

Everything runs in **America/Adak (UTC-10)**. Django's `USE_TZ=True` ensures:
- All datetimes are timezone-aware
- Database stores in UTC
- Comparisons work correctly
- No naive datetime bullshit

## Known Issues

Big latency, around 200-300 ms. For a high load system it is not a great statistics. In the dev i'm using polling, but i HIGHLY, HUGELY recommend using webhook (you can choose it in .env), it's a lot more reliable. Task reminder working fine but sometimes it may be late, because of the architecture itself, deadline may fall into the "waiting for celery to see me" state, it's not bad but certainly there was a lot of fixes like schedule based on pings, notif from database and they have their own flaws. Django DRF is sync, fully sync, the PostgreSQL is sync too. Interface - async calls, but its not enough for full "asynchronous I/O". DRF and PostgreSQL blocking the loop and remaining sync, i selected this path because it provided simple troubleshooting and development of prototype, also in technical task there wasn't anything about "async", myself i would choose FastAPI or any other fully async python framework. Database is full of indexes for quick-access and search of needed data, addressed N+1 problems (related with getting categories, tasks), basically i was following django best practices. Gracefull shutdown, everything works fine. For full production of course we need servers, clusters, scaling backend, and especially - change the framework for async i/o, add async database (PostgreSQL+asyncpg), it will be a lot more reasonable, BUT ! it's your decision to assign django so i won't argue with it. Issues i faced: security, added internal api key to resolve problem of everyone hitting backend, and also added rate-limiting on api.

## Production Checklist (medium priority, not implemented)

- **HSTS** — `SECURE_HSTS_SECONDS` is not set in `production.py`. Without it browsers don't enforce HTTPS-only after the first redirect. Add `SECURE_HSTS_SECONDS = 31536000` before going live.
- **Structured logging** — logs are plaintext stdout. For aggregators (Datadog, Loki, CloudWatch) swap to JSON via `python-json-logger`.
- **Gunicorn workers** — currently hardcoded to 2 workers in `docker-compose.yml`. For real traffic scale to `2*CPU+1` and add `--timeout 30`.
- **Observability** - No Sentry, OpenTelemetry, reminders silently fail.
- **NO TESTS!** - it is important to have tests, unit testing, integration testing, but in tech-task it wasn't included so i skipped it.

## Technical Decisions

**Why separate bot and backend?**
- Bot can restart without affecting API
- Can add web frontend later
- Services can scale independently

**Why Celery instead of cron?**
- Distributed task queue
- Better failure handling
- Can scale workers horizontally

**Why SOLID over Django monoliths?**
- Testable code (when we write tests, but i decided not to.)
- Easy to understand
- Services < 150 lines each

## Contributing

Technical task

## License

MIT or whatever ? technical task.

## Credits

Emirkhan Khajifazlyoglu

---

**Stack**: Django 6.0 | Aiogram 3.x | Celery 5.6 | PostgreSQL | Redis | Docker
