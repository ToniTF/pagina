from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app1 import views as views_app1

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # App principal
    path('', include('app1.urls', namespace='app1')),
    
    # Autenticación personalizada
    path('register/', views_app1.register, name='register'),
    
    # Autenticación incorporada de Django
    path('accounts/', include('django.contrib.auth.urls')),
]

# DESCOMENTA ESTAS LÍNEAS para servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)