from django.urls import path
from . import views

app_name = 'app1'

urlpatterns = [
    path('', views.home, name='home'),
    path('posts/', views.lista_posts, name='lista_posts'),
    path('post/<slug:slug>/', views.detalle_post, name='detalle_post'),
    path('categoria/<slug:slug>/', views.posts_por_categoria, name='posts_por_categoria'),
    path('nuevo-post/', views.nuevo_post, name='nuevo_post'),
    path('post/<slug:slug>/editar/', views.editar_post, name='editar_post'),
    path('post/<slug:slug>/eliminar/', views.eliminar_post, name='eliminar_post'),
    path('mis-posts/', views.mis_posts, name='mis_posts'),
    path('perfil/editar/', views.edit_profile, name='edit_profile'),
]