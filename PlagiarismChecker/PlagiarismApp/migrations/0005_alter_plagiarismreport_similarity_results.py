# Generated by Django 5.0.3 on 2024-03-28 21:02

import json.encoder
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PlagiarismApp', '0004_plagiarismreport'),
    ]

    operations = [
        migrations.AlterField(
            model_name='plagiarismreport',
            name='similarity_results',
            field=models.JSONField(encoder=json.encoder.JSONEncoder),
        ),
    ]