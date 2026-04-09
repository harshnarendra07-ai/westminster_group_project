from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
import datetime
from healthcheck.models import Meeting
from .forms import MeetingForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Meeting


# Authentication views
def login_view(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        if user:
            login(request, user)
            return redirect("dashboard")

    return render(request, "healthcheck/login.html")

def signup_view(request):
    if request.method == "POST":
        user = User.objects.create_user(
            username=request.POST.get("username"),
            password=request.POST.get("password")
        )
        login(request, user)
        return redirect("dashboard")

    return render(request, "healthcheck/signup.html")

def logout_view(request):
    logout(request)
    return redirect("login")




# Views for core pages

def dashboard_view(request):
    return render(request, "healthcheck/dashboard.html")

def teams_view(request):
    return render(request, "healthcheck/team.html")

def department_view(request):
    return render(request, "healthcheck/department.html")

def organisation_view(request):
    return render(request, "healthcheck/organisation.html")

def message_view(request):
    return render(request, "healthcheck/message.html")



def report_view(request):
    return render(request, "healthcheck/report.html")


def schedule_view(request):
    if request.method == "POST":
        form = MeetingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("schedule")
    else:
        form = MeetingForm()

   
    filter_type = request.GET.get('view', 'all')
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0)
    
    if filter_type == 'today':
        end_of_day = today_start + datetime.timedelta(days=1)
        meetings = Meeting.objects.filter(date_time__range=[today_start, end_of_day]).order_by('date_time')
    elif filter_type == 'weekly':
        next_week = today_start + datetime.timedelta(days=7)
        meetings = Meeting.objects.filter(date_time__range=[today_start, next_week]).order_by('date_time')
    elif filter_type == 'monthly':
        next_month = today_start + datetime.timedelta(days=30)
        meetings = Meeting.objects.filter(date_time__range=[today_start, next_month]).order_by('date_time')
    else:
        meetings = Meeting.objects.all().order_by('date_time')

   
    calendar_days = []
    for i in range(7):
        current_day = today_start + datetime.timedelta(days=i)
        next_day = current_day + datetime.timedelta(days=1)
        
        
        day_meetings = Meeting.objects.filter(date_time__range=[current_day, next_day]).order_by('date_time')
        
        calendar_days.append({
            'date_string': current_day.strftime('%a'), # "Mon", "Tue"
            'day_number': current_day.strftime('%d/%m'), # "09/04"
            'meetings': day_meetings
        })

    context = {
        "form": form, 
        "meetings": meetings, 
        "current_filter": filter_type,
        "calendar_days": calendar_days # Pass the calendar data to HTML
    }
    return render(request, "healthcheck/schedule.html", context)
# Function to edit an existing meeting
def edit_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id)
    
    if request.method == "POST":
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            return redirect('schedule')
    else:
        
        form = MeetingForm(instance=meeting)
    
    
    return render(request, 'healthcheck/schedule.html', {'form': form, 'editing': True})


# Function to delete a meeting
def delete_meeting(request, meeting_id):
    meet = get_object_or_404(Meeting, pk=meeting_id)
    meet.delete()
    return redirect('schedule')


def profile_view(request):
    return render(request, "healthcheck/profile.html")


## view for none critical pages below

def help_view(request):
    return render(request, 'healthcheck/help.html')

def support_view(request):
    return render(request, "healthcheck/support.html")