from django.db import models
from django.contrib.auth.models import User 
from django.contrib.auth import get_user_model

from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Message(models.Model):
    message_text = models.CharField(max_length=200)
    # TODO ##
    author = models.ForeignKey(User) 

    pub_date = models.DateTimeField(auto_now_add=True)
    expires_date = models.DateField(blank=True, null=True)

    # ForeignKey to either Division or SubDivision
    limit = models.Q(app_label='mesg', model='Division')
    limit |= models.Q(app_label='mesg', model='SubDivision')
    content_type = models.ForeignKey(ContentType, limit_choices_to=limit)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __unicode__(self):
        return self.message_text


class Division(models.Model):
    name = models.CharField(max_length=32)
    messages = GenericRelation(Message)

    def __unicode__(self):
        return self.name


class SubDivision(models.Model):
    name = models.CharField(max_length=32)
    division = models.ForeignKey(Division, related_name='subdivisions')
    messages = GenericRelation(Message)

    def __unicode__(self):
        return self.name + ' Parent: ' + self.division.name

