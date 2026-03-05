from django.contrib import admin
from .models import Department, Manager, Skill, Team, UserProfile, Dependency, Project, Repository, Meeting, Message, AuditLog, Session, HealthCard, Vote

# Registering all tables 
admin.site.register(Department)
admin.site.register(Manager)
admin.site.register(Skill)
admin.site.register(Team)
admin.site.register(UserProfile)
admin.site.register(Dependency)
admin.site.register(Project)
admin.site.register(Repository)
admin.site.register(Meeting)
admin.site.register(Message)
admin.site.register(AuditLog)
admin.site.register(Session)
admin.site.register(HealthCard)
admin.site.register(Vote)