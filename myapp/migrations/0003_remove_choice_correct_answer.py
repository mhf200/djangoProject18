# Generated by Django 4.2.1 on 2023-06-05 08:58

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('myapp', '0002_choice_correct_answer'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='choice',
            name='correct_answer',
        ),
    ]
