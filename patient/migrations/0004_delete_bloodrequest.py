# Generated by Django 4.2.19 on 2025-03-18 18:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('patient', '0003_bloodrequest'),
    ]

    operations = [
        migrations.DeleteModel(
            name='BloodRequest',
        ),
    ]
