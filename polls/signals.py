from django.db.models.signals import post_save
from .models import Poll
from django.core.cache import cache


# 当有新的poll提交时，删除index缓存
def remove_cache(sender, instance, created, **kwargs):
    cache.delete('/polls/')
    cache.delete_pattern('/polls/?*')


post_save.connect(remove_cache, sender=Poll, dispatch_uid='remove_index_cache')



