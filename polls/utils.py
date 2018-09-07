from django.utils import timezone


def now_delta(timedelta):
    return timezone.now() + timedelta




