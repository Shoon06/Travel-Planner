# C:\Users\ASUS\MyanmarTravelPlanner\planner\migrations\XXXX_alter_hotel_price_per_night.py
# Replace XXXX with your next migration number (e.g., 0019)

from django.db import migrations, models
import django.core.validators  # Add this import

class Migration(migrations.Migration):

    dependencies = [
        ('planner', '0018_roomavailability_room_planner_roo_hotel_i_e17a2d_idx_and_more'),  # Use your actual last migration number
    ]

    operations = [
        migrations.AlterField(
            model_name='hotel',
            name='price_per_night',
            field=models.DecimalField(
                blank=True, 
                null=True,
                decimal_places=0, 
                max_digits=10,
                validators=[django.core.validators.MinValueValidator(0)],
                help_text='Price in MMK (Myanmar Kyat)'
            ),
        ),
    ]