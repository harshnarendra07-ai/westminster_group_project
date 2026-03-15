from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import MeetingForm

def schedule_view(request):
    if request.method == "POST":
        form = MeetingForm(request.POST) 
        if form.is_valid():
            form.save() 
            return redirect('schedule') 
    else:
        form = MeetingForm()
    
    context = {'form': form}
    return render(request, 'healthcheck/schedule.html', context)