from django.db import migrations

class Migration(migrations.Migration):

    dependencies = [
        ('MoneyMapControl', '0001_initial'),
    ]

    operations = [
        # removed duplicate field - target_amount already exists in 0001
    ]