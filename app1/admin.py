from django.contrib import admin
from .models import Categoria, Post, Comentario

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'slug')
    prepopulated_fields = {'slug': ('nombre',)}
    search_fields = ('nombre',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('titulo', 'autor', 'categoria', 'fecha_publicacion', 'publicado', 'destacado')
    list_filter = ('publicado', 'destacado', 'categoria', 'fecha_publicacion')
    search_fields = ('titulo', 'contenido', 'autor__username')
    prepopulated_fields = {'slug': ('titulo',)}
    date_hierarchy = 'fecha_publicacion'
    list_editable = ('publicado', 'destacado')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(autor=request.user)

@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ('autor', 'post', 'fecha', 'activo')
    list_filter = ('activo', 'fecha')
    search_fields = ('autor__username', 'contenido', 'post__titulo')
    actions = ['aprobar_comentarios', 'rechazar_comentarios']
    
    def aprobar_comentarios(self, request, queryset):
        queryset.update(activo=True)
    
    def rechazar_comentarios(self, request, queryset):
        queryset.update(activo=False)