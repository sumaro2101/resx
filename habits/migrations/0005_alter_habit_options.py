# Generated by Django 5.0.7 on 2024-07-20 18:08

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('habits', '0004_alter_habit_options'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='habit',
            options={'ordering': ['time_to_do'], 'verbose_name': 'Habit', 'verbose_name_plural': 'Habits'},
        ),
    ]
