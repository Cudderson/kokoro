# Generated by Django 3.1.7 on 2021-04-02 21:27

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('kokoro_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='PerfectBalance',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('perfect_mind', models.CharField(max_length=100)),
                ('perfect_body', models.CharField(max_length=100)),
                ('perfect_soul', models.CharField(max_length=100)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]