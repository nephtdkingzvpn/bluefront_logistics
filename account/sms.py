import threading
import logging
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

class AsyncSMSMixin:
    def send_sms_async(self, send_function, to, template=None, context=None, message=None, **kwargs):
        def send():
            try:
                # Render message from template if provided
                final_message = message
                if template:
                    final_message = render_to_string(template, context or {}).strip()

                if not final_message:
                    raise ValueError("SMS message content is empty.")

                send_function(to=to, message=final_message, **kwargs)
                logger.info(f"SMS sent to {to}")
            except Exception as e:
                logger.error(f"Failed to send SMS to {to}: {e}", exc_info=True)

        threading.Thread(target=send).start()


