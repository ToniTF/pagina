from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count
from django.core.paginator import Paginator
from .models import Post, Categoria, Comentario
from .forms import PostForm, ComentarioForm, CategoriaForm, UserRegisterForm

def home(request):
    # Posts destacados para el carrusel
    posts_destacados = Post.objects.filter(destacado=True, publicado=True)[:5]
    
    # Posts recientes
    posts_recientes = Post.objects.filter(publicado=True)[:6]
    
    # Categorías populares
    categorias = Categoria.objects.annotate(num_posts=Count('posts')).order_by('-num_posts')[:5]
    
    context = {
        'posts_destacados': posts_destacados,
        'posts_recientes': posts_recientes,
        'categorias': categorias,
    }
    return render(request, 'app1/home.html', context)

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'¡Cuenta creada para {username}! Ya puedes iniciar sesión.')
            return redirect('login')
    else:
        form = UserRegisterForm()
    return render(request, 'app1/register.html', {'form': form})

def lista_posts(request):
    categoria_slug = request.GET.get('categoria')
    
    if categoria_slug:
        categoria = get_object_or_404(Categoria, slug=categoria_slug)
        posts_list = Post.objects.filter(categoria=categoria, publicado=True)
        titulo_pagina = f"Artículos en: {categoria.nombre}"
    else:
        posts_list = Post.objects.filter(publicado=True)
        titulo_pagina = "Todos los artículos"
    
    # Paginación
    paginator = Paginator(posts_list, 9)  # 9 posts por página
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    categorias = Categoria.objects.annotate(num_posts=Count('posts')).order_by('nombre')
    
    context = {
        'posts': posts,
        'categorias': categorias,
        'titulo_pagina': titulo_pagina,
        'categoria_actual': categoria_slug,
    }
    return render(request, 'app1/lista_posts.html', context)

def detalle_post(request, slug):
    post = get_object_or_404(Post, slug=slug, publicado=True)
    comentarios = post.comentarios.filter(activo=True)
    
    # Posts relacionados
    posts_relacionados = Post.objects.filter(
        categoria=post.categoria, 
        publicado=True
    ).exclude(id=post.id)[:3]
    
    # Formulario de comentarios
    if request.method == 'POST' and request.user.is_authenticated:
        comentario_form = ComentarioForm(request.POST)
        if comentario_form.is_valid():
            nuevo_comentario = comentario_form.save(commit=False)
            nuevo_comentario.post = post
            nuevo_comentario.autor = request.user
            nuevo_comentario.save()
            messages.success(request, '¡Comentario añadido correctamente!')
            return redirect('app1:detalle_post', slug=post.slug)
    else:
        comentario_form = ComentarioForm()
    
    context = {
        'post': post,
        'comentarios': comentarios,
        'comentario_form': comentario_form,
        'posts_relacionados': posts_relacionados,
    }
    return render(request, 'app1/detalle_post.html', context)

def posts_por_categoria(request, slug):
    categoria = get_object_or_404(Categoria, slug=slug)
    posts_list = Post.objects.filter(categoria=categoria, publicado=True)
    
    # Paginación
    paginator = Paginator(posts_list, 9)
    page = request.GET.get('page')
    posts = paginator.get_page(page)
    
    context = {
        'categoria': categoria,
        'posts': posts,
        'titulo_pagina': f"Artículos en: {categoria.nombre}",
    }
    return render(request, 'app1/posts_por_categoria.html', context)

@login_required
def mis_posts(request):
    posts = Post.objects.filter(autor=request.user).order_by('-fecha_publicacion')
    return render(request, 'app1/mis_posts.html', {'posts': posts})

@login_required
def nuevo_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.autor = request.user
            post.save()
            messages.success(request, '¡Artículo creado correctamente!')
            return redirect('app1:detalle_post', slug=post.slug)
    else:
        form = PostForm()
    
    return render(request, 'app1/editar_post.html', {
        'form': form,
        'titulo_pagina': 'Crear nuevo artículo'
    })

@login_required
def editar_post(request, slug):
    post = get_object_or_404(Post, slug=slug, autor=request.user)
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, '¡Artículo actualizado correctamente!')
            return redirect('app1:detalle_post', slug=post.slug)
    else:
        form = PostForm(instance=post)
    
    return render(request, 'app1/editar_post.html', {
        'form': form,
        'post': post,
        'titulo_pagina': 'Editar artículo'
    })

@login_required
def eliminar_post(request, slug):
    post = get_object_or_404(Post, slug=slug, autor=request.user)
    
    if request.method == 'POST':
        post.delete()
        messages.success(request, '¡Artículo eliminado correctamente!')
        return redirect('app1:mis_posts')
    
    return render(request, 'app1/eliminar_post.html', {'post': post})