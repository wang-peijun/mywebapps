from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models import Model, BooleanField

# Create your models here.


class User(AbstractUser):
    is_staff = BooleanField(default=True, blank=True)

