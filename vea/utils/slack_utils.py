import os
import logging
import re
from typing import Optional
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logger = logging.getLogger(__name__)


def markdown_to_mrkdwn(text: str) -> str:
    """Convert common Markdown formatting to Slack's mrkdwn style."""
    text = re.sub(r"\*\*(.*?)\*\*", r"*\1*", text)
    text = re.sub(r"__(.*?)__", r"*\1*", text)
   
    return text


def send_slack_dm(message: str, *, token: Optional[str] = None, quiet: bool = False) -> None:
    """Send a direct message to the authenticated user."""
    token = token or os.environ.get("SLACK_TOKEN")
    if not token:
        logger.warning("SLACK_TOKEN not set; cannot send Slack DM")
        return

    client = WebClient(token=token)
    try:
        user_id = client.auth_test()["user_id"]
        channel_id = client.conversations_open(users=user_id)["channel"]["id"]
        mrkdwn_message = markdown_to_mrkdwn(message)
        client.chat_postMessage(
            channel=channel_id,
            text=mrkdwn_message,
            blocks=[{"type": "section", "text": {"type": "mrkdwn", "text": mrkdwn_message}}],
        )
        if not quiet:
            logger.info("Sent Slack DM to user")
    except SlackApiError as e:
        logger.warning(f"Failed to send Slack DM: {e.response['error']}")
