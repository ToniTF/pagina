from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from app1 import views as views_app1  # AÑADIR esta importación

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # App principal
    path('', include('app1.urls')),
    
    # Autenticación
    path('register/', views_app1.register, name='register'),  # AÑADIR esta línea
    path('login/', auth_views.LoginView.as_view(template_name='app1/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # ... resto de tus URLs
]