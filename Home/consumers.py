from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.template.loader import render_to_string
from django.db.models import F, Count, Prefetch
from Profile.models import Friends
from Home.models import PostModel, PostLikes, PostComments, UserNotification
from Profile.models import Friends
from Home.tasks import send_notifications, del_notifications
import json, asyncio
from hashlib import sha256

class CentralPerkHomeConsumer(AsyncWebsocketConsumer):

    async def update_friends_list(self):
        while True:
            await asyncio.sleep(2)
            online_user_list, followers_list, following_list = await self.get_friends_list()
            await self.send(text_data=json.dumps({
                'type' : 'update_friends_list',
                'online-users-list': render_to_string("u-online.html", {'online_users':online_user_list}),
                'followers-list': render_to_string("u-followers.html", {'followers':followers_list}),
                'following-list': render_to_string("u-following.html", {'following':following_list}),
            }))

    async def connect(self):
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()
        else:
            # Accept the connection
            await self.accept()
        await self.add_channel_name_to_user(channel_name=self.channel_name)

        # Send list of followers, following & online friends
        run_task = asyncio.ensure_future(self.update_friends_list())

    async def disconnect(self, close_code):
        pass

    async def receive(self, text_data):
        if self.scope["user"].is_anonymous:
            # Reject the connection
            await self.close()
        data_from_client = json.loads(text_data)
        if data_from_client.get('task') is not None:
            # like/Dislike posts from wall-posts
            if data_from_client['task'] == 'post_like':
                post_id = data_from_client.get('post_id', None)
                response = await self.like_post_from_wall(post_id=post_id)
                await self.send(text_data=json.dumps({
                    'type' : 'likes_count',
                    'post_id' : post_id,
                    'count' : response,
                }))
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
            # Clear all notifications
            elif data_from_client['task'] == 'clear_notif_all':
                await self.del_notifications_all()
                response = await self.send_updated_notif()
                if response is not None:
                    await self.send(text_data=json.dumps({
                        'type' : 'updated_notif',
                        'notif' : render_to_string("notifications.html", {'notifications':response}),
                    }))
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
            else:
                pass
    
    @database_sync_to_async
    def add_channel_name_to_user(self, channel_name):
        user = self.scope['user']
        user.channel_name = channel_name
        user.save()
    
    @database_sync_to_async
    def get_friends_list(self):
        user = self.scope['user']
        online_users, followers, following = Friends.get_friends_list(current_user=user)
        return [online_users, followers, following]

    @database_sync_to_async
    def like_post_from_wall(self, post_id):
        user = self.scope['user']
        try:
            post = PostModel.objects.get_post(post_id=post_id)
            if post.post_like_obj.filter(user=user).exists():
                # Dislike post
                post.post_like_obj.filter(user=user).delete()
                del_notifications.delay(username=user.username, reaction="Disliked", send_to_username=post.user.username, post_id=post_id)
                post.likes_count = F('likes_count') - 1
                post.save()
                post.refresh_from_db()
            else:
                # Like post
                post.post_like_obj.add(PostLikes.objects.create(post_obj=post, user=user))
                post.likes_count = F('likes_count') + 1
                post.save()
                post.refresh_from_db()
                # Notify the user whose post is being liked
                send_notifications.delay(username=user.username, reaction="Liked", send_to_username=post.user.username, post_id=post_id)
            return post.likes_count
        except:
            pass

    @database_sync_to_async
    def post_comment_from_wall(self, post_id, comment):
        user = self.scope['user']
        if comment.isspace() or not len(comment):
            # Cannot accept blank comments or comments with only spaces or newlines
            return 'comment cannot be empty'
        try:
            post_obj = PostModel.objects.get_post(post_id=post_id)
            post_obj.post_comment_obj.add(PostComments.objects.create(user=user, post_obj=post_obj, comment=comment))
            post_obj.comment_count = F('comment_count') + 1
            post_obj.save()
            post_obj.refresh_from_db()
            # Notify the user whose post you commented on
            send_notifications.delay(username=user.username, reaction='Commented', send_to_username=post_obj.user.username, post_id=post_id)
            return post_obj.comment_count
        except:
            pass
    
    @database_sync_to_async
    def save_unsave_post(self, post_id):
        try:
            user = self.scope['user']
            post_obj = PostModel.objects.get_post(post_id=post_id)
            if user in post_obj.saved_by.all():
                post_obj.saved_by.remove(user)
                return 'unsaved'
            else:
                post_obj.saved_by.add(user)
                return 'saved'
        except:
            pass

    @database_sync_to_async
    def accept_reject_private_request(self, notif_id, option):
        user = self.scope['user']
        private_request_id = str(user.user_id) + str(notif_id) 
        private_request_hash = sha256(bytes(private_request_id, encoding='utf-8')).hexdigest()
        #print(private_request_hash)
        if UserNotification.objects.filter(private_request_id=private_request_hash).exists():
            notification = UserNotification.objects.get(private_request_id=private_request_hash)
            request_by = notification.poked_by
            if option == 'accept_request':
                Friends.follow(request_by, user)
                send_notifications.delay(username=user.username, reaction="Accept Follow Request", 
                send_to_username=request_by.username, private_request=False)
            notification.delete()
            Friends.rm_from_pending(user, request_by)

    @database_sync_to_async
    def del_notifications_all(self):
        try:
            user = self.scope['user']
            user.notifications.all().delete()
            notifications = user.notifications.all().values_list(
                'poked_by__username', 'date_time', 'reaction', 'poked_by__profile_pic', named=True)
            return notifications
        except:
            return None

    @database_sync_to_async
    def search_results(self, query=None):
        query_res = Friends.objects.filter(current_user__username__startswith=query).annotate(f_count=Count('followers'))\
            .order_by('-f_count').values_list('current_user__username', 'current_user__full_name', 'current_user__profile_pic', named=True)
        return query_res[:10]

    async def send_updated_notif(self, event=None):
        try:
            user = self.scope['user']
            notifications = user.notifications.values_list(
                    'poked_by__username', 'date_time', 'reaction', 'poked_by__profile_pic', named=True)
            await self.send(text_data=json.dumps({
                'type' : 'updated_notif',
                'notif' : render_to_string("notifications.html", {'notifications':notifications}),
            }))
        except:
            pass

    async def update_wall(self, event=None):
        try:
            user = self.scope['user']
            posts = user.connections.prefetch_related(Prefetch('saved_by')).select_related('user')
            await self.send(text_data=json.dumps({
                'type' : 'updated_wall',
                'posts' : render_to_string("wall.html", {'posts':posts}),
            }))
        except:
            pass