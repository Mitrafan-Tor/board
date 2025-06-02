from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.template.loader import render_to_string
from django.utils.html import strip_tags

from .models import Response, Newsletter
from .tasks import send_newsletter


@receiver(post_save, sender=Response)
def notify_ad_author(sender, instance, created, **kwargs):
    if created:
        subject = f'New response to your advertisement: {instance.advertisement.title}'
        html_message = render_to_string('board/response_notification.html', {
            'response': instance,
            'ad': instance.advertisement,
        })
        plain_message = strip_tags(html_message)

        send_mail(
            subject=subject,
            message=plain_message,
            html_message=html_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.advertisement.author.email],
            fail_silently=False,
        )


@receiver(post_save, sender=Newsletter)
def schedule_newsletter(sender, instance, created, **kwargs):
    if created:
        send_newsletter.delay(instance.id)