from django.contrib import admin
from django.urls import path
from healthcheck import views
from healthcheck.report_views import report_view

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Authentication Pages
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),

    # Core Pages (Team's work)
    path('', views.dashboard_view, name='dashboard'),
    path('team/', views.team_view, name='team'),
    path('departments/', views.department_view, name='department'),
    path('organisation/', views.organisation_view, name='organisation'),
    path('messages/', views.message_view, name='message'),
    path('report/', report_view, name='report'),
    path('profile/', views.profile_view, name='profile'),
    path('help/', views.help_view, name='help'),
    path('support/', views.support_view, name='support'),
    # Schedule Pages
    path('schedule/', views.schedule_view, name='schedule'),
    path('schedule/edit/<int:meeting_id>/', views.edit_meeting, name='edit_meeting'),
    path('schedule/delete/<int:meeting_id>/', views.delete_meeting, name='delete_meeting'),
]