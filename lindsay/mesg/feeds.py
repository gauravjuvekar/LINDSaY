from django.contrib.syndication.views import Feed
from django.core.urlresolvers import reverse
from django.contrib.syndication.views import FeedDoesNotExist
from django.shortcuts import get_object_or_404
from django.db.models import Q
from django.utils import timezone

from mesg.models import Message, SubDivision, Division

class DivisionFeed(Feed):
    def get_object(self, request, division_name):
        return get_object_or_404(
                Division,
                name=division_name,
        )

    def title(self, division):
        return "Feed for division %s" % division.name
    
    def link(self, division):
        return reverse(
                'mesg:division',
                kwargs={'division_name': division.name}
        )

    def items(self, division):
        messages = division.messages.filter(
                Q(expires_date__isnull=True)|
                Q(expires_date__gte=timezone.now())
        )

        for subdivision in division.subdivisions.all():
            messages |= subdivision.division.messages.filter(
                    Q(expires_date__isnull=True)|
                    Q(expires_date__gte=timezone.now())
            )

        messages = messages.order_by('-pub_date')
        return messages

    def item_link(self, message):
        return reverse('mesg:message', kwargs={'message_id': message.pk})


class SubDivisionFeed(Feed):
    def get_object(self, request, division_name, subdivision_name):
        return get_object_or_404(
                SubDivision,
                name=subdivision_name,
                division=get_object_or_404(Division, name=division_name),
        )

    def title(self, subdivision):
        return "Feed for division %s, subdivision %s" % (
                subdivision.division.name,
                subdivision.name,
        )
    
    def link(self, subdivision):
        return reverse(
                'mesg:subdivision', kwargs={
                    'division_name': subdivision.division.name,
                    'subdivision_name': subdivision.name,
                }
        )

    def items(self, subdivision):
        messages = subdivision.messages.filter(
                Q(expires_date__isnull=True)|
                Q(expires_date__gte=timezone.now())
        )

        messages |= subdivision.division.messages.filter(
                Q(expires_date__isnull=True)|
                Q(expires_date__gte=timezone.now())
        )

        messages = messages.order_by('-pub_date')
        return messages

    def item_link(self, message):
        return reverse('mesg:message', kwargs={'message_id': message.pk})

