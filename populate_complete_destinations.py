# C:\Users\ASUS\MyanmarTravelPlanner\planner\management\commands\populate_complete_destinations_fixed.py

from django.core.management.base import BaseCommand
from planner.models import Destination
import os
from django.conf import settings
from django.core.files import File


class Command(BaseCommand):
    help = 'Populate complete destination data with correct folder names'

    def handle(self, *args, **kwargs):
        # First, get all actual folder names
        base_dir = os.path.join(settings.MEDIA_ROOT, 'destinations')
        actual_folders = []
        
        if os.path.exists(base_dir):
            actual_folders = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
            self.stdout.write(f'📂 Actual folders found: {actual_folders}')
        
        destination_data = {
            # 1. Yangon
            'Yangon': {
                'latitude': 16.8409,
                'longitude': 96.1735,
                'history': 'Former capital of Myanmar until 2005...',
                'attractions': '• Shwedagon Pagoda (2,500 years old, covered in gold)...',
                'activities': '• Visit golden pagodas at sunrise or sunset...',
                'cultural_info': 'Mix of British colonial architecture and traditional Burmese culture...',
                'best_time_to_visit': 'November to February (cool and dry season)',
                'local_cuisine': '• Mohinga (national dish - fish noodle soup)...',
                'tips': '• Visit Shwedagon Pagoda at sunset for magical lighting...',
                'folder_name': 'Yangon'  # This should match your actual folder
            },
            # 2. Mandalay
            'Mandalay': {
                'latitude': 21.9588,
                'longitude': 96.0891,
                'history': 'Last royal capital of the Burmese monarchy...',
                'folder_name': 'Mandalay'
            },
            # 3. Bagan
            'Bagan': {
                'latitude': 21.1717,
                'longitude': 94.8585,
                'history': 'Ancient capital of the Pagan Kingdom...',
                'folder_name': 'Bagan'
            },
            # 4. Inle Lake
            'Inle Lake': {
                'latitude': 20.5860,
                'longitude': 96.9100,
                'history': 'Freshwater lake at 880m altitude...',
                'folder_name': 'InleLake'  # ADJUST THIS based on actual folder
            },
            # ... continue with all destinations
        }

        # Map destination names to actual folder names
        folder_mapping = {}
        for folder in actual_folders:
            # Try to match folder names with destination names
            folder_lower = folder.lower().replace(' ', '').replace('_', '').replace('-', '')
            
            for dest_name in destination_data.keys():
                dest_lower = dest_name.lower().replace(' ', '').replace('_', '').replace('-', '')
                if folder_lower == dest_lower:
                    folder_mapping[dest_name] = folder
                    break
        
        self.stdout.write(f'📋 Folder mapping: {folder_mapping}')

        for dest_name, data in destination_data.items():
            try:
                destination = Destination.objects.get(name=dest_name)
                self.stdout.write(f'\n🔍 Processing {dest_name}...')

                # Text fields
                for field in [
                    'history', 'attractions', 'activities',
                    'cultural_info', 'best_time_to_visit',
                    'local_cuisine', 'tips'
                ]:
                    if field in data:
                        setattr(destination, field, data[field])

                # Coordinates
                destination.latitude = data.get('latitude')
                destination.longitude = data.get('longitude')

                # Images - use actual folder name
                folder_name = folder_mapping.get(dest_name, data.get('folder_name'))
                
                if folder_name:
                    folder_path = os.path.join(base_dir, folder_name)
                    
                    if os.path.exists(folder_path):
                        # Clear existing images first
                        if destination.main_image:
                            destination.main_image.delete(save=False)
                        if destination.image:
                            destination.image.delete(save=False)
                        for i in range(1, 5):
                            field_name = f'gallery_image{i}'
                            if hasattr(destination, field_name):
                                img = getattr(destination, field_name)
                                if img:
                                    img.delete(save=False)
                        
                        # Main image
                        main_image = os.path.join(folder_path, 'main.jpg')
                        if os.path.exists(main_image):
                            with open(main_image, 'rb') as f:
                                destination.main_image.save(
                                    'main.jpg',  # Just the filename
                                    File(f),
                                    save=False
                                )
                        
                        # Gallery images
                        for i in range(1, 5):
                            gallery_image = os.path.join(folder_path, f'gallery{i}.jpg')
                            field_name = f'gallery_image{i}'
                            
                            if os.path.exists(gallery_image) and hasattr(destination, field_name):
                                with open(gallery_image, 'rb') as f:
                                    getattr(destination, field_name).save(
                                        f'gallery{i}.jpg',
                                        File(f),
                                        save=False
                                    )

                destination.save()
                self.stdout.write(self.style.SUCCESS(f'✅ Updated {dest_name}'))

            except Destination.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'❌ Destination {dest_name} not found'))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'❌ Error updating {dest_name}: {str(e)}'))

        self.stdout.write(self.style.SUCCESS('\n🎉 DESTINATIONS UPDATED!'))