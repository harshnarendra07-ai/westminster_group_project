from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
import json
import datetime
from .forms import MeetingForm, UserUpdateForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Meeting, Message, Department, Team ,Dependency
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Team


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

    # get next 3 meetings for dashboard
    meetings = Meeting.objects.order_by('date_time')[:3]

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
    query = request.GET.get("q", "")
    teams = Team.objects.all()

    if query:
        teams = teams.filter(
            Q(team_name__icontains=query) |
            Q(department__dept_name__icontains=query) |
            Q(development_focus_area__icontains=query)
        )

    paginator = Paginator(teams, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)    

    context = {
        "teams": page_obj,
        "query": query,
    }
    return render(request, "healthcheck/team.html", context)

@login_required(login_url='login')
def department_view(request):
    departments = Department.objects.prefetch_related('team_set')

    context = {
        'departments': departments
    }

    return render(request, "healthcheck/department.html", context)

@login_required(login_url='login')
def organisation_view(request):
    departments = Department.objects.prefetch_related(
        'team_set__depends_on__upstream_team',
        'team_set__supports__downstream_team'
    )
    teams = Team.objects.select_related('department').all()
    deps = Dependency.objects.select_related('downstream_team', 'upstream_team').all()
    graph_nodes = []
    for team in teams:
        graph_nodes.append({
            "id": team.id,
            "name": team.team_name,
            "department": team.department.dept_name,
            "team_type": team.team_type,
        })

    graph_links = []
    for dep in Dependency.objects.all():
        graph_links.append({
            "source": dep.downstream_team.id,
            "target": dep.upstream_team.id,
        })

    # Serialize graph_nodes and graph_links as JSON for use in JavaScript in the template
    context = {
        'departments': departments,
        'total_departments': departments.count(),
        'total_teams': teams.count(),
        'graph_nodes': json.dumps(graph_nodes),  # Changed: serialize to JSON
        'graph_links': json.dumps(graph_links),  # Changed: serialize to JSON
    }

    return render(request, "healthcheck/organisation.html", context)

@login_required(login_url='login')
def message_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    teams = Team.objects.all()
    current_filter = request.GET.get("filter", "inbox")
    error_message = ""
    success_message = ""

    # send message
    if request.method == "POST":
        team_id = request.POST.get("team")
        subject = request.POST.get("subject")
        body = request.POST.get("body")

        if not team_id or not subject or not body:
            error_message = "Please fill in all fields"
        else:
            try:
                team = Team.objects.get(id=team_id)

                if team.manager and team.manager.user:
                    receiver_user = team.manager.user

                    Message.objects.create(
                        subject=subject,
                        body=body,
                        status="Sent",
                        sender=request.user,
                        receiver=receiver_user
                    )

                    success_message = "Message sent successfully"
                    current_filter = "sent"
                else:
                    error_message = "This team does not have a manager linked yet"

            except Team.DoesNotExist:
                error_message = "Selected team was not found"

    # show messages depending on selected box
    if current_filter == "sent":
        messages = Message.objects.filter(sender=request.user).order_by("-id")
    elif current_filter == "draft":
        messages = Message.objects.filter(sender=request.user, status="Draft").order_by("-id")
    elif current_filter == "new":
        messages = Message.objects.none()
    else:
        messages = Message.objects.filter(receiver=request.user).order_by("-id")

    context = {
        "teams": teams,
        "messages": messages,
        "current_filter": current_filter,
        "user_name": request.user.username,
        "user_email": request.user.email,
        "error_message": error_message,
        "success_message": success_message,
    }

    return render(request, "healthcheck/message.html", context)

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
    if request.method == 'POST':
        if 'update_profile' in request.POST:
            user_form = UserUpdateForm(request.POST, instance=request.user)
            password_form = PasswordChangeForm(request.user) 
            
            if user_form.is_valid():
                user_form.save()
                return redirect('profile')
                
        elif 'change_password' in request.POST:
            user_form = UserUpdateForm(instance=request.user) 
            password_form = PasswordChangeForm(request.user, request.POST)
            
            if password_form.is_valid():
                user = password_form.save()
                update_session_auth_hash(request, user)
                return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        password_form = PasswordChangeForm(request.user)

    context = {
        'user_form': user_form,
        'password_form': password_form
    }
    return render(request, "healthcheck/profile.html", context)


# view for non critical pages
@login_required(login_url='login')
def help_view(request):
    return render(request, 'healthcheck/help.html')

@login_required(login_url='login')
def support_view(request):
    return render(request, "healthcheck/support.html") 