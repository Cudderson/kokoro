# Generated by Django 3.1.7 on 2021-05-02 02:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('kokoro_app', '0012_contactinfo'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contactinfo',
            name='user_email',
            field=models.EmailField(max_length=254, null=True),
        ),
    ]
