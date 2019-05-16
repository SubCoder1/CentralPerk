from django.contrib import admin
from Home.models import PostModel

class PostModelAdmin(admin.ModelAdmin):
    readonly_fields=('unique_id','post_id')
    list_display = ('post_id', 'user', 'date_time',)


admin.site.register(PostModel, PostModelAdmin)