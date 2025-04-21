from django.contrib import admin
from django.urls import path, include
# from django.contrib.auth import views as auth_views # Ya no es necesario si usamos include
from django.conf import settings
from django.conf.urls.static import static
from app1 import views as views_app1 # Necesario para la vista de registro personalizada

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # App principal (asumiendo que app1.urls define las URLs de la app como /posts/, etc.)
    path('', include('app1.urls', namespace='app1')), # Añadido namespace para claridad

    # Autenticación personalizada
    # Mantenemos el registro personalizado si lo tienes en app1.views
    path('register/', views_app1.register, name='register'),

    # Autenticación incorporada de Django (bajo /accounts/)
    # Esto define: login, logout, password_reset, password_change, etc.
    # Buscará las plantillas en 'registration/' por defecto.
    path('accounts/', include('django.contrib.auth.urls')),

    # Si necesitas que la URL de login sea /login/ en lugar de /accounts/login/
    # podrías descomentar la siguiente línea y comentar la inclusión anterior,
    # pero asegúrate de definir TODAS las URLs de auth manualmente o incluir las que falten.
    # path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    # path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'), # Especifica a dónde ir después del logout

]

# Configuración para servir archivos media en DESARROLLO (DEBUG=True)
# En PythonAnywhere (DEBUG=False), esto se configura en la pestaña "Web"
# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Nota: Los archivos estáticos (STATIC_URL, STATIC_ROOT) en producción (DEBUG=False)
# se configuran a través de collectstatic y la pestaña "Web" de PythonAnywhere.