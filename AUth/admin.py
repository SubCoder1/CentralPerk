from django.contrib import admin
from AUth.models import User
from AUth.forms import UserAdminChangeForm, Registerform
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group

class UserAdmin(BaseUserAdmin):
    change_form = UserAdminChangeForm
    add_form = Registerform

    list_display = ('username', 'email', 'active')
    list_filter = ('admin', 'staff', 'active')
    fieldsets = (
        ( None, {'fields' : ('email', 'password')} ),
        ( 'Personal Info', {'fields' : ('full_name', 'birthdate', 'gender', 'username', 'bio', 'profile_pic')} ),
        ( 'Likes', {'fields' : ('post_liked',)} ),
        ( 'Permissions', {'fields' : ('admin', 'staff', 'active')} ),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password',)}
        ),
    )
    search_fields = ('email', 'username',)
    ordering = ('username',)
    filter_horizontal = ()

admin.site.unregister(Group)
admin.site.register(User, UserAdmin)
admin.site.site_header = 'DJokerAdmin'