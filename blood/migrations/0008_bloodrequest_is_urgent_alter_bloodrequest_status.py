# Generated by Django 4.2.19 on 2025-03-22 10:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blood', '0007_alter_bloodrequest_request_by_patient'),
    ]

    operations = [
        migrations.AddField(
            model_name='bloodrequest',
            name='is_urgent',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='bloodrequest',
            name='status',
            field=models.CharField(choices=[('PENDING', 'Pending'), ('APPROVED', 'Approved'), ('REJECTED', 'Rejected')], default='PENDING', max_length=20),
        ),
    ]
