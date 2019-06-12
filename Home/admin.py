from django.contrib import admin
from Home.models import PostModel, PostLikes, PostComments, UserNotification

class PostModelAdmin(admin.ModelAdmin):
    readonly_fields = ('unique_id','post_id')
    fieldsets = (
        ( 'Posted By', {'fields' : ('user',)} ),
        ( 'ID', {'fields' : ('post_id', 'unique_id',)} ),
        ( 'Post', {'fields' : ('status', 'caption', 'pic', 'date_time', 'location', )} ),
        ( 'Send_to', {'fields' : ('send_to', )} ),
        ( 'Likes', {'fields' : ('likes_count', 'likes')} ),
    )

class UserNotificationAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Notified to', {'fields' : ('user_to_notify',)} ),
        ('Reaction', {'fields' : ('poked_by', 'reaction', 'post')} ),
    )

admin.site.register(PostModel, PostModelAdmin)
admin.site.register(UserNotification, UserNotificationAdmin)
admin.site.register(PostLikes)
admin.site.register(PostComments)