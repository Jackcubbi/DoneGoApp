import logging

from twilio.rest import Client

from app.config import settings

logger = logging.getLogger(__name__)


def send_whatsapp_report(pdf_bytes: bytes, filename: str, message: str) -> bool:
    """Send a WhatsApp message via Twilio. PDF is noted in the message body
    (direct file upload requires a publicly accessible URL; use message for MVP)."""
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        logger.warning("Twilio credentials not configured – skipping WhatsApp send.")
        return False
    if not settings.WHATSAPP_GROUP_TO:
        logger.warning("WHATSAPP_GROUP_TO not configured – skipping WhatsApp send.")
        return False

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    client.messages.create(
        body=message,
        from_=settings.TWILIO_WHATSAPP_FROM,
        to=settings.WHATSAPP_GROUP_TO,
    )
    return True
