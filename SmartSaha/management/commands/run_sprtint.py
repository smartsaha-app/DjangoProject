# agriculture/management/commands/run_sprint.py
from django.core.management.base import BaseCommand
from SmartSaha.services import SprintPlanner


class Command(BaseCommand):
    help = 'Planifie et exécute un sprint de développement'

    def add_arguments(self, parser):
        parser.add_argument('sprint_number', type=int, help='Numéro du sprint')

    def handle(self, *args, **options):
        sprint_planner = SprintPlanner()
        sprint_number = options['sprint_number']

        sprint_planner.plan_sprint(sprint_number)
        self.stdout.write(
            self.style.SUCCESS(f'Sprint {sprint_number} planifié avec succès!')
        )