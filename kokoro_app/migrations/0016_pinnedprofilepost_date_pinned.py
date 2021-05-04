# Generated by Django 3.1.7 on 2021-05-04 19:34

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('kokoro_app', '0015_pinnedprofilepost'),
    ]

    operations = [
        migrations.AddField(
            model_name='pinnedprofilepost',
            name='date_pinned',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
