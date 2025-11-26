from django.contrib import admin
from .models import Category, Topic, Post, Ban


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'author', 'created_at')
    list_filter = ('category',)
    search_fields = ('title', 'author__username')


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('topic', 'author', 'created_at', 'is_deleted')
    list_filter = ('is_deleted', 'created_at')
    search_fields = ('topic__title', 'author__username', 'content')


@admin.register(Ban)
class BanAdmin(admin.ModelAdmin):
    list_display = ('user', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('user__username',)
