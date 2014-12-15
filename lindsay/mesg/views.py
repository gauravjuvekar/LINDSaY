from django.shortcuts import render , get_object_or_404
from django.http import HttpResponse

from mesg.models import Division, SubDivision
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

    messages = division.messages.filter(expires_date__gte=timezone.now())
    for subdivision in subdivisions_list:
        messages |= subdivision.messages.filter(
                expires_date__gte=timezone.now()
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

    messages = division.messages.filter(expires_date__gte=timezone.now())
    messages |= subdivision.messages.filter(expires_date__gte=timezone.now())
    messages = messages.order_by('-pub_date')

    context = {
            'subdivision': subdivision,
            'messages': messages,
    }
    return render(request, 'mesg/subdivision.html', context)

