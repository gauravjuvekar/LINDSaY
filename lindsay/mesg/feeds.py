from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.contrib.syndication.views import FeedDoesNotExist
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

from mesg.models import Category, Message
from mesg.views import get_messages


class CategoryFeed(Feed):
    def get_object(self, request, category_name):
        return get_object_or_404(Category, url=category_name)

    def title(self, category):
        return "Feed for category %s" % category.url

    def link(self, category):
        return reverse('mesg:category', kwargs={'category_name': category.url})

    def items(self, category):
        messages = get_messages(category,
                                Q(expires_date__isnull=True) |
                                Q(expires_date__gte=timezone.now())
                                ).order_by('-pub_date')
        return messages

    def item_link(self, message):
        return reverse('mesg:message', kwargs={'message_id': message.pk})

