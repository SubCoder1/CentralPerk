from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from Home.models import UserNotification
from Profile.models import User

@receiver([post_save, post_delete], sender=UserNotification)
def update_notifications(sender, instance, **kwargs):
    channel_name = instance.user_to_notify.channel_name
    if channel_name is not "":
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.send)(
            channel_name, {
                "type" : "send.updated.notif",
            }
        )