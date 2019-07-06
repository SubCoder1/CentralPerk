from django.contrib import admin
from Profile.models import User, Friends
from Profile.forms import UserAdminChangeForm
from AUth.forms import Registerform
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

# Define your model Admins here.
class UserAdmin(BaseUserAdmin):
    change_form = UserAdminChangeForm
    add_form = Registerform

    list_display = ('username', 'email', 'active')
    list_filter = ('admin', 'staff', 'active')
    fieldsets = (
        ( None, {'fields' : ('email', 'password')} ),
        ( 'Personal Info', {'fields' : ('full_name', 'birthdate', 'gender', 'username', 'bio', 'profile_pic')} ),
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

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(Friends)