from django.db import models
from django.contrib.auth.models import User as DjangoUser
from django.contrib.auth import get_user_model

class Division(models.Model):
    name = models.CharField(max_length=32)

class SubDivision(models.Model):
    name = models.CharField(max_length=32)
    division = models.ForeignKey(Division)

class Message(models.Model):
    message_text = models.CharField(max_length=200)
    # TODO ##
    author = models.ForeignKey(DjangoUser) 
    pub_date = models.DateTimeField(auto_now_add=True)

