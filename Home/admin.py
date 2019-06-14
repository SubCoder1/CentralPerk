from django.contrib import admin
from Home.models import PostModel, PostLikes, PostComments, UserNotification

class PostModelAdmin(admin.ModelAdmin):
    list_display = ('unique_id', 'location', 'user', 'date_time', )
    readonly_fields = ('unique_id','post_id', 'likes_count')
    fieldsets = (
        ( 'Posted By', {'fields' : ('user',)} ),
        ( 'ID', {'fields' : ('post_id', 'unique_id',)} ),
        ( 'Post', {'fields' : ('status_caption', 'pic', 'location', )} ),
        ( 'Send_to', {'fields' : ('send_to', )} ),
        ( 'Likes', {'fields' : ('likes_count',)} ),
    )

class PostCommentsAdmin(admin.ModelAdmin):
    list_display = ('post_obj', 'user', 'date_time')
    readonly_fields = ('post_id', 'date_time',)
    fieldsets = (
        ( 'Commented by', {'fields' : ('user',)} ),
        ( 'Post_ID', {'fields' : ('post_id',)} ),
        ( 'Commented on', {'fields' : ('post_obj', )} ),
        ( 'Comment', {'fields' : ('comment',)} ),
        ( 'Date_time', {'fields' : ('date_time',)} ),
        ( 'Replies', {'fields' : ('reply',)} ),
    )

class UserNotificationAdmin(admin.ModelAdmin):
    fieldsets = (
        ('Notified to', {'fields' : ('user_to_notify',)} ),
        ('Reaction', {'fields' : ('poked_by', 'reaction', 'post')} ),
    )

admin.site.register(PostModel, PostModelAdmin)
admin.site.register(UserNotification, UserNotificationAdmin)
admin.site.register(PostLikes)
admin.site.register(PostComments, PostCommentsAdmin)