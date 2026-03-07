# kaggle-dingdong

Kaggle competition notifier that sends alerts via email, Slack, and Discord.

## Features

- Fetches competitions from Kaggle API with configurable page count
- Filters by category (Featured, Research, etc.) and tags (tabular, nlp, etc.)
- Sends HTML emails with clickable links, reward info, and deadlines
- Sends Slack notifications via Incoming Webhook (Block Kit format)
- Sends Discord notifications via Webhook (rich embeds)
- Tracks sent competitions to avoid duplicates (capped at 200 entries)
- Supports multiple email recipients (comma-separated)
- Automatically enables channels based on configured environment variables

## Setup

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager
- Kaggle API credentials (`~/.kaggle/kaggle.json`)

### Install

```bash
uv sync
```

### Configuration

1. Copy `.env.example` to `.env` and fill in your SMTP settings:

```bash
cp .env.example .env
```

2. Edit `config.json` to customize filters and behavior:

```json
{
  "filters": { "category": ["Featured", "Research"], "tags": [] },
  "max_pages": 3,
  "history_limit": 200
}
```

### Run locally

```bash
uv run kaggle-dingdong
```

### Run tests

```bash
uv run pytest
```

## GitHub Actions

The workflow runs daily at 09:00 UTC. Add the following secrets to your repository:

| Secret | Description |
|--------|-------------|
| `KAGGLE_USERNAME` | Kaggle username |
| `KAGGLE_KEY` | Kaggle API key |
| `SMTP_SERVER` | SMTP server (e.g. `smtp.gmail.com`) |
| `SMTP_PORT` | SMTP port (e.g. `587`) |
| `SMTP_USER` | SMTP login email |
| `SMTP_PASSWORD` | SMTP password / app password |
| `EMAIL` | Recipient(s), comma-separated |
| `SLACK_WEBHOOK_URL` | Slack Incoming Webhook URL (optional) |
| `DISCORD_WEBHOOK_URL` | Discord Webhook URL (optional) |
