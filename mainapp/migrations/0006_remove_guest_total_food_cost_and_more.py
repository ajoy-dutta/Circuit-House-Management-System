# Generated by Django 5.1.4 on 2024-12-27 07:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('mainapp', '0005_guest_total_food_cost_guest_total_other_cost'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='guest',
            name='total_food_cost',
        ),
        migrations.RemoveField(
            model_name='guest',
            name='total_other_cost',
        ),
    ]
