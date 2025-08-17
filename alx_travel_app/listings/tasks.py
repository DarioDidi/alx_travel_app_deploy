from django.core.mail import send_mail
from celery import shared_task


@shared_task
def send_confirmation_email(email_address, message):
    """Sends an email when the payment has been submitted."""

    send_mail(
        "Payment verification",
        f"\t{message}\n\nThank you!",
        "support@example.com",
        [email_address],
        fail_silently=False,
    )
