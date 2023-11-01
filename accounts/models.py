from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(max_length=128, unique=True, )  # 계정명
    latitude = models.CharField(max_length=128, )  # 위도
    longitude = models.CharField(max_length=128, )  # 위도
    is_recommend = models.BooleanField(default=False)