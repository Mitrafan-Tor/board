from django import forms
from .models import Advertisement, Response, Category, Newsletter
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['category', 'title', 'content', 'image', 'video']
        labels = {
            'category': 'Категория',
            'title': 'Заголовок',
            'content': 'Содержание',
            'image': 'Изображение',
            'video': 'Видео',
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }


class ResponseForm(forms.ModelForm):
    class Meta:
        model = Response
        fields = ['content']  # Только содержание, остальные поля устанавливаются в view

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['content'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Введите ваш отклик...',
            'rows': 3
        })


class NewsletterForm(forms.ModelForm):
    class Meta:
        model = Newsletter
        fields = ['subject', 'message']
        labels = {
            'subject': 'Предмет',
            'message': 'Сообщение',
        }
        widgets = {
            'message': forms.Textarea(attrs={'rows': 10}),
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')
        labels = {
            'username': 'Предмет',
            'email': 'Сообщение',
            'password1': 'Пароль 1',
            'password2': 'Пароль 2'
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Этот адрес уже зарегистрирован.")
        return email