from django.db import models
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.name


class Topic(models.Model):
    category = models.ForeignKey(
        Category,
        related_name='topics',
        on_delete=models.CASCADE
    )
    title = models.CharField(max_length=200)
    author = models.ForeignKey(
        User,
        related_name='topics',
        on_delete=models.CASCADE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Post(models.Model):
    topic = models.ForeignKey(
        Topic,
        related_name='posts',
        on_delete=models.CASCADE
    )
    author = models.ForeignKey(
        User,
        related_name='posts',
        on_delete=models.CASCADE
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.author} -> {self.topic}'


class Ban(models.Model):
    user = models.OneToOneField(
        User,
        related_name='ban',
        on_delete=models.CASCADE
    )
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return f'Ban({self.user.username}) - {"active" if self.is_active else "inactive"}'
