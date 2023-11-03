from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    username = models.CharField(max_length=128, unique=True, )  # 계정명
    latitude = models.CharField(max_length=128, )  # 위도
    longitude = models.CharField(max_length=128, )  # 위도
    is_recommend = models.BooleanField(default=False)


class Location(models.Model):
    dosi = models.CharField(max_length=100)
    sgg = models.CharField(max_length=100)
    longitude = models.CharField(max_length=100)
    latitude = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    
    def __str__(self):
        return f"{self.do_si}, {self.sgg}: [{self.longitude}, {self.latitude}]"
