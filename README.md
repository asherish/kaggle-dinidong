# kaggle-dingdong

Kaggle competition notifier that sends alerts via Email, Slack, and Discord.

## Features

- Fetches competitions from Kaggle API (SDK v2.0.0)
- Filters by category (e.g. Featured) and tags (e.g. tabular, nlp)
- Sends HTML emails with competition cards (clickable links, reward, deadline)
- Sends Slack notifications via Incoming Webhook (Block Kit format)
- Sends Discord notifications via Webhook (rich embeds, auto-chunked per 10)
- Tracks sent competitions to avoid duplicates (JSON history, capped at 200)
- Channels are automatically enabled based on configured environment variables
- Runs daily via GitHub Actions (09:00 UTC) or manually via `workflow_dispatch`

## Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- [Kaggle API token](https://www.kaggle.com/settings)

### Install

```bash
uv sync
```

### Configuration

Edit `config.json` to customize filters and behavior:

```json
{
  "filters": {
    "category": ["Featured"],
    "tags": []
  },
  "max_pages": 3,
  "history_limit": 200
}
```

| Key | Description |
|-----|-------------|
| `filters.category` | Competition categories to include (empty = all). e.g. `Featured`, `Research`, `Playground`, `Getting Started` |
| `filters.tags` | Tags to include (empty = all). e.g. `tabular`, `nlp`, `image` |
| `max_pages` | Number of API pages to fetch (each page ~20 competitions) |
| `history_limit` | Max number of sent competition titles to keep in history |

### Environment variables

For local use, copy `.env.example` to `.env` and fill in your settings:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|----------|----------|-------------|
| `KAGGLE_API_TOKEN` | No** | Kaggle API token (from [Settings](https://www.kaggle.com/settings)). Alternative to `~/.kaggle/kaggle.json` |
| `SMTP_SERVER` | No* | SMTP server (e.g. `smtp.gmail.com`) |
| `SMTP_PORT` | No* | SMTP port (default: `587`) |
| `SMTP_USER` | No* | SMTP login email |
| `SMTP_PASSWORD` | No* | SMTP password or [Gmail app password](https://myaccount.google.com/apppasswords) |
| `EMAIL` | No* | Recipient(s), comma-separated |
| `SLACK_WEBHOOK_URL` | No | Slack [Incoming Webhook](https://api.slack.com/messaging/webhooks) URL |
| `DISCORD_WEBHOOK_URL` | No | Discord Webhook URL |

\* At least one notification channel (Email, Slack, or Discord) must be configured.

\*\* Locally, you can use `~/.kaggle/kaggle.json` instead. For GitHub Actions, set `KAGGLE_API_TOKEN` as a secret.

### Run locally

```bash
uv run kaggle-dingdong
```

### Run tests

```bash
uv run pytest
```

## GitHub Actions

The included workflow (`.github/workflows/notify.yml`) runs daily at **09:00 UTC** and can be triggered manually.

### Required secrets

Set these via `gh secret set <NAME>` or in the repository Settings > Secrets:

| Secret | Description |
|--------|-------------|
| `KAGGLE_API_TOKEN` | Kaggle API token |
| `SMTP_SERVER` | SMTP server (e.g. `smtp.gmail.com`) |
| `SMTP_PORT` | SMTP port (e.g. `587`) |
| `SMTP_USER` | SMTP login email |
| `SMTP_PASSWORD` | SMTP password / app password |
| `EMAIL` | Recipient(s), comma-separated |
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL (optional) |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL (optional) |

### History cache

Sent competition titles are stored in `sent_competitions.json` and persisted across runs using `actions/cache`. To re-send all competitions, delete the cache:

```bash
gh cache list
gh cache delete <cache-id>
```

## Project structure

```
kaggle-dingdong/
├── .github/workflows/notify.yml   # GitHub Actions workflow
├── src/kaggle_dingdong/
│   ├── __main__.py                # Entry point
│   ├── competitions.py            # Kaggle API fetch & filter
│   ├── config.py                  # Config & env var loading
│   ├── email_sender.py            # HTML email via SMTP
│   ├── slack_sender.py            # Slack Block Kit webhook
│   ├── discord_sender.py          # Discord embed webhook
│   └── history.py                 # Sent history tracking
├── tests/                         # pytest test suite
├── config.json                    # Filter & behavior settings
├── .env.example                   # Environment variable template
└── pyproject.toml                 # Project metadata & dependencies
```

## License

MIT
