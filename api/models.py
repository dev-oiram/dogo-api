from django.contrib.auth.models import User
from django.db import models

# Create your models here.
class Item(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

class UserKey(models.Model):
    email = models.CharField(max_length=100)
    key = models.CharField(max_length=255)

    def __str__(self):
        return self.email
