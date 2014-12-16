from django.shortcuts import render , get_object_or_404
from django.http import HttpResponse
from django.db.models import Q

from mesg.models import Division, SubDivision, Message
from django.utils import timezone


def index(request):
    divisions_list = [
            (division, division.subdivisions.all()) for division in
            Division.objects.all()
    ]
    context = {
            'divisions_list': divisions_list,
    }
    return render(request, 'mesg/index.html', context)


def division(request, division_name):
    division = get_object_or_404(Division, name=division_name)
    subdivisions_list = division.subdivisions.all()

    # Includes messages from the current division and
    # all its subdivisions
    messages = division.messages.filter(
            Q(expires_date__isnull=True) |
            Q(expires_date__gte=timezone.now())
    )
    for subdivision in subdivisions_list:
        messages |= subdivision.messages.filter(
                Q(expires_date__isnull=True) |
                Q(expires_date__gte=timezone.now())
        )
    messages = messages.order_by('-pub_date')

    context = {
            'division': division,
            'subdivisions_list': subdivisions_list,
            'messages': messages,
    }
    return render(request, 'mesg/division.html', context)


def subdivision(request, division_name , subdivision_name):
    division = get_object_or_404(Division, name=division_name)
    subdivision = get_object_or_404(
            SubDivision,
            name=subdivision_name,
            division=division
    )

    # Includes messages from the current subdivision and
    # its parent division (excluding siblings)
    messages = division.messages.filter(
            Q(expires_date__isnull=True) |
            Q(expires_date__gte=timezone.now())
    )
    messages |= subdivision.messages.filter(
            Q(expires_date__isnull=True) |
            Q(expires_date__gte=timezone.now())
    )
    messages = messages.order_by('-pub_date')

    context = {
            'subdivision': subdivision,
            'messages': messages,
    }
    return render(request, 'mesg/subdivision.html', context)


def message(request, message_id):
    message = get_object_or_404(Message, pk=message_id)

    division = subdivision = None

    if (message.content_type.model == 'subdivision'):
        subdivision = message.content_object
        division = subdivision.division
    else:
        division = message.content_object

    context = {
            'message': message,
            'division': division,
            'subdivision': subdivision,
    }
    return render(request, 'mesg/message.html', context)

