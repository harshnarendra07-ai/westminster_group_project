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

#------------------------------
# Shedule view start here;
# This view handles the meeting scheduling, displaying meetings based on the selected filter (today, weekly, monthly), and rendering the schedule page with the appropriate context.
def schedule_view(request):
    if request.method == "POST":
        form = MeetingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("schedule")
    else:
        form = MeetingForm()

    filter_type = request.GET.get('view', 'weekly') # Default to weekly
    now = timezone.now()
    today_start = now.replace(hour=0, minute=0, second=0)
    
    
    if filter_type == 'today':
        days_to_show = 1
        end_date = today_start + datetime.timedelta(days=1)
    elif filter_type == 'monthly':
        days_to_show = 30
        end_date = today_start + datetime.timedelta(days=30)
    else: 
        days_to_show = 7
        end_date = today_start + datetime.timedelta(days=7)

    
    meetings = Meeting.objects.filter(date_time__range=[today_start, end_date]).order_by('date_time')

    
    calendar_days = []
    for i in range(days_to_show): 
        current_day = today_start + datetime.timedelta(days=i)
        next_day = current_day + datetime.timedelta(days=1)
        
        day_meetings = Meeting.objects.filter(date_time__range=[current_day, next_day]).order_by('date_time')
        
        calendar_days.append({
            'date_string': current_day.strftime('%a'),
            'day_number': current_day.strftime('%d/%m'),
            'meetings': day_meetings
        })

    context = {
        "form": form, 
        "meetings": meetings, 
        "current_filter": filter_type,
        "calendar_days": calendar_days
    }
    return render(request, "healthcheck/schedule.html", context)

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


def delete_meeting(request, meeting_id):
    meet = get_object_or_404(Meeting, pk=meeting_id)
    meet.delete()
    return redirect('schedule')
#the schedule view ends here;
#------------------------------


def profile_view(request):
    return render(request, "healthcheck/profile.html")


## view for none critical pages below

def help_view(request):
    return render(request, 'healthcheck/help.html')

def support_view(request):
    return render(request, "healthcheck/support.html")