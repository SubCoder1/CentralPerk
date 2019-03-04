
from django.contrib import admin
from django.urls import include, path
from AUth.views import register_user, user_login

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', user_login),
    path('register/', register_user, name='register_user'),
]
