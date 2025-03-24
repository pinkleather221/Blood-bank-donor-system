# Generated by Django 4.2.19 on 2025-03-22 10:55

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('donor', '0007_blooddonate_health_check_donor_health_status_and_more'),
        ('patient', '0005_patient_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='assigned_donor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_patients', to='donor.donor'),
        ),
    ]
