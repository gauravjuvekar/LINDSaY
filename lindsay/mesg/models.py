from django.db import models
from django.contrib.auth.models import User
#from django.contrib.auth import get_user_model



class Category(models.Model):
    name = models.CharField(max_length=32)
    #level = models.PositiveSmallIntegerField()
    parent = models.ForeignKey(
            'self', null=True, blank=True,
            related_name='subcategories'
    )

    def __unicode__(self):
        name = []
        obj = self
        while obj != None:
            name.append(obj.name)
            obj = obj.parent

        return '/'.join(name[::-1])


class Message(models.Model):
    message_text = models.CharField(max_length=200)
    # TODO ##
    author = models.ForeignKey(User)
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_date = models.DateField(blank=True, null=True, db_index=True)
    category = models.ForeignKey(
            Category,
            related_name='messages',
            db_index=True
    )

    def __unicode__(self):
        return self.message_text



class UserDetails(models.Model):
    user = models.OneToOneField(User, related_name='details')
    category_choice = models.ForeignKey(Category)

    def __unicode__(self):
        return self.user.username
