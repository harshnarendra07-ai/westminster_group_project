from django import forms
from .models import Meeting
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User

class MeetingForm(forms.ModelForm):
    
    PLATFORM_CHOICES = [
        ('Microsoft Teams', 'Microsoft Teams'),
        ('Zoom', 'Zoom'),
        ('Google Meet', 'Google Meet'),
        ('Slack Huddle', 'Slack Huddle'),
        ('In-Person', 'In-Person'),
    ]

    platform = forms.ChoiceField(
        choices=PLATFORM_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Meeting
        fields = ['title', 'date_time', 'message', 'platform', 'team'] 
        
        widgets = {
            'date_time': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'team': forms.Select(attrs={'class': 'form-select'}),
        }
        
    def clean_date_time(self):
        date_time = self.cleaned_data.get('date_time')
        if date_time and date_time < timezone.now():
            raise ValidationError("Cannot schedule meetings in the past")
        return date_time

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'username', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }