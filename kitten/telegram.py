import json
import logging
import urllib.request
from django.conf import settings

logger = logging.getLogger(__name__)


def send_telegram_message(bot_token, chat_id, text):
    """
    Sends an HTML-formatted message to a Telegram chat using standard library urllib.
    Returns (success: bool, message: str).
    """
    if not bot_token or not chat_id:
        return False, "Token del bot o Chat ID non configurati."

    bot_token = bot_token.strip()
    chat_id = str(chat_id).strip()

    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = json.dumps({
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML',
        'disable_web_page_preview': True,
    }).encode('utf-8')

    req = urllib.request.Request(
        url,
        data=payload,
        headers={
            'Content-Type': 'application/json',
            'User-Agent': 'MaisAdoptionBot/1.0',
        }
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            res_body = response.read().decode('utf-8')
            res_json = json.loads(res_body)
            if res_json.get('ok'):
                return True, "Messaggio Telegram inviato con successo!"
            return False, res_json.get('description', 'Errore Telegram sconosciuto.')
    except urllib.error.HTTPError as e:
        try:
            err_body = e.read().decode('utf-8')
            err_json = json.loads(err_body)
            desc = err_json.get('description', str(e))
        except Exception:
            desc = str(e)
        logger.warning(f"HTTPError Telegram notification: {desc}")
        return False, f"Errore Telegram ({e.code}): {desc}"
    except Exception as e:
        logger.warning(f"Errore durante l'invio della notifica Telegram: {e}")
        return False, f"Errore di connessione: {e}"


def notify_new_inquiry(kitten, inquiry, message_text):
    """
    Sends an instant notification to Telegram when a new adoption inquiry or chat message arrives.
    """
    bot_token = (kitten.telegram_bot_token or getattr(settings, 'TELEGRAM_BOT_TOKEN', '')).strip()
    chat_id = (kitten.telegram_chat_id or getattr(settings, 'TELEGRAM_CHAT_ID', '')).strip()

    if not kitten.telegram_notifications_enabled:
        return False, "Notifiche Telegram disabilitate nelle impostazioni."

    if not bot_token or not chat_id:
        return False, "Bot Token o Chat ID mancanti."

    site_url = "https://labustagialla.it"
    text = (
        f"🐾 <b>NUOVA RICHIESTA D'ADOZIONE PER {kitten.name.upper()}!</b> 🐾\n\n"
        f"👤 <b>Da:</b> {inquiry.name}\n"
        f"📞 <b>Contatto:</b> <code>{inquiry.contact}</code>\n"
        f"💬 <b>Messaggio:</b>\n<i>«{message_text}»</i>\n\n"
        f"👉 <a href='{site_url}/mais/gestione/#inquiries'>Apri e rispondi dal Pannello</a>"
    )

    return send_telegram_message(bot_token, chat_id, text)
