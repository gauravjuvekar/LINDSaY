from django.db import models
from django.contrib.auth.models import User
from django.template.defaultfilters import slugify
from mptt.models import MPTTModel, TreeForeignKey


class Category(MPTTModel):
    name = models.CharField(max_length=32)
    parent = TreeForeignKey('self', null=True, blank=True, db_index=True,
                            related_name='subcategories')

    slug = models.SlugField(db_index=False)
    url = models.TextField(max_length=200, db_index=True)

    def __unicode__(self):
        return self.url

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        if self.parent:
            self.url = '%s/%s' % (self.parent.url, self.slug)
        else:
            self.url = self.slug
        MPTTModel.save(self, *args, **kwargs)


class Message(models.Model):
    message_text = models.CharField(max_length=200)
    author = models.ForeignKey(User)
    pub_date = models.DateTimeField(auto_now_add=True, db_index=True)
    expires_date = models.DateField(blank=True, null=True, db_index=True)
    category = models.ForeignKey(Category, related_name='messages',
                                 db_index=True)

    def __unicode__(self):
        return self.message_text


class UserDetails(models.Model):
    user = models.OneToOneField(User, related_name='details')
    category_choice = models.ForeignKey(Category)

    def __unicode__(self):
        return self.user.username
