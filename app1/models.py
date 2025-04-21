from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse
from ckeditor.fields import RichTextField

class Categoria(models.Model):
    nombre = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    descripcion = models.TextField(blank=True)
    
    def __str__(self):
        return self.nombre
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nombre)
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name_plural = "Categorías"

class Post(models.Model):
    titulo = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, max_length=200)
    contenido = RichTextField()
    extracto = models.TextField(max_length=300, blank=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    ultima_modificacion = models.DateTimeField(auto_now=True)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='posts')
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    imagen_destacada = models.ImageField(upload_to='posts/', blank=True, null=True)
    publicado = models.BooleanField(default=True)
    destacado = models.BooleanField(default=False)
    
    def __str__(self):
        return self.titulo
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.titulo)
        
        if not self.extracto and self.contenido:
            # Crear extracto automático desde el contenido
            texto_plano = self.contenido.replace('<p>', '').replace('</p>', ' ')
            self.extracto = texto_plano[:297] + '...' if len(texto_plano) > 300 else texto_plano
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('app1:detalle_post', kwargs={'slug': self.slug})
    
    class Meta:
        ordering = ['-fecha_publicacion']
        verbose_name_plural = "Posts"

class Comentario(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    
    def __str__(self):
        return f'Comentario de {self.autor.username} en {self.post.titulo}'
    
    class Meta:
        ordering = ['fecha']