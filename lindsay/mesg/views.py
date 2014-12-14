from django.shortcuts import render
from django.http import HttpResponse


def index(request):
    return HttpResponse('Hello World')

def division(request, division_name):
    return HttpResponse('List page for division %s' % division_name)

def subdivision(request, division_name , subdivision_name):
    return HttpResponse('List page for division %s , subdivision %s' %
            (division_name , subdivision_name))
