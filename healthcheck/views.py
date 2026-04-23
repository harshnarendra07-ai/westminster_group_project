from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
import datetime
from .forms import MeetingForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
<<<<<<< Updated upstream
from .models import Meeting, Department, Team
=======
from .models import Meeting, Department, Team, Message, Dependency, UserProfile
>>>>>>> Stashed changes
from django.contrib.auth.decorators import login_required


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
        
        username_input = request.POST.get("username")
        password_input = request.POST.get("password")
        confirm_input = request.POST.get("confirm_password")

        
        if password_input != confirm_input:
            return render(request, "healthcheck/signup.html", {"error": "Passwords do not match. Please try again."})
        try:
            user = User.objects.create_user(
                username=username_input,
                password=password_input
            )
            login(request, user)
            return redirect("dashboard")
    
        except Exception:        
            return render(request, "healthcheck/signup.html", {"error": "That username is already taken."})
    return render(request, "healthcheck/signup.html")


def logout_view(request):
    logout(request)
    return redirect("login")


# Views for core pages
@login_required(login_url='login')
def dashboard_view(request):
    # get all departments and teams
    departments = Department.objects.all()
    teams = Team.objects.all()

    labels = []
    values = []

    # count teams in each department
    for dept in departments:
        labels.append(dept.dept_name)
        team_count = Team.objects.filter(department=dept).count()
        values.append(team_count)

    # get next 3 meetings for the user's specific team
    if hasattr(request.user, 'userprofile') and request.user.userprofile.team:
        meetings = Meeting.objects.filter(team=request.user.userprofile.team).order_by('date_time')[:3]
    else:
        meetings = Meeting.objects.none()

    # send data to dashboard page
    context = {
        "labels": labels,
        "values": values,
        "total_departments": departments.count(),
        "total_teams": teams.count(),
        "meetings": meetings,
    }

    return render(request, "healthcheck/dashboard.html", context)

@login_required(login_url='login')
def team_view(request):
    return render(request, "healthcheck/team.html")

@login_required(login_url='login')
def department_view(request):
    return render(request, "healthcheck/department.html")

@login_required(login_url='login')
def organisation_view(request):
    return render(request, "healthcheck/organisation.html")

@login_required(login_url='login')
def message_view(request):
    return render(request, "healthcheck/message.html")

@login_required(login_url='login')
def report_view(request):
    return render(request, "healthcheck/report.html")

#------------------------------
# Shedule view start here;
# This view handles the meeting scheduling, displaying meetings based on the selected filter (today, weekly, monthly), and rendering the schedule page with the appropriate context.
@login_required(login_url='login') 
def schedule_view(request):
    if request.method == "POST":
        form = MeetingForm(request.POST)
        if form.is_valid():
            new_meeting = form.save(commit=False)          
            new_meeting.organiser = request.user 
            new_meeting.save()
            if not meeting_to_edit:
                team_members = UserProfile.objects.filter(team=new_meeting.team)
                
                formatted_date = new_meeting.date_time.strftime('%d/%m/%Y %H:%M')
                
                for profile in team_members:
                    if profile.user != request.user:
                        Message.objects.create(
                            subject=f"New Meeting Scheduled: {new_meeting.title}",
                            body=f"You have been scheduled for a new meeting by {request.user.username}.\n\n"
                                 f"Date & Time: {formatted_date}\n"
                                 f"Platform: {new_meeting.platform}\n"
                                 f"Details: {new_meeting.message}",
                            status="Sent",
                            sender=request.user,
                            receiver=profile.user
                        )
            return redirect("schedule")
    else:
        form = MeetingForm()


    filter_type = request.GET.get('view', 'weekly') 
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

    
   
    search_text = request.GET.get('search_query', '')

    meetings = Meeting.objects.filter(date_time__range=[today_start, end_date])
    
   
    if search_text:
        meetings = meetings.filter(title__icontains=search_text)
        
    meetings = meetings.order_by('date_time')

    
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


# Function to edit an existing meeting or delete a meeting. Both functions ensure that only the organiser of the meeting can perform these actions, and they redirect back to the schedule view after completion.

@login_required(login_url='login')
def edit_meeting(request, meeting_id):
    meeting = get_object_or_404(Meeting, pk=meeting_id, organiser=request.user)

    if request.method == "POST":
        form = MeetingForm(request.POST, instance=meeting)
        if form.is_valid():
            form.save()
            return redirect('schedule')
    else:
        form = MeetingForm(instance=meeting)
    return render(request, 'healthcheck/edit_schedule.html', {'form': form})

@login_required(login_url='login')
def delete_meeting(request, meeting_id):
    meet = get_object_or_404(Meeting, pk=meeting_id, organiser=request.user)
    meet.delete()
    return redirect('schedule')

#the schedule view ends here;
#------------------------------

@login_required(login_url='login')
def profile_view(request):
    return render(request, "healthcheck/profile.html")


# view for non critical pages
@login_required(login_url='login')
def help_view(request):
    return render(request, 'healthcheck/help.html')

@login_required(login_url='login')
def support_view(request):
    return render(request, "healthcheck/support.html") 