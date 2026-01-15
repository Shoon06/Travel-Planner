# C:\Users\ASUS\MyanmarTravelPlanner\planner\management\commands\generate_schedules.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from planner.models import BusService, TransportSchedule
from datetime import datetime, timedelta
import calendar

class Command(BaseCommand):
    help = 'Generate transport schedules for all active buses'

    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=90, help='Number of days to generate schedules for')
        parser.add_argument('--overwrite', action='store_true', help='Overwrite existing schedules')

    def handle(self, *args, **options):
        days = options['days']
        overwrite = options['overwrite']
        
        start_date = timezone.now().date()
        end_date = start_date + timedelta(days=days - 1)
        
        self.stdout.write(f'Generating bus schedules from {start_date} to {end_date}...')
        
        # Get all active buses
        buses = BusService.objects.filter(is_active=True)
        
        total_schedules_created = 0
        
        for bus in buses:
            schedules_created = 0
            current_date = start_date
            
            while current_date <= end_date:
                # Check if schedule already exists
                schedule_exists = TransportSchedule.objects.filter(
                    transport_type='bus',
                    transport_id=bus.id,
                    travel_date=current_date
                ).exists()
                
                if not schedule_exists or overwrite:
                    # Create or update schedule
                    schedule, created = TransportSchedule.objects.update_or_create(
                        transport_type='bus',
                        transport_id=bus.id,
                        travel_date=current_date,
                        defaults={
                            'departure_time': bus.departure_time,
                            'total_seats': bus.total_seats,
                            'available_seats': bus.available_seats,
                            'price': bus.price,
                            'is_active': bus.is_active,
                        }
                    )
                    if created:
                        schedules_created += 1
                
                current_date += timedelta(days=1)
            
            if schedules_created > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'Created {schedules_created} schedules for {bus.company} bus')
                )
                total_schedules_created += schedules_created
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {total_schedules_created} bus schedules!')
        )