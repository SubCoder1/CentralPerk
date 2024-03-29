from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.template.loader import render_to_string
from django.db.models import F, Count, Prefetch, Q
from django.db import close_old_connections, transaction
from django.contrib.sessions.models import Session
from channels.layers import get_channel_layer
from Profile.models import User, Friends, UserBlockList
from Profile.tasks import create_or_update_convo_obj
from Home.models import PostModel, PostLikes, PostComments, UserNotification, Conversations
from Home.tasks import (
    send_notifications, del_notifications, 
    monitor_user_status, share_post_to_users
)
import json, asyncio, pytz
from hashlib import sha256
from datetime import datetime, timedelta
from itertools import chain

class CentralPerkHomeConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def update_session_exp_datetime(self):
        try:
            tz = pytz.timezone('Asia/Kolkata')
            user = self.scope['user']
            session_key = self.scope['session'].session_key
            cache_key = self.scope['session'].cache_key
            session_obj = Session.objects.get(session_key=session_key)
            session_obj.expire_date = datetime.now().astimezone(tz=tz) + timedelta(minutes=8)
            session_obj.save()
            if user.monitor_task_id == "":
                user.monitor_task_id = str(monitor_user_status.apply_async((user.username, session_key, cache_key), countdown=480).task_id)
                user.save()
            print(f"session expiry date after update -> {session_obj.expire_date}")
        except Exception as e:
            print(str(e))

    async def connect(self):
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()
        else:
            # Accept the connection
            await self.accept()
            # fix session timeout of 10mins & schedule a monitoring task
            await self.update_session_exp_datetime()
        await self.add_channel_name_to_user(channel_name=self.channel_name)

    async def disconnect(self, close_code):
        # This code is useful against sudden refresh in landing page
        # Without this, open convos before refresh will stay open after. . .
        await self.close_existing_open_p_chat()

    async def receive(self, text_data):
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()
        data_from_client = json.loads(text_data)
        if data_from_client.get('task') is not None:
            # extend user's session time-out as he/she is clearly active!
            await self.update_session_exp_datetime()

            # like/Dislike posts from wall-posts
            if data_from_client['task'] == 'post_like':
                post_id = data_from_client.get('post_id', None)
                if post_id is not None:
                    await self.like_post_from_wall(post_id=post_id)
            # Post comments from wall-posts
            elif data_from_client['task'] == 'post_comment':
                post_id = data_from_client.get('post_id', None)
                comment = data_from_client.get('comment', None)
                response = await self.post_comment_from_wall(post_id=post_id, comment=comment)
                if response == 'comment cannot be empty' or response is None:
                    await self.send(text_data=json.dumps({
                        'type' : 'error',
                        'error' : response,
                    }))
                else:
                    await self.send(text_data=json.dumps({
                        'type' : 'comment_count',
                        'post_id' : post_id,
                        'count' : response,
                    }))
            # Save/Unsave posts
            elif data_from_client['task'] == 'save_unsave_post':
                post_id = data_from_client.get('post_id', None)
                response = await self.save_unsave_post(post_id=post_id)
                if response is None:
                    await self.send(text_data=json.dumps({
                        'type' : 'error',
                        'error' : response,
                    }))
                else:
                    await self.send(text_data=json.dumps({
                        'type' : 'save_unsave_post_response',
                        'post_id' : post_id,
                        'result' : response,
                    }))
            # Get notifications
            elif data_from_client['task'] == 'get_notifications':
                await self.send_updated_notif()
            # Clear all notifications
            elif data_from_client['task'] == 'clear_notif_all':
                await self.del_notifications_all()
                await self.send_updated_notif()
            #accept_reject_private_request
            elif data_from_client['task'] == 'accept_reject_p_request':
                notif_id = data_from_client.get('notif_id', None)
                option = data_from_client.get('option', None)
                await self.accept_reject_private_request(notif_id, option)
            # Username search
            elif data_from_client['task'] == 'search':
                if data_from_client['query'] is not None:
                    response = await self.search_results(query=data_from_client['query'])
                    await self.send(text_data=json.dumps({
                        'type' : 'search_results',
                        'results' : render_to_string("search.html", {'results':response}),
                    }))
            # Get p_chat_cover
            elif data_from_client['task'] == 'get_p_chat_cover':
                await self.send_p_chat_cover()
            # Get p_chat
            elif data_from_client['task'] == 'get_p_chat':
                username = data_from_client.get('user', None)
                if username is not None:
                    await self.send_p_chat(username=username)
                else:
                    pass
            # Get p_chat msg
            elif data_from_client['task'] == 'p_chat_msg':
                message = data_from_client.get('msg', None)
                convo_id = data_from_client.get('convo_id', None)
                date_time = data_from_client.get('date_time', None)
                signal = data_from_client.get('signal', None)
                if date_time is not None:
                    try:
                        # date_time is only attached if msg is sent, format checking is done here!
                        d_t = datetime.strptime(str(date_time), "%m/%d/%Y, %H:%M %p")
                        await self.send_msg(message=message, convo_id=convo_id, date_time=date_time, signal=signal)
                    except Exception as e:
                        print(str(e))
                else:
                    await self.send_msg(message=message, convo_id=convo_id, date_time=date_time, signal=signal)
            # Get friends list
            elif data_from_client['task'] == 'get_friends_list':
                await self.send_friends_list()
            # else do nothing :|
            else:
                pass
    
    @database_sync_to_async
    def add_channel_name_to_user(self, channel_name):
        try:
            user = self.scope['user']
            user.channel_name = channel_name
            user.save()
        except Exception as e:
            print(str(e))
    
    @database_sync_to_async
    def get_user_by_username(self, username):   # Helper function
        return User.get_user_obj(username=username)

    @database_sync_to_async
    def get_wall_posts(self):
        try:
            user = self.scope['user']
            posts = user.connections.prefetch_related(Prefetch('saved_by')).select_related('user')
            return posts
        except Exception as e:
            print(str(e))

    @database_sync_to_async
    def like_post_from_wall(self, post_id):
        user = self.scope['user']
        try:
            post = PostModel.objects.filter(post_id=post_id).prefetch_related(Prefetch('post_like_obj')).select_related('user').first()
            post_user_block_obj = UserBlockList.objects.filter(current_user=post.user).first()
            # check if user's not being blocked by post.user
            if not post_user_block_obj.blocked_user.filter(username=user.username).exists():
                print("waah bc")
                if post.post_like_obj.filter(user=user).exists():
                    # Dislike post
                    post.post_like_obj.filter(user=user).delete()
                    del_notifications.delay(username=user.username, reaction="Disliked", send_to_username=post.user.username, post_id=post_id)
                    post.likes_count = F('likes_count') - 1
                    post.save()
                    post.refresh_from_db()
                else:
                    # Like post
                    post_like_obj = PostLikes.objects.create(post_obj=post, user=user)
                    post.post_like_obj.add(post_like_obj)
                    post.likes_count = F('likes_count') + 1
                    post.save()
                    post.refresh_from_db()
                    # Notify the user whose post is being liked
                    send_notifications.delay(username=user.username, reaction="Liked", send_to_username=post.user.username, post_id=post_id)
        except Exception as e:
            print(str(e))

    @database_sync_to_async
    def post_comment_from_wall(self, post_id, comment):
        try:
            user = self.scope['user']
            if comment.isspace() or not len(comment):
                # Cannot accept blank comments or comments with only spaces or newlines
                return 'comment cannot be empty'
            post_obj = PostModel.objects.get_post(post_id=post_id)
            post_user_block_obj = UserBlockList.objects.filter(current_user=post_obj.user).first()
            # check if user's not being blocked by post.user
            if not post_user_block_obj.blocked_user.filter(username=user.username).exists():
                c = PostComments.objects.create(user=user, post_obj=post_obj, comment=comment)
                post_obj.post_comment_obj.add(c)
                post_obj.comment_count = F('comment_count') + 1
                post_obj.save()
                post_obj.refresh_from_db()
                # Notify the user whose post you commented on
                send_notifications.delay(username=user.username, reaction='Commented', 
                send_to_username=post_obj.user.username, post_id=post_id, comment_id=c.comment_id)
            return post_obj.comment_count
        except Exception as e:
            print(str(e))
    
    @database_sync_to_async
    def save_unsave_post(self, post_id):
        try:
            user = self.scope['user']
            post_obj = PostModel.objects.get_post(post_id=post_id)
            post_user_block_obj = UserBlockList.objects.filter(current_user=post_obj.user).first()
            # check if user's not being blocked by post.user
            if not post_user_block_obj.blocked_user.filter(username=user.username).exists():
                if user in post_obj.saved_by.all():
                    post_obj.saved_by.remove(user)
                    return 'unsaved'
                else:
                    post_obj.saved_by.add(user)
                    return 'saved'
        except Exception as e:
            print(str(e))

    @database_sync_to_async
    def accept_reject_private_request(self, notif_id, option):
        try:
            user = self.scope['user']
            private_request_id = str(user.user_id) + str(notif_id) 
            private_request_hash = sha256(bytes(private_request_id, encoding='utf-8')).hexdigest()
            #print(private_request_hash)
            if UserNotification.objects.filter(private_request_id=private_request_hash).exists():
                notification = UserNotification.objects.get(private_request_id=private_request_hash)
                request_by = notification.poked_by
                if option == 'accept_request':
                    # Create or update a conversation model btw request_by_user & user
                    create_or_update_convo_obj.delay(request_by.username, user.username, 'follow')
                    Friends.follow(request_by, user)
                    # delete any existing similar notification
                    del_notifications(reaction="Accept Follow Request", username=user.username, send_to_username=request_by.username)
                    send_notifications.delay(username=user.username, reaction="Accept Follow Request", 
                    send_to_username=request_by.username, private_request=False)
                    # share two of user's recent posts *(if any) to request_by.user's wall
                    share_post_to_users.delay(username=user.username, send_to=[str(request_by.username)], to_wall=True)
                else:
                    create_or_update_convo_obj.delay(request_by.username, user.username, 'unfollow')
                notification.delete()
                Friends.rm_from_pending(user, request_by)
        except Exception as e:
            print(str(e))

    @database_sync_to_async
    def del_notifications_all(self):
        try:
            user = self.scope['user']
            user.notifications.all().delete()
            return 'cleared all notif :)'
        except Exception as e:
            print(str(e))
            return None

    @database_sync_to_async
    def search_results(self, query=None):
        try:
            q = Q(current_user__username__startswith=query)
            q.add(Q(current_user__admin=False), Q.AND)
            query_res = Friends.objects.filter(q).annotate(f_count=Count('followers'))\
                .order_by('-f_count').select_related('current_user')
            return query_res[:10]
        except Exception as e:
            print(str(e))

    @database_sync_to_async
    def get_notifications(self):
        try:
            user = self.scope['user']
            notifications = user.notifications.select_related('poked_by')
            return notifications
        except Exception as e:
            print(str(e))

    @database_sync_to_async
    def close_existing_open_p_chat(self):
        # Close any open conversations from this end
        # Build query
        user = self.scope['user']
        query_a = Q(user_a=user)
        query_a.add(Q(chat_active_from_a=True), Q.AND)
        query_b = Q(user_b=user)
        query_b.add(Q(chat_active_from_b=True), Q.AND)
        with transaction.atomic():
            open_convo_list_a = Conversations.objects.filter(query_a).select_for_update()
            open_convo_list_b = Conversations.objects.filter(query_b).select_for_update()

            open_convo_list = list(chain(open_convo_list_a, open_convo_list_b))
            for convo in open_convo_list:   # Theoretically this loop should run for at most 1 times
                if convo.user_a == user:
                    convo.chat_active_from_a = False
                else:
                    convo.chat_active_from_b = False
                convo.save()

    @database_sync_to_async
    def get_p_chat_cover(self):
        user = self.scope['user']
        query = Q(user_a=user)
        query.add(Q(user_b=user), Q.OR)
        convo_list = Conversations.objects.filter(query).select_related('user_a', 'user_b')
        return convo_list
    
    @database_sync_to_async
    def get_p_chat(self, username):
        try:
            # check if user exists
            p_chat_user = User.objects.filter(username=username).select_related('user_setting').first()
            # If exists . . .
            if p_chat_user is not None:
                # p_chat_user exists, now check if convo obj exists btw these two
                user = self.scope['user']
                # Build query obj to get convo obj
                query = Q()
                query_a = Q(user_a=user)
                query_a.add(Q(user_b=p_chat_user), Q.AND)
                query_b = Q(user_a=p_chat_user)
                query_b.add(Q(user_b=user), Q.AND)
                query.add(query_a, Q.OR)
                query.add(query_b, Q.OR)

                with transaction.atomic():
                    convo = Conversations.objects.filter(query).select_related('user_a', 'user_b').select_for_update().first()
                    if convo is not None:
                        # Activate conversation from this end
                        if convo.user_a == user:
                            convo.chat_active_from_a = True
                            convo.save()
                        else:
                            convo.chat_active_from_b = True
                            convo.save()

                    # check if there are any saved convo (unseen)
                    clear_convo = False
                    if convo.convo_counter:
                        # if any, check if they are sent from opposite user
                        if convo.convo['0']['msg_from'] != user.username:
                            clear_convo = True
                    # create convo_unique_id
                    unique_id = sha256(bytes(str(convo.id), encoding='utf-8')).hexdigest()
                    # Return convo obj
                    return (
                        convo, unique_id,
                        p_chat_user.user_setting.activity_status and user.user_setting.activity_status,
                        clear_convo
                    )
            # else return None
            return
        except Exception as e:
            print(str(e))

    @database_sync_to_async
    def get_active_convo_send_to(self, convo_id):
        # From this function, we get the user to whom request.user wants the msg to be delivered.
        try:
            # Build query
            user = self.scope['user']
            query_a = Q(user_a=user)
            query_a.add(Q(chat_active_from_a=True), Q.AND)
            open_convo_list_a = Conversations.objects.filter(query_a).first()
            if open_convo_list_a:
                if convo_id == str(open_convo_list_a.id):
                    return (open_convo_list_a, open_convo_list_a.user_b, open_convo_list_a.user_a.username)
                else:
                    return (None, None, None)

            query_b = Q(user_b=user)
            query_b.add(Q(chat_active_from_b=True), Q.AND)
            open_convo_list_b = Conversations.objects.filter(query_b).first()
            if open_convo_list_b:
                if convo_id == str(open_convo_list_b.id):
                    return (open_convo_list_b, open_convo_list_b.user_a, open_convo_list_b.user_b.username)
                else:
                    return (None, None, None)
        except Exception as e:
            print(str(e))

    @database_sync_to_async
    def validate_open_convo_by_id(self, convo_id):
        # This function is used during chat_receive
        # The purpose is to check whether receiving user has sender's p_chat open or not
        user = self.scope['user']
        convo = Conversations.objects.filter(id=convo_id).first()
        if convo.user_a == user and convo.chat_active_from_a:
            return True
        elif convo.user_b == user and convo.chat_active_from_b:
            return True
        return False

    @database_sync_to_async
    def update_convo_obj(self, convo_id, clear_convo): # Helper function
        with transaction.atomic():
            convo_obj = Conversations.objects.filter(id=convo_id).select_for_update().first()
            if clear_convo:
                convo_obj.convo_counter = 0
                convo_obj.convo = {}
                convo_obj.save()
                return True
            else:
                convo_obj.date_time = datetime.now(pytz.UTC)
                convo_obj.save()  

    @database_sync_to_async
    def get_friends_list(self):
        user = self.scope['user']
        followers, following = Friends.get_friends_list(current_user=user)
        return (followers, following)

    async def send_friends_list(self, event=None):
        followers, following = await self.get_friends_list()
        await self.send(text_data=json.dumps({
                'type' : 'friends_list_f_server',
                'following' : render_to_string("u-following.html", {'following':following}),
                'followers' : render_to_string("u-followers.html", {'followers':followers}),
            }))

    async def send_updated_notif(self, event=None):
        try:
            notifications = await self.get_notifications()
            await self.send(text_data=json.dumps({
                'type' : 'updated_notif',
                'notif' : render_to_string("notifications.html", {'notifications':notifications}),
            }))
        except Exception as e:
            print(str(e))

    async def update_wall(self, event=None):
        try:
            posts = await self.get_wall_posts()
            await self.send(text_data=json.dumps({
                'type' : 'updated_wall',
                'posts' : render_to_string("wall.html", {'posts':posts}),
            }))
        except Exception as e:
            print(str(e))

    async def send_p_chat_cover(self, event=None):
        try:
            # clean existing open p-chat
            await self.close_existing_open_p_chat()
            # get a fresh new list
            friends_list = await self.get_p_chat_cover()
            # send it to the client!
            await self.send(text_data=json.dumps({
                'type' : 'p_chat_cover_f_server',
                'p-chat-cover' : render_to_string("p-chat-cover.html", {'friends':friends_list, 'user':self.scope['user']}),
            }))
        except Exception as e:
            print(str(e))

    async def send_p_chat(self, username, event=None):
        try:
            friend, unique_id, f_activity_status, clear_convo = await self.get_p_chat(username=username)
            if friend is not None:
                context = {
                    'friend':friend, 'user':self.scope['user'], 
                    'activity_status':f_activity_status,'unique_id':unique_id,
                    'convo_id':friend.id, 'unseen_dm' : clear_convo,
                    'date_now': datetime.now().strftime("%m/%d/%Y") ,
                }
                await self.send(text_data=json.dumps({
                    'type' : 'p_chat_f_server',
                    'p-chat' : render_to_string("p-chat.html", context),
                }))

                # clear saved convo (if any and clear_convo is True)
                if clear_convo:
                    signal = await self.update_convo_obj(convo_id=friend.id, clear_convo=True)
                    if signal:  # signal will be true iff there were some stored convo in obj
                        send_to = friend.user_a if friend.user_b == self.scope['user'] else friend.user_b
                        # send seen signal to opposite user if he/she's active
                        if send_to.channel_name is not "":
                            channel_layer = get_channel_layer()
                            await channel_layer.send(send_to.channel_name, {
                                "type" : "receive.msg",
                                "signal" : "seen",
                                "convo_id" : friend.id,
                            })

        except Exception as e:
            print(str(e))

    async def send_msg(self, message, convo_id, date_time, signal, event=None):
        if convo_id is not None:
            # This will get the user to which the msg is to be sent
            convo_obj, send_to, msg_from = await self.get_active_convo_send_to(convo_id=convo_id)
            if convo_obj is not None:
                if send_to.channel_name is not "":
                    channel_layer = get_channel_layer()
                    # check if it's a signal (typing...) instead of msg
                    if signal == 'typing...' and message is None and date_time is None:
                        await channel_layer.send(send_to.channel_name, {
                            "type" : "receive.msg",
                            "signal" : "typing...",
                            "msg_from" : msg_from,
                            "convo_id" : convo_obj.id,
                        })
                    else:
                        # It's a plain-old msg
                        # send the msg to user
                        unique_id = sha256(bytes(str(convo_obj.id), encoding='utf-8')).hexdigest()
                        await channel_layer.send(send_to.channel_name, {
                            "type" : "receive.msg",
                            "msg" : message,
                            "msg_from" : msg_from,
                            "convo_id" : convo_obj.id,
                            "date_time" : date_time,
                            "unique_id" : unique_id,
                        })
                else:
                    # store dm in convo field, to show later as send_to is not active
                    if signal == None:
                        date, time = date_time.split(',')
                        data = {
                            "msg": message, "convo_id": convo_id,
                            "date": date, "time":time, "msg_from": msg_from,
                        }
                        with transaction.atomic():
                            convo_obj = Conversations.objects.filter(id=convo_id).select_for_update().first()
                            convo_obj.convo[str(convo_obj.convo_counter)] = data
                            # sort convo for ordering
                            convo_obj.convo = {k : convo_obj.convo[k] for k in sorted(convo_obj.convo)}
                            convo_obj.convo_counter += 1
                            convo_obj.save()
                # finally, update convo_obj date time so that it shows up on top 
                # of your & opp. user's p-chat-cover
                await self.update_convo_obj(convo_id=convo_obj.id, clear_convo=False)

    async def receive_msg(self, event=None):
        result = await self.validate_open_convo_by_id(convo_id=event['convo_id'])
        if result:
            # user is active and has the same convo p-chat open, where this msg is supposed to go!
            if event.get('signal', None) == "seen":
                # It's a 'seen' signal, send it quickly as result is also True
                await self.send(text_data=json.dumps({
                    'type' : 'p_chat_msg_seen',
                    'msg' : 'seen',
                    'convo_id' : event['convo_id'],
                }))
            elif event.get('signal', None) == 'typing...':
                # It's a 'typing...' signal, send it quickly as result is also True
                unique_id = sha256(bytes(str(event['convo_id']), encoding='utf-8')).hexdigest()
                await self.send(text_data=json.dumps({
                    'type' : 'p_chat_typing_signal',
                    'msg' : 'typing...',
                    'convo_id' : event['convo_id'],
                    'unique_id' : unique_id,
                }))
            else:
                # It's an incoming msg!
                # First, send the msg to this user         
                await self.send(text_data=json.dumps({
                    'type' : 'p_chat_msg_f_server',
                    'msg' : event['msg'],
                    'convo_id' : event['convo_id'],
                    'date_time' : event['date_time'],
                    'unique_id' : event['unique_id'],
                }))
                # Then, send 'seen' signal to the opposite user
                channel_layer = get_channel_layer()
                send_to = await self.get_user_by_username(username=event['msg_from'])
                if send_to.channel_name is not "":
                    await channel_layer.send(send_to.channel_name, {
                        "type" : "receive.msg",
                        "signal" : "seen",
                        "convo_id" : event['convo_id'],
                    })
        else:
            # user is active but has different or no p-chat open. . . 
            # save this msg in convo_obj
            if event.get('signal', None) == None:
                date, time = event['date_time'].split(',')
                data = {
                    "msg": event['msg'], "convo_id": event['convo_id'],
                    "date": date, "time":time, "msg_from": event['msg_from'],
                }
                with transaction.atomic():
                    convo_obj = Conversations.objects.filter(id=event['convo_id']).select_for_update().first()
                    convo_obj.convo[str(convo_obj.convo_counter)] = data
                    # sort convo for ordering
                    convo_obj.convo = {k : convo_obj.convo[k] for k in sorted(convo_obj.convo)} 
                    convo_obj.convo_counter += 1
                    convo_obj.save()
                # send a notif to user that someone has sent a msg
                await self.send(text_data=json.dumps({
                    'type' : 'p_chat_notif_f_server',
                    'p_chat_notif' : render_to_string('p-chat-notif.html', {'msg_from':event['msg_from']}),
                }))
    
    async def update_p_chat(self, event=None):
        try:
            await self.send(text_data=json.dumps({
                    'type' : 'update_p_chat',
                    'unique_id' : event['convo_unique_id'],
                    'activity' : event['activity'],
            }))
        except Exception as e:
            print(str(e))