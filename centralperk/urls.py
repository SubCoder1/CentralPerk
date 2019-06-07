from django.contrib import admin
from django.urls import include, path
from AUth.views import register_user, user_login, user_logout
from Profile.views import (
    view_profile, edit_profile, 
    manage_relation, del_user_post,
    post_view )
from Home.views import home_view, clear_all_notification
from Home.views import manage_home_post_likes as manage_likes_home
from Profile.views import manage_profile_post_likes as manage_likes_profile
from django.conf import settings
from django.conf.urls.static import static

AUth = [
    path('admin/', admin.site.urls),
    path('', user_login, name='user_login'),
    path('logout/', user_logout, name='user_logout'),
    path('register/', register_user, name='register_user'),
]

Home = [
    path('home/', home_view.as_view(), name='home_view'),
    path('home/<str:post_id>/like', manage_likes_home, name='post_like_home'),
    path('home/notifications/del_all', clear_all_notification, name='clear_notifications'),
]

Profile = [
    path('profile/<str:username>', view_profile, name='view_profile'),
    path('profile/<str:username>/edit', edit_profile.as_view(), name='edit_profile'),
    path('profile/<str:post_id>/view', post_view, name='view_post'),
    path('profile/<str:username>/<str:post_id>/like/<str:view_post>', manage_likes_profile, name='like_from_post_view'),
    path('profile/<str:username>/<str:post_id>/like', manage_likes_profile, name='like_from_profile_post'),
    path('profile/<str:post_id>/del', del_user_post, name='del_user_post'),
    path('profile/<str:username>/<str:option>', manage_relation, name='manage_relation'),
]

urlpatterns = AUth + Home + Profile + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns