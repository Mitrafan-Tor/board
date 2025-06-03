from django.urls import path
from .views import (
    AdvertisementListView, AdvertisementDetailView, AdvertisementCreateView,
    AdvertisementUpdateView, AdvertisementDeleteView, create_response,
    private_page, accept_response, delete_response, NewsletterCreateView,
    RegisterView, activate_account, unsubscribe
)

urlpatterns = [
    path('', AdvertisementListView.as_view(), name='ad_list'),
    path('ad/<int:pk>/', AdvertisementDetailView.as_view(), name='ad_detail'),
    path('ad/new/', AdvertisementCreateView.as_view(), name='ad_create'),
    path('ad/<int:pk>/edit/', AdvertisementUpdateView.as_view(), name='ad_edit'),
    path('ad/<int:pk>/delete/', AdvertisementDeleteView.as_view(), name='ad_delete'),
    path('ad/<int:pk>/response/', create_response, name='create_response'),
    path('private/', private_page, name='private_page'),
    path('response/<int:pk>/accept/', accept_response, name='accept_response'),
    path('response/<int:pk>/delete/', delete_response, name='delete_response'),
    path('newsletter/', NewsletterCreateView.as_view(), name='newsletter'),
    path('register/', RegisterView.as_view(), name='register'),
    path('activate/<uidb64>/<token>/', activate_account, name='activate'),
    path('unsubscribe/', unsubscribe, name='unsubscribe'),
]