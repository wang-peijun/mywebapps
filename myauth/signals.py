from django.contrib.auth.signals import user_logged_in
from django.db.models.signals import post_save
from .models import User
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from polls.models import Poll


# 当用户第一次注册时，添加poll的后台管理权限, created表示save操作是不是第一次创建，还是更新
def do_stuff(sender, instance, created, **kwargs):
    if created:
        content_type = ContentType.objects.get_for_model(Poll)
        permissions = Permission.objects.filter(
            content_type=content_type
        )
        instance.user_permissions.add(*permissions)
        instance.save()


# user_logged_in.connect(do_stuff)
post_save.connect(do_stuff, sender=User, dispatch_uid='user_post_save')




