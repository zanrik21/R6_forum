from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponseForbidden


class BanMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            ban = getattr(request.user, 'ban', None)
            if ban and ban.is_active:
                allowed_paths = [
                    reverse('logout'),
                    reverse('profile_detail', kwargs={'username': request.user.username}),
                    '/admin/',   # дозволимо адмінам самому собі, але можна забрати
                ]
                # Якщо це не дозволений шлях — забороняємо
                if not any(request.path.startswith(p) for p in allowed_paths):
                    return HttpResponseForbidden("Ви заблоковані адміном.")
        return self.get_response(request)
