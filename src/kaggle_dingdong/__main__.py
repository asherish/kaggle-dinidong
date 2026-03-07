import sys
from pathlib import Path

from .competitions import fetch_competitions, filter_competitions
from .config import PROJECT_ROOT, get_discord_config, get_slack_config, get_smtp_config, load_config
from .discord_sender import send_discord
from .email_sender import build_html_body, send_email
from .history import load_history, save_history
from .slack_sender import send_slack

HISTORY_PATH = PROJECT_ROOT / "sent_competitions.json"


def main() -> None:
    try:
        config = load_config()
        history_limit = config.get("history_limit", 200)

        history_list, sent_titles = load_history(HISTORY_PATH)

        comps = fetch_competitions(max_pages=config.get("max_pages", 3))
        new_comps = filter_competitions(comps, config.get("filters", {}), sent_titles)

        if not new_comps:
            print("No new competitions found.")
            return

        smtp_config = get_smtp_config()
        slack_url = get_slack_config()
        discord_url = get_discord_config()

        if not any([smtp_config, slack_url, discord_url]):
            print("Warning: No notification channels configured.", file=sys.stderr)
            return

        print(f"Found {len(new_comps)} new competition(s). Sending notifications...")

        errors: list[str] = []

        if smtp_config:
            try:
                html_body = build_html_body(new_comps)
                send_email("New Kaggle Competitions", html_body, smtp_config)
                print("  Email sent.")
            except Exception as e:
                errors.append(f"Email: {e}")
                print(f"  Email failed: {e}", file=sys.stderr)

        if slack_url:
            try:
                send_slack(new_comps, slack_url)
                print("  Slack notification sent.")
            except Exception as e:
                errors.append(f"Slack: {e}")
                print(f"  Slack failed: {e}", file=sys.stderr)

        if discord_url:
            try:
                send_discord(new_comps, discord_url)
                print("  Discord notification sent.")
            except Exception as e:
                errors.append(f"Discord: {e}")
                print(f"  Discord failed: {e}", file=sys.stderr)

        new_titles = [c["title"] for c in new_comps]
        save_history(history_list, new_titles, HISTORY_PATH, limit=history_limit)

        if errors:
            print(f"Done with errors: {'; '.join(errors)}", file=sys.stderr)
            sys.exit(1)

        print("Done.")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
