from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.contrib.syndication.views import FeedDoesNotExist
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

from mesg.models import Category, Message


from mesg.views import get_messages

class DivisionFeed(Feed):
    def get_object(self, request, division_name):
        return get_object_or_404(
                Category,
                name=division_name,
                parent=None
        )

    def title(self, division):
        return "Feed for division %s" % division.name
    
    def link(self, division):
        return reverse(
                'mesg:division',
                kwargs={'division_name': division.name}
        )

    def items(self, division):
        messages = get_messages(
                division,
                Q(expires_date__isnull=True)|Q(expires_date__gte=timezone.now())       
        ).order_by('-pub_date')
        return messages

    def item_link(self, message):
        return reverse('mesg:message', kwargs={'message_id': message.pk})


class SubDivisionFeed(Feed):
    def get_object(self, request, division_name, subdivision_name):
        return get_object_or_404(
                Category,
                name=subdivision_name,
                division=get_object_or_404(
                    Category,
                    name=division_name,
                    parent=None
                ),
        )

    def title(self, subdivision):
        return "Feed for division %s, subdivision %s" % (
                subdivision.parent.name,
                subdivision.name,
        )
    
    def link(self, subdivision):
        return reverse(
                'mesg:subdivision', kwargs={
                    'division_name': subdivision.parent.name,
                    'subdivision_name': subdivision.name,
                }
        )

    def items(self, subdivision):
        messages = get_messages(
                division,
                Q(expires_date__isnull=True)|Q(expires_date__gte=timezone.now())       
        ).order_by('-pub_date')
        return messages

    def item_link(self, message):
        return reverse('mesg:message', kwargs={'message_id': message.pk})

