from django.shortcuts import redirect
from django.contrib import messages
from django.urls import reverse


class BanBlockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            # беремо пов’язаний бан-об’єкт, якщо він є
            ban = getattr(request.user, "ban", None)

            if ban and ban.is_active:
                # дозволяємо тільки logout і перегляд власного профілю
                allowed_urls = [
                    reverse("logout"),
                    reverse("profile_detail", args=[request.user.username]),
                ]

                if request.path not in allowed_urls:
                    messages.error(request, "Ваш акаунт заблоковано. Доступ заборонений.")
                    return redirect("profile_detail", username=request.user.username)

        return self.get_response(request)
