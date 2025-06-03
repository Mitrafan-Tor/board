from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.db.models import Q
from .models import Advertisement, Response, Category, Newsletter
from .forms import AdvertisementForm, ResponseForm, NewsletterForm
from django.contrib.auth.models import User
from django.utils.http import urlsafe_base64_decode
from django.contrib.auth.tokens import default_token_generator
from .registration import send_confirmation_email
from .forms import CustomUserCreationForm


class AdvertisementListView(ListView):
    model = Advertisement
    template_name = 'board/ad_list.html'
    context_object_name = 'ads'
    paginate_by = 10

    def get_queryset(self):
        queryset = super().get_queryset().order_by('-created_at')
        category_slug = self.request.GET.get('category')

        if category_slug:
            queryset = queryset.filter(category__name=category_slug)

        search_query = self.request.GET.get('q')
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) |
                Q(content__icontains=search_query)
            )

        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class AdvertisementDetailView(DetailView):
    model = Advertisement
    template_name = 'board/ad_detail.html'
    context_object_name = 'ad'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Получаем все ответы к объявлению
        responses = self.object.responses.all().order_by('-created_at')

        # Проверяем, может ли текущий пользователь оставить отклик
        if self.request.user.is_authenticated and self.request.user != self.object.author:
            context['response_form'] = ResponseForm()

        context['responses'] = responses
        return context


class AdvertisementCreateView(LoginRequiredMixin, CreateView):
    model = Advertisement
    form_class = AdvertisementForm
    template_name = 'board/ad_create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        messages.success(self.request, 'Your advertisement has been created!')
        return reverse_lazy('ad_detail', kwargs={'pk': self.object.pk})


class AdvertisementUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Advertisement
    form_class = AdvertisementForm
    template_name = 'board/ad_edit.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        ad = self.get_object()
        return self.request.user == ad.author

    def get_success_url(self):
        messages.success(self.request, 'Your advertisement has been updated!')
        return reverse_lazy('ad_detail', kwargs={'pk': self.object.pk})


class AdvertisementDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Advertisement
    template_name = 'board/ad_confirm_delete.html'
    success_url = reverse_lazy('ad_list')

    def test_func(self):
        ad = self.get_object()
        return self.request.user == ad.author

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Your advertisement has been deleted!')
        return super().delete(request, *args, **kwargs)


@login_required
@require_POST
def create_response(request, pk):
    # 1. Получаем объявление или возвращаем 404
    advertisement = get_object_or_404(Advertisement, pk=pk)

    # 2. Проверяем, что пользователь не автор объявления
    if request.user == advertisement.author:
        messages.error(request, "Вы не можете оставить отклик на свое объявление")
        return redirect('ad_detail', pk=pk)

    # 3. Создаем форму с данными из POST-запроса
    form = ResponseForm(request.POST)

    if form.is_valid():
        # 4. Создаем объект Response, но пока не сохраняем в БД
        response = form.save(commit=False)

        # 5. УСТАНАВЛИВАЕМ СВЯЗИ (это ключевое исправление)
        response.advertisement = advertisement  # Связываем с объявлением
        response.author = request.user  # Устанавливаем автора

        # 6. Сохраняем в БД
        response.save()

        # 7. Отправляем уведомление (ваш код отправки email)
        send_response_notification(response, request)

        messages.success(request, 'Ваш отклик успешно отправлен!')
    else:
        messages.error(request, 'Ошибка при отправке отклика: ' + str(form.errors))

    return redirect('ad_detail', pk=advertisement.pk)


def send_response_notification(response, request):
    """Функция отправки уведомления о новом отклике"""
    subject = f'Новый отклик на ваше объявление: {response.advertisement.title}'
    message = f'Пользователь {response.author.username} оставил отклик:\n\n'
    message += f'{response.content}\n\n'
    message += f'Просмотреть отклик: {request.build_absolute_uri(reverse("private_page"))}'

    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[response.advertisement.author.email],
        fail_silently=False,
    )


@login_required
def private_page(request):
    user_ads = Advertisement.objects.filter(author=request.user)
    responses = Response.objects.filter(advertisement__in=user_ads).order_by('-created_at')

    ad_filter = request.GET.get('ad_filter')
    if ad_filter:
        responses = responses.filter(advertisement_id=ad_filter)

    context = {
        'user_ads': user_ads,
        'responses': responses,
    }

    return render(request, 'board/private_page.html', context)


@login_required
@require_POST
def accept_response(request, pk):
    response = get_object_or_404(Response, pk=pk)

    if request.user != response.advertisement.author:
        messages.error(request, "У вас нет прав для этого действия")
        return redirect('private_page')

    response.is_accepted = True
    response.save()

    # Отправка уведомления
    subject = f'Ваш отклик принят!'
    message = f'Ваш отклик на объявление "{response.advertisement.title}" был принят.'
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[response.author.email],
    )

    messages.success(request, 'Отклик успешно принят!')
    return redirect('private_page')  # Исправленный редирект


@login_required
@require_POST
def delete_response(request, pk):
    response = get_object_or_404(Response, pk=pk)

    if request.user != response.advertisement.author:
        messages.error(request, "You don't have permission to delete this response.")
        return redirect('private_page.html')

    response.delete()
    messages.success(request, 'Response has been deleted!')
    return redirect('private_page.html')


class NewsletterCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Newsletter
    form_class = NewsletterForm
    template_name = 'news/newsletter.html'
    success_url = reverse_lazy('ad_list')

    def test_func(self):
        return self.request.user.is_superuser

    def form_valid(self, form):
        messages.success(self.request, 'Newsletter has been scheduled for sending.')
        return super().form_valid(form)


class RegisterView(CreateView):
    model = User
    form_class = CustomUserCreationForm  # Используем кастомную форму
    template_name = 'registration/register.html'
    success_url = reverse_lazy('login')

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False  # Пользователь не активен до подтверждения
        user.save()

        # Отправляем email с подтверждением
        send_confirmation_email(user, self.request)

        messages.info(
            self.request,
            'На ваш email отправлено письмо с подтверждением. '
            'Пожалуйста, проверьте почту и перейдите по ссылке.'
        )
        return redirect(self.success_url)


def activate_account(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True
        user.save()
        messages.success(request, 'Ваш аккаунт успешно активирован! Можете войти.')
        return redirect('login')
    else:
        messages.error(request, 'Ссылка активации недействительна!')
        return redirect('ad_list')