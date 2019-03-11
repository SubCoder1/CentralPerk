
from django.contrib import admin
from django.urls import include, path
from AUth.views import register_user, user_login, user_logout

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_login, name='user_login'),
    path('logout/', user_logout, name='user_logout'),
    path('register/', register_user, name='register_user'),
]
