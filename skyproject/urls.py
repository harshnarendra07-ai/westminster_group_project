from django.contrib import admin
from django.urls import path, include
from healthcheck import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.dashboard_view, name='dashboard'), 
    path('teams/', views.teams_view, name='teams'), 
    path('schedule/', views.schedule_view, name='schedule'),    
    path('schedule/edit/<int:meeting_id>/', views.edit_meeting, name='edit_meeting'),
    path('schedule/delete/<int:meeting_id>/', views.delete_meeting, name='delete_meeting'),
    path('help/', views.help_view, name='help'),
    path('support/', views.support_view, name='support'),
    path('department/', views.department_view, name='department'),
    path('organisation/', views.organisation_view, name='organisation'),
    path('messages/', views.message_view, name='message'),
    path('reports/', views.report_view, name='report'),
    path('profile/', views.profile_view, name='profile'),
    path('logout/', views.logout_view, name='logout'),
    path('login/', views.login_view, name='login'),
]