from urllib import request

from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
import datetime
from .forms import MeetingForm, UserUpdateForm
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Meeting, Department, Team, Message, Dependency, UserProfile, AuditLog
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages


# Authentication views


def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

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

def help_view(request):
    return render(request, "healthcheck/help.html")


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
    query = request.GET.get("q", "")

    teams_qs = Team.objects.select_related(
        'department',
        'manager__user'
    ).prefetch_related(
        'skills'
    ).all()

    if query:
        teams_qs = teams_qs.filter(
            Q(team_name__icontains=query) |
            Q(department__dept_name__icontains=query) |
            Q(development_focus_area__icontains=query) |
            Q(manager__user__username__icontains=query) |
            Q(manager__user__first_name__icontains=query) |
            Q(manager__user__last_name__icontains=query)
        ).distinct()

    paginator = Paginator(teams_qs, 8)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    users = User.objects.exclude(id=request.user.id)
    all_teams = Team.objects.select_related('department', 'manager__user').all()

    context = {
        "teams": page_obj,
        "query": query,
        "users": users,
        "all_teams": all_teams,
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
        'team_set__supports__downstream_team',
        'team_set__project_set',
         'team_set__repository_set'
    )
    teams = Team.objects.select_related('department').all()
    team_types = Team.objects.values_list('team_type', flat=True).distinct().order_by('team_type')
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

    context = {
        'departments': departments,
        'team_types': team_types,
        'total_departments': departments.count(),
        'total_teams': teams.count(),
        'graph_nodes': graph_nodes,
        'graph_links': graph_links,
    }

    return render(request, "healthcheck/organisation.html", context)

@login_required(login_url='login')
def message_view(request):
    if not request.user.is_authenticated:
        return redirect("login")

    users = User.objects.exclude(id=request.user.id)
    current_filter = request.GET.get("filter", "inbox")
    error_message = ""
    success_message = request.GET.get("success", "")

    if request.method == "POST":
        action_type = request.POST.get("action_type")


        if action_type == "delete":
            message_id = request.POST.get("message_id")
            try:
                # We use Q to ensure the user is either the sender OR receiver 
                # before allowing deletion, for security.
                msg_to_delete = Message.objects.get(
                    Q(sender=request.user) | Q(receiver=request.user), 
                    id=message_id
                )
                msg_to_delete.delete()
                
                # Redirect back to the same tab they were just on with a success message
                return redirect(f"/messages?filter={current_filter}&success=Message deleted successfully")
                
            except Message.DoesNotExist:
                error_message = "Message not found or you do not have permission to delete it."
                
        else:
            receiver_id = request.POST.get("receiver")
            subject = request.POST.get("subject")
            body = request.POST.get("body")

            if not receiver_id or not subject or not body:
                error_message = "Please fill in all fields"
                current_filter = "new"
            else:
                try:
                    receiver_user = User.objects.get(id=receiver_id)

                    if action_type == "draft":
                        status_value = "Draft"
                        success_text = "Draft saved successfully"
                        redirect_filter = "draft"
                    else:
                        status_value = "Sent"
                        success_text = "Message sent successfully"
                        redirect_filter = "sent"

                    Message.objects.create(
                        subject=subject,
                        body=body,
                        status=status_value,
                        sender=request.user,
                        receiver=receiver_user
                    )

                    return redirect(f"/messages?filter={redirect_filter}&success={success_text}")

                except User.DoesNotExist:
                    error_message = "Selected user was not found"
                    current_filter = "new"

    if current_filter == "sent":
        messages = Message.objects.filter(sender=request.user, status="Sent").order_by("-id")
    elif current_filter == "draft":
        messages = Message.objects.filter(sender=request.user, status="Draft").order_by("-id")
    elif current_filter == "new":
        messages = Message.objects.none()
    else:
        messages = Message.objects.filter(receiver=request.user).order_by("-id")

    context = {
        "users": users,
        "messages": messages,
        "current_filter": current_filter,
        "error_message": error_message,
        "success_message": success_message,
    }

    return render(request, "healthcheck/message.html", context)

#------------------------------
# Shedule view start here;
# This view handles the meeting scheduling, displaying meetings based on the selected filter (today, weekly, monthly), and rendering the schedule page with the appropriate context.
@login_required(login_url='login') 
def schedule_view(request):
    # 1. Check if the user clicked "Edit" (we will pass 'edit=ID' in the URL)
    edit_id = request.GET.get('edit')
    meeting_to_edit = None
    
    if edit_id:
        # Grab the specific meeting they want to edit
        meeting_to_edit = get_object_or_404(Meeting, pk=edit_id, organiser=request.user)

    # 2. Handle the Form Submission (when they click Save/Schedule)
    if request.method == "POST":
        if meeting_to_edit:
            # We are saving an EDITED meeting
            form = MeetingForm(request.POST, instance=meeting_to_edit)
        else:
            form = MeetingForm(request.POST)
            
        if form.is_valid():
            new_meeting = form.save(commit=False)          
            new_meeting.organiser = request.user 
            new_meeting.save()

            AuditLog.objects.create(user=request.user, action="Downloaded a secure Engineering CSV Report")
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
        if meeting_to_edit:
            form = MeetingForm(instance=meeting_to_edit)
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
        "calendar_days": calendar_days,
        "editing": True if meeting_to_edit else False,
        "edit_id": edit_id
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
            AuditLog.objects.create(user=request.user, action="Downloaded a secure Engineering CSV Report")
            return redirect('schedule')
    else:
        form = MeetingForm(instance=meeting)
    return render(request, 'healthcheck/edit_schedule.html', {'form': form})

@login_required(login_url='login')
def delete_meeting(request, meeting_id):
    meet = get_object_or_404(Meeting, pk=meeting_id, organiser=request.user)
    meet.delete()
    AuditLog.objects.create(user=request.user, action="Downloaded a secure Engineering CSV Report")
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
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        section = request.POST.get("section")
        issue_type = request.POST.get("issue_type")
        message_text = request.POST.get("message")

        if name and email and section and issue_type and message_text:
            messages.success(request, "Your support request has been submitted successfully.")
            return redirect("support")
        else:
            messages.error(request, "Please fill in all fields.")

    return render(request, "healthcheck/support.html") 
