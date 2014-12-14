from django.shortcuts import render
from django.http import HttpResponse

from mesg.models import Division, SubDivision

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
    return HttpResponse('List page for division %s' % division_name)

def subdivision(request, division_name , subdivision_name):
    return HttpResponse('List page for division %s , subdivision %s' %
            (division_name , subdivision_name))
