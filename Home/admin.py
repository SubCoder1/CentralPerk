from django.contrib import admin
from Home.models import PostModel

class PostModelAdmin(admin.ModelAdmin):
    readonly_fields = ('unique_id','post_id')
    fieldsets = (
        ( 'Posted By', {'fields' : ('user',)} ),
        ( 'ID', {'fields' : ('post_id', 'unique_id',)} ),
        ( 'Post', {'fields' : ('status', 'caption', 'pic', 'date_time', 'location', )} ),
        ( 'Send_to', {'fields' : ('send_to', )} ),
    )


admin.site.register(PostModel, PostModelAdmin)