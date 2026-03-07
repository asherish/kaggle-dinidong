import html
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def build_html_body(competitions: list[dict]) -> str:
    """Build an HTML email body with competition cards."""
    cards = []
    for comp in competitions:
        title = html.escape(comp['title'])
        url = html.escape(comp['url'])
        category = html.escape(comp['category'])
        reward = html.escape(comp['reward'])
        deadline = html.escape(comp['deadline'])
        cards.append(f"""
        <div style="border:1px solid #ddd; border-radius:8px; padding:16px; margin-bottom:12px; font-family:Arial,sans-serif;">
            <h3 style="margin:0 0 8px 0;">
                <a href="{url}" style="color:#1a73e8; text-decoration:none;">{title}</a>
            </h3>
            <p style="margin:4px 0; color:#555; font-size:14px;">
                Category: {category} | Reward: {reward} | Deadline: {deadline}
            </p>
        </div>""")

    return f"""<!DOCTYPE html>
<html>
<body style="background:#f9f9f9; padding:20px;">
    <h2 style="font-family:Arial,sans-serif; color:#333;">New Kaggle Competitions</h2>
    {''.join(cards)}
</body>
</html>"""


def send_email(subject: str, html_body: str, smtp_config: dict) -> None:
    """Send an HTML email to all recipients."""
    msg = MIMEMultipart("alternative")
    msg["Subject"] = subject
    msg["From"] = smtp_config["user"]
    msg["To"] = ", ".join(smtp_config["recipients"])
    msg.attach(MIMEText(html_body, "html"))

    with smtplib.SMTP(smtp_config["server"], smtp_config["port"]) as server:
        server.starttls()
        server.login(smtp_config["user"], smtp_config["password"])
        server.sendmail(
            smtp_config["user"], smtp_config["recipients"], msg.as_string()
        )
