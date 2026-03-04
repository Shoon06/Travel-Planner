# C:\Users\ASUS\MyanmarTravelPlanner\planner\management\commands\delete_all_attractions.py

from django.core.management.base import BaseCommand
from planner.models import Destination

class Command(BaseCommand):
    help = 'Delete ALL existing attractions from the database'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('⚠️ WARNING: This will delete ALL attractions!'))
        self.stdout.write(self.style.WARNING('Press Ctrl+C to cancel or wait 5 seconds to continue...'))
        
        import time
        time.sleep(5)
        
        # Find all attractions (destinations with type='attraction')
        attractions = Destination.objects.filter(type='attraction')
        count = attractions.count()
        
        self.stdout.write(f"\n📊 Found {count} attractions to delete")
        
        if count > 0:
            # Delete all attractions
            attractions.delete()
            self.stdout.write(self.style.SUCCESS(f"✅ Successfully deleted {count} attractions"))
        else:
            self.stdout.write("ℹ️ No attractions found to delete")
        
        # Also delete any activities if they exist
        activities = Destination.objects.filter(type='activity')
        activity_count = activities.count()
        
        if activity_count > 0:
            activities.delete()
            self.stdout.write(self.style.SUCCESS(f"✅ Successfully deleted {activity_count} activities"))
        
        self.stdout.write(self.style.SUCCESS("\n✅ Database cleaned! Ready for new attractions."))