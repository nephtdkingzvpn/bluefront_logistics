import requests
import logging
from django.conf import settings
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client as TwilioClient

logger = logging.getLogger(__name__)

def send_sms_twilio(to, message):
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    from_number = getattr(settings, 'TWILIO_FROM', None)
    alphanumeric_sender = getattr(settings, 'TWILIO_ALPHANUMERIC_SENDER', None)  

    if not all([account_sid, auth_token, from_number]):
        raise ValueError("Twilio credentials are not fully configured in settings.")

    client = TwilioClient(account_sid, auth_token)

    if alphanumeric_sender:
        try:
            logger.info(f"Trying to send SMS to {to} using alphanumeric sender '{alphanumeric_sender}'")
            message_response = client.messages.create(
                body=message,
                from_=alphanumeric_sender,
                to=to
            )
            logger.info(f"SMS sent successfully with alphanumeric sender to {to}, SID: {message_response.sid}")
            return message_response.sid
        except TwilioRestException as e:
            logger.warning(f"Failed to send SMS with alphanumeric sender to {to}: {e}. Falling back to number sender.")
        except Exception as e:
            logger.error(f"Unexpected error sending SMS with alphanumeric sender to {to}: {e}")
            raise

    # Fall back to sending with Twilio number
    try:
        logger.info(f"Sending SMS to {to} using number sender '{from_number}'")
        message_response = client.messages.create(
            body=message,
            from_=from_number,
            to=to
        )
        logger.info(f"SMS sent successfully with number sender to {to}, SID: {message_response.sid}")
        return message_response.sid
    except Exception as e:
        logger.error(f"Failed to send SMS with number sender to {to}: {e}", exc_info=True)
        raise


def send_sms_sweego_direct(to, message, region="CA", **kwargs):
    """
    Send SMS via Sweego, using a short-name if required by region (e.g. NG).
    """

    api_key = getattr(settings, "SWEEGO_API_KEY", None)
    short_name = getattr(settings, "SWEEGO_SHORT_NAME", None)  # <--- set in settings.py

    if not api_key:
        raise ValueError("Sweego API key not configured.")
    if not short_name:
        raise ValueError("Sweego short-name is required for this region.")

    headers = {
        "Api-Key": api_key,
        "Content-Type": "application/json"
    }

    payload = {
        "channel": "sms",
        "provider": "sweego",
        "short-name": short_name,  # ✅ required for NG
        "campaign-type": "transac",
        "recipients": [
            {
                "num": to,
                "region": region
            }
        ],
        "message-txt": message
    }

    try:
        logger.info(f"Sending SMS to {to} via Sweego (region: {region})")
        response = requests.post("https://api.sweego.io/send", headers=headers, json=payload)
        response.raise_for_status()
        logger.info(f"Sweego SMS sent to {to}: {response.json()}")
        return response.json()
    except requests.HTTPError as e:
        logger.error(f"Sweego HTTP error for {to}: {e.response.text}", exc_info=True)
        raise
    except Exception as e:
        logger.error(f"Unexpected error sending SMS to {to}: {e}", exc_info=True)
        raise




# def send_sms_nexmo(to, message):
#     api_key = getattr(settings, 'NEXMO_API_KEY', None)
#     api_secret = getattr(settings, 'NEXMO_API_SECRET', None)
#     from_number = getattr(settings, 'NEXMO_FROM', None)

#     if not all([api_key, api_secret, from_number]):
#         raise ValueError("Nexmo credentials are not fully configured in settings.")

#     client = vonage.Client(key=api_key, secret=api_secret)
#     sms = vonage.Sms(client)
#     response = sms.send_message({
#         "from": from_number,
#         "to": to,
#         "text": message
#     })

#     if response["messages"][0]["status"] != "0":
#         raise Exception(f"Nexmo SMS failed: {response['messages'][0]['error-text']}")