import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mtravel.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
django.setup()

# Delete migration files (be careful with this!)
import shutil

# Remove migration files
migration_dirs = [
    'planner/migrations/',
    'users/migrations/',
]

for dir_path in migration_dirs:
    if os.path.exists(dir_path):
        for filename in os.listdir(dir_path):
            if filename != '__init__.py':
                file_path = os.path.join(dir_path, filename)
                try:
                    if os.path.isfile(file_path):
                        os.unlink(file_path)
                        print(f"Deleted: {file_path}")
                except Exception as e:
                    print(f"Error deleting {file_path}: {e}")

print("Migration files cleared. Now run:")
print("1. python manage.py makemigrations")
print("2. python manage.py migrate")
print("3. python manage.py createsuperuser")
print("4. python populate_all_data.py")