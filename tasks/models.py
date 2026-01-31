from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

# מודל צוות
class Team(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

# מודל פרופיל
class Profile(models.Model):
    ROLE_CHOICES = [
        ('manager', 'מנהל'),
        ('employee', 'עובד'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.user.username} - {self.role} ({self.team.name})"

# מודל משימה
class Task(models.Model):
    STATUS_CHOICES = [
        ('new', 'חדש'),
        ('in_progress', 'בתהליך'),
        ('completed', 'הושלם'),
    ]

    title = models.CharField(max_length=210)
    description = models.TextField(blank=True)
    due_date = models.DateField(default=timezone.now)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title