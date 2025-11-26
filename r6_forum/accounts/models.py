from django.db import models
from django.contrib.auth.models import User


def user_avatar_path(instance, filename):
    # шлях може бути будь-який, головне — щоб функція існувала
    return f"avatars/{instance.user.username}/{filename}"


class Profile(models.Model):
    RANK_CHOICES = [
        ('champion', 'Champion'),
        ('diamond', 'Diamond'),
        ('platinum', 'Platinum'),
        ('gold', 'Gold'),
        ('silver', 'Silver'),
        ('bronze', 'Bronze'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    # можеш лишити як було (рядок) або перейти на функцію — не критично
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    # або так, якщо хочеш використовувати ту функцію:
    # avatar = models.ImageField(upload_to=user_avatar_path, blank=True, null=True)

    bio = models.TextField(blank=True)
    rank = models.CharField(max_length=20, choices=RANK_CHOICES, default='bronze')
    show_admin_status = models.BooleanField(default=True)

    def __str__(self):
        return f'Profile({self.user.username})'
