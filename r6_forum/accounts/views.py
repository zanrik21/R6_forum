from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages

from .forms import ProfileEditForm  # ← ВАЖЛИВО: тут ProfileEditForm, НЕ ProfileForm

from forum.models import Topic, Post


# --------------------- АВТОРИЗАЦІЯ --------------------- #

def login_view(request):
    """Вхід користувача."""
    if request.user.is_authenticated:
        return redirect('category_list')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            auth_login(request, user)
            messages.success(request, "Вхід успішний.")
            return redirect('category_list')
    else:
        form = AuthenticationForm(request)

    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    """Вихід користувача."""
    if request.user.is_authenticated:
        auth_logout(request)
        messages.info(request, "Ви вийшли із акаунта.")
    return redirect('category_list')


def register(request):
    """Реєстрація нового користувача."""
    if request.user.is_authenticated:
        return redirect('category_list')

    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()

            # На всякий випадок створюємо профіль (якщо є модель Profile)
            try:
                from .models import Profile
                Profile.objects.get_or_create(user=user)
            except Exception:
                pass

            auth_login(request, user)
            messages.success(request, "Акаунт створено, ви увійшли в систему.")
            return redirect('category_list')
    else:
        form = UserCreationForm()

    return render(request, 'accounts/register.html', {'form': form})


# --------------------- ПРОФІЛЬ --------------------- #

def profile_detail(request, username):
    """Сторінка профілю користувача."""
    profile_user = get_object_or_404(User, username=username)
    profile = getattr(profile_user, 'profile', None)

    # останні теми та пости
    last_topics = Topic.objects.filter(author=profile_user).order_by('-created_at')[:5]
    last_posts = Post.objects.filter(author=profile_user, is_deleted=False).order_by('-created_at')[:5]

    # інфа про бан (якщо є зв’язана модель ban)
    ban = getattr(profile_user, 'ban', None)

    return render(request, 'accounts/profile_detail.html', {
        'profile_user': profile_user,
        'profile': profile,
        'last_topics': last_topics,
        'last_posts': last_posts,
        'ban': ban,
    })


@login_required
def profile_edit(request):
    """Редагування власного профілю."""
    profile = request.user.profile

    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)

            # Простим юзерам — захист: вони не можуть вмикати show_admin_status
            if not (request.user.is_staff or request.user.is_superuser):
                if hasattr(profile, "show_admin_status"):
                    profile.show_admin_status = False

            profile.save()
            messages.success(request, "Профіль оновлено.")
            return redirect('profile_detail', username=request.user.username)
    else:
        form = ProfileEditForm(instance=profile)

    return render(request, 'accounts/profile_edit.html', {
        'form': form,
    })


# --------------------- СПИСОК КОРИСТУВАЧІВ --------------------- #

def user_list(request):
    """Список користувачів із пошуком по ніку."""
    q = request.GET.get('q', '').strip()
    users = User.objects.all().order_by('username')
    if q:
        users = users.filter(username__icontains=q)

    return render(request, 'accounts/user_list.html', {
        'users': users,
        'q': q,
    })
