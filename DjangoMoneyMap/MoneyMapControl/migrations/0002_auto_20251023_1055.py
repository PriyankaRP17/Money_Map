from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('MoneyMapControl', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='goal',
            name='target_amount',
            field=models.DecimalField(default=0, max_digits=12, decimal_places=2),
        ),
    ]
