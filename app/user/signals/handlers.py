from django.dispatch import receiver
from user.signals import follow_user
from core.models import Following
  

@receiver(follow_user)
def add_to_following_list(sender, **kwargs):
    """Whenever a user follows others this function will triggered to
    add it to the following list"""
    Following.objects.create(
        user=kwargs['data']['user'],
        following_id=kwargs['data']['following_id'],
        following_name=kwargs['data']['following_name']
    )
