# TodoBot - Telegram Task Manager

A production-ready todo list bot with smart reminders. Built with Django, Aiogram, and Celery.

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

None. System is solid.

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
