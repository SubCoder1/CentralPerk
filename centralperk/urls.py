from django.contrib import admin
from django.urls import include, path
from AUth.views import register_user, user_login, user_logout
from Profile.views import (
    view_profile, edit_profile, 
    manage_relation, del_user_post,
    post_view, manage_post_likes )
from Home.views import home_view
from django.conf import settings
from django.conf.urls.static import static

AUth = [
    path('admin/', admin.site.urls),
    path('', user_login, name='user_login'),
    path('logout/', user_logout, name='user_logout'),
    path('register/', register_user, name='register_user'),
    path('session_security/', include('session_security.urls')),
]

Home = [
    path('home/', home_view.as_view(), name='home_view'),
]

Profile = [
    path('profile/<str:username>', view_profile, name='view_profile'),
    path('profile/<str:username>/edit', edit_profile.as_view(), name='edit_profile'),
    path('profile/<str:post_id>/view', post_view, name='view_post'),
    path('profile/<str:post_id>/like', manage_post_likes, name='like_from_post_view'),
    path('profile/<str:post_id>/del', del_user_post, name='del_user_post'),
    path('profile/<str:username>/<str:option>', manage_relation, name='manage_relation'),
]

urlpatterns = AUth + Home + Profile + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)