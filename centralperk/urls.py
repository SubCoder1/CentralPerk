
from django.contrib import admin
from django.urls import include, path
from AUth.views import register_user, user_login, user_logout
from Profile.views import view_profile, edit_profile, manage_relation
from Home.views import home_view, manage_likes
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', user_login, name='user_login'),
    path('logout/', user_logout, name='user_logout'),
    path('register/', register_user, name='register_user'),
    path('profile/<str:username>', view_profile, name='view_profile'),
    path('profile/<str:username>/edit', edit_profile.as_view(), name='edit_profile'),
    path('profile/<str:username>/<str:option>', manage_relation, name='manage_relation'),
    path('home/', home_view.as_view(), name='home_view'),
    path('home/<str:post_id>/like', manage_likes, name='post_like'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar

    urlpatterns = [
                      path('__debug__/', include(debug_toolbar.urls)),
                  ] + urlpatterns