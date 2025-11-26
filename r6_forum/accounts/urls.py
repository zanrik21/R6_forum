from django.urls import path
from . import views

urlpatterns = [
    path('login/',    views.login_view,    name='login'),
    path('logout/',   views.logout_view,   name='logout'),
    path('register/', views.register,      name='register'),

    # ВАЖЛИВО: спочатку /profile/edit/, потім /profile/<username>/
    path('profile/edit/',            views.profile_edit,  name='profile_edit'),
    path('profile/<str:username>/', views.profile_detail, name='profile_detail'),

    path('users/', views.user_list, name='user_list'),
]
