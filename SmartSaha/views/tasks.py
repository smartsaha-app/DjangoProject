from datetime import timedelta

from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.shortcuts import render
from django.utils import timezone
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from SmartSaha.models import Task, TaskPriority, TaskStatus, ParcelCrop
from SmartSaha.serializers import TaskSerializer, TaskPrioritySerializer, TaskStatusSerializer


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ['name', 'due_date', 'priority', 'status']

    def get_queryset(self):
        # Filtrer les tâches de l'utilisateur connecté
        return Task.objects.filter(parcelCrop__parcel__owner= self.request.user)

    @action(detail=True, methods=['post'])
    def mark_done(self, request, pk=None):
        task = self.get_object()
        task.mark_as_done()
        return Response({"status": "Task marked as done", "completed_at": task.completed_at})

    @action(detail=False, methods=['get'])
    def upcoming(self, request):
        """Notifier les tâches dues dans 24h."""
        tomorrow = timezone.now().date() + timedelta(days=1)
        tasks_due = Task.objects.filter(parcelCrop__parcel__owner=request.user, due_date=tomorrow)
        for task in tasks_due:
            send_mail(
                subject=f"Task due tomorrow: {task.name}",
                message=f"Your task '{task.name}' is due on {task.due_date}.",
                from_email=None,
                recipient_list=[request.user.email],
            )
        return Response({"notified_tasks": [t.name for t in tasks_due]})

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """Résumé par status et priorité"""
        tasks = Task.objects.filter(parcelCrop__parcel__owner=request.user)
        summary = {
            "by_status": {},
            "by_priority": {}
        }
        for status in TaskStatus.objects.all():
            summary["by_status"][status.name] = tasks.filter(status=status).count()
        for priority in TaskPriority.objects.all():
            summary["by_priority"][priority.name] = tasks.filter(priority=priority).count()
        return Response(summary)

class TaskStatusViewSet(viewsets.ModelViewSet):
    queryset = TaskStatus.objects.all()
    serializer_class = TaskStatusSerializer
    permission_classes = [permissions.AllowAny]

class TaskPriorityViewSet(viewsets.ModelViewSet):
    queryset = TaskPriority.objects.all()
    serializer_class = TaskPrioritySerializer
    permission_classes = [permissions.AllowAny]


@login_required(login_url='login')
def tasks_view(request):
    # Récupère toutes les parcelles de l'utilisateur
    parcel_crops = ParcelCrop.objects.filter(parcel__owner=request.user)

    # Récupère toutes les tâches liées à ces parcelles
    tasks = Task.objects.filter(parcelCrop__in=parcel_crops).select_related('parcelCrop', 'status')
    if tasks is None:
        return  render(request, 'tasks.html', {
            'tasks': None
        })
    return render(request, 'tasks.html', {
        'tasks': tasks
    })