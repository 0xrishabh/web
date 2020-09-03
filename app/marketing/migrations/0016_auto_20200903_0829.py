# Generated by Django 2.2.4 on 2020-09-03 08:29

import datetime
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('marketing', '0015_auto_20200626_1424'),
    ]

    operations = [
        migrations.AddField(
            model_name='roundupemail',
            name='issue',
            field=models.SmallIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='roundupemail',
            name='news',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='roundupemail',
            name='release_date',
            field=models.DateField(default=datetime.datetime.now),
        ),
        migrations.AddField(
            model_name='roundupemail',
            name='updates',
            field=django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict),
        ),
        migrations.AddField(
            model_name='roundupemail',
            name='videos',
            field=models.TextField(blank=True, max_length=15000),
        ),
    ]