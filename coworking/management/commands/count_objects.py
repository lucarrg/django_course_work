from django.core.management.base import BaseCommand
from coworking.models import Coworking, Workplace

class Command(BaseCommand):
    help = 'Выводит количество коворкингов и рабочих мест в базе'

    def handle(self, *args, **options):
        coworking_count = Coworking.objects.count()
        workplace_count = Workplace.objects.count()

        self.stdout.write(self.style.SUCCESS(f'Коворкингов в базе: {coworking_count}'))
        self.stdout.write(self.style.SUCCESS(f'Рабочих мест в базе: {workplace_count}'))
