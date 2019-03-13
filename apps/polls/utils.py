from django.utils import timezone


# 提供一个timedelta，获得下一个时间
def now_delta(timedelta):
    return timezone.now() + timedelta




