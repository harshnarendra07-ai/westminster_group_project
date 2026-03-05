from django.shortcuts import render
from django.http import HttpResponse

def schedule_view(request):
    return render(request, 'healthcheck/base.html')
