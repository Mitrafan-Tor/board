from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def send_response_notification(response):
    """Отправка уведомления о новом отклике"""
    subject = f'Новый отклик на ваше объявление: {response.advertisement.title}'
    message = render_to_string('board/response_notification_email.html', {
        'response': response,
    })
    send_mail(
        subject=subject,
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[response.advertisement.author.email],
        html_message=message,
    )

def send_acceptance_notification(response):
    """Отправка уведомления о принятии отклика"""
    subject = f'Ваш отклик принят: {response.advertisement.title}'
    message = render_to_string('board/acceptance_notification_email.html', {
        'response': response,
    })
    send_mail(
        subject=subject,
        message='',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[response.author.email],
        html_message=message,
    )