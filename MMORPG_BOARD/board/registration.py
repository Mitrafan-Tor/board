from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.contrib.auth.tokens import default_token_generator
from django.conf import settings

User = get_user_model()


def send_confirmation_email(user, request):
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))

    subject = 'Подтверждение регистрации на MMORPG Board'
    message = render_to_string('registration/confirmation_email.html', {
        'user': user,
        'domain': request.get_host(),
        'protocol': 'https' if request.is_secure() else 'http',
        'uid': uid,
        'token': token,
    })

    send_mail(
        subject=subject,
        message='',  # Текстовая версия пустая, так как используем html
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user.email],
        html_message=message,
    )