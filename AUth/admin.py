from django.contrib import admin
from AUth.models import User
from django.contrib.auth.models import Group

admin.site.unregister(Group)
admin.site.register(User)