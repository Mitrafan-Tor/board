from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView

from django.conf import settings              #  в режиме разработки
from django.conf.urls.static import static    #  в режиме разработки


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('board.urls')),
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    #path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/logout/',
         LogoutView.as_view(http_method_names=['get', 'post']),
         name='logout'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)