# Generated by Django 4.2.4 on 2023-08-23 15:38

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('students_app', '0003_rename_address_modelstaff_address_text'),
    ]

    operations = [
        migrations.AlterField(
            model_name='modelsubjects',
            name='staff_id',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL),
        ),
    ]
