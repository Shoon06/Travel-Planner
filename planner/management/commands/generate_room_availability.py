# C:\Users\ASUS\MyanmarTravelPlanner\planner\management\commands\generate_room_availability.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from planner.models_room import Room, RoomAvailability
from django.db import transaction
import time

class Command(BaseCommand):
    help = 'Generate room availability for 60 days in advance (batched)'
    
    def add_arguments(self, parser):
        parser.add_argument('--days', type=int, default=60, help='Number of days to generate availability for')
        parser.add_argument('--batch-size', type=int, default=1000, help='Number of records to create per batch')
    
    def handle(self, *args, **options):
        days = options['days']
        batch_size = options['batch_size']
        today = timezone.now().date()
        end_date = today + timedelta(days=days)
        
        self.stdout.write(f"Generating room availability from {today} to {end_date}")
        
        # Get all active rooms
        rooms = list(Room.objects.filter(is_active=True).values_list('id', flat=True))
        total_rooms = len(rooms)
        self.stdout.write(f"Found {total_rooms} active rooms")
        
        if total_rooms == 0:
            self.stdout.write(self.style.WARNING('No rooms found. Please create rooms first.'))
            return
        
        # Calculate total records to create
        total_records = total_rooms * days
        self.stdout.write(f"Total records to create: {total_records}")
        
        # Confirm with user
        confirm = input(f"This will create {total_records} records. Continue? (y/n): ")
        if confirm.lower() != 'y':
            self.stdout.write(self.style.WARNING('Operation cancelled.'))
            return
        
        created_count = 0
        skipped_count = 0
        batch_count = 0
        start_time = time.time()
        
        # Process in batches by room
        for i in range(0, len(rooms), batch_size):
            room_batch = rooms[i:i+batch_size]
            batch_count += 1
            
            self.stdout.write(f"Processing batch {batch_count}: rooms {i+1} to {i+len(room_batch)}")
            
            # Create availability records for this batch of rooms
            batch_created = self.create_availability_for_rooms(room_batch, today, end_date)
            created_count += batch_created
            
            # Progress report
            elapsed = time.time() - start_time
            rate = created_count / elapsed if elapsed > 0 else 0
            self.stdout.write(
                self.style.SUCCESS(
                    f"  Created {batch_created} records. Total: {created_count}/{total_records} "
                    f"({(created_count/total_records*100):.1f}%) - {rate:.0f} records/sec"
                )
            )
        
        elapsed = time.time() - start_time
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Successfully generated {created_count} availability records in {elapsed:.1f} seconds\n'
                f'   Average: {created_count/elapsed:.0f} records/sec'
            )
        )
    
    @transaction.atomic
    def create_availability_for_rooms(self, room_ids, start_date, end_date):
        """Create availability records for a batch of rooms"""
        from django.db import connection
        
        created = 0
        current_date = start_date
        
        # Build list of dates
        dates = []
        while current_date <= end_date:
            dates.append(current_date)
            current_date += timedelta(days=1)
        
        # Get existing records to avoid duplicates
        existing = set()
        for room_id in room_ids:
            existing_records = RoomAvailability.objects.filter(
                room_id__in=room_ids,
                date__range=[start_date, end_date]
            ).values_list('room_id', 'date')
            
            for room_id, date in existing_records:
                existing.add((room_id, date))
        
        # Prepare bulk create list
        availability_list = []
        for room_id in room_ids:
            for date in dates:
                if (room_id, date) not in existing:
                    availability_list.append(
                        RoomAvailability(
                            room_id=room_id,
                            date=date,
                            is_available=True
                        )
                    )
                    
                    # Bulk create in smaller chunks to avoid memory issues
                    if len(availability_list) >= 1000:
                        RoomAvailability.objects.bulk_create(availability_list, ignore_conflicts=True)
                        created += len(availability_list)
                        availability_list = []
        
        # Create remaining records
        if availability_list:
            RoomAvailability.objects.bulk_create(availability_list, ignore_conflicts=True)
            created += len(availability_list)
        
        return created