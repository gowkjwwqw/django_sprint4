from django.urls import path, include
from . import views

app_name = 'users'

urlpatterns = [
    # Стандартные URL для аутентификации
    path('auth/', include('django.contrib.auth.urls')),

    path(
        'auth/registration/',
        views.ProfileCreateView.as_view(),
        name='registration',
    ),

    path(
        "profile/edit/",
        views.ProfileUpdateView.as_view(),
        name="edit_profile",
    )
]
