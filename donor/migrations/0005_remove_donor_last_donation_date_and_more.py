# Generated by Django 4.2.19 on 2025-03-18 18:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donor', '0004_donor_last_donation_date_alter_donor_profile_pic'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='donor',
            name='last_donation_date',
        ),
        migrations.AlterField(
            model_name='donor',
            name='profile_pic',
            field=models.ImageField(upload_to='profile_pic/Donor/'),
        ),
    ]
