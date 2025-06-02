import requests
import logging
from django.conf import settings
from twilio.base.exceptions import TwilioRestException
from twilio.rest import Client as TwilioClient

from .utils import build_full_url

logger = logging.getLogger(__name__)

# def send_sms_twilio(to, message):
#     account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
#     auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
#     from_number = getattr(settings, 'TWILIO_FROM', None)
#     alphanumeric_sender = getattr(settings, 'TWILIO_ALPHANUMERIC_SENDER', None)  

#     if not all([account_sid, auth_token, from_number]):
#         raise ValueError("Twilio credentials are not fully configured in settings.")

#     client = TwilioClient(account_sid, auth_token)

#     if alphanumeric_sender:
#         try:
#             logger.info(f"Trying to send SMS to {to} using alphanumeric sender '{alphanumeric_sender}'")
#             message_response = client.messages.create(
#                 body=message,
#                 from_=alphanumeric_sender,
#                 to=to
#             )
#             logger.info(f"SMS sent successfully with alphanumeric sender to {to}, SID: {message_response.sid}")
#             return message_response.sid
#         except TwilioRestException as e:
#             logger.warning(f"Failed to send SMS with alphanumeric sender to {to}: {e}. Falling back to number sender.")
#         except Exception as e:
#             logger.error(f"Unexpected error sending SMS with alphanumeric sender to {to}: {e}")
#             raise

#     # Fall back to sending with Twilio number
#     try:
#         logger.info(f"Sending SMS to {to} using number sender '{from_number}'")
#         message_response = client.messages.create(
#             body=message,
#             from_=from_number,
#             to=to
#         )
#         logger.info(f"SMS sent successfully with number sender to {to}, SID: {message_response.sid}")
#         return message_response.sid
#     except Exception as e:
#         logger.error(f"Failed to send SMS with number sender to {to}: {e}", exc_info=True)
#         raise


def send_sms_twilio(to, message, request=None, **kwargs):
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    from_number = getattr(settings, 'TWILIO_FROM', None)
    alphanumeric_sender = getattr(settings, 'TWILIO_ALPHANUMERIC_SENDER', None)

    if not all([account_sid, auth_token, from_number]):
        return {
            "status": "ERROR",
            "error_message": "Twilio credentials are not fully configured in settings.",
            "sid": None
        }

    client = TwilioClient(account_sid, auth_token)

    # get callback url
    status_callback_url = build_full_url(request, 'account:sms_status_callback')
    
    # Try alphanumeric sender first
    if alphanumeric_sender:
        try:
            logger.info(f"Trying alphanumeric sender '{alphanumeric_sender}' to {to}")
            message_response = client.messages.create(
                body=message,
                from_=alphanumeric_sender,
                to=to,
                status_callback=status_callback_url
            )
            return {
                "status": "SENT",
                "sid": message_response.sid,
                "error_message": None
            }
        except TwilioRestException as e:
            logger.warning(f"Alphanumeric send failed: {e}. Falling back to number.")
        except Exception as e:
            return {
                "status": "ERROR",
                "error_message": f"Unexpected error with alphanumeric sender: {str(e)}",
                "sid": None
            }

    try:
        logger.info(f"Sending SMS using number sender '{from_number}' to {to}")
        message_response = client.messages.create(
            body=message,
            from_=from_number,
            to=to,
            status_callback=status_callback_url
        )
        return {
            "status": "SENT",
            "sid": message_response.sid,
            "error_message": None
        }
    except Exception as e:
        return {
            "status": "FAILED",
            "sid": None,
            "error_message": str(e)
        }