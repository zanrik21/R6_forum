from django.urls import path
from . import views

urlpatterns = [
    path('', views.category_list, name='category_list'),
    path('search/', views.topic_search, name='topic_search'),

    path('category/<int:pk>/', views.topic_list, name='topic_list'),
    path('category/<int:pk>/delete/', views.category_delete, name='category_delete'),

    path('topic/create/', views.topic_create, name='topic_create'),
    path('topic/<int:pk>/', views.topic_detail, name='topic_detail'),
    path('topic/<int:pk>/delete/', views.topic_delete, name='topic_delete'),

    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),

    path('ban/<int:user_id>/', views.ban_user, name='ban_user'),
    path('unban/<int:user_id>/', views.unban_user, name='unban_user'),
    path('category/<int:pk>/delete/', views.category_delete, name='category_delete'),
]
