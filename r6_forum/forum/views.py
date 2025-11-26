from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.utils.timezone import now  # 🔥 для online-статусу

from .models import Category, Topic, Post, Ban
from .forms import TopicForm, PostForm


def is_admin(user):
    return user.is_superuser or user.is_staff


# ======================= КАТЕГОРІЇ / ТЕМИ =======================

def category_list(request):
    categories = Category.objects.all()
    return render(request, 'forum/category_list.html', {
        'categories': categories
    })


def topic_list(request, pk):
    category = get_object_or_404(Category, pk=pk)
    topics = category.topics.order_by('-created_at')
    return render(request, 'forum/topic_list.html', {
        'category': category,
        'topics': topics
    })


def topic_detail(request, pk):
    topic = get_object_or_404(Topic, pk=pk)

    posts = (
        topic.posts
        .filter(is_deleted=False)
        .select_related('author')
        .order_by('created_at')
    )

    # прапор бану + онлайн для автора кожного поста
    for p in posts:
        ban = getattr(p.author, 'ban', None)
        p.author_is_banned = ban.is_active if ban else False

        last_login = getattr(p.author, 'last_login', None)
        if last_login:
            delta = now() - last_login
            p.author_is_online = (delta.total_seconds() < 300)  # 5 хв
        else:
            p.author_is_online = False

    # прапор бану для автора теми
    topic_author_ban = getattr(topic.author, 'ban', None)
    topic.author_is_banned = topic_author_ban.is_active if topic_author_ban else False

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')

        form = PostForm(request.POST)
        if form.is_valid():
            post = form.save(commit=False)
            post.topic = topic
            post.author = request.user
            post.save()
            messages.success(request, "Коментар додано.")
            return redirect('topic_detail', pk=topic.pk)
    else:
        form = PostForm()

    return render(request, 'forum/topic_detail.html', {
        'topic': topic,
        'posts': posts,
        'form': form
    })


def topic_search(request):
    q = request.GET.get('q', '').strip()
    topics = []
    if q:
        topics = Topic.objects.filter(
            title__icontains=q
        ).select_related('category', 'author').order_by('-created_at')

    return render(request, 'forum/topic_search.html', {
        'q': q,
        'topics': topics,
    })


# ======================= СТВОРЕННЯ ТЕМИ =======================

@login_required
def topic_create(request):
    """
    Усі залогінені користувачі можуть створювати тему.
    Звичайний юзер вибирає ЛИШЕ існуючу категорію.
    Адмін / мод може або створити нову категорію, або вибрати зі списку.
    """
    categories = Category.objects.all()
    user_is_admin = is_admin(request.user)

    if request.method == 'POST':
        form = TopicForm(request.POST)
        post_form = PostForm(request.POST)

        if not (form.is_valid() and post_form.is_valid()):
            messages.error(request, "Перевір поля форми.")
            return render(request, 'forum/topic_create.html', {
                'form': form,
                'post_form': post_form,
                'categories': categories,
                'can_create_category': user_is_admin,
            })

        category = None

        # Якщо адмін / модератор – може створити нову категорію
        if user_is_admin:
            category_name = form.cleaned_data.get('category_name', '').strip()
            if category_name:
                base_slug = slugify(category_name) or "cat"
                slug = base_slug
                i = 1
                while Category.objects.filter(slug=slug).exists():
                    slug = f"{base_slug}-{i}"
                    i += 1
                category, created = Category.objects.get_or_create(
                    name=category_name,
                    defaults={'slug': slug}
                )

        # Якщо не створили нову категорію (або юзер не адмін) – беремо зі списку
        if category is None:
            selected_category_id = request.POST.get('category')
            category = Category.objects.filter(id=selected_category_id).first()
            if not category:
                messages.error(request, "Потрібно вибрати категорію зі списку.")
                return render(request, 'forum/topic_create.html', {
                    'form': form,
                    'post_form': post_form,
                    'categories': categories,
                    'can_create_category': user_is_admin,
                })

        # Створюємо тему
        topic = Topic.objects.create(
            category=category,
            title=form.cleaned_data['title'],
            author=request.user
        )

        # Перший пост
        first_post = post_form.save(commit=False)
        first_post.topic = topic
        first_post.author = request.user
        first_post.save()

        messages.success(request, "Тема створена.")
        return redirect('topic_detail', pk=topic.pk)

    else:
        form = TopicForm()
        post_form = PostForm()

    return render(request, 'forum/topic_create.html', {
        'form': form,
        'post_form': post_form,
        'categories': categories,
        'can_create_category': user_is_admin,
    })


# ======================= ПОСТИ: РЕДАГУВАННЯ / ВИДАЛЕННЯ =======================

@login_required
def post_edit(request, pk):
    post = get_object_or_404(Post, pk=pk, is_deleted=False)

    if not (request.user == post.author or is_admin(request.user)):
        messages.error(request, "У вас немає прав редагувати це повідомлення.")
        return redirect('topic_detail', pk=post.topic.pk)

    if request.method == 'POST':
        form = PostForm(request.POST, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, "Повідомлення оновлено.")
            return redirect('topic_detail', pk=post.topic.pk)
    else:
        form = PostForm(instance=post)

    return render(request, 'forum/post_edit.html', {
        'form': form,
        'post': post,
    })


@login_required
def post_delete(request, pk):
    """
    Автор може видалити свій пост.
    Адмін / модератор може видалити будь-який.
    """
    post = get_object_or_404(Post, pk=pk, is_deleted=False)

    if not (request.user == post.author or is_admin(request.user)):
        messages.error(request, "У вас немає прав видаляти це повідомлення.")
        return redirect('topic_detail', pk=post.topic.pk)

    post.is_deleted = True
    post.save()
    messages.success(request, "Коментар видалено.")
    return redirect('topic_detail', pk=post.topic.pk)


# ======================= ВИДАЛЕННЯ ТЕМИ / КАТЕГОРІЇ =======================

@login_required
def topic_delete(request, pk):
    """
    Видалити тему може:
    - автор теми
    - адмін / модератор
    """
    topic = get_object_or_404(Topic, pk=pk)

    if not (request.user == topic.author or is_admin(request.user)):
        messages.error(request, "У вас немає прав видаляти цю тему.")
        return redirect('topic_detail', pk=topic.pk)

    category_pk = topic.category.pk
    topic.delete()
    messages.success(request, "Тему видалено.")
    return redirect('topic_list', pk=category_pk)


@user_passes_test(is_admin)
def category_delete(request, pk):
    category = get_object_or_404(Category, pk=pk)
    name = category.name
    category.delete()
    messages.success(request, f"Категорію «{name}» видалено.")
    return redirect('category_list')


# ======================= БАН / РОЗБАН =======================

@user_passes_test(is_admin)
def ban_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    ban, created = Ban.objects.get_or_create(user=user)
    ban.is_active = True
    ban.save()
    messages.success(request, f"Користувача {user.username} заблоковано.")
    return redirect('profile_detail', username=user.username)


@user_passes_test(is_admin)
def unban_user(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    ban = getattr(user, 'ban', None)
    if ban:
        ban.is_active = False
        ban.save()
    messages.success(request, f"Користувача {user.username} розблоковано.")
    return redirect('profile_detail', username=user.username)
