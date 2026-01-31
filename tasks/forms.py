from django import forms
from django.contrib.auth.models import User
from .models import Team

# טופס רישום בסיסי
class SimpleRegistrationForm(forms.Form):
    username = forms.CharField(
        max_length=150,
        label="שם משתמש",
        widget=forms.TextInput(attrs={'placeholder': 'הזן שם משתמש', 'class': 'form-control'})
    )
    password = forms.CharField(
        label="סיסמה",
        widget=forms.PasswordInput(attrs={'placeholder': 'הזן סיסמה', 'class': 'form-control'})
    )

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("שם המשתמש כבר קיים במערכת")
        return username

# טופס הגדרת פרופיל
class ProfileSetupForm(forms.Form):
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        label="צוות",
        empty_label="בחר צוות",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    role = forms.ChoiceField(
        choices=[('employee', '👤 עובד'), ('manager', '🎖️ מנהל')],
        label="תפקיד במערכת",
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )