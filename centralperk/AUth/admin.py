from django.contrib import admin
from django.contrib.auth.models import Group

admin.site.site_header = 'DJokerAdmin'
admin.site.unregister(Group)