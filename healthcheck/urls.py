from django.urls import path
from django.views.generic import RedirectView
from . import views
from .report_views import report_view

urlpatterns = [
    path('', RedirectView.as_view(pattern_name='login', permanent=False), name='root'),
    path('', views.dashboard_view, name='dashboard'),

    path('team/', views.team_view, name='team'),
    path('departments/', views.department_view, name='department'),
    path('organisation/', views.organisation_view, name='organisation'),
    path('messages/', views.message_view, name='message'),
    path('schedule/', views.schedule_view, name='schedule'),
    path('report/', report_view, name='report'),
    path('profile/', views.profile_view, name='profile'),

    
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),

   
    path('help/', views.help_view, name='help'),
    path('support/', views.support_view, name='support'),
]

