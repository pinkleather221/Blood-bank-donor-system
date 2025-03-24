# Generated by Django 4.2.19 on 2025-03-23 15:09

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('blood', '0008_bloodrequest_is_urgent_alter_bloodrequest_status'),
    ]

    operations = [
        migrations.CreateModel(
            name='EmailCampaign',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('subject', models.CharField(max_length=255)),
                ('message', models.TextField()),
                ('recipient_type', models.CharField(max_length=50)),
                ('recipient_count', models.IntegerField(default=0)),
                ('date_sent', models.DateTimeField(auto_now_add=True)),
                ('sent_by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
