from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.utils import timezone
from .models import Profile, Team, Task
from .forms import SimpleRegistrationForm  # וודא שהטופס הזה קיים ב-forms.py


# --- 1. הרשמה (Registration) ---
def register(request):
    if request.method == 'POST':
        form = SimpleRegistrationForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            try:
                # יצירת המשתמש
                user = User.objects.create_user(username=username, password=password)
                # יצירת פרופיל ריק (הצוות והתפקיד יוגדרו ב-Setup)
                Profile.objects.get_or_create(user=user)

                # חיבור המשתמש ומעבר לדף הגדרות
                login(request, user)
                return redirect('setup_profile')
            except IntegrityError:
                form.add_error('username', 'שם המשתמש כבר תפוס, נסה שם אחר.')
    else:
        form = SimpleRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})


# --- 2. הגדרת פרופיל (Setup Profile) ---
@login_required
def setup_profile(request):
    profile, created = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        team_id = request.POST.get('team')
        role_selected = request.POST.get('role')

        if team_id and role_selected:
            profile.team = get_object_or_404(Team, id=team_id)
            profile.role = role_selected
            profile.save()
            return redirect('task_list')

    teams = Team.objects.all()
    # אם אין צוותים במערכת, ניצור אחד כדי שהדף לא יהיה ריק
    if not teams.exists():
        Team.objects.create(name="צוות כללי")
        teams = Team.objects.all()

    return render(request, 'registration/setup_profile.html', {
        'teams': teams,
        'profile': profile
    })


# --- 3. רשימת משימות (Task List) ---
@login_required
def task_list(request):
    profile = get_object_or_404(Profile, user=request.user)

    # אם המשתמש עוד לא הגדיר צוות, נשלח אותו ל-Setup
    if not profile.team:
        return redirect('setup_profile')

    # סינון בסיסי לפי הצוות של המשתמש
    tasks = Task.objects.filter(team=profile.team).order_by('due_date')

    # קליטת סינונים מה-URL (עבור ה-HTML המעוצב שלך)
    selected_status = request.GET.get('status')
    selected_worker = request.GET.get('worker')

    if selected_status:
        tasks = tasks.filter(status=selected_status)

    if selected_worker:
        if selected_worker == 'unassigned':
            tasks = tasks.filter(assigned_to__isnull=True)
        else:
            tasks = tasks.filter(assigned_to_id=selected_worker)

    team_members = User.objects.filter(profile__team=profile.team)

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'profile': profile,
        'is_manager': profile.role == 'manager',
        'team_members': team_members,
        'selected_status': selected_status,
        'selected_worker': selected_worker
    })


# --- 4. יצירת משימה (Create Task) ---
@login_required
def create_task(request):
    if request.user.profile.role != 'manager':
        return redirect('task_list')

    if request.method == 'POST':
        # שימוש בשדה title כפי שמופיע במודל שלך
        Task.objects.create(
            title=request.POST.get('title'),
            description=request.POST.get('description'),
            due_date=request.POST.get('due_date'),
            team=request.user.profile.team,
            status='new'
        )
        return redirect('task_list')

    return render(request, 'tasks/create_task.html', {
        'today': timezone.now().date().isoformat()
    })


# --- 5. עריכת משימה (Edit Task) ---
@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, team=request.user.profile.team)

    if request.user.profile.role != 'manager':
        return redirect('task_list')

    if request.method == 'POST':
        task.title = request.POST.get('title')
        task.description = request.POST.get('description')
        task.due_date = request.POST.get('due_date')
        task.save()
        return redirect('task_list')

    return render(request, 'tasks/edit_task.html', {'task': task})


# --- 6. מחיקת משימה (Delete Task) ---
@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, team=request.user.profile.team)
    if request.user.profile.role == 'manager':
        task.delete()
    return redirect('task_list')


# --- 7. שיוך משימה לעובד (Assign Task) ---
@login_required
def assign_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, team=request.user.profile.team)
    # רק עובד יכול לשייך לעצמו משימה פנויה
    if request.user.profile.role == 'employee' and not task.assigned_to:
        task.assigned_to = request.user
        task.status = 'in_progress'
        task.save()
    return redirect('task_list')


# --- 8. שינוי סטטוס משימה (Change Status) ---
@login_required
def change_status(request, task_id):
    task = get_object_or_404(Task, id=task_id, team=request.user.profile.team)
    # רק המבצע של המשימה יכול לשנות לה סטטוס
    if task.assigned_to == request.user and request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()
    return redirect('task_list')


# --- 9. התנתקות (Logout) ---
def logout_view(request):
    logout(request)
    return redirect('register')