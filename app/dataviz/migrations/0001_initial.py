# Generated by Django 2.1.4 on 2018-12-26 17:16

import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import economy.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='DataPayload',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_on', models.DateTimeField(db_index=True, default=economy.models.get_time)),
                ('modified_on', models.DateTimeField(default=economy.models.get_time)),
                ('key', models.CharField(db_index=True, help_text='key for this data report', max_length=255)),
                ('report', models.CharField(blank=True, help_text='The report associated with this project', max_length=255)),
                ('payload', django.contrib.postgres.fields.jsonb.JSONField(blank=True, default=dict)),
                ('comments', models.TextField(blank=True)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
