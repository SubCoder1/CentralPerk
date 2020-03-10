from __future__ import absolute_import, unicode_literals
from celery import shared_task
from django.core.exceptions import ObjectDoesNotExist
from django.db import close_old_connections, transaction
from django.db.models import Q
from channels.layers import get_channel_layer
from asgiref.sync import AsyncToSync
from Profile.models import User, Account_Settings, Friends, UserBlockList
from Home.models import Conversations, PostModel
from Home.tasks import del_notifications
from datetime import datetime
import pytz

@shared_task
def update_user_acc_settings(username, data):
    try:
        user = User.get_user_obj(username=username)
        if user is not None:
            user_acc_settings = Account_Settings.objects.filter(user=user).first()
            if user_acc_settings is not None:
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
                user_acc_settings.f_requests = data.get('f_requests') == 'true'
                user_acc_settings.private_acc = data.get('private_acc') == 'true'
                user_acc_settings.activity_status = data.get('activity_status') == 'true'
                user_acc_settings.save()
                return f"User - {user.username}'s account was successfully updated."
        return 'User object not found :('
    except:
        return 'User account settings was not successfully updated :('
    finally:
        close_old_connections()

@shared_task
def block_user(current_user_username, follow_unfollow_username):
    try:
        current_user = User.get_user_obj(username=current_user_username)
        curr_user_block_obj = UserBlockList.objects.filter(current_user=current_user).first()
        follow_unfollow_user = User.get_user_obj(username=follow_unfollow_username)
        # block the user
        # delete relationship from both end!
        Friends.unfollow(current_user, follow_unfollow_user)
        Friends.unfollow(follow_unfollow_user, current_user)
        # add follow_unfollow_user to block list
        curr_user_block_obj.blocked_user.add(follow_unfollow_user)
        # delete convo_obj
        create_or_update_convo_obj.delay(current_user.username, follow_unfollow_user.username, 'delete')
        # in case, user requested to follow then blocked em
        # private account corner case
        Friends.rm_from_pending(current_user, follow_unfollow_user)
        Friends.rm_from_pending(follow_unfollow_user, current_user)
        # delete any posts from blocked user's wall
        follow_unfollow_user.connections.remove(*PostModel.objects.filter(user=current_user))
        current_user.connections.remove(*PostModel.objects.filter(user=follow_unfollow_user))
        if follow_unfollow_user.channel_name is not "":
            channel_layer = get_channel_layer()
            AsyncToSync(channel_layer.send)(follow_unfollow_user.channel_name, { "type" : "update.wall" })
        del_notifications.delay(username=current_user.username, reaction="Sent Follow Request", send_to_username=follow_unfollow_user.username)

        return "User blocked successfully :)"
    except Exception as e:
        print(str(e))
    finally:
        close_old_connections()

@shared_task
def create_or_update_convo_obj(user_a_username, user_b_username, option):
    # user_a_username followed/unfollowed user_b_username (order is imp!)
    try:
        user_a = User.get_user_obj(username=user_a_username)
        user_b = User.get_user_obj(username=user_b_username)
        # build query
        q_a = Q(user_a=user_a)
        q_a.add(Q(user_b=user_b), Q.AND)
        q_b = Q(user_a=user_b)  # If the reverse exists (circumstances like B followed A first then unfollowed)
        q_b.add(Q(user_b=user_a), Q.AND)
        # get convo obj
        convo_q_a = Conversations.objects.filter(q_a)
        convo_q_b = Conversations.objects.filter(q_b)
        if option == 'follow':
            if False is (convo_q_a.exists() or convo_q_b.exists()):
                Conversations.objects.create(user_a=user_a, user_b=user_b, convo={})
                return "convo created successfully :)"
            else:
                with transaction.atomic():
                    convo_obj = convo_q_a.select_for_update().first() if convo_q_a.exists() else convo_q_b.select_for_update().first()
                    convo_obj.date_time = datetime.now(pytz.UTC)
                    convo_obj.save()
                return "convo already exists, updated data-time of obj :)"
        else:
            convo_obj = convo_q_a.first() if convo_q_a.exists() else convo_q_b.first()
            friend_obj = Friends.objects.get(current_user=user_b)
            if not friend_obj.following.filter(username=user_a_username).exists():
                # nobody follows each other, delete their convo obj (if exists)
                convo_obj.delete()
                return "deleted convo obj :)"
            return "nothing to update :|"

    except Exception as e:
        return str(e)
    finally:
        close_old_connections()