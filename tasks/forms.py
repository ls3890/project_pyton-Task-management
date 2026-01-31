from django import forms
from .models import Team

class SimpleRegistrationForm(forms.Form):
    username = forms.CharField(max_length=150, label="שם משתמש")
    password = forms.CharField(widget=forms.PasswordInput, label="סיסמה")

class ProfileSetupForm(forms.Form):
    team = forms.ModelChoiceField(
        queryset=Team.objects.all(),
        label="צוות",
        empty_label="בחר צוות"
    )