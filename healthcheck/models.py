from django.db import models
from django.contrib.auth.models import User

#  CORE COMPANY STRUCTURE 
class Department(models.Model):
    dept_name = models.CharField(max_length=255, unique=True)
    dept_head = models.CharField(max_length=255) 

    def __str__(self):
        return self.dept_name

class Manager(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username

class Skill(models.Model):
    skill_name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.skill_name

class Team(models.Model):
    team_name = models.CharField(max_length=255, unique=True)
    development_focus_area = models.CharField(max_length=255)
    wiki_url = models.URLField(blank=True, null=True)
    team_type = models.CharField(max_length=100)
    owned_software = models.CharField(max_length=255, blank=True, null=True)
    slack_channel = models.CharField(max_length=100)
    methodology = models.CharField(max_length=100)
    search_keywords = models.CharField(max_length=255, blank=True, null=True)
    
    department = models.ForeignKey(Department, on_delete=models.RESTRICT)
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True, blank=True)
    skills = models.ManyToManyField(Skill, blank=True)

    downstream_dependency = models.CharField(max_length=255, blank=True, null=True)
    dependency_type = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return self.team_name
    
class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default='Engineer')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}" 

# PROJECTS, REPOS & DEPENDENCIES 
class Dependency(models.Model):
    downstream_team = models.ForeignKey(Team, related_name='depends_on', on_delete=models.CASCADE)
    upstream_team = models.ForeignKey(Team, related_name='supports', on_delete=models.CASCADE)

class Project(models.Model):
    jira_project_name = models.CharField(max_length=255)
    jira_board_url = models.URLField()
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

class Repository(models.Model):
    repo_url = models.URLField(unique=True)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

#  COMMUNICATIONS & LOGS 
class Meeting(models.Model):
    title = models.CharField(max_length=255)
    date_time = models.DateTimeField()
    message = models.TextField(blank=True, null=True)
    platform = models.CharField(max_length=100)
    organiser = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)

class Message(models.Model):
    subject = models.CharField(max_length=255)
    body = models.TextField()
    status = models.CharField(max_length=50, default='Draft')
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)

class AuditLog(models.Model):
    action = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

#  HEALTH CHECK SYSTEM 
class Session(models.Model):
    session_name = models.CharField(max_length=100)
    start_date = models.DateField()
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.session_name

class HealthCard(models.Model):
    card_name = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.card_name

class Vote(models.Model):
    TRAFFIC_LIGHT_CHOICES = [('Green', 'Green'), ('Amber', 'Amber'), ('Red', 'Red')]
    TREND_CHOICES = [('Better', 'Getting Better'), ('Same', 'Staying the Same'), ('Worse', 'Getting Worse')]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    session = models.ForeignKey(Session, on_delete=models.CASCADE)
    card = models.ForeignKey(HealthCard, on_delete=models.CASCADE)
    traffic_light = models.CharField(max_length=10, choices=TRAFFIC_LIGHT_CHOICES)
    trend = models.CharField(max_length=10, choices=TREND_CHOICES)
    
    class Meta:
        unique_together = ('user', 'session', 'card')

## report models
# stores the different categories a report can be like "Performance Report" or "Team Summary"
class ReportType(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


# main model for a generated report, stores everything about it at the time it was created
class Report(models.Model):

    # defines what level the report covers
    SCOPE_TYPES = [
        ("user", "Individual User"),
        ("manager", "Manager"),
        ("team", "Team"),
        ("department", "Department"),
    ]

    title = models.CharField(max_length=200)
    report_type = models.ForeignKey(ReportType, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports")
    scope_type = models.CharField(max_length=30, choices=SCOPE_TYPES, default="team")

    # only one of these will be set depending on which scope was picked
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports")
    manager = models.ForeignKey(Manager, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports")
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports")
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports")
    session = models.ForeignKey(Session, on_delete=models.SET_NULL, null=True, blank=True, related_name="reports")

    # tracks which data the user wanted included
    include_votes = models.BooleanField(default=True)
    include_messages = models.BooleanField(default=False)
    include_meetings = models.BooleanField(default=False)

    # snapshot of the counts at the time the report was generated
    total_votes = models.IntegerField(default=0)
    total_messages = models.IntegerField(default=0)
    total_meetings = models.IntegerField(default=0)

    # set automatically when the report is saved
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title