# Generated by Django 2.1.2 on 2019-01-18 18:32

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0006_bounty_estimated_hours'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='last_visit',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]