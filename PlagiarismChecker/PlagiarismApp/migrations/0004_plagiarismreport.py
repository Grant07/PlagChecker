# Generated by Django 5.0.3 on 2024-03-28 20:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('PlagiarismApp', '0003_alter_student_year_of_study'),
    ]

    operations = [
        migrations.CreateModel(
            name='PlagiarismReport',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('current_submission_id', models.UUIDField()),
                ('similarity_results', models.JSONField()),
            ],
        ),
    ]
