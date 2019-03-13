from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Poll
from django.core.cache import cache


# 删除index缓存
@receiver(post_save, sender=Poll, weak=False)
def remove_cache(sender, instance, created, **kwargs):
    cache.delete('/polls/')
    cache.delete_pattern('/polls/?*')


# 当有新的poll提交时，删除缓存
# post_save.connect(remove_cache, sender=Poll, dispatch_uid='save_remove_index', weak=False)
# post_delete.connect(remove_cache, sender=Poll, dispatch_uid='delete_remove_index_cache', weak=False)



