from django import forms
from .models import Advertisement, Response, Category, Newsletter
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class AdvertisementForm(forms.ModelForm):
    class Meta:
        model = Advertisement
        fields = ['category', 'title', 'content', 'image', 'video']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
        }


# class ResponseForm(forms.ModelForm):
#     class Meta:
#         model = Response
#         fields = ['content']
#         widgets = {
#             'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your response here...'}),
#         }
#
#     def clean(self):
#         cleaned_data = super().clean()
#         advertisement = self.instance.advertisement
#         author = self.instance.author
#
#         if advertisement.author == author:
#             raise ValidationError("You cannot respond to your own advertisement.")
#
#         return cleaned_data
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
        widgets = {
            'message': forms.Textarea(attrs={'rows': 10}),
        }


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already registered.")
        return email