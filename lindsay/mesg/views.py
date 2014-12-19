from django.shortcuts import render , get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.core.urlresolvers import reverse

from django.db.models import Q

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from mesg.models import Division, SubDivision, Message
from django.utils import timezone

from mesg.forms import CreateMessageForm
import re

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



def user_login(request):
    context = RequestContext(request)

    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            return HttpResponseRedirect(reverse('mesg:index'))
        else:
            return HttpResponse("Invalid login details")
    else:
        return render_to_response('mesg/login.html', {}, context)


# TODO: circular links from login to logout page
@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('mesg:index'))


@login_required
def create_message(request):
    if request.method == 'POST':
        form = CreateMessageForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            # the category names from form select are '(sub)?division_(pk)'
            # as both divisions and subdivisions can be selected in a single
            # dropdown list though being different models

            division = re.match(r'^division_(?P<pk>\d+)$', data['category'])
            if division:
                category_object = Division.objects.get(
                        pk=int(division.group('pk'))
                )
            else:
                subdivision = re.match(
                    r'^subdivision_(?P<pk>\d+)$',
                    data['category'],
                )
                category_object = SubDivision.objects.get(
                        pk=int(subdivision.group('pk'))
                )
            message = Message(
                    message_text=data['message_text'],
                    author=request.user,
                    expires_date=data['expires_date'],
                    content_object=category_object,
            )
            message.save()

            return HttpResponseRedirect(reverse(
                        'mesg:message',
                        kwargs={'message_id': message.pk},
                    )
            )
    else:
        form = CreateMessageForm()
    return render(request, 'mesg/create_message.html', {'form': form})
