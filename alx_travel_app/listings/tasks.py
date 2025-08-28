from django.core.mail import send_mail
from celery import shared_task


@shared_task
def send_notification_email(email_address, title, content):
    """ email notification feature for bookings."""

    send_mail(
        "Payment verification",
        content,
        "support@example.com",
        [email_address],
        fail_silently=False,
    )
