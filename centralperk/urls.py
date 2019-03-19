
from django.contrib import admin
from django.urls import include, path
from AUth.views import register_user, user_login, user_logout
from Profile.views import view_profile
from Home.views import home_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_login, name='user_login'),
    path('logout/', user_logout, name='user_logout'),
    path('register/', register_user, name='register_user'),
    path('profile/<str:username>', view_profile, name='view_profile'),
    path('home/', home_view.as_view(), name='home_view'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
