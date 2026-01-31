from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.contrib.auth.models import User
from datetime import date
from .models import Task, Profile, Team
from .forms import SimpleRegistrationForm, ProfileSetupForm


def is_manager(user):
    return hasattr(user, 'profile') and user.profile.role == 'manager'


def is_worker(user):
    return hasattr(user, 'profile') and user.profile.role == 'employee'


def register(request):
    if request.method == 'POST':
        form = SimpleRegistrationForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password']
            )
            return render(request, 'registration/register.html', {
                'success': True, 'username': user.username, 'form': SimpleRegistrationForm()
            })
    else:
        form = SimpleRegistrationForm()
    return render(request, 'registration/register.html', {'form': form, 'success': False})


@login_required
def setup_profile(request):
    # אם המשתמש כבר מוגדר לגמרי, שלח אותו למשימות
    if hasattr(request.user, 'profile') and request.user.profile.role and request.user.profile.team:
        return redirect('task_list')

    if not Team.objects.exists():
        Team.objects.create(name="צוות פיתוח")
        Team.objects.create(name="צוות שיווק")

    if request.method == 'POST':
        form = ProfileSetupForm(request.POST)
        if form.is_valid():
            # מחיקה של פרופיל ישן/חלקי לפני יצירת החדש
            Profile.objects.filter(user=request.user).delete()
            Profile.objects.create(
                user=request.user,
                team=form.cleaned_data['team'],
                role=form.cleaned_data['role']
            )
            return redirect('task_list')
    else:
        form = ProfileSetupForm()

    return render(request, 'registration/setup_profile.html', {'form': form})


@login_required
def task_list(request):
    if not hasattr(request.user, 'profile'):
        return redirect('setup_profile')

    profile = request.user.profile
    tasks = Task.objects.filter(team=profile.team).order_by('due_date')

    status_filter = request.GET.get('status')
    worker_filter = request.GET.get('worker')

    if status_filter:
        tasks = tasks.filter(status=status_filter)
    if worker_filter:
        if worker_filter == 'unassigned':
            tasks = tasks.filter(assigned_to__isnull=True)
        else:
            tasks = tasks.filter(assigned_to__id=worker_filter)

    team_members = User.objects.filter(profile__team=profile.team)

    return render(request, 'tasks/task_list.html', {
        'tasks': tasks,
        'team_members': team_members,
        'selected_status': status_filter,
        'selected_worker': worker_filter,
        'is_manager': is_manager(request.user),
        'is_worker': is_worker(request.user),
    })


@login_required
def create_task(request):
    if not is_manager(request.user):
        return HttpResponseForbidden("גישה נדחתה")
    if request.method == 'POST':
        Task.objects.create(
            title=request.POST['title'],
            description=request.POST.get('description', ''),
            due_date=request.POST['due_date'],
            team=request.user.profile.team,
            status='new'
        )
        return redirect('task_list')
    return render(request, 'tasks/create_task.html', {'today': date.today().isoformat()})


@login_required
def edit_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, team=request.user.profile.team)
    if not is_manager(request.user) or task.assigned_to:
        return HttpResponseForbidden("לא ניתן לערוך")
    if request.method == 'POST':
        task.title = request.POST['title']
        task.description = request.POST.get('description', '')
        task.due_date = request.POST['due_date']
        task.save()
        return redirect('task_list')
    return render(request, 'tasks/edit_task.html', {'task': task})


@login_required
def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, team=request.user.profile.team)
    if is_manager(request.user) and not task.assigned_to:
        task.delete()
    return redirect('task_list')


@login_required
def assign_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, team=request.user.profile.team)
    if is_worker(request.user) and not task.assigned_to:
        task.assigned_to = request.user
        task.status = 'in_progress'
        task.save()
    return redirect('task_list')


@login_required
def change_status(request, task_id):
    task = get_object_or_404(Task, id=task_id, team=request.user.profile.team)
    if task.assigned_to == request.user and request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in dict(Task.STATUS_CHOICES):
            task.status = new_status
            task.save()
    return redirect('task_list')