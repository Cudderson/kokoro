# Generated by Django 3.1.7 on 2021-06-24 19:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kokoro_app', '0011_auto_20210624_1413'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='supportreport',
            name='owner',
        ),
        migrations.AddField(
            model_name='supportreport',
            name='username',
            field=models.CharField(default='', max_length=150),
        ),
    ]
