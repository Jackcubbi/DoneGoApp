import logging

from twilio.rest import Client

from app.config import settings

logger = logging.getLogger(__name__)


def send_whatsapp_report(pdf_bytes: bytes, filename: str, message: str) -> bool:
    """Send a WhatsApp message via Twilio.

    PDF attachment via Twilio requires a publicly accessible media URL.
    For MVP the PDF details are included in the message body only.

    Raises:
        ValueError: If Twilio credentials or recipient are not configured.
        RuntimeError: If the Twilio API call fails.
    """
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        raise ValueError(
            "WhatsApp-lähetys ei onnistu: Twilio-tunnukset puuttuvat (.env)."
        )
    if not settings.WHATSAPP_GROUP_TO:
        raise ValueError(
            "WhatsApp-lähetys ei onnistu: vastaanottajan numero puuttuu (WHATSAPP_GROUP_TO)."
        )

    try:
        client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
        client.messages.create(
            body=message,
            from_=settings.TWILIO_WHATSAPP_FROM,
            to=settings.WHATSAPP_GROUP_TO,
        )
    except Exception as exc:
        logger.exception("Twilio send failed: %s", exc)
        raise RuntimeError(
            f"WhatsApp-viesti epäonnistui: {exc}"
        ) from exc

    return True
