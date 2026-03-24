from django.shortcuts import render, redirect
from .forms import MeetingForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User

## basic login, signup and logout, build upon it
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



## each page can have its own dedicated view page if your area becomes too bloated, please refer to report_views to see how if needed.

def dashboard_view(request):
    return render(request, "healthcheck/dashboard.html")

def team_view(request):
    return render(request, "healthcheck/team.html")

def department_view(request):
    return render(request, "healthcheck/department.html")

def organisation_view(request):
    return render(request, "healthcheck/organisation.html")

def message_view(request):
    return render(request, "healthcheck/message.html")

def schedule_view(request):
    if request.method == "POST":
        form = MeetingForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("schedule")
    else:
        form = MeetingForm()

    context = {"form": form}
    return render(request, "healthcheck/schedule.html", context)

def profile_view(request):
    return render(request, "healthcheck/profile.html")


## none critical pages below

def help_view(request):
    return render(request, "healthcheck/help.html")

def support_view(request):
    return render(request, "healthcheck/support.html")