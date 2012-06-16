from django.db import models
import math
import datetime


class WhitelistedSession(models.Model):
    expiry = models.DateTimeField()
    sessionkey = models.CharField(max_length=128,  null=True, blank=True)
    ip = models.CharField(max_length=15,  null=True, blank=True)


class AccessKey(models.Model):
    key = models.CharField(max_length=10)
    accessesLeft = models.IntegerField(default=1)
