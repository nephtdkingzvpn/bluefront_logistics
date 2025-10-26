from django.core.mail import EmailMessage
from django.conf import settings

# def email_send(subject, message, receiver):
# 	email = EmailMessage(
# 		subject,
# 		message,
# 		settings.DEFAULT_FROM_EMAIL,
# 		[receiver],
# 		)
# 	email.content_subtype = "html"
# 	email.fail_silently = False
# 	email.send()

# 	return message


def email_send(subject, message, receiver):
    """
    Sends an HTML email via Anymail + Resend.
    Uses DEFAULT_FROM_EMAIL and optionally DEFAULT_REPLY_TO_EMAIL.
    """
    reply_to_address = getattr(settings, "DEFAULT_REPLY_TO_EMAIL", None)

    email = EmailMessage(
        subject=subject,
        body=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[receiver],
        reply_to=[reply_to_address] if reply_to_address else None,
    )
    email.content_subtype = "html"
    email.fail_silently = False
    email.send()

    return message