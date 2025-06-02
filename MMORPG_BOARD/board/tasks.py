from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import get_user_model
from django.template.loader import render_to_string

User = get_user_model()


@shared_task
def send_weekly_newsletter():
    users = User.objects.filter(is_active=True)
    subject = "Еженедельные новости MMORPG - Доска объявлений"

    for user in users:
        message = render_to_string('news/newsletter.html', {
            'user': user,
        })
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=message,
            fail_silently=False,
        )


@shared_task
def test():
    return "Celery работает!"