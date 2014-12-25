from django.shortcuts import render , get_object_or_404
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
from django.http import HttpResponseBadRequest
from django.core.urlresolvers import reverse

from django.db.models import Q

from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.template import RequestContext

from mesg.models import Category, Message, UserDetails
from django.utils import timezone

from mesg.forms import CreateMessageForm, UserConfigForm

def index(request):
    category_list = [
            (category, category.subcategories.all()) for category in
            Category.objects.filter(parent__isnull=True)
    ]
    context = {
            'divisions_list': category_list,
    }
    return render(request, 'mesg/index.html', context)


def get_messages(category, query):
    def get_child_messages(category, query):
        messages = category.messages.filter(query)
        for child in category.subcategories.all():
            messages |= get_child_messages(child, query)
        return messages
    def get_parent_messages(category, query):
        messages = Category.objects.none()
        while category != None:
            messages |= category.messages.filter(query)
            category = category.parent
        return messages
    messages = get_parent_messages(category,query)
    messages |= get_child_messages(category,query)
    return messages


def division(request, division_name):
    division = get_object_or_404(Category, name=division_name, parent=None)
    subdivisions_list = division.subcategories.all()

    messages = get_messages(
            division,
            Q(expires_date__isnull=True)|Q(expires_date__gte=timezone.now())
    ).order_by('-pub_date')

    context = {
            'division': division,
            'subdivisions_list': subdivisions_list,
            'messages': messages,
    }
    return render(request, 'mesg/division.html', context)



def subdivision(request, division_name , subdivision_name):
    division = get_object_or_404(Category, name=division_name, parent=None)
    subdivision = get_object_or_404(
            Category,
            name=subdivision_name,
            parent=division
    )

    messages = get_messages(
            subdivision,
            Q(expires_date__isnull=True)|Q(expires_date__gte=timezone.now())
    ).order_by('-pub_date')

    context = {
            'division': division,
            'subdivision': subdivision,
            'messages': messages,
    }
    return render(request, 'mesg/subdivision.html', context)



def message(request, message_id):
    message = get_object_or_404(Message, pk=message_id)

    division = subdivision = None
    category = message.category
    if category.parent != None:
        subdivision = message.category
        division = category.parent
    else:
        division = category

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

        next_url=request.POST['next']

        user = authenticate(username=username, password=password)
        if user:
            login(request, user)
            if next_url:
                return HttpResponseRedirect(next_url)
            else:
                return HttpResponseRedirect(reverse('mesg:index'))
        else:
            state = "Invalid credentials"
            # NOTE: not redirecting from a POST
            return render_to_response(
                    'mesg/login.html',
                    {'state': state, 'next': next_url},
                    context,
            )
    else:
        return render_to_response('mesg/login.html', {}, context)


def user_logout(request):
    logout(request)
    next_url = request.GET.get('next', None)
    if next_url:
        return HttpResponseRedirect(next_url)
    else:
        return HttpResponseRedirect(reverse('mesg:index'))


@login_required
def create_message(request):
    if request.method == 'POST':
        form = CreateMessageForm(request.POST)

        if form.is_valid():
            data = form.cleaned_data
            try:
                category = Category.objects.get(pk=data['category'])
            except ObjectDoesNotExist:
                return HttpResponseBadRequest

            message = Message(
                    message_text=data['message_text'],
                    author=request.user,
                    category=category,
                    expires_date=data['expires_date'],
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


@login_required
def expire_message(request, message_id):
    message = get_object_or_404(Message, pk=message_id)

    if message.expires_date == None:
        message.expires_date = timezone.now()
        message.save()
        return HttpResponseRedirect(reverse(
                'mesg:message',
                kwargs={'message_id': message.id}
            )
        )
    else:
        return HttpResponseBadRequest

@login_required
def user_config(request):
    if request.method == 'POST':
        form = UserConfigForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            try:
                category = Category.objects.get(pk=data['category'])
            except ObjectDoesNotExist:
                return HttpResponseBadRequest

        preferences, created = UserDetails.objects.update_or_create(
                user=request.user,
                defaults={'category_choice': category},
        )

        preferences.save()

        return HttpResponseRedirect(reverse('mesg:index'))
    else:
        # Set an initial value of category selection if already set
        try:
            initial_category = request.user.details.category_choice
        except UserDetails.DoesNotExist:
            initial_category = None

        form = UserConfigForm(initial={'category': initial_category})

    return render(request, 'mesg/user_config.html', {'form': form})
