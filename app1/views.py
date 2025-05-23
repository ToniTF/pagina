from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.core.paginator import Paginator
from .models import Post, Categoria, Comentario
from .forms import PostForm, ComentarioForm, CategoriaForm, UserRegisterForm, UserProfileForm
import feedparser  # Importa la librería
import logging  # Para registrar errores si un feed falla
from urllib.parse import urlencode  # Importar urlencode

logger = logging.getLogger(__name__)

# Lista de URLs de feeds RSS (Solo los que funcionan en Free Tier)
RSS_FEEDS = {
    'Yahoo News': 'https://news.yahoo.com/rss/',
    'Google News (ES)': 'https://news.google.com/rss?hl=es&gl=ES&ceid=ES:es',
    'Bing News (World)': 'https://www.bing.com/news/search?q=world&format=rss',
    'MSN News (via Bing)': 'https://www.bing.com/news/search?q=site:msn.com&format=rss',
}
MAX_NEWS_ITEMS_PER_FEED = 3


def get_rss_news():
    """Obtiene y procesa noticias de los feeds RSS definidos."""
    all_news_items = []
    for source_name, feed_url in RSS_FEEDS.items():
        try:
            feed = feedparser.parse(feed_url)
            if feed.bozo:
                logger.error(f"Error parsing feed from {source_name} ({feed_url}): {feed.bozo_exception}")
                continue

            count = 0
            for entry in feed.entries:
                if count >= MAX_NEWS_ITEMS_PER_FEED:
                    break

                if hasattr(entry, 'title') and hasattr(entry, 'link'):
                    image_url = None
                    # Intenta obtener imagen de media_thumbnail (más común)
                    if hasattr(entry, 'media_thumbnail') and entry.media_thumbnail and 'url' in entry.media_thumbnail[0]:
                        image_url = entry.media_thumbnail[0]['url']
                    # Si no, intenta con media_content
                    elif hasattr(entry, 'media_content') and entry.media_content and 'url' in entry.media_content[0]:
                        image_url = entry.media_content[0]['url']
                    # Si no, busca en links tipo 'enclosure' de imagen
                    elif hasattr(entry, 'links'):
                        for link in entry.links:
                            if link.get('rel') == 'enclosure' and link.get('type', '').startswith('image/'):
                                image_url = link.get('href')
                                break # Usa la primera que encuentre

                    all_news_items.append({
                        'title': entry.title,
                        'link': entry.link,
                        'source': source_name,
                        'image': image_url, # Añade la URL de la imagen (puede ser None)
                    })
                    count += 1
        except Exception as e:
            logger.error(f"Could not fetch or process feed from {source_name} ({feed_url}): {e}")
    return all_news_items


def home(request):
    # Posts destacados por número de comentarios activos Y LUEGO por fecha
    posts_destacados = Post.objects.filter(
        publicado=True
    ).annotate(
        num_comentarios_activos=Count('comentarios', filter=Q(comentarios__activo=True))
    ).order_by(
        '-num_comentarios_activos', # 1. Más comentarios activos primero
        '-fecha_publicacion'       # 2. Si hay empate, el más reciente primero
    )[:5]

    # Posts recientes
    posts_recientes = Post.objects.filter(publicado=True).order_by('-fecha_publicacion')[:6]

    # Categorías populares
    categorias = Categoria.objects.annotate(num_posts=Count('posts', filter=Q(posts__publicado=True))).order_by('-num_posts')[:5]

    # Obtener noticias RSS
    noticias_rss = get_rss_news()

    context = {
        'posts_destacados': posts_destacados,
        'posts_recientes': posts_recientes,
        'categorias': categorias,
        'noticias_rss': noticias_rss,  # Añade las noticias al contexto
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


@login_required # Asegura que solo usuarios logueados puedan acceder
def edit_profile(request):
    if request.method == 'POST':
        # Pasar request.POST y la instancia del usuario actual al formulario
        form = UserProfileForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save() # Guarda los cambios en el usuario
            messages.success(request, '¡Tu perfil ha sido actualizado correctamente!')
            # Redirigir a la misma página o a otra (ej. home)
            return redirect('app1:edit_profile') 
        else:
            # Si el formulario no es válido, se mostrarán los errores en la plantilla
            messages.error(request, 'Por favor, corrige los errores indicados.')
    else:
        # Para GET, mostrar el formulario con los datos actuales del usuario
        form = UserProfileForm(instance=request.user)

    context = {
        'form': form
    }
    return render(request, 'app1/edit_profile.html', context)


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

    # --- INICIO: Preparar datos para compartir ---
    # Obtener la URL absoluta del post
    try:
        absolute_url = request.build_absolute_uri(post.get_absolute_url())
    except AttributeError:
        # Fallback por si get_absolute_url no existe o falla
        absolute_url = request.build_absolute_uri(reverse('app1:detalle_post', kwargs={'slug': post.slug}))

    # Preparar texto y URLs codificadas
    share_text = post.titulo
    encoded_url = urlencode({'': absolute_url})[1:]
    encoded_title = urlencode({'': share_text})[1:]
    encoded_text_whatsapp = urlencode({'': f"{share_text} {absolute_url}"})[1:]
    encoded_text_email_body = urlencode({'': f"Echa un vistazo a este artículo:\n\n{share_text}\n{absolute_url}"})[1:]

    share_urls = {
        'whatsapp': f"https://wa.me/?text={encoded_text_whatsapp}",
        'email': f"mailto:?subject={encoded_title}&body={encoded_text_email_body}",
        'twitter': f"https://twitter.com/intent/tweet?url={encoded_url}&text={encoded_title}",
        'facebook': f"https://www.facebook.com/sharer/sharer.php?u={encoded_url}",
        'copy_url': absolute_url  # URL para el botón de copiar
    }
    # --- FIN: Preparar datos para compartir ---

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
        'share_urls': share_urls,  # Añadir URLs de compartir al contexto
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