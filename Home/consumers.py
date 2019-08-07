from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.db.models import F
from Profile.models import User
from Home.models import PostModel, PostLikes
from Home.tasks import send_notifications, del_notifications
import json

class CentralPerkHomeConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        await self.accept()

    async def disconnect(self, close_code):
        pass
    
    async def receive(self, text_data):
        data_from_client = json.loads(text_data)
        if data_from_client.get('task') is not None:
            if data_from_client['task'] == 'post_like':
                post_id = data_from_client['post_id']
                response = await self.like_post_from_wall(post_id=post_id)
                await self.send(text_data=json.dumps({
                    'type' : 'likes_count',
                    'post_id' : post_id,
                    'count' : response,
                }))
    
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

    
