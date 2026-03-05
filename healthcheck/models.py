from django.db import models
from django.contrib.auth.models import User

# 1. CORE COMPANY STRUCTURE 
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

    def __str__(self):
        return self.team_name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=50, default='Engineer')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

# 2. PROJECTS, REPOS & DEPENDENCIES 
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

# 3. COMMUNICATIONS & LOGS 
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

# 4. HEALTH CHECK SYSTEM 
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