from __future__ import absolute_import, unicode_literals
from celery import shared_task
from Profile.models import User, Account_Notif_Settings
from django.core.exceptions import ObjectDoesNotExist

@shared_task
def update_user_acc_settings(username, data):
    try:
        user = User.get_user_obj(username=username)
        user_acc_settings = Account_Notif_Settings.objects.get(user=user)
        post_choices = ('Disable', 'From People I Follow', 'From Everyone')
        if data.get('disable_all') == 'true':
            user_acc_settings.disable_all = True
        else:
            user_acc_settings.disable_all = False
        if data.get('p_likes') in post_choices:
            user_acc_settings.p_likes = data['p_likes']
        if data.get('p_comments') in post_choices:
            user_acc_settings.p_comments = data['p_comments']
        if data.get('p_comment_likes') in post_choices:
            user_acc_settings.p_comment_likes = data['p_comment_likes']
        if data.get('f_requests') == 'true':
            user_acc_settings.f_requests = True
        else:
            user_acc_settings.f_requests = False
        user_acc_settings.save()

        return f"User - {user.username}'s account was successfully updated."
    except ObjectDoesNotExist:
        return 'User object not found'
    except:
        return 'User account settings was not successfully updated :('

