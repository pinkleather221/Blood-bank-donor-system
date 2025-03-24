# Generated by Django 4.2.19 on 2025-03-22 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('donor', '0006_blooddonate_health_check_passed_donor_email_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='blooddonate',
            name='health_check',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('PASSED', 'Passed'), ('FAILED', 'Failed')], default='PENDING', max_length=20),
        ),
        migrations.AddField(
            model_name='donor',
            name='health_status',
            field=models.CharField(choices=[('ELIGIBLE', 'Eligible'), ('INELIGIBLE', 'Ineligible'), ('UNKNOWN', 'Unknown')], default='UNKNOWN', max_length=20),
        ),
        migrations.AddField(
            model_name='donor',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved')], default='PENDING', max_length=20),
        ),
        migrations.AlterField(
            model_name='blooddonate',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', max_length=20),
        ),
    ]
